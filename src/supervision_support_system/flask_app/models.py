from datetime import datetime

from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app
from flask_app import db, login_manager
import datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


waitingStudents = db.Table('waiting_students',
                           db.Column('student_id', db.Integer,
                                     db.ForeignKey('student.id', ondelete='CASCADE'), primary_key=True),
                           db.Column('waiting_list_id', db.Integer,
                                     db.ForeignKey('wait_list.id', ondelete='CASCADE'), primary_key=True)
                           )


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    telephone_number = db.Column(db.String(50), nullable=True)
    password = db.Column(db.String(60), nullable=False)

    # ForeignKey
    student_id = db.relationship('Student', backref='student_info', lazy=True, uselist=False, passive_deletes=True)
    supervisor_id = db.relationship('Supervisor', backref='student_info', lazy=True, uselist=False,
                                    passive_deletes=True)

    reservations = db.relationship('Reservation', backref='user_info', lazy=True, passive_deletes=True)

    def __init__(self, email, name, surname, password, telephone_number=''):
        self.email = email
        self.name = name
        self.surname = surname
        self.telephone_number = telephone_number
        self.password = password

    def get_reset_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token, expires_sec=900):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, expires_sec)['user_id']
        except:
            return None
        return User.query.get(user_id)


class AllowedEmail(db.Model):
    email = db.Column(db.String(50), primary_key=True)

    def __init__(self, email):
        self.email = email

    def __repr__(self):
        return f"AllowedEmails('{self.email}') "


class Supervisor(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True, nullable=False)

    def __repr__(self):
        return f"User('{self.info}')"


class Student(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True, nullable=False)
    note = db.Column(db.Text)


class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(20), nullable=False)

    creation_datetime = db.Column(db.DateTime, nullable=False)
    cancellation_datetime = db.Column(db.DateTime, nullable=True)
    student_note = db.Column(db.Text)
    supervisor_note = db.Column(db.Text)

    # Users
    # ForeignKey key
    reserved_user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    creator_user_id = db.Column(db.Integer, nullable=False)
    canceller_user_id = db.Column(db.Integer, nullable=True)

    consultation_term_id = db.Column(db.Integer, db.ForeignKey('consultation_term.id', ondelete='CASCADE'),
                                     nullable=False)

    def __init__(self, reserved_user_id, creator_user_id, consultation_term_id, student_note):
        self.state = 'active'
        self.creation_datetime = datetime.datetime.now()
        self.reserved_user_id = reserved_user_id
        self.creator_user_id = creator_user_id
        self.consultation_term_id = consultation_term_id
        self.student_note = student_note


class ConsultationTerm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    state = db.Column(db.String(20), nullable=False)

    reservations = db.relationship('Reservation', backref='time_window', lazy=True, passive_deletes=True)

    def __init__(self, date, start_time, end_time):
        self.date = date
        self.start_time = start_time
        self.end_time = end_time
        self.state = 'free'

    def __repr__(self):
        return f"ConsultationTerm('{self.date}','{self.start_time}', '{self.end_time}', '{self.state}')"


class WaitList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True)
    waiting_students = db.relationship('Student', secondary=waitingStudents, lazy='subquery')

    def __init__(self, date):
        self.date = date

    def __repr__(self):
        return f"WaitList('{self.id}','{self.date}', '{self.waiting_students}')"


class InformationBoard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    content = db.Column(db.Text)

    def __init__(self, title, content):
        self.title = title
        self.content = content


class NonWorkingWindow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

    def __init__(self, title, start, end):
        self.title = title
        self.start_date = start
        self.end_date = end

