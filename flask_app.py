"""
    Веб-сайт "Student Multiprog"
    Авторы: Фархитов Арслан, Грачев Константин, Крейдлина Эмилия
"""


import os
import easyocr
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from datetime import time
from datetime import date as Date
from data.schedules import Schedule
from data.users import User
from forms.SignInForm import SignInForm
from forms.SignUpForm import SignUpForm
from forms.NoteForm import NoteForm
from data.notes import Note
from data import db_session
from pathlib import Path
from flask import Flask, render_template, url_for, redirect, request
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from forms.ScheduleForm import ScheduleForm

db_session.global_init('databases/users.db')

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'mysecretkey'
cur_dir = Path.cwd()

HEADERS = {"User-Agent": UserAgent().random}
imgs_formulas = {}


@app.route("/calc")
@login_required
def calc():
    return render_template("calc.html", title='Калькулятор')


@app.route("/graph-calc")
@login_required
def graph_calc():
    return render_template("graph-calc.html")


@app.route("/calendar/get", methods=['GET'])
@login_required
def get_schedule():
    # Получаем дату из запроса
    date = request.args.get('date')
    db_sess = db_session.create_session()
    # выбираем из базы данных расписание на день
    schedule = db_sess.query(Schedule).filter(Schedule.user_id == current_user.get_id(), Schedule.date == date)
    # возвращаем html код, который увидит пользоватьель (в js этот код становится содержимым тега div)
    return render_template("calendar_form.html", schedule=schedule)


@app.route("/calendar")
@login_required
def calendar():
    db_sess = db_session.create_session()
    schedule = db_sess.query(Schedule).filter(Schedule.user_id == current_user.get_id())
    return render_template("calendar_read.html", schedule=schedule)


@app.route("/calendar/new", methods=['GET', 'POST'])
@login_required
def calendar_add():
    date = request.args.get('date')
    form = ScheduleForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        schedule = Schedule(
            title=form.title.data,
            content=form.content.data,
            time=time(form.hour.data, form.minute.data),
            date=Date(*map(int, date.split('-'))),  # превращаем дату из строки в datetime.date
            user_id=current_user.get_id()
        )
        db_sess.add(schedule)
        db_sess.commit()
        return redirect('/calendar')
    return render_template('calendar_write.html', form=form)


@app.route('/translator')
@login_required
def translator():
    return render_template('translator.html')


@app.route("/")
def index():
    # Страница для не зарегистрирован
    if current_user.is_authenticated:  # Если пользователь зарегистрирован, отправляем его на главную страницу
        return render_template("main_page.html")
    return render_template("register.html")


@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    if current_user.is_authenticated:
        return render_template("main_page.html")
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
    if current_user.is_authenticated:
        return render_template("main_page.html")
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


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/notes', methods=['GET', 'POST'])  # Страница, где можно создать новую заметку и посмотреть все свои заметки
@login_required
def notes():
    db_sess = db_session.create_session()
    form = NoteForm()  # Создаем форму для заметки
    if form.validate_on_submit():  # Если форма готова, добавляем ее в бд и отображаем
        title = form.title.data
        content = form.content.data
        note = Note(title=title, content=content, user_id=current_user.id)
        db_sess.add(note)
        db_sess.commit()
        return redirect(url_for('notes'))
    notes = db_sess.query(Note).filter(Note.user_id == current_user.id).all()  # Находим все заметки пользователя
    return render_template('notes.html', form=form, notes=notes)


@app.route('/notes/<int:id>', methods=['GET', 'POST'])  # Страница редактирования заметки
@login_required
def edit_note(id):
    db_sess = db_session.create_session()
    note = db_sess.query(Note).filter(Note.id == id).first()  # Находим заметку с тем айди, который получили
    form = NoteForm(obj=note)
    if form.validate_on_submit():  # Если заметка готова, изменяем ее
        form.populate_obj(note)
        db_sess.commit()
        return redirect(url_for('notes'))
    return render_template('edit_note.html', form=form, note=note)


@app.route('/notes/delete/<int:id>', methods=['POST'])  # Удаление заметки
@login_required
def delete_note(id):
    db_sess = db_session.create_session()
    note = db_sess.query(Note).filter(Note.id == id).first()
    db_sess.delete(note)
    db_sess.commit()
    return redirect(url_for('notes'))


