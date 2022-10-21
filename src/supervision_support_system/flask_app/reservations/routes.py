from flask import Blueprint, redirect, render_template, request, make_response, jsonify, abort
from flask_login import login_required

from flask_app.reservations.forms import *
from flask_app.reservations.utils import *
from mail import send_email

reservations = Blueprint('reservations', __name__)


@reservations.route("/reservation_calendar", methods=['GET', 'POST'])
@login_required
def reservation_calendar():
    title = 'calendar_of_consultations'
    info_board = get_info_board(title)
    content = info_board.content

    if current_user_supervisor():
        form = NoteForm(content=content)

        if form.validate_on_submit():
            change_info_board_content(info_board, form.content.data)
            return redirect(url_for('reservations.reservation_calendar'))

        return render_template('supervisor/reservation_calendar.html', form=form, content=content)

    return render_template('student/reservation_calendar.html', content=content)


@reservations.route("/consultation_days", methods=["POST"])
@login_required
def consultation_days():
    req = request.get_json()
    month = (req['month'] + 1) % 13
    year = req['year']

    month_occupancy = {
        "free_consultation_days": get_consultation_days(month, year, 'free'),
        "full_consultation_days": get_consultation_days(month, year, 'busy') + get_consultation_days(month, year,
                                                                                                     'blocked'),
    }

    res = make_response(jsonify(month_occupancy), 200)
    return res


@reservations.route("/reservations/<int:day>/<int:month>/<int:year>", methods=["GET", "POST"])
@login_required
def reservation_list(day, month, year):
    try:
        date_str = f'{year}-{(int(month) + 1) % 13}-{day}'
        date_var = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        abort(404)

    if not get_consultation_term_list_by_date(date_var):
        abort(404)

    if current_user_supervisor():
        return render_template('supervisor/reservations.html',
                               reserve_info=get_reservations_info_supervisor(date_var),
                               waiting_list=get_wait_list_info(date_var),
                               add_reservation_form=AddReservationAdminForm(date=date_var),
                               delete_reservation_form=DeleteReservationAdminForm(date=date_var),
                               disable_term_form=DisableTermAdminForm(date=date_var))
    else:
        return render_template('student/reservations.html',
                               reserve_info=get_reservations_info_student(date_var),
                               add_reservation_form=AddReservationUserForm(date=date_var),
                               delete_reservation_form=DeleteReservationUserForm(date=date_var),
                               add_waiter_form=AddWaiterForm(date=date_var),
                               move_reservation=MoveReservationUserForm(date=date_var)
                               )


@reservations.route("/add_reservation", methods=["POST"])
@login_required
def add_reservation():
    if current_user_supervisor():
        form = AddReservationAdminForm()
        date_var = form.date.data

        if form.validate_on_submit():
            time_var = form.time.data
            reserved_user_id = form.student.data
            creator_user = current_user

            consultation_term = get_consultation_term_by_date_time(date_var, time_var)

            add_reservation_(consultation_term, creator_user, reserved_user_id)

            flash(f'Rezervace byla vytvořena', category='success')
            return redirect(get_reservations_url(date_var))
    else:
        form = AddReservationUserForm()
        date_var = form.date.data

        if form.validate_on_submit():
            time_var = form.time.data
            reserved_user_id = current_user.id
            note = form.note.data

            consultation_term = get_consultation_term_by_date_time(date_var, time_var)

            add_reservation_(consultation_term, current_user, reserved_user_id, note)

            flash(f'Rezervace byla vytvořena', category='success')
            return redirect(get_reservations_url(date_var))
    return '<script>document.location.href = document.referrer</script>'


