from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TelField, BooleanField, SubmitField, EmailField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

from flask_app.auth.utils import get_user_by_email, get_allowed_email


def get_length_validate_message(min_val, max_val):
    return f'Délka musí být alespoň {min_val} znaky a ne více než {max_val} znaků.'


class RegistrationForm(FlaskForm):
    name = StringField('Jméno',
                       validators=[DataRequired(),
                                   Length(min=2, max=50, message=get_length_validate_message(2, 50))])
    surname = StringField('Příjmení',
                          validators=[DataRequired(),
                                      Length(min=2, max=50, message=get_length_validate_message(2, 50))])
    email = StringField('E-mail',
                        validators=[DataRequired(), Email('Špatný formát e-mailu.')])
    telephone_number = TelField('Telefonní číslo')
    password = PasswordField('Heslo',
                             validators=[DataRequired(), Length(min=5, max=60,
                                                                message=get_length_validate_message(2, 60))])
    confirm_password = PasswordField('Ověření hesla',
                                     validators=[DataRequired(), Length(min=5, max=60,
                                                                        message=get_length_validate_message(2, 60)),
                                                 EqualTo('password', message='Pole se musí rovnat heslu.')])
    submit = SubmitField('Odeslat')

    def validate_email(self, email):
        user = get_user_by_email(email.data)
        if user:
            raise ValidationError('Tento e-mail již existuje')
        if not get_allowed_email(email.data):
            raise ValidationError('''Nemáte právo na registraci.
            Zkuste zadat svůj školní e-mail nebo kontaktujte učitele. ''')


class LoginForm(FlaskForm):
    email = StringField('E-mail',
                        validators=[DataRequired(), Email('Špatný formát e-mailu.')])
    password = PasswordField('Heslo',
                             validators=[DataRequired(), Length(min=2, max=60,
                                                                message=get_length_validate_message(2, 50))])

    remember = BooleanField('Trvalé přihlášení')
    submit = SubmitField('Přihlásit se')

    def validate_email(self, email):
        ""
        # user = User.query.filter_by(email=email.data).first()
        # if not user:
        #     raise ValidationError('Špatný email nebo heslo')


class RequestResetForm(FlaskForm):
    email = EmailField('E-mail', validators=[DataRequired()])
    submit = SubmitField('Obnovit heslo')

    def validate_email(self, email):
        user = get_user_by_email(email.data)
        if not user:
            raise ValidationError('Špatný email')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Nové heslo',
                             validators=[DataRequired(), Length(min=5, max=60,
                                                                message=get_length_validate_message(2, 60))])
    confirm_password = PasswordField('Ověření hesla',
                                     validators=[DataRequired(), Length(min=5, max=60,
                                                                        message=get_length_validate_message(5, 60)),
                                                 EqualTo('password', message='Pole se musí rovnat heslu.')])
    submit = SubmitField('Odeslat')


