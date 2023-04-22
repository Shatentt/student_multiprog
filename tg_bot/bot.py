import logging

import requests
from deep_translator.exceptions import LanguageNotSupportedException
from dotenv import load_dotenv
from telegram.ext import Application, Updater, CommandHandler, MessageHandler, filters
from config import BOT_TOKEN
import sqlite3
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from deep_translator import GoogleTranslator

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

is_translating = False
from_lang = "auto"
to_lang = "auto"

# Соединяемся с базой данных SQL
conn = sqlite3.connect('../databases/notes.db')
cur = conn.cursor()

# Создаем таблицу для хранения заметок
cur.execute('''CREATE TABLE IF NOT EXISTS notes
               (id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT,
                content TEXT)''')


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)
logger = logging.getLogger(__name__)
load_dotenv()


async def formulas_handler(update, context):
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

async def handle_text(update, context):
    if to_lang != "auto":
        text = update.message.text
        translated = GoogleTranslator(source=from_lang, target=to_lang).translate(text)
        await update.message.reply_text(f'Перевод вашего сообщения c {from_lang} на {to_lang} - {translated}')


async def start(update, context):
    await update.message.reply_text(f'Привет! Я бот-помощник для студентов и школьников. Чтобы узнать, что я могу, ты можешь написать:\n/notes - показать все команды для заметок\n/translate - показать информацию о переводчике\n/formulas - показать информацию о формулах')

async def translate_handler(update, context):
    global from_lang, to_lang
    if len(context.args) == 0:
        s = ""
        langs_dict = GoogleTranslator().get_supported_languages(as_dict=True)
        for i in langs_dict:
            s += f"{i} - {langs_dict[i]}\n"
        await update.message.reply_text(f'Введите /translate <from_language> <to_language>, чтобы установить с какого и на какой язык переводить.После выбора языка напишите боту любое сообщение, и он скажет вам его перевод.\nАйди языков:\n{s}')
    elif len(context.args) == 2:
        try:
            translated = GoogleTranslator(source=context.args[0], target=context.args[1]).translate("")
            from_lang = context.args[0]
            to_lang = context.args[1]
            await update.message.reply_text(f'Вы успешно сменили языки!')
        except LanguageNotSupportedException:
            await update.message.reply_text(f'Ошибка! Неправильно введен айди языка')


async def notes_handler(update, context):
    if len(context.args) == 0:
        await update.message.reply_text('Команды для заметок:\n/notes view - посмотреть ваши заметки и их айди\n/notes create <note_name> - создать заметку с названием <note_name>\n/notes edit <note_id> <text> - изменить текст заметки по айди\n/notes delete <note_id> - удалить заметку по айди')
    elif context.args[0] == "create":
        user_id = update.message.from_user.id
        title = ' '.join(context.args[1:])
        content = ""
        cur.execute('INSERT INTO notes (user_id, title, content) VALUES (?, ?, ?)', (user_id, title, content))
        conn.commit()
        await update.message.reply_text('Заметка успешно создана!')
    elif context.args[0] == "view":
        user_id = update.message.from_user.id
        cur.execute('SELECT id, title, content FROM notes WHERE user_id = ?', (user_id,))
        notes = cur.fetchall()
        if len(notes) == 0:
            await update.message.reply_text('У вас нет заметок!')
        else:
            for note in notes:
                await update.message.reply_text(f'{note[0]}. {note[1]}\n\n{note[2]}')
    elif context.args[0] == "edit":
        user_id = update.message.from_user.id
        note_id = context.args[1]
        content = ' '.join(context.args[2:])
        cur.execute('UPDATE notes SET content = ? WHERE id = ? AND user_id = ?', (content, note_id, user_id))
        conn.commit()
        if cur.rowcount == 0:
            await update.message.reply_text('Заметка не найдена!')
        else:
            await update.message.reply_text('Заметка успешно отредактирована!')
    elif context.args[0] == "delete":
        user_id = update.message.from_user.id
        note_id = context.args[1]
        cur.execute('DELETE FROM notes WHERE id = ? AND user_id = ?', (note_id, user_id))
        conn.commit()
        if cur.rowcount == 0:
            await update.message.reply_text('Заметка не найдена!')
        else:
            await update.message.reply_text('Заметка успешно удалена!')


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler('notes', notes_handler))
    application.add_handler(CommandHandler('formulas', formulas_handler))
    application.add_handler(CommandHandler('translate', translate_handler))
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT, handle_text))
    application.run_polling()


if __name__ == '__main__':
    main()