from flask import Flask, render_template, request, redirect, url_for, g, session
from sqlite3 import connect
import os
from auth import Auth
from database import init_tables

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect('snippetsaver.db')
    return db

app = Flask(__name__)
app.secret_key = os.urandom(24)

auth = Auth(get_db)

# Close db connection when the context is destroyed
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    return render_template('index.html', username=session.get('username'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('username'):
        return redirect(url_for('index'))
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        return auth.login(username, password)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('username'):
        return redirect(url_for('index'))
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        return auth.register(username, password)
    
@app.route('/logout', methods=['POST'])
def logout():
    return auth.logout()

if __name__ == '__main__':
    app.run(debug=True)
    init_tables()