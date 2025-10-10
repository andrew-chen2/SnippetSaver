from flask import session, redirect, url_for, render_template
from re import match

class Auth:
    def __init__(self, get_db):
        self.get_db = get_db
        self.username = None
        self.user_id = None

    def register(self, username: str, password: str):
        con = self.get_db()
        
        # Check if user(name) already exists
        sql = "Select 1 FROM users WHERE username = ?"
        cur = con.execute(sql, (username,))
        if cur.fetchone() is not None:
            return render_template('register.html', error="Username already taken.")
        
        # Input validation
        if username.strip() == '' or password.strip() == '':
            return render_template('register.html', error="Username and password cannot be empty.")
        regex = "^[a-zA-Z0-9_]+$"
        if not match(regex, username):
            return render_template('register.html', error="Username can only contain letters, numbers, and underscores.")
        if len(password) < 6:
            return render_template('register.html', error="Password must be at least 6 characters long.")
        if len(username) < 3:
            return render_template('register.html', error="Username must be at least 3 characters long.")
        if len(password) > 64:
            return render_template('register.html', error="Password cannot be longer than 64 characters.")
        if len(username) > 20:
            return render_template('register.html', error="Username cannot be longer than 20 characters.")

        # Store in database
        sql = "INSERT INTO users (username, password) VALUES (?, ?)"
        cur = con.execute(sql, (username, password))
        con.commit()
        
        session['username'] = username
        self.username = username
        self.user_id = cur.lastrowid

        return redirect(url_for('index'))

    def login(self, username: str, password: str):
        con = self.get_db()
        sql = "SELECT * FROM users WHERE username = ? AND password = ?"
        cur = con.execute(sql, (username, password))
        user = cur.fetchone()
        if user:
            session['username'] = username
            self.username = username
            self.user_id = user[0]

            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid username or password.")
        
    def logout(self):
        session.pop('username', None)
        self.username = None
        self.user_id = None

        return redirect(url_for('index'))
    
    def is_authenticated(self):
        return 'username' in session

    def require_auth(self, func):
        def wrapper(*args, **kwargs):
            if not self.is_authenticated():
                return redirect(url_for('login'))
            return func(*args, **kwargs)
        wrapper.__name__ = func.__name__
        return wrapper

    def require_guest(self, func):
        def wrapper(*args, **kwargs):
            if self.is_authenticated():
                return redirect(url_for('index'))
            return func(*args, **kwargs)
        wrapper.__name__ = func.__name__
        return wrapper