from flask import flash
from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, TimeField, SubmitField, TextAreaField, SelectMultipleField
from wtforms import widgets
from wtforms.validators import DataRequired, ValidationError, Optional
import datetime as dt
from datetime import datetime

from flask_app.reservations.utils import get_consultation_date_time_list, get_consultation_term_by_date_time, \
    get_reservation_by_consultation_term, return_student_tuple_list


def outdated_date_check(form, date_var):
    current_date = datetime.date(datetime.now())
    if current_date > date_var.data:
        raise ValidationError('Zastaralé datum.')


def outdated_time_check(form, time_var):
    current_time = datetime.now().time()
    if current_time > time_var.data:
        raise ValidationError('Zastaralý čas.')


class AddReservationAdminForm(FlaskForm):
    date = DateField('Datum', validators=[DataRequired(), outdated_date_check])
    time = TimeField(validators=[DataRequired()])
    student = SelectField('Student', choices=[], validators=[DataRequired()])
    add_submit = SubmitField('Odeslat')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.student.choices = return_student_tuple_list()

    # def validate(self, extra_validators=None):
    #     ""
    # datetime_var = dt.datetime.combine(self.date.data, self.time.data)
    #
    # if get_time_window(datetime_var):
    #     if not get_active_reservation_by_datetime(datetime_var):
    #         return True
    # return False


class DeleteReservationAdminForm(FlaskForm):
    date = DateField('Datum', validators=[DataRequired(), outdated_date_check])
    time = TimeField(validators=[DataRequired()])
    delete_submit = SubmitField('Ano')

    # def validate(self, extra_validators=None):
    #     datetime_var = dt.datetime.combine(self.date.data, self.time.data)
    #
    #     if get_time_window(datetime_var):
    #         if get_active_reservation_by_datetime(datetime_var):
    #             return True
    #     return False


class AddReservationUserForm(FlaskForm):
    date = DateField('Datum', validators=[DataRequired(), outdated_date_check])
    time = TimeField(validators=[DataRequired(), outdated_time_check])
    note = TextAreaField('Poznámka pro vedoucího:')
    add_submit = SubmitField('Odeslat')

    # def validate(self, extra_validators=None):
    #     datetime_var = dt.datetime.combine(self.date.data, self.time.data)
    #     if free_time_window(datetime_var):
    #         return True
    #     else:
    #         return False


class DeleteReservationUserForm(FlaskForm):
    date = DateField('Datum', validators=[DataRequired(), outdated_date_check])
    time = TimeField(validators=[DataRequired(), outdated_time_check])
    delete_submit = SubmitField('Ano')

    def validate(self, extra_validators=None):
        consultation_term = get_consultation_term_by_date_time(self.date.data, self.time.data)
        reservation = get_reservation_by_consultation_term(consultation_term)
        if reservation.supervisor_note is None:
            return True
        else:
            flash('Rezervaci nemůžete sami zrušit, kontaktujte učitele', category='danger')
            return False


class AddWaiterForm(FlaskForm):
    date = DateField('Datum', validators=[DataRequired(), outdated_date_check])
    add_waiter_submit = SubmitField('Ano')

    def validate(self, extra_validators=None):
        date_var = self.date.data
        current_date = dt.date.today()
        if current_date >= date_var:
            flash(f'Již nemůžete být zařazeni na čekací listinu', category='danger')
            return False
        else:
            return True


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class DisableTermAdminForm(FlaskForm):
    date = DateField('Datum', validators=[DataRequired(), outdated_date_check])
    time_list = MultiCheckboxField(choices=[])
    note = TextAreaField('Poznámka pro studenty:')
    disable_submit = SubmitField('Ano')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.time_list.choices = get_consultation_date_time_list(self.date.data, ['free', 'busy'])


class MoveReservationUserForm(FlaskForm):
    date = DateField('Datum', validators=[DataRequired(), outdated_date_check])
    time = TimeField(validators=[DataRequired(), outdated_time_check])
    new_time = SelectField(validators=[DataRequired()])

    move_submit = SubmitField('Odeslat')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        time_list_choices = []
        time_list = get_consultation_date_time_list(self.date.data, ['free'])
        for time_str in time_list:
            time_obj = datetime.strptime(time_str, '%H:%M').time()
            current_time = datetime.now().time()
            if current_time < time_obj:
                time_list_choices.append(time_str)

        self.new_time.choices = time_list_choices

    def validate_new_time(self, new_time):
        new_time_var = datetime.strptime(new_time.data, '%H:%M').time()
        current_time = datetime.now().time()
        if current_time > new_time_var:
            raise ValidationError('Zastaralý čas')


class NoteForm(FlaskForm):
    content = TextAreaField(validators=[Optional()])
    submit = SubmitField('Odeslat')
