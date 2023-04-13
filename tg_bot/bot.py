import logging

from dotenv import load_dotenv
from telegram.ext import Application, Updater, CommandHandler, MessageHandler
from config import BOT_TOKEN
import sqlite3

# Соединяемся с базой данных SQL
conn = sqlite3.connect('notes.db')
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


# Функция для создания заметки
async def create_note_handler(update, context):
    user_id = update.message.from_user.id
    title = ' '.join(context.args)
    content = ""
    cur.execute('INSERT INTO notes (user_id, title, content) VALUES (?, ?, ?)', (user_id, title, content))
    conn.commit()
    await update.message.reply_text('Заметка успешно создана!')


# Функция для просмотра заметок
async def view_notes_handler(update, context):
    user_id = update.message.from_user.id
    cur.execute('SELECT id, title, content FROM notes WHERE user_id = ?', (user_id,))
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
    cur.execute('UPDATE notes SET content = ? WHERE id = ? AND user_id = ?', (content, note_id, user_id))
    conn.commit()
    if cur.rowcount == 0:
        await update.message.reply_text('Заметка не найдена!')
    else:
        await update.message.reply_text('Заметка успешно отредактирована!')


# Функция для удаления заметки
async def delete_note_handler(update, context):
    user_id = update.message.from_user.id
    note_id = context.args[0]
    cur.execute('DELETE FROM notes WHERE id = ? AND user_id = ?', (note_id, user_id))
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
    application.run_polling()


if __name__ == '__main__':
    main()