from flask import Flask, render_template, request, redirect, url_for, g
from sqlite3 import connect
import re

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

# Close db connection when the context is destroyed
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        con = get_db()
        username = request.form['username']
        password = request.form['password']

        sql = "SELECT * FROM users WHERE username = ? AND password = ?"
        cur = con.execute(sql, (username, password))
        user = cur.fetchone()
        if user:
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid username or password.")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        con = get_db()
        username = request.form['username']
        password = request.form['password']

        # Input validation
        if username.strip() == '' or password.strip() == '':
            return render_template('register.html', error="Username and password cannot be empty.")
        if len(password) < 6:
            return render_template('register.html', error="Password must be at least 6 characters long.")
        if len(username) < 3:
            return render_template('register.html', error="Username must be at least 3 characters long.")
        if len(password) > 64:
            return render_template('register.html', error="Password cannot be longer than 64 characters.")
        if len(username) > 20:
            return render_template('register.html', error="Username cannot be longer than 20 characters.")
        regex = "^[a-zA-Z0-9_]+$"
        if not re.match(regex, username):
            return render_template('register.html', error="Username can only contain letters, numbers, and underscores.")
        
        # Check if user(name) already exists
        sql = "Select 1 FROM users WHERE username = ?"
        cur = con.execute(sql, (username,))
        if cur.fetchone() is not None:
            return render_template('register.html', error="Username already taken.")

        # Store in database
        sql = "INSERT INTO users (username, password) VALUES (?, ?)"
        con.execute(sql, (username, password))
        con.commit()
        return "User registered successfully!"

if __name__ == '__main__':
    app.run(debug=True)
    init_tables()