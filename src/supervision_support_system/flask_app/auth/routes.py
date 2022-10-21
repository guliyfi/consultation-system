from flask import Blueprint, flash, url_for, render_template, redirect, current_app, request
from flask_login import login_required, login_user, logout_user
from itsdangerous import URLSafeTimedSerializer as Serializer

from flask_app import bcrypt
from flask_app.auth.forms import *
from flask_app.auth.utils import *
from mail import send_email

auth = Blueprint('auth', __name__)


@auth.route("/registration", methods=['POST', 'GET'])
def registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        s = Serializer(current_app.config['SECRET_KEY'])
        token = s.dumps({'email': form.email.data, 'name': form.name.data, 'surname': form.surname.data,
                         'telephone_number': form.telephone_number.data, 'password': hashed_password})
        flash('Na váš e-mail byl zaslán odkaz pro dokončení registrace.', 'info')

        title = 'Dokončení registrace'
        content = f'''Registraci dokončíte kliknutím na odkaz:\n{url_for('auth.registration_confirm', token=token, _external=True)}\nPokud jste tento požadavek nepodali, tento e-mail ignorujte a nebudou provedeny žádné změny.'''

        send_email(form.email.data, title, content)

    return render_template('general/register.html', form=form)


@auth.route("/registration/<token>", methods=['POST', 'GET'])
def registration_confirm(token):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        email = s.loads(token)['email']
        name = s.loads(token)['name']
        surname = s.loads(token)['surname']
        telephone_number = s.loads(token)['telephone_number']
        password = s.loads(token)['password']

        user = get_user(email=email, name=name, surname=surname, telephone_number=telephone_number, password=password)
        if get_user_by_email(email):
            flash('Uživatel již existuje', 'danger')
            return redirect(url_for('auth.login'))
        else:
            delete_email_from_allowed_email_list(email)
            add_user(user)
            add_student(user)
    except:
        flash('To je neplatný nebo vypršelý token', 'danger')
        return redirect(url_for('auth.registration'))
    flash('Registrace úspěšně dokončena', 'success')
    return redirect(url_for('auth.login'))


@auth.route("/login", methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = get_user_by_email(form.email.data)
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next = request.args.get('next')
            return redirect(next) if next else redirect(url_for('users.home'))
        else:
            flash('Zkontrolujte prosím e-mail a heslo', 'danger')
    return render_template('general/login.html', form=form)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route("/reset_request", methods=['GET', 'POST'])
def reset_request():
    form = RequestResetForm()
    if form.validate_on_submit():
        user = get_user_by_email(form.email.data)
        token = get_reset_token(user)
        title = 'Požadavek na obnovení hesla'
        message = f'''Pro obnovu hesla, navštivte následující odkaz:\n{url_for('auth.reset_password', token=token, _external=True)}\nPokud jste tento požadavek nepodali, tento e-mail ignorujte a nebudou provedeny žádné změny.'''
        send_email(user.email, title, message)
        flash('Byl odeslán e-mail s pokyny k obnovení hesla.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('general/reset_request.html', form=form)


@auth.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    user = get_user_by_token(token)
    if user is None:
        flash('To je neplatný nebo vypršelý token', 'danger')
        return redirect(url_for('auth.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        change_user_password(user, hashed_password)
        flash('Vaše heslo bylo aktualizováno! Nyní se můžete přihlásit', 'success')
        return redirect(url_for('auth.login'))
    return render_template('general/reset_password.html', title='Reset Password', form=form)
