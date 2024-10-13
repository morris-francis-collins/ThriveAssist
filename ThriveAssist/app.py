from flask import Flask, render_template, request, session, redirect, jsonify
from flask_session import Session
import sqlite3
import os
from wrapper import chat, generate_questions

app = Flask(__name__)
conn = sqlite3.connect('database.db', check_same_thread=False)
db = conn.cursor()
app.config["SECRET_KEY"] = os.urandom(24)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/journal', methods = ['GET', 'POST'])
def journal():
    if not session.get("loggedin", None) or not session.get("user_id", None):
        return redirect('/login')

    if request.method == 'GET':
        user_id = session['user_id']
        user_id, q1, a1, q2, a2, q3, a3, j = db.execute('SELECT * FROM journals WHERE user_id = ? SORT BY DESC LIMIT = 1', (user_id,))
        if not j:
            questions = ["How are you feeling today?", "What are you grateful for today?", "What are you looking forward to tomorrow?"]
        else:
            prompt = f"Journal: {j}\n{q1}\n{a1}\n{q2}\n{a2}\n{q3}\n{a3}"
            questions = generate_questions(prompt)
        return render_template('journal.html', questions = questions)
    else:
        return redirect('/')


@app.route('/api/journal', methods = ['POST'])
def post_journal():

    if request.method == 'POST':
        q1 = request.form["question1"]
        q2 = request.form["question2"]
        q3 = request.form["question3"]
        a1 = request.form["answer1"]
        a2 = request.form["answer2"]
        a3 = request.form["answer3"]
        j = request.form["journal"]
        if any(not x for x in [q1, q2, q3, a1, a2, a3, j]):
            return render_template('apology.html', message = "Fill out every form.")
        
        db.execute('INSERT INTO journals (?, ?, ?, ?, ?, ?, ?, ?)', (session['user_id'], q1, q2, q3, a1, a2, a3, j))
        
        prompt = f"Journal: {j}\n{q1}\n{a1}\n{q2}\n{a2}\n{q3}\n{a3}"
        return chat(prompt)
    else:
        return jsonify({1:True})

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            return render_template('apology.html', message = "Please fill in all fields.")

        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if not user:
            return render_template('apology.html', message = "Invalid username or password.")
        user_id, user_username, user_password = user

        if password != user_password:
            return render_template('apology.html', message = "Invalid username or password.")
        
        session['loggedin'] = True
        session['user_id'] = user_id
        return redirect('/')
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    session['loggedin'] = False
    session['user_id'] = None
    return redirect('/')

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirmation = request.form['confirmation']

        if len(username) > 20:
            return render_template('apology.html', message = "Username must be 20 or less characters.")
        if len(password) > 64:
            return render_template('apology.html', message = "Password must be 64 or less characters.")
        if password != confirmation:
            return render_template('apology.html', message = "Passwords do not match.")
        if not username or not password or not confirmation:
            return render_template('apology.html', message = "Please fill out all fields.")
        
        usernames = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchall()

        for user in usernames:
            if username == user[1]:
                return render_template('apology.html', message = "Username already taken.")

        db.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

        session['loggedin'] = True
        session['user_id'] = user[0]

        return redirect('/')
    
    else:
        return render_template('register.html')
    
@app.route('/apology')
def apology():
    return render_template('apology.html')

if __name__ == '__main__':
    app.run(debug=True)