@app.route('/main')  # Главная страница
@login_required
def main_index():
    return render_template("main_page.html")


@app.route('/text-recognize')  # Страница загрузки изображения и выбора языка для распознавания текста
@login_required
def upload_image():
    return render_template('image_upload.html')


@app.route('/text-recognize/done', methods=['POST'])  # Страница показа результата распознавания текста
@login_required
def recognized_text():
    file = request.files['file']
    file.save(os.path.join('static/assets/images', file.filename))  # Сохраняем в папку images файл, который выбрал
    # пользователь
    language = request.form['language']
    reader = easyocr.Reader([language])
    try:
        result = reader.readtext(os.path.join('static/assets/images', file.filename))  # распознаем текст
        words = []
        for r in result:
            words.append(r[1])
        words = " ".join(words)  # приводим текст к читаемому виду
        if os.path.isfile(os.path.join('static/assets/images', file.filename)):
            os.remove(os.path.join('static/assets/images', file.filename))  # После использования удаляем файл с севера
    except AttributeError:  # Если easyocr не может найти файл, выдаем ошибку
        words = "Ошибка! Возможно, вам стоит изменить расширение файла или поменять его название (! название не " \
                "должно содержать русские буквы !) "
    return render_template('recognize_result.html', words=words)


@app.route('/formulas')
@login_required
def formulas():
    # math
    url_math = "https://educon.by/index.php/formuly/formmat"
    response_math = requests.get(url_math, headers=HEADERS)
    sp_math = BeautifulSoup(response_math.text, 'lxml')
    data_math = sp_math.find('div', itemprop="articleBody")
    themes_math = data_math.find('ul').text.split('\n')[1:-4]
    a = data_math.find_all('img')
    b = []
    for elem in a:
        b.append('https://educon.by' + elem.get('src'))
    imgs_formulas['Формулы сокращенного умножения'] = b[:9]
    imgs_formulas['Квадратное уравнение и формула разложения квадратного трехчлена на множители'] = b[9:17]
    imgs_formulas['Свойства степеней и корней'] = b[20:36]
    imgs_formulas['Формулы с логарифмами'] = b[36:49]
    imgs_formulas['Арифметическая прогрессия'] = b[49:54]
    imgs_formulas['Геометрическая прогрессия'] = b[54:60]
    imgs_formulas['Тригонометрия'] = b[60:100]
    imgs_formulas['Тригонометрические уравнения'] = b[100:113]
    imgs_formulas['Геометрия на плоскости (планиметрия)'] = b[113:169]
    imgs_formulas['Геометрия в пространстве (стереометрия)'] = b[169:183]
    imgs_formulas['Координаты'] = b[183:187]
    ###

    # physics
    url_physics = "https://educon.by/index.php/formuly/formfiz"
    response_physics = requests.get(url_physics, headers=HEADERS)
    sp_physics = BeautifulSoup(response_physics.text, 'lxml')
    data_physics = sp_physics.find('div', itemprop="articleBody")
    themes_physics = data_physics.find('ul').text.split('\n')[1:-3]
    a = data_physics.find_all('img')
    b = []
    for elem in a:
        b.append('https://educon.by' + elem.get('src'))
    imgs_formulas['Кинематика'] = b[:35]
    imgs_formulas['Динамика'] = b[35:50]
    imgs_formulas['Статика'] = b[50:53]
    imgs_formulas['Гидростатика'] = b[53:60]
    imgs_formulas['Импульс'] = b[60:67]
    imgs_formulas['Работа, мощность, энергия'] = b[67:77]
    imgs_formulas['Молекулярная физика'] = b[77:94]
    imgs_formulas['Термодинамика'] = b[94:120]
    imgs_formulas['Электростатика'] = b[120:147]
    imgs_formulas['Электрический ток'] = b[147:169]
    imgs_formulas['Магнетизм'] = b[169:187]
    imgs_formulas['Колебания'] = b[187:224]
    imgs_formulas['Оптика'] = b[224:233]
    imgs_formulas['Атомная и ядерная физика'] = b[233:254]
    imgs_formulas['Основы специальной теории относительности (СТО)'] = b[254:264]
    ###
    return render_template('formulas.html', title='Темы', list_math=themes_math, list_physics=themes_physics)


@app.route('/formulas/<theme>')
@login_required
def themes(theme):
    return render_template('theme.html', title=theme, theme=theme, list=imgs_formulas)


def main():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
