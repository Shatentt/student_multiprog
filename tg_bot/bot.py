import logging

import requests
from dotenv import load_dotenv
from telegram.ext import Application, Updater, CommandHandler, MessageHandler, filters
from config import BOT_TOKEN
import sqlite3
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

HEADERS = {"User-Agent": UserAgent().random}
imgs_formulas_maths = {}
imgs_formulas_physics = {}
url_math = "https://educon.by/index.php/formuly/formmat"
response_math = requests.get(url_math, headers=HEADERS)
sp_math = BeautifulSoup(response_math.text, 'lxml')
data_math = sp_math.find('div', itemprop="articleBody")
themes_math = data_math.find('ul').text.split('\n')[1:-4]
a = data_math.find_all('img')
b = []
for elem in a:
    b.append('https://educon.by' + elem.get('src'))
imgs_formulas_maths['Формулы сокращенного умножения'] = b[:9]
imgs_formulas_maths['Квадратное уравнение и формула разложения квадратного трехчлена на множители'] = b[9:17]
imgs_formulas_maths['Свойства степеней и корней'] = b[20:36]
imgs_formulas_maths['Формулы с логарифмами'] = b[36:49]
imgs_formulas_maths['Арифметическая прогрессия'] = b[49:54]
imgs_formulas_maths['Геометрическая прогрессия'] = b[54:60]
imgs_formulas_maths['Тригонометрия'] = b[60:100]
imgs_formulas_maths['Тригонометрические уравнения'] = b[100:113]
imgs_formulas_maths['Геометрия на плоскости (планиметрия)'] = b[113:169]
imgs_formulas_maths['Геометрия в пространстве (стереометрия)'] = b[169:183]
imgs_formulas_maths['Координаты'] = b[183:187]
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
imgs_formulas_physics['Кинематика'] = b[:35]
imgs_formulas_physics['Динамика'] = b[35:50]
imgs_formulas_physics['Статика'] = b[50:53]
imgs_formulas_physics['Гидростатика'] = b[53:60]
imgs_formulas_physics['Импульс'] = b[60:67]
imgs_formulas_physics['Работа, мощность, энергия'] = b[67:77]
imgs_formulas_physics['Молекулярная физика'] = b[77:94]
imgs_formulas_physics['Термодинамика'] = b[94:120]
imgs_formulas_physics['Электростатика'] = b[120:147]
imgs_formulas_physics['Электрический ток'] = b[147:169]
imgs_formulas_physics['Магнетизм'] = b[169:187]
imgs_formulas_physics['Колебания'] = b[187:224]
imgs_formulas_physics['Оптика'] = b[224:233]
imgs_formulas_physics['Атомная и ядерная физика'] = b[233:254]
imgs_formulas_physics['Основы специальной теории относительности (СТО)'] = b[254:264]

# Соединяемся с базой данных SQL
conn = sqlite3.connect('../databases/notes.db')
cur = conn.cursor()

# Создаем таблицу для хранения заметок
cur.execute('''CREATE TABLE IF NOT EXISTS notes
               (id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT,
                content TEXT,
                tg BOOLEAN)''')


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)
logger = logging.getLogger(__name__)
load_dotenv()


async def show_formulas(update, context):
    if len(context.args) == 0:
        await update.message.reply_text("/show_formulas maths - посмотреть названия и id тем по математике\n/show_formulas phisics - посмотреть названия и id тем по физике\n/show_formulas <id> - найти формулы по айди темы")
    elif context.args[0] == "maths":
        keys = list(imgs_formulas_maths)
        for i in range(len(keys)):
            await update.message.reply_text(f"{i}. {keys[i]}")
    elif context.args[0] == "physics":
        keys = list(imgs_formulas_physics)
        for i in range(len(keys)):
            await update.message.reply_text(f"{11 + i}. {keys[i]}")
    elif context.args[0].isdigit() and 0 <= int(context.args[0]) <= 25:
        if int(context.args[0]) < 11:
            for i in imgs_formulas_maths[list(imgs_formulas_maths)[int(context.args[0])]]:
                await update.message.reply_photo(i)
        else:
            for i in imgs_formulas_physics[list(imgs_formulas_physics)[int(context.args[0]) - 11]]:
                await update.message.reply_photo(i)


# Функция для создания заметки
async def create_note_handler(update, context):
    user_id = update.message.from_user.id
    title = ' '.join(context.args)
    content = ""
    cur.execute('INSERT INTO notes (user_id, title, content, tg) VALUES (?, ?, ?, ?)', (user_id, title, content, 1))
    conn.commit()
    await update.message.reply_text('Заметка успешно создана!')


async def handle_text(update, context):
    text = update.message.text
    await update.message.reply_text(f'Ваше сообщение - {text}')


# Функция для просмотра заметок
async def view_notes_handler(update, context):
    user_id = update.message.from_user.id
    cur.execute('SELECT id, title, content FROM notes WHERE tg = 1 AND user_id = ?', (user_id,))
    notes = cur.fetchall()
    if len(notes) == 0:
        await update.message.reply_text('У вас нет заметок!')
    else:
        for note in notes:
            await update.message.reply_text(f'{note[0]}. {note[1]}\n\n{note[2]}')


# Функция для редактирования заметки
async def edit_note_handler(update, context):
    user_id = update.message.from_user.id
    note_id = context.args[0]
    content = ' '.join(context.args[1:])
    cur.execute('UPDATE notes SET content = ? WHERE tg = 1 AND id = ? AND user_id = ?', (content, note_id, user_id))
    conn.commit()
    if cur.rowcount == 0:
        await update.message.reply_text('Заметка не найдена!')
    else:
        await update.message.reply_text('Заметка успешно отредактирована!')


# Функция для удаления заметки
async def delete_note_handler(update, context):
    user_id = update.message.from_user.id
    note_id = context.args[0]
    cur.execute('DELETE FROM notes WHERE id = ? AND user_id = ? AND tg = 1', (note_id, user_id))
    conn.commit()
    if cur.rowcount == 0:
        await update.message.reply_text('Заметка не найдена!')
    else:
        await update.message.reply_text('Заметка успешно удалена!')


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler('create_note', create_note_handler))
    application.add_handler(CommandHandler('view_notes', view_notes_handler))
    application.add_handler(CommandHandler('edit_note', edit_note_handler))
    application.add_handler(CommandHandler('delete_note', delete_note_handler))
    application.add_handler(CommandHandler('show_formulas', show_formulas))
    application.add_handler(MessageHandler(filters.TEXT, handle_text))
    application.run_polling()


if __name__ == '__main__':
    main()