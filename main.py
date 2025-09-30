from flask import Flask, render_template
from sqlite3 import connect

con = connect('snippetsaver.db')

def create_table(name: str, columns: dict):
    '''
    columns: {
        'column_name': ['PROPERTY1', 'PROPERTY2'],
        'some_other_column': ['PROPERTY1', 'PROPERTY2', ...],
        ...
    }

    cols: column_name PROPERTY1 PROPERTY2, some_other_column PROPERTY1 PROPERTY2 ...
    '''
    cols = ', '.join([f"{col} {' '.join(props)}" for col, props in columns.items()])
    sql = f"CREATE TABLE IF NOT EXISTS {name} ({cols})"
    con.execute(sql)

def init_tables():
    user_columns = {
        'id': ['INTEGER', 'PRIMARY KEY', 'AUTOINCREMENT'],
        'username': ['TEXT', 'UNIQUE', 'NOT NULL'],
        'password': ['TEXT', 'NOT NULL']
    }

    create_table('users', user_columns)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

if __name__ == '__main__':
    init_tables()
    app.run(debug=True)