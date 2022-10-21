from flask_mail import Message

from flask_app import db, mail
from flask_app.models import User, AllowedEmail, Student


def get_user_by_email(email):
    return User.query.filter_by(email=email).first()


def get_allowed_email(email):
    return AllowedEmail.query.filter_by(email=email).first()


def add_email_to_allowed_email_list(email):
    if not get_allowed_email(email):
        allowed_email = AllowedEmail(email=email)
        db.session.add(allowed_email)
        db.session.commit()


def add_user(user):
    db.session.add(user)
    db.session.commit()


def add_student(user):
    student = Student(id=user.id)
    db.session.add(student)
    db.session.commit()


def get_reset_token(user):
    return user.get_reset_token()


def get_user_by_token(token):
    return User.verify_reset_token(token)


def change_user_password(user, new_password):
    user.password = new_password
    db.session.commit()


def delete_email_from_allowed_email_list(email):
    allowed_email = AllowedEmail.query.filter_by(email=email).first()
    db.session.delete(allowed_email)
    db.session.commit()


def get_user(email, name, surname, telephone_number, password):
    return User(email=email, name=name, surname=surname, telephone_number=telephone_number, password=password)



