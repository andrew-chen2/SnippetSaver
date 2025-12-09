from flask import Flask, render_template, request, g, session, redirect, url_for, abort
from sqlite3 import connect
import os
from auth import Auth
from database import init_tables, delete_rows
from snippet import Snippet
from snippet_controller import SnippetController

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect('snippetsaver.db')
    return db

app = Flask(__name__)
app.secret_key = os.urandom(24)

auth = Auth(get_db)
controller = SnippetController(get_db)

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
@auth.require_auth
def new():
    title = request.form['title']
    language = request.form['language']
    code = request.form['code']

    if title.strip() == '' or code.strip() == '' or not language:
        abort(400, "Title, code, and language cannot be empty.")

    if len(title) > 128 or len(code) > 4000:
        abort(400, "Title or code exceeds maximum length.")

    return controller.create_snippet(auth.user_id, title, code, language)

@app.route('/snippets')
@auth.require_auth
def snippets():
    return controller.search_snippets(auth.user_id, '', 'recent', False, False)

@app.route('/snippets/search')
@auth.require_auth
def search_snippets():
    query = request.args.get('q', '').strip().lower()
    sort = request.args.get('sort', 'recent')
    include_code = request.args.get('include_code')
    fuzzy = request.args.get('fuzzy')

    return controller.search_snippets(auth.user_id, query, sort, include_code, fuzzy)

@app.route('/snippets/<int:id>/edit', methods=['GET', 'POST'])
@auth.require_auth
def edit(id):
    if request.method == 'GET':
        snippet = controller.get_snippet(id, auth.user_id)
        if snippet:
            return render_template('edit.html', snippet=snippet)
        abort(404)
    elif request.method == 'POST':
        title = request.form['title']
        language = request.form['language']
        code = request.form['code']

        if title.strip() == '' or code.strip() == '' or not language:
            abort(400, "Title, code, and language cannot be empty.")
        
        if len(title) > 128 or len(code) > 4000:
            abort(400, "Title or code exceeds maximum length.")

        snippet = controller.get_snippet_from_id(id, auth.user_id)
        snippet.edit(title, code, language)

        return redirect(url_for('snippet', id=id))

@app.route('/snippets/<id>')
@auth.require_auth
def snippet(id):
    if id == 'new':
        return render_template('new.html')
    
    snippet = controller.get_snippet(id, auth.user_id)
    if snippet:
        return render_template('snippet.html', snippet=snippet)
    abort(404)

@app.route('/snippets/<int:id>/delete')
@auth.require_auth
def delete_snippet(id):
    snippet = controller.get_snippet_from_id(id, auth.user_id)
    snippet.delete()
    return redirect(url_for('snippets'))

@app.route('/snippets/<int:id>/share')
@auth.require_auth
def share_snippet(id):
    snippet = controller.get_snippet_from_id(id, auth.user_id)
    snippet.share()
    return redirect(url_for('shared', share_id=snippet.share_id))

@app.route('/snippets/<int:id>/unshare')
@auth.require_auth
def unshare_snippet(id):
    snippet = controller.get_snippet_from_id(id, auth.user_id)
    snippet.unshare()
    return redirect(url_for('snippet', id=id))

@app.route('/shared/<string:share_id>')
def shared(share_id):
    return controller.get_shared_snippet(share_id, auth.user_id)

@app.route('/shared/<string:share_id>/add')
@auth.require_auth
def add_shared(share_id):
    return controller.add_shared_snippet(share_id, auth.user_id)

if __name__ == '__main__':
    app.run(debug=True)