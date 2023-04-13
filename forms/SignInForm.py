from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired


class SignInForm(FlaskForm):
    password = PasswordField('Пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
