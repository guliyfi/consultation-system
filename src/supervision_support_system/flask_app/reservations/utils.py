from flask import url_for, flash
from flask_login import current_user
from sqlalchemy import func, and_

from flask_app import db
from flask_app.models import ConsultationTerm, Reservation, User, InformationBoard, Supervisor, Student, WaitList
import calendar
import datetime as dt

from mail import send_email


def get_consultation_date_time_list(date_var, state):
    time_list = []
    consultation_term_list = get_consultation_term_list_by_date(date_var)
    for consultation in consultation_term_list:
        if consultation.state in state:
            time_list.append(consultation.start_time.strftime("%H:%M"))
    return time_list


def get_consultation_term_list_by_date(date_var):
    return ConsultationTerm.query.filter_by(date=date_var).order_by(ConsultationTerm.start_time).all()


def get_consultation_term_by_date_time(date_var, time_var):
    return ConsultationTerm.query.filter_by(date=date_var) \
        .filter_by(start_time=time_var).first()


def get_reservation_by_consultation_term(consultation_term):
    reservation = Reservation.query.filter_by(consultation_term_id=consultation_term.id, state='active').first()
    if reservation:
        return reservation
    else:
        return Reservation.query.filter_by(consultation_term_id=consultation_term.id, state='blocked').first()


def return_student_tuple_list():
    student_tuple_list = []
    students = db.session.query(User.id, User.name, User.surname).filter(User.id == Student.id).all()
    student_tuple_list.append(('', ''))
    for el in students:
        student_tuple_list.append((el[0], el[1] + ' ' + el[2]))
    return student_tuple_list


def get_info_board(title):
    return InformationBoard.query.filter_by(title=title).first()


def current_user_supervisor():
    return Supervisor.query.filter_by(id=current_user.id).scalar()


def change_info_board_content(info_board, new_content):
    info_board.content = new_content
    db.session.commit()


def get_consultation_days(month, year, state):
    num_days = calendar.monthrange(year, month)[1]
    start_date = dt.date(year, month, 1)
    end_date = dt.date(year, month, num_days)

    consultation_term_day_list = db.session.query(func.extract("day", ConsultationTerm.date)).distinct(
        ConsultationTerm.date).filter(
        and_(ConsultationTerm.date >= start_date, ConsultationTerm.date <= end_date,
             ConsultationTerm.state == state)).all()

    consultation_term_day_list = [int(item) for t in consultation_term_day_list for item in t]

    return consultation_term_day_list


def get_reservations_info_supervisor(date_var):
    reservations_info = []

    consultation_term_list = get_consultation_term_list_by_date(date_var)
    for consultation_term in consultation_term_list:
        list_var = [consultation_term.start_time]
        if consultation_term.state == 'free':
            list_var.extend([None, None, None])
            list_var.append(get_supervisor_button(date_var, consultation_term))
        elif consultation_term.state == 'busy':
            reservation = get_reservation_by_consultation_term(consultation_term)
            user = get_user_by_reservation(reservation)
            list_var.extend([user.name, user.surname, reservation.id])
            list_var.append(get_supervisor_button(date_var, consultation_term))
        elif consultation_term.state == 'blocked':
            reservation = get_reservation_by_consultation_term(consultation_term)
            if reservation:
                user = get_user_by_reservation(reservation)
                list_var.extend([user.name, user.surname, reservation.id])
                list_var.append(get_supervisor_button(date_var, consultation_term))
            else:
                list_var.extend([None, None, None])
                list_var.append(get_supervisor_button(date_var, consultation_term))

        reservations_info.append(list_var)

    return reservations_info


def get_supervisor_button(date_var, consultation_term):
    if consultation_term.state == 'blocked':
        return "blocked_btn"
    if date_var >= dt.date.today():
        if consultation_term.state == 'busy':
            return "unbook_btn"
        else:
            return "book_btn"
    else:
        return "no_btn"


def get_user_by_reservation(reservation):
    user_id = reservation.reserved_user_id
    return get_user_by_id(user_id)


def current_student_reservation(reservation):
    return get_user_by_reservation(reservation) == current_user


def get_user_by_id(user_id):
    return User.query.get(user_id)


