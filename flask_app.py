import os
from datetime import time
from datetime import date as Date
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data.schedules import Schedule
from data.users import User
from forms.SignInForm import SignInForm
from flask import Flask, render_template, redirect, request
from data import db_session
from forms.SignUpForm import SignUpForm
from forms.ScheduleForm import ScheduleForm

db_session.global_init('databases/users.db')

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'student_multiprog_secret_key'


@app.route("/calc")
def calc():
    return render_template("calc.html", title='Калькулятор')


@app.route("/graph-calc")
def graph_calc():
    return render_template("graph-calc.html")


@app.route("/calendar/get", methods=['GET'])
def get_schedule():
    date = request.args.get('date')
    db_sess = db_session.create_session()
    schedule = db_sess.query(Schedule).filter(Schedule.user_id == current_user.get_id(), Schedule.date == date)
    return render_template("calendar_form.html", schedule=schedule)


@app.route("/calendar")
def calendar():
    db_sess = db_session.create_session()
    schedule = db_sess.query(Schedule).filter(Schedule.user_id == current_user.get_id())
    return render_template("calendar_read.html", schedule=schedule)


@app.route("/calendar/new", methods=['GET', 'POST'])
def calendar_add():
    date = request.args.get('date')
    form = ScheduleForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        schedule = Schedule(
            title=form.title.data,
            content=form.content.data,
            time=time(form.hour.data, form.minute.data),
            date=Date(*map(int, date.split('-'))),
            user_id=current_user.get_id()
        )
        db_sess.add(schedule)
        db_sess.commit()
        return redirect('/calendar')
    return render_template('calendar_write.html', form=form)


@app.route("/")
def index():
    return render_template("register.html")


@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    form = SignInForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.name == form.name.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/main")
        return render_template('sign_in.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('sign_in.html', title='Авторизация', form=form)


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    form = SignUpForm()
    if form.validate_on_submit():
        if form.password.data != form.confirm_password.data:
            return render_template('sign_up.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('sign_up.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.username.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/sign_in')
    return render_template('sign_up.html', title='Регистрация', form=form)


@app.route('/translator')
def translator():
    return render_template('translator.html')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/main')
def main_index():
    return render_template("main_page.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


def main():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


def test():
    app.run(host='127.0.0.1', port=5000)


if __name__ == '__main__':
    # main()
    test()
