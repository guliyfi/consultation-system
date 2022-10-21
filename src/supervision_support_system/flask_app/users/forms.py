from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, TextAreaField, EmailField
from wtforms.validators import DataRequired, Length, Email, Optional


def get_length_validate_message(min_val, max_val):
    return f'Délka musí být alespoň {min_val} znaky a ne více než {max_val} znaků.'


class UserProfileForm(FlaskForm):
    name = StringField('Jméno:', validators=[DataRequired()])
    surname = StringField('Příjmení:', validators=[DataRequired()])
    phone_number = StringField('Telefonní číslo', validators=[Optional()])
    profile_submit = SubmitField('Odeslat')


class AdminProfileForm(FlaskForm):
    name = StringField('Jméno:', validators=[DataRequired()])
    surname = StringField('Příjmení:', validators=[DataRequired()])
    email = EmailField('E-mail', validators=[DataRequired()])
    phone_number = StringField('Telefonní číslo', validators=[Optional()])
    profile_submit = SubmitField('Odeslat')


class ChangePasswordForm(FlaskForm):
    actual_password = PasswordField('Původní heslo:', validators=[DataRequired(),
                                                                  Length(min=2, max=60,
                                                                         message=get_length_validate_message(
                                                                             2, 50))])
    new_password = PasswordField('Nové heslo:', validators=[DataRequired(),
                                                            Length(min=2, max=60,
                                                                   message=get_length_validate_message(
                                                                       2, 50))])
    password_submit = SubmitField('Odeslat')


class NoteForm(FlaskForm):
    content = TextAreaField(validators=[Optional()])
    submit = SubmitField('Odeslat')


class AddUserForm(FlaskForm):
    emails = TextAreaField('Přidejte jeden nebo více e-mailů',
                           validators=[DataRequired(), Email('Špatný formát e-mailu')])
    note_content = TextAreaField('Poznámka pro studenty:', validators=[Optional()])
    submit = SubmitField('Odeslat')


class DeleteUserForm(FlaskForm):
    user_id = IntegerField(validators=[DataRequired()])
    submit = SubmitField('Ano')
