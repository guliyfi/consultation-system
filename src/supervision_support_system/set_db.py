from flask_app import db, bcrypt
from flask_app.models import User, Supervisor, Student, InformationBoard
db.create_all()

hashed_password = bcrypt.generate_password_hash('12345').decode('utf-8')

supervisor_user = User(email='supervisor@fit.cz', name='Supervisor', surname='Supervisor', password=hashed_password)
student_user = User(email='student@fit.cz', name='Student', surname='Student', password=hashed_password)

db.session.add(supervisor_user)
db.session.add(student_user)
db.session.commit()

info_board = InformationBoard(title='calendar_of_consultations', content='')

student = Student(id=User.query.filter_by(email='student@fit.cz').first().id)
supervisor = Supervisor(id=User.query.filter_by(email='supervisor@fit.cz').first().id)

db.session.add(student)
db.session.add(supervisor)
db.session.add(info_board)
db.session.commit()
