from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class NoteForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired(), Length(max=100)])
    content = TextAreaField('Содержание', validators=[Length(max=1000)])
    submit = SubmitField('Создать заметку')