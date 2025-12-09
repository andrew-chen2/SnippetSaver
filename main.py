from flask import Flask, render_template, request, g, session, redirect, url_for, abort
from sqlite3 import connect
import os
from auth import Auth
from database import init_tables, delete_rows
from snippets.snippet import Snippet

LANGS = {
    "python": 'Python',
    "javascript": 'JavaScript',
    "java": 'Java',
    "cpp": 'C++',
    "csharp": 'C#',
    "html": 'HTML',
    "other": 'Other',
}

def get_snippet_dict(snippet):
    return {
        'id': snippet[0],
        'title': snippet[2],
        'code': snippet[3],
        'language': LANGS[snippet[4]],
        'created_at': snippet[6],
        'modified_at': snippet[7],
    }

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

@app.cli.command('resetdb')
def resetdb():
    init_tables()
    delete_rows(['users', 'snippets'])
    print("Database reset.")

@app.route('/')
def index():
    return render_template('index.html', username=session.get('username'))

@app.route('/login', methods=['GET', 'POST'])
@auth.require_guest
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        return auth.login(username, password)

@app.route('/register', methods=['GET', 'POST'])
@auth.require_guest
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        return auth.register(username, password)
    
@app.route('/logout', methods=['POST'])
@auth.require_auth
def logout():
    return auth.logout()

@app.route('/new', methods=['POST'])
def new():
    title = request.form['title']
    language = request.form['language']
    code = request.form['code']

    if title.strip() == '':
        return render_template('new.html', error='Title cannot be empty.')
    if language.strip() == '':
        return render_template('new.html', error='Language cannot be empty.')
    if code.strip() == '':
        return render_template('new.html', error='Code cannot be empty.')
    
    snippet = Snippet(get_db, auth.user_id, title, code, language)
    snippet.save()

    return redirect(url_for('snippet', id = snippet.snippet_id))

@app.route('/snippets')
def snippets():
    con = get_db()
    sql = "SELECT * FROM snippets WHERE user_id = ?"
    cur = con.execute(sql, (auth.user_id,))
    snippets = cur.fetchall()
    snippets_arr = []
    for snippet in snippets:
        snippets_arr.append(get_snippet_dict(snippet))
    return render_template('library.html', snippets = snippets_arr)

@app.route('/snippets/search')
def search_snippets():
    con = get_db()
    query = request.args.get('q', '').strip()
    sort = request.args.get('sort', 'recent')

    sql = "SELECT * FROM snippets WHERE user_id = ? AND title LIKE ?"
    cur = con.execute(sql, (auth.user_id, f'%{query}%'))
    snippets = cur.fetchall()
    snippets_arr = []
    for snippet in snippets:
        snippets_arr.append(get_snippet_dict(snippet))
    
    match sort:
        case 'recent':
            snippets_arr.sort(key=lambda x: x['modified_at'] or x['created_at'], reverse=True)
        case 'title':
            snippets_arr.sort(key=lambda x: x['title'].lower())
        case 'language':
            snippets_arr.sort(key=lambda x: x['language'].lower())

    return render_template('library.html', snippets = snippets_arr)

@app.route('/snippets/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    if request.method == 'GET':
        con = get_db()
        sql = "SELECT * FROM snippets WHERE id = ? AND user_id = ?"
        cur = con.execute(sql, (id, auth.user_id))
        snippet = cur.fetchone()
        if snippet:
            snippet_dict = get_snippet_dict(snippet)
            return render_template('edit.html', snippet = snippet_dict)
        return 'Not found'
    elif request.method == 'POST':
        title = request.form['title']
        language = request.form['language']
        code = request.form['code']

        snippet = Snippet(get_db, auth.user_id, snippet_id=id)
        snippet.edit(title, code, language)

        return redirect(url_for('snippet', id = id))

@app.route('/snippets/<id>')
def snippet(id):
    if id == 'new':
        return render_template('new.html')
    con = get_db()
    sql = "SELECT * FROM snippets WHERE id = ? AND user_id = ?"
    cur = con.execute(sql, (id, auth.user_id))
    snippet = cur.fetchone()
    if snippet:
        snippet_dict = get_snippet_dict(snippet)
        return render_template('snippet.html', snippet = snippet_dict)
    return 'Not found'

@app.route('/snippets/<int:id>/delete')
def delete_snippet(id):
    snippet = Snippet(get_db, auth.user_id, snippet_id=id)
    snippet.delete()
    return redirect(url_for('snippets'))

if __name__ == '__main__':
    app.run(debug=True)