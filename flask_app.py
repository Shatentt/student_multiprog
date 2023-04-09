import os

from flask import Flask, render_template, redirect, url_for
from forms.NoteForm import NoteForm
from data.notes import db, Note
from pathlib import Path

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
cur_dir = Path.cwd()
db_path = cur_dir / 'databases' / 'notes.db'
print(db_path)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
db.init_app(app)


@app.route("/")
def index():
    return render_template("main_page.html")


@app.route('/notes', methods=['GET', 'POST'])
def notes():
    form = NoteForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        note = Note(title=title, content=content)
        db.session.add(note)
        db.session.commit()
        return redirect(url_for('notes'))
    notes = Note.query.all()
    return render_template('notes.html', form=form, notes=notes)


@app.route('/notes/<int:id>', methods=['GET', 'POST'])
def edit_note(id):
    note = Note.query.get_or_404(id)
    form = NoteForm(obj=note)
    if form.validate_on_submit():
        form.populate_obj(note)
        db.session.commit()
        return redirect(url_for('notes'))
    return render_template('edit_note.html', form=form, note=note)


@app.route('/notes/delete/<int:id>', methods=['POST'])
def delete_note(id):
    note = Note.query.get_or_404(id)
    db.session.delete(note)
    db.session.commit()
    return redirect(url_for('notes'))



def main():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()