@reservations.route("/delete_reservation", methods=["POST"])
@login_required
def cancel_reservation():
    if current_user_supervisor():
        form = DeleteReservationAdminForm()
        if form.validate_on_submit():
            date_var = form.date.data
            time_var = form.time.data
            cancel_reservation_(date_var, time_var)
            wait_list_emails = get_wait_list_emails(date_var)

            title = 'Čekací listina'
            content = f'''Uvolnilo místo dne {date_var.strftime('%d-%m-%Y')}, {time_var.strftime('%H:%M')}'''

            for email in wait_list_emails:
                send_email(email, title=title, content=content)

            release_wait_list(date_var)
            return redirect(get_reservations_url(date_var))
    else:
        form = DeleteReservationUserForm()
        if form.validate_on_submit():
            date_var = form.date.data
            time_var = form.time.data
            cancel_reservation_(date_var, time_var)
            wait_list_emails = get_wait_list_emails(date_var)

            title = 'Čekací listina'
            content = f'''Uvolnilo místo dne {date_var.strftime('%d-%m-%Y')}, {time_var.strftime('%H:%M')}'''

            for email in wait_list_emails:
                send_email(email, title=title, content=content)

            release_wait_list(date_var)
            return redirect(get_reservations_url(date_var))
    return '<script>document.location.href = document.referrer</script>'


@reservations.route("/disable_term", methods=["POST"])
@login_required
def disable_term():
    form = DisableTermAdminForm()

    if form.validate_on_submit():
        date_var = form.date.data
        time_str_list = form.time_list.data
        note = form.note.data

        for time_str in time_str_list:
            time_var = dt.datetime.strptime(time_str, '%H:%M').time()
            consultation_term = get_consultation_term_by_date_time(date_var, time_var)
            disable_consultation_term(consultation_term, note)

        flash(f'Konzultační termín byl zablokován', category='success')
    else:
        date_var = form.date.data
    return redirect(get_reservations_url(date_var))


@reservations.route("/add_waiter", methods=["POST"])
@login_required
def add_waiter():
    form = AddWaiterForm()
    date_var = form.date.data

    if form.validate_on_submit():
        user_id = current_user.id
        add_student_to_wait_list(date_var, user_id)
        flash(f'Byli jste přidáni na čekací listinu', category='success')

    return redirect(get_reservations_url(date_var))


@reservations.route("/move_reservation", methods=["POST"])
@login_required
def move_reservation():
    form = MoveReservationUserForm()

    if form.validate_on_submit():
        # Form data
        date_var = form.date.data
        time_var = form.time.data
        new_time_var = datetime.strptime(form.new_time.data, '%H:%M').time()

        consultation_term = get_consultation_term_by_date_time(date_var, time_var)
        new_consultation_term = get_consultation_term_by_date_time(date_var, new_time_var)

        move_reservation_(consultation_term, new_consultation_term)

    else:
        date_var = form.date.data
        flash(f'Konzultaci již nemůžete přesunout, konzultace již začala', category='danger')

    return redirect(get_reservations_url(date_var))


@reservations.route("/reservation_detail/<int:reservation_id>", methods=["GET", "POST"])
@login_required
def reservation_detail(reservation_id):
    if not get_reservation(reservation_id):
        abort(404)

    reservation = get_reservation(reservation_id)
    supervisor_note = reservation.supervisor_note
    student_note = reservation.student_note

    form = NoteForm(content=supervisor_note)

    if form.validate_on_submit():
        note = form.content.data
        change_supervisor_reservation_note(reservation, note)
        return redirect(url_for('reservations.reservation_detail', reservation_id=reservation_id))

    reserve_info = get_reservation_detail_info(reservation_id)

    if current_user_supervisor():
        return render_template('supervisor/reservation_detail.html', supervisor_note=supervisor_note,
                               student_note=student_note,
                               reserve_info=reserve_info, form=form)

    if current_student_reservation(reservation):
        return render_template('student/reservation_detail.html', student_note=student_note, reserve_info=reserve_info)

    abort(403)


@reservations.route("/reservations_history")
@login_required
def reservations_history():
    if current_user_supervisor():
        return render_template('supervisor/reservations_history.html', info=get_supervisor_reservation_history_info())
    return render_template('student/reservations_history.html', user_info=get_user_info(current_user),
                           reservation_info=get_student_reservation_history_info(current_user.id))
