from flask import Blueprint, abort, render_template, redirect, url_for
from flask_login import login_required

from flask_app.terms.utils import *
from flask_app.terms.forms import *

terms = Blueprint('terms', __name__)


@terms.route("/create_term", methods=["GET", "POST"])
@login_required
def create_term():
    if current_user_supervisor():
        form = CreateTermForm()

        if form.validate_on_submit():
            start_date = form.start_date.data
            end_date = form.end_date.data
            start_time = form.start_time.data
            end_time = form.end_time.data
            term_count = form.term_count.data
            term_duration = form.term_duration.data
            repeat_bool = form.repeat_bool.data
            repeat_interval = form.repeat.data
            week_day_list = [form.monday.data, form.tuesday.data, form.wednesday.data,
                             form.thursday.data, form.friday.data, form.saturday.data, form.sunday.data]
            user = form.student.data
            detect_non_working_term = form.detect_non_working_term.data
            submit_btn = form.create_submit.data
            count_btn = form.count_submit.data

            if term_duration:
                term_count = find_consultation_term_count(start_time, end_time, term_duration)
            elif term_count:
                term_duration = find_consultation_term_duration(start_time, end_time, term_count)
                term_count = find_consultation_term_count(start_time, end_time, term_duration)
            else:
                term_count = 1
                term_duration = find_consultation_term_duration(start_time, end_time, term_count)

            if submit_btn:
                date_list = get_date_list(start_date, end_date, repeat_bool, repeat_interval, week_day_list)
                start_time_list = get_time_list(start_time, term_duration, term_count)
                consultation_term_list = get_consultation_term_list(date_list, start_time_list, term_duration,
                                                                    detect_non_working_term)
                add_consultation_term_list(consultation_term_list)
                add_wait_list(date_list)

                if user:
                    for consultation_term in consultation_term_list:
                        creator_user = current_user
                        reserved_user = user
                        add_reservation_(consultation_term, creator_user, reserved_user)

                # return redirect(url_for('create_term'))

            elif count_btn:
                if form.term_duration.data:
                    flash(f'Počet konzultačních termínů je {term_count}', category='info')
                else:
                    flash(f'Délka konzultačního termínu je {term_duration}', category='info')

        return render_template('supervisor/create_term.html', form=form)
    abort(403)


@terms.route("/delete_term", methods=["GET", "POST"])
@login_required
def delete_term():
    if current_user_supervisor():
        form = DeleteTermForm()

        if form.validate_on_submit():
            start_date = form.start_date.data
            end_date = form.end_date.data
            start_time = form.start_time.data
            end_time = form.end_time.data
            repeat_bool = form.repeat_bool.data
            repeat_interval = form.repeat.data
            week_day_list = [form.monday.data, form.tuesday.data, form.wednesday.data,
                             form.thursday.data, form.friday.data, form.saturday.data, form.sunday.data]

            term_count = 1
            term_duration = find_consultation_term_duration(start_time, end_time, term_count)

            date_list = get_date_list(start_date, end_date, repeat_bool, repeat_interval, week_day_list)
            start_time_list = get_time_list(start_time, term_duration, term_count)
            delete_collision_consultation_term(date_list, start_time_list, term_duration)

        return render_template('supervisor/delete_term.html', form=form)
    abort(403)


@terms.route("/schedule", methods=["GET", "POST"])
@login_required
def schedule():
    if current_user_supervisor():
        add_form = AddNonWorkingWindowForm()
        delete_form = DeleteNonWorkingWindowForm()
        if add_form.add_submit.data and add_form.validate():
            add_non_working_window(add_form.title.data, add_form.start_date.data, add_form.end_date.data)
            flash(f'Událost úspěšně přidána', category='success')
            return redirect(url_for('terms.schedule'))
        elif delete_form.delete_submit.data and delete_form.validate():
            delete_non_working_window(delete_form.non_working_window_id.data)
            flash(f'Událost úspěšně smazána', category='success')
        return render_template('supervisor/schedule.html',
                               add_form=add_form, delete_form=delete_form,
                               non_working_window_info=get_non_working_window_info())
    abort(403)
