from threading import Thread
from flask import current_app
from flask_mail import Message
from time import sleep
from flask_app import mail


def send_async_email(app, msg):
    with app.app_context():
        for i in range(10, -1, -1):
            sleep(2)
        mail.send(msg)


def send_email(user_email, title, content):
    app = current_app._get_current_object()
    msg = Message(f'{title}',
                  sender='noreply@demo.com',
                  recipients=[user_email])
    msg.body = content
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
