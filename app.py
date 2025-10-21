from flask import Flask, render_template, request, redirect, url_for, session
import random
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"  # session key


# ---------- DATABASE SETUP ----------
def init_db():
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            attempts INTEGER,
            result TEXT
        )
    ''')
    conn.commit()
    conn.close()


# ---------- HOME PAGE ----------
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        session['name'] = request.form['name']
        session['number'] = random.randint(100, 999)
        session['attempts'] = 0
        return redirect(url_for('guess'))
    return render_template('index.html')


# ---------- GUESS PAGE ----------
@app.route('/guess', methods=['GET', 'POST'])
def guess():
    if 'number' not in session:
        return redirect(url_for('index'))

    message = ''
    if request.method == 'POST':
        guess = int(request.form['guess'])
        session['attempts'] += 1

        if guess < session['number']:
            message = "Too low! Try again."
        elif guess > session['number']:
            message = "Too high! Try again."
        else:
            # Save result to DB
            conn = sqlite3.connect('game.db')
            c = conn.cursor()
            c.execute("INSERT INTO players (name, attempts, result) VALUES (?, ?, ?)",
                      (session['name'], session['attempts'], 'Win'))
            conn.commit()
            conn.close()
            return redirect(url_for('result', status='win'))

        if session['attempts'] >= 10:
            conn = sqlite3.connect('game.db')
            c = conn.cursor()
            c.execute("INSERT INTO players (name, attempts, result) VALUES (?, ?, ?)",
                      (session['name'], session['attempts'], 'Lose'))
            conn.commit()
            conn.close()
            return redirect(url_for('result', status='lose'))

    return render_template('guess.html', message=message, attempts=session['attempts'])


# ---------- RESULT PAGE ----------
@app.route('/result/<status>')
def result(status):
    number = session.get('number', None)
    name = session.get('name', None)
    attempts = session.get('attempts', 0)
    session.clear()

    return render_template('result.html', status=status, number=number, name=name, attempts=attempts)


# ---------- VIEW SCORES ----------
@app.route('/scores')
def scores():
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute("SELECT * FROM players ORDER BY id DESC")
    data = c.fetchall()
    conn.close()
    return render_template('scores.html', data=data)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)

