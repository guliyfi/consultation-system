from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import SubmitField, BooleanField, TimeField, DateField, SelectField, \
    IntegerField, StringField
from wtforms.validators import DataRequired, ValidationError, Optional

from flask_app.terms.utils import return_student_tuple_list


def outdated_date_check(form, date_var):
    current_date = datetime.date(datetime.now())
    if current_date > date_var.data:
        raise ValidationError('Zastaralé datum.')


def date_interval_check(form, field):
    if form.start_date.data > form.end_date.data:
        raise ValidationError('Neplatný časový interval.')


def time_interval_check(form, field):
    if form.start_time.data > form.end_time.data or form.start_time.data == form.end_time.data:
        raise ValidationError('Neplatný hodinový interval.')


class CreateTermForm(FlaskForm):
    start_date = DateField('Časový interval', validators=[DataRequired(), outdated_date_check])
    end_date = DateField(validators=[DataRequired(), outdated_date_check, date_interval_check])
    start_time = TimeField('Hodinový interval', validators=[DataRequired()])
    end_time = TimeField(validators=[DataRequired(), time_interval_check])
    repeat = SelectField('Opakování', choices=[(7, '1. tyden'), (14, '2. tyden'), (31, 'Měsíc')],
                         validators=[Optional()])
    repeat_bool = BooleanField('Opakování')

    monday = BooleanField('po')
    tuesday = BooleanField('út')
    wednesday = BooleanField('st')
    thursday = BooleanField('čt')
    friday = BooleanField('pá')
    saturday = BooleanField('so')
    sunday = BooleanField('ne')
    student = SelectField('Přihlásit', choices=[('', '')],
                          validators=[Optional()])

    term_duration = IntegerField('Délka konzultačního termínu (v minutách)', validators=[Optional()])
    term_count = IntegerField('Počet konzultačních termínů (během jednoho dne)', validators=[Optional()])
    detect_non_working_term = BooleanField('Brát v úvahu dny pracovního klidu?', default=True)
    create_submit = SubmitField('Ano')
    count_submit = SubmitField('Spočítat')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.student.choices = return_student_tuple_list()

    def validate_start_time(self, time_var):
        current_date = datetime.date(datetime.now())
        current_time = datetime.now().time()
        if current_date == self.start_date.data:
            if current_time > time_var.data:
                raise ValidationError('Zastaralý čas')


class DeleteTermForm(FlaskForm):
    start_date = DateField('Časový interval', validators=[DataRequired()])
    end_date = DateField(validators=[DataRequired(), date_interval_check])
    start_time = TimeField('Hodinový interval', validators=[DataRequired()])
    end_time = TimeField(validators=[DataRequired(), time_interval_check])
    repeat = SelectField('Opakování', choices=[(7, '1. tyden'), (14, '2. tyden'), (31, 'Měsíc')],
                         validators=[Optional()])

    repeat_bool = BooleanField('Opakování')

    monday = BooleanField('po')
    tuesday = BooleanField('út')
    wednesday = BooleanField('st')
    thursday = BooleanField('čt')
    friday = BooleanField('pá')
    saturday = BooleanField('so')
    sunday = BooleanField('ne')

    submit = SubmitField('Ano')


class AddNonWorkingWindowForm(FlaskForm):
    title = StringField('Název události', validators=[DataRequired()])
    start_date = DateField('Časový interval', validators=[DataRequired(), date_interval_check])
    end_date = DateField(validators=[DataRequired()])
    add_submit = SubmitField('Odeslat')


class DeleteNonWorkingWindowForm(FlaskForm):
    non_working_window_id = IntegerField(validators=[DataRequired()])
    delete_submit = SubmitField('Ano')
