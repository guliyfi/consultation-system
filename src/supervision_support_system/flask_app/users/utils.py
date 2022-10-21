from flask_login import current_user
from flask_mail import Message
from sqlalchemy import null

from flask_app import db, bcrypt, mail
from flask_app.models import Supervisor, User, AllowedEmail, Student, Reservation, ConsultationTerm


def get_user_info(user):
    name = user.name
    surname = user.surname
    email = user.email
    telephone_number = user.telephone_number
    return [[name, surname, email, telephone_number]]


def current_user_supervisor():
    return Supervisor.query.filter_by(id=current_user.id).scalar()


def change_user_profile_data(name, surname, telephone_number, email=None):
    user = get_user_by_id(current_user.id)
    if current_user_supervisor():
        user.name = name
        user.surname = surname
        user.telephone_number = telephone_number
        user.email = email
    else:
        user.name = name
        user.surname = surname
        user.telephone_number = telephone_number
    db.session.commit()


def get_user_by_id(user_id):
    return User.query.get(user_id)


def check_passwd(user, password):
    return bcrypt.check_password_hash(user.password, password)


def set_passwd(user, new_password):
    user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
    db.session.commit()


def add_email_to_allowed_email_list(email):
    if not get_allowed_email(email):
        allowed_email = AllowedEmail(email=email)
        db.session.add(allowed_email)
        db.session.commit()


def get_allowed_email(email):
    return AllowedEmail.query.filter_by(email=email).first()


def delete_user(user):
    active_reservations = get_student_active_reservations(user.id)
    change_consultation_window_state(active_reservations, 'free')

    db.session.delete(user)
    db.session.commit()


def get_student_user_info():
    student_user_info = []
    student_user_list = get_student_user_list()
    for user in student_user_list:
        student_user_info.append([user.name, user.surname, user.email, user.id])
    return student_user_info


def get_student_user_list():
    return db.session.query(User).filter(User.student_id != null()).all()


def get_supervisor_note_about_student(student_id):
    student = get_student_by_id(student_id)
    return student.note


def get_student_by_id(user_id):
    return Student.query.get(user_id)


def get_student_reservation_history_info(student_id):
    reservation_history_info = []
    reservation_list = get_student_reservations(student_id)
    for reservation in reservation_list:
        consultation_term = get_consultation_term_by_id(reservation.consultation_term_id)
        reservation_history_info.append(
            [reservation.id, reservation.state, consultation_term.date, consultation_term.start_time])
    return reservation_history_info


def set_supervisor_note_about_student(student_id, note):
    student = get_student_by_id(student_id)
    student.note = note
    db.session.commit()


def get_student_reservations(student_id):
    return Reservation.query.filter_by(reserved_user_id=student_id).all()


def get_student_active_reservations(student_id):
    return Reservation.query.filter_by(reserved_user_id=student_id, state='active').all()


def change_consultation_window_state(reservations, state):
    for reservation in reservations:
        consultation_term_id = reservation.consultation_term_id
        get_consultation_term_by_id(consultation_term_id).state = state


def get_consultation_term_by_id(consultation_term_id):
    return ConsultationTerm.query.get(consultation_term_id)
