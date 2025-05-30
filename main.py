
from flask import Flask, render_template, request, redirect, session, g
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'
DATABASE = 'instance/attendance.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        teacher = db.execute("SELECT * FROM teacher WHERE username=? AND password=?", (username, password)).fetchone()
        if teacher:
            session['teacher'] = username
            return redirect('/dashboard')
        else:
            error = 'Invalid Credentials'
    return render_template('login.html', error=error)

@app.route('/dashboard')
def dashboard():
    if 'teacher' not in session:
        return redirect('/')
    db = get_db()
    students = db.execute("SELECT * FROM student").fetchall()
    return render_template('dashboard.html', students=students)

@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    if 'teacher' not in session:
        return redirect('/')
    db = get_db()
    today = datetime.today().strftime('%Y-%m-%d')
    for key, value in request.form.items():
        db.execute("INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)", (key, today, value))
    db.commit()
    return redirect('/dashboard')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81)

