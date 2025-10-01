from flask import Flask, render_template, request, redirect, url_for, g, session
from sqlite3 import connect
import os
from auth import Auth

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect('snippetsaver.db')
    return db

def create_table(name: str, columns: dict):
    '''
    columns: {
        'column_name': ['PROPERTY1', 'PROPERTY2'],
        'some_other_column': ['PROPERTY1', 'PROPERTY2', ...],
        ...
    }

    cols: column_name PROPERTY1 PROPERTY2, some_other_column PROPERTY1 PROPERTY2 ...
    '''
    con = get_db()
    cols = ', '.join([f"{col} {' '.join(props)}" for col, props in columns.items()])
    sql = f"CREATE TABLE IF NOT EXISTS {name} ({cols})"
    con.execute(sql)

def init_tables():
    user_columns = {
        'id': ['INTEGER', 'PRIMARY KEY', 'AUTOINCREMENT'],
        'username': ['TEXT', 'UNIQUE', 'NOT NULL'],
        'password': ['TEXT', 'NOT NULL']
    }

    snippet_columns = {
        'id': ['INTEGER', 'PRIMARY KEY', 'AUTOINCREMENT'],
        'user_id': ['INTEGER', 'NOT NULL'],
        'title': ['TEXT', 'NOT NULL'],
        'code': ['TEXT', 'NOT NULL'],
        'language': ['TEXT'],
        'created_at': ['TIMESTAMP', 'DEFAULT CURRENT_TIMESTAMP'],
        'FOREIGN KEY(user_id)': ['REFERENCES users(id)']
    }

    create_table('users', user_columns)
    create_table('snippets', snippet_columns)

app = Flask(__name__)
app.secret_key = os.urandom(24)

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
    auth = Auth(get_db)