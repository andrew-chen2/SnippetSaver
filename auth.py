from flask import session, redirect, url_for, flash
from re import match
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

class Auth:
    def __init__(self, get_db):
        self.get_db = get_db
        self.username = None
        self.user_id = None
        self.failed_attempts = 0
        self.last_login_at = None

    def register(self, username: str, password: str):
        con = self.get_db()
        
        # Check if user(name) already exists
        sql = "Select 1 FROM users WHERE username = ?"
        cur = con.execute(sql, (username,))
        if cur.fetchone() is not None:
            flash('Username already taken.', 'error')
            return redirect(url_for('register'))
        
        # Input validation
        if username.strip() == '' or password.strip() == '':
            flash('Username and password cannot be empty.', 'error')
            return redirect(url_for('register'))
        regex = "^[a-zA-Z0-9_]+$"
        if not match(regex, username):
            flash('Username can only contain letters, numbers, and underscores.', 'error')
            return redirect(url_for('register'))
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return redirect(url_for('register'))
        if len(username) < 3:
            flash('Username must be at least 3 characters long.', 'error')
            return redirect(url_for('register'))
        if len(password) > 64:
            flash('Password cannot be longer than 64 characters.', 'error')
            return redirect(url_for('register'))
        if len(username) > 20:
            flash('Username cannot be longer than 20 characters.', 'error')
            return redirect(url_for('register'))

        # Store in database
        sql = "INSERT INTO users (username, password) VALUES (?, ?)"
        cur = con.execute(sql, (username, generate_password_hash(password)))
        user_id = cur.lastrowid
        con.commit()
        
        session['username'] = username
        session['user_id'] = user_id
        self.username = username
        self.user_id = user_id
        self.last_login_at = datetime.datetime.now()

        return redirect(url_for('index'))

    def login(self, username: str, password: str):
        con = self.get_db()
        sql = "SELECT * FROM users WHERE username = ?"
        cur = con.execute(sql, (username,))
        user = cur.fetchone()
        *_, hashed_password = user if user else (None, None, None)
        if user and check_password_hash(hashed_password, password):
            user_id = user[0]
            session['username'] = username
            session['user_id'] = user_id
            self.username = username
            self.user_id = user_id
            self.last_login_at = datetime.datetime.now()
            self.failed_attempts = 0

            return redirect(url_for('index'))
        else:
            self.failed_attempts += 1
            
            flash('Invalid username or password.', 'error')
            return redirect(url_for('login'))
        
    def logout(self):
        session.pop('username', None)
        session.pop('user_id', None)
        self.username = None
        self.user_id = None

        return redirect(url_for('index'))

    @property
    def is_authenticated(self):
        return 'username' in session

    def require_auth(self, func):
        def wrapper(*args, **kwargs):
            if not self.is_authenticated:
                return redirect(url_for('login'))
            return func(*args, **kwargs)
        wrapper.__name__ = func.__name__
        return wrapper

    def require_guest(self, func):
        def wrapper(*args, **kwargs):
            if self.is_authenticated:
                return redirect(url_for('index'))
            return func(*args, **kwargs)
        wrapper.__name__ = func.__name__
        return wrapper
