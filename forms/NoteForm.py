from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class NoteForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    content = TextAreaField('Content', validators=[Length(max=1000)])
    submit = SubmitField('Create Note')