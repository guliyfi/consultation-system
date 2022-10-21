from flask import Blueprint, flash, redirect, url_for, render_template, abort
from flask_login import login_required, current_user

from mail import send_email
from flask_app.users.forms import *
from flask_app.users.utils import *

users = Blueprint('users', __name__)


@users.route("/")
@login_required
def home():
    return redirect(url_for('reservations.reservation_calendar'))


@users.route("/user_profile", methods=["GET", "POST"])  # decorator in python
@login_required
def user_profile():
    user_info = get_user_info(current_user)
    if current_user_supervisor():
        profile_form = AdminProfileForm(prefix='admin_profile')
        password_form = ChangePasswordForm(prefix='passwd')

        for name, surname, email, telephone_number in user_info:
            profile_form = AdminProfileForm(prefix='admin_profile', name=name, surname=surname, email=email,
                                            phone_number=telephone_number)

        if profile_form.profile_submit.data and profile_form.validate():  # notice the order
            change_user_profile_data(name=profile_form.name.data, surname=profile_form.surname.data,
                                     email=profile_form.email.data, telephone_number=profile_form.phone_number.data)
            flash('Vaše údaje byly úspěšně změněny', category='success')
            return redirect(url_for('users.user_profile'))
        if password_form.password_submit.data and password_form.validate():  # notice the order
            if check_passwd(current_user, password_form.actual_password.data):
                set_passwd(current_user, password_form.new_password.data)
                flash('Heslo bylo úspěšně změněno', category='success')
                return redirect(url_for('users.user_profile'))
            else:
                flash('Zadali jste nesprávně aktuální heslo', category='danger')
        if profile_form.errors or password_form.errors:
            flash(f'Špatně jste vyplnili formulář', category='danger')

        return render_template('supervisor/profile.html',
                               profile_form=profile_form, password_form=password_form,
                               user_info=user_info)
    else:
        profile_form = UserProfileForm(prefix='user_profile')
        for name, surname, email, telephone_number in user_info:
            profile_form = UserProfileForm(prefix='user_profile', name=name, surname=surname,
                                           phone_number=telephone_number)
        password_form = ChangePasswordForm(prefix='passwd')

        if profile_form.profile_submit.data and profile_form.validate():
            change_user_profile_data(name=profile_form.name.data, surname=profile_form.surname.data,
                                     telephone_number=profile_form.phone_number.data)
            flash('Vaše údaje byly úspěšně změněny', category='success')
            return redirect(url_for('users.user_profile'))
        if password_form.password_submit.data and password_form.validate():
            if check_passwd(current_user, password_form.actual_password.data):
                set_passwd(current_user, password_form.new_password.data)
                flash('Heslo bylo úspěšně změněno', category='success')
                return redirect(url_for('users.user_profile'))
            else:
                flash('Zadali jste nesprávně aktuální heslo', category='danger')
        if profile_form.errors or password_form.errors:
            flash(f'Špatně jste vyplnili formulář', category='danger')
        return render_template('student/profile.html',
                               profile_form=profile_form, password_form=password_form,
                               user_info=user_info)


@users.route("/student_list", methods=['GET', 'POST'])
@login_required
def student_list():
    if current_user_supervisor():
        add_form = AddUserForm()
        delete_form = DeleteUserForm()

        if add_form.validate_on_submit():
            note = add_form.note_content.data
            emails = add_form.emails.data.split()

            title = 'Registrace'
            content = note + '\n' + f'''Pro registraci následujte odkaz: {url_for('auth.registration', _external=True)}\n'''

            for email in emails:
                add_email_to_allowed_email_list(email)
                send_email(email, title, content)

            return redirect(url_for('users.student_list'))

        if delete_form.validate_on_submit():
            user_id = delete_form.user_id.data
            user = get_user_by_id(user_id)
            delete_user(user)

            return redirect(url_for('users.student_list'))

        if add_form.errors or delete_form.errors:
            flash(f'Špatně jste vyplnili formulář', category='danger')

        return render_template('supervisor/students_list.html', add_form=add_form, delete_form=delete_form,
                               student_info=get_student_user_info())
    abort(403)


@users.route("/student_information/<int:user_id>", methods=["GET", "POST"])
@login_required
def student_information(user_id):
    if current_user_supervisor():
        if not get_user_by_id(user_id):
            print(get_user_by_id(user_id))
            abort(404)
        user_info = get_user_info(get_user_by_id(user_id))
        note = get_supervisor_note_about_student(user_id)
        reservation_info = get_student_reservation_history_info(user_id)

        form = NoteForm(content=note)

        if form.validate_on_submit():
            set_supervisor_note_about_student(user_id, form.content.data)
            return redirect(url_for('users.student_information', user_id=user_id))

        return render_template('supervisor/user_info.html',
                               form=form, note=note,
                               user_info=user_info, reservation_info=reservation_info
                               )
    abort(403)
