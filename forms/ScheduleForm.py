from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired


class ScheduleForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    content = StringField('Описание', validators=[DataRequired()])
    hour = IntegerField('Час', validators=[DataRequired()])
    minute = IntegerField('Минута', validators=[DataRequired()])
    submit = SubmitField('Добавить')