def get_reservations_info_student(date_var):
    reservations_info = []

    consultation_term_list = get_consultation_term_list_by_date(date_var)
    for consultation_term in consultation_term_list:
        list_var = [consultation_term.start_time]
        if consultation_term.state == 'free':
            list_var.extend([None, None])
            list_var.append(get_user_button(date_var, consultation_term, None))
        elif consultation_term.state == 'busy':
            reservation = get_reservation_by_consultation_term(consultation_term)
            user = get_user_by_reservation(reservation)
            list_var.extend([user.name, user.surname])
            list_var.append(get_user_button(date_var, consultation_term, reservation))
        elif consultation_term.state == 'blocked':
            reservation = get_reservation_by_consultation_term(consultation_term)
            if reservation:
                user = get_user_by_reservation(reservation)
                list_var.extend([user.name, user.surname])
                list_var.append(get_user_button(date_var, consultation_term, reservation))
            else:
                list_var.extend([None, None])
                list_var.append(get_user_button(date_var, consultation_term, None))

        reservations_info.append(list_var)

    return reservations_info


def get_user_button(date_var, consultation_term, reservation):
    if consultation_term.state == 'blocked':
        return "blocked_btn"
    if date_var == dt.date.today():
        if consultation_term.state == 'busy':
            if reservation.reserved_user_id == current_user.id:
                return "move_btn"
            else:
                return "no_btn"
        else:
            return "book_btn"
    elif date_var > dt.date.today():
        if consultation_term.state == 'busy':
            if reservation.reserved_user_id == current_user.id:
                return "unbook_btn"
            else:
                return "no_btn"
        else:
            return "book_btn"
    else:
        return "no_btn"


def get_wait_list_info(date_var):
    student_name_surname_list = []
    student_id_list = []

    wait_list = get_wait_list(date_var)
    if wait_list:
        for student in wait_list.waiting_students:
            user = get_user_by_id(student.id)
            student_name_surname = user.name + ' ' + user.surname
            student_id_list.append(student.id)
            student_name_surname_list.append(student_name_surname)
    return zip(student_id_list, student_name_surname_list)


def get_wait_list(date_var):
    return db.session.query(WaitList).filter(WaitList.date == date_var).first()


def get_consultation_term_by_date_time(date_var, time_var):
    return ConsultationTerm.query.filter_by(date=date_var) \
        .filter_by(start_time=time_var).first()


def add_reservation_(consultation_term, creator_user, reserved_user_id, student_note=None):
    reservation = Reservation(reserved_user_id, creator_user.id, consultation_term.id, student_note)
    change_consultation_term_state(consultation_term, 'busy')
    db.session.add(reservation)
    db.session.commit()


def get_reservations_url(date_var):
    day = date_var.day
    month = date_var.month - 1
    year = date_var.year

    return url_for('reservations.reservation_list', day=day, month=month, year=year)


def change_consultation_term_state(consultation_term, state):
    consultation_term.state = state


def cancel_reservation_(date_var, time_var):
    consultation_term = get_consultation_term_by_date_time(date_var, time_var)
    reservation = get_reservation_by_consultation_term(consultation_term)

    if not current_user_supervisor() and reservation.reserved_user_id != current_user.id:
        flash('Nemáte právo zrušit rezervaci', category='danger')
        return

    if not current_user_supervisor() and reservation.supervisor_note is not None:
        flash('Tento termín nemůžete sami smazat, kontaktujte svého vyučujícího', category='warning')
        return

    change_consultation_term_state(consultation_term, 'free')
    reservation.state = 'cancelled'
    reservation.canceller_user_id = current_user.id
    reservation.cancellation_datetime = dt.datetime.now()

    db.session.commit()


def get_wait_list_emails(date_var):
    wait_list_emails = []
    wait_list = get_wait_list(date_var)
    for student in wait_list.waiting_students:
        user = get_user_by_id(student.id)
        wait_list_emails.append(user.email)
    return wait_list_emails


def release_wait_list(date_var):
    wait_list = get_wait_list(date_var)
    wait_list.waiting_students = []
    db.session.commit()


def disable_consultation_term(consultation_term, note):
    consultation_term.state = 'blocked'
    reservation = get_reservation_by_consultation_term(consultation_term)
    if reservation:
        reservation.state = 'blocked'
        reservation.cancellation_datetime = dt.datetime.now()
        reservation.canceller_user_id = current_user.id

        title = 'Zrušená rezervace'
        content = f'''Vaše rezervace na {consultation_term.date.strftime("%d-%m-%Y")} {consultation_term.start_time.strftime("%H:%M")} byla zrušena.''' + '\n' + note

        user = get_user_by_id(reservation.reserved_user_id)
        send_email(user.email, title, content)

    db.session.commit()


