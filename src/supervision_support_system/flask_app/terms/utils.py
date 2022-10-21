from flask import flash
from flask_login import current_user
from sqlalchemy import and_, or_

from flask_app import db
from flask_app.models import User, Student, Supervisor, NonWorkingWindow, ConsultationTerm, Reservation, WaitList
from datetime import timedelta
import datetime as dt


def return_student_tuple_list():
    student_tuple_list = []
    students = db.session.query(User.id, User.name, User.surname).filter(User.id == Student.id).all()
    student_tuple_list.append(('', ''))
    for el in students:
        student_tuple_list.append((el[0], el[1] + ' ' + el[2]))
    return student_tuple_list


def current_user_supervisor():
    return Supervisor.query.filter_by(id=current_user.id).scalar()


def add_non_working_window(title, start, end):
    non_working_window = NonWorkingWindow(title=title, start=start, end=end)
    db.session.add(non_working_window)
    db.session.commit()


def delete_non_working_window(non_working_window_id):
    non_working_window = get_non_working_window_by_id(non_working_window_id)
    db.session.delete(non_working_window)
    db.session.commit()


def get_non_working_window_info():
    non_working_window_info = []
    non_working_window_list = get_non_working_window_list()
    for non_working_window in non_working_window_list:
        non_working_window_info.append([non_working_window.id, non_working_window.title, non_working_window.start_date,
                                        non_working_window.end_date])
    return non_working_window_info


def get_non_working_window_list():
    return NonWorkingWindow.query.all()


def get_non_working_window_by_id(non_working_window_id):
    return NonWorkingWindow.query.get(non_working_window_id)


def find_consultation_term_count(start_time, end_time, term_duration):
    if term_duration == 0:
        return 0
    term_count = int(get_time_diff_minutes(start_time, end_time) / term_duration)
    return term_count


def find_consultation_term_duration(start_time, end_time, time_window_count):
    term_duration = int(get_time_diff_minutes(start_time, end_time) / time_window_count)
    return term_duration


def get_time_diff_minutes(start_time, end_time):
    t_s = timedelta(hours=start_time.hour, minutes=start_time.minute)
    t_e = timedelta(hours=end_time.hour, minutes=end_time.minute)
    time_diff = t_e - t_s
    time_diff_minutes = time_diff.total_seconds() / 60
    return time_diff_minutes


def get_date_list(start_date, end_date, repeat_bool, repeat_interval, week_day_list):
    date_list = []
    if repeat_bool:
        for idx, week_day in enumerate(week_day_list):
            if week_day:
                date_list.extend(daterange_weekday(start_date, end_date, idx, repeat_interval))
    else:
        date_list.extend(daterange(start_date, end_date))

    return date_list


def daterange_weekday(start_date, end_date, weekday, repeat):
    date_list = []
    repeat = int(repeat)
    for n in range(int((end_date - start_date).days) + 1):
        date_it = start_date + dt.timedelta(n)
        if date_it.weekday() == weekday:
            if date_list:
                if diff_dates(date_list[-1], date_it) == repeat:
                    date_list.append(date_it)
            else:
                date_list.append(date_it)
    return date_list


def daterange(start_date, end_date):
    date_list = []
    for n in range(int((end_date - start_date).days) + 1):
        date_it = start_date + dt.timedelta(n)
        date_list.append(date_it)
    return date_list


def diff_dates(date1, date2):
    return abs(date2 - date1).days


def get_time_list(start_time, duration, count):
    time_list = []

    for i in range(count):
        time_list.append(start_time)
        start_time = time_obj_add_minutes(start_time, duration)

    return time_list


def delete_collision_consultation_term(date_list, start_time_list, term_duration):
    for date in date_list:
        for start_time in start_time_list:
            end_time = time_obj_add_minutes(start_time, term_duration)
            consultation_term = ConsultationTerm(date, start_time, end_time)
            detect_collision(consultation_term).delete()
            db.session.commit()


def time_obj_add_minutes(time_var, minutes):
    datetime_var = dt.datetime.now().replace(hour=time_var.hour, minute=time_var.minute, second=0, microsecond=0)
    datetime_var += timedelta(minutes=minutes)
    return datetime_var.time()


def detect_collision(consultation_term):
    return db.session.query(ConsultationTerm).filter(
        and_
            (
            ConsultationTerm.date == consultation_term.date,
            or_(
                and_
                    (
                    ConsultationTerm.start_time <= consultation_term.start_time,
                    ConsultationTerm.end_time > consultation_term.start_time
                ),
                and_
                    (
                    ConsultationTerm.start_time < consultation_term.end_time,
                    ConsultationTerm.end_time >= consultation_term.end_time
                ),
                and_(
                    ConsultationTerm.start_time > consultation_term.start_time,
                    ConsultationTerm.end_time < consultation_term.end_time
                )
            )
        ))


def add_reservation_(consultation_term, creator_user, reserved_user_id, student_note=None):
    reservation = Reservation(reserved_user_id, creator_user.id, consultation_term.id, student_note)
    change_consultation_term_state(consultation_term, 'busy')
    db.session.add(reservation)
    db.session.commit()


def change_consultation_term_state(consultation_term, state):
    consultation_term.state = state


def add_consultation_term_list(consultation_term_list):
    for consultation_term in consultation_term_list:
        db.session.add(consultation_term)
    db.session.commit()


def add_wait_list(date_list):
    for date_var in date_list:
        if not get_wait_list(date_var):
            wait_list = WaitList(date_var)
            db.session.add(wait_list)
            db.session.commit()


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


def get_user_by_id(user_id):
    return User.query.get(user_id)


def get_wait_list(date_var):
    return db.session.query(WaitList).filter(WaitList.date == date_var).first()


def get_consultation_term_list(date_list, start_time_list, term_duration, detect_non_working_term):
    consultation_term_list = []
    for date in date_list:
        for start_time in start_time_list:
            end_time = time_obj_add_minutes(start_time, term_duration)
            consultation_term = ConsultationTerm(date, start_time, end_time)
            if not detect_collision(consultation_term).first():
                if detect_non_working_term:
                    if detect_non_working_window_collision(consultation_term):
                        flash(
                            f'Konsultační termín [{consultation_term.date.strftime("%d-%m-%Y")}, {consultation_term.start_time.strftime("%H:%M")} - {consultation_term.end_time.strftime("%H:%M")}] '
                            f'nebyl přidán, protože termín připadá na den pracovního klidu',
                            category='danger')
                    else:
                        consultation_term_list.append(consultation_term)
                else:
                    consultation_term_list.append(consultation_term)
            else:
                flash(
                    f'Konsultační termín [{consultation_term.date.strftime("%d-%m-%Y")}, {consultation_term.start_time.strftime("%H:%M")} - {consultation_term.end_time.strftime("%H:%M")}] '
                    f'nebyl přidán, protože byla nalezena kolize',
                    category='danger')
    return consultation_term_list


def detect_non_working_window_collision(consultation_term):
    non_working_window_list = get_non_working_window_list()
    for non_working_window in non_working_window_list:
        dt1 = (int(non_working_window.start_date.strftime('%m')), int(non_working_window.start_date.strftime('%d')))
        dt2 = (int(consultation_term.date.strftime('%m')), int(consultation_term.date.strftime('%d')))
        dt3 = (int(non_working_window.end_date.strftime('%m')), int(non_working_window.end_date.strftime('%d')))
        if dt1 <= dt2 <= dt3:
            return True
    return False