def add_student_to_wait_list(date_var, student_id):
    wait_list = get_wait_list(date_var)
    student = get_student_by_id(student_id)
    wait_list.waiting_students.append(student)
    db.session.add(wait_list)
    db.session.commit()


def get_student_by_id(user_id):
    return Student.query.get(user_id)


def move_reservation_(consultation_term, new_consultation_term):
    reservation = get_reservation_by_consultation_term(consultation_term)
    if current_user.id != reservation.reserved_user_id:
        flash('Nemáte právo posunut rezervaci', category='danger')
        return
    consultation_term.state = 'free'
    new_consultation_term.state = 'busy'
    reservation.consultation_term_id = new_consultation_term.id
    reservation.canceller_user_id = current_user.id
    reservation.cancellation_datetime = dt.datetime.now()
    db.session.commit()
    flash(f'Vaše rezervace byla úspěšně posunuta', category='success')


def get_reservation(reservation_id):
    return Reservation.query.get(reservation_id)


def change_supervisor_reservation_note(reservation, note):
    reservation.supervisor_note = note
    db.session.commit()


def get_reservation_detail_info(reservation_id):
    q = db.session.query(
        Reservation.reserved_user_id, Reservation.state, Reservation.creator_user_id,
        Reservation.canceller_user_id, ConsultationTerm.date, ConsultationTerm.start_time,
        Reservation.creation_datetime,
        Reservation.cancellation_datetime
    ).filter(
        Reservation.consultation_term_id == ConsultationTerm.id
    ).filter(
        Reservation.id == reservation_id
    ).all()

    list_var = []
    for reserved_user_id, state, creator_user_id, canceller_user_id, term_date, term_time, creation_datetime, cancellation_datetime in q:
        reserved_user = get_user_by_id(reserved_user_id)
        creator_user = get_user_by_id(creator_user_id)
        canceller_user = get_user_by_id(canceller_user_id)

        reserved = reserved_user.name + ' ' + reserved_user.surname
        creator = creator_user.name + ' ' + creator_user.surname
        if canceller_user:
            canceller = canceller_user.name + ' ' + canceller_user.surname
        else:
            canceller = None

        list_var.extend(
            [reserved, state, creator, canceller, term_date, term_time, creation_datetime, cancellation_datetime,
             reserved_user_id])

    return [list_var]


def get_student_reservation_history_info(student_id):
    reservation_history_info = []
    reservation_list = get_student_reservations(student_id)
    for reservation in reservation_list:
        consultation_term = get_consultation_term_by_id(reservation.consultation_term_id)
        reservation_history_info.append(
            [reservation.id, reservation.state, consultation_term.date, consultation_term.start_time])
    return reservation_history_info


def get_supervisor_reservation_history_info():
    reservation_history_info = []
    reservation_list = get_all_reservations()
    for reservation in reservation_list:
        consultation_term = get_consultation_term_by_id(reservation.consultation_term_id)
        user = get_user_by_id(reservation.reserved_user_id)
        reservation_history_info.append(
            [user.id, user.name, user.surname, reservation.state, reservation.id, consultation_term.date,
             consultation_term.start_time])
    return reservation_history_info


def get_student_reservations(student_id):
    return Reservation.query.filter_by(reserved_user_id=student_id).all()


def get_consultation_term_by_id(consultation_term_id):
    return ConsultationTerm.query.get(consultation_term_id)


def get_all_reservations():
    return Reservation.query.all()


def get_user_info(user):
    name = user.name
    surname = user.surname
    email = user.email
    telephone_number = user.telephone_number
    return [[name, surname, email, telephone_number]]


def get_student_reservation_history_info(student_id):
    reservation_history_info = []
    reservation_list = get_student_reservations(student_id)
    for reservation in reservation_list:
        consultation_term = get_consultation_term_by_id(reservation.consultation_term_id)
        reservation_history_info.append(
            [reservation.id, reservation.state, consultation_term.date, consultation_term.start_time])
    return reservation_history_info
