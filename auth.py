from flask import session, redirect, url_for, render_template
from re import match

class Auth:
    def __init__(self, get_db):
        self.get_db = get_db

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
        con.execute(sql, (username, password))
        con.commit()
        
        session['username'] = username
        return redirect(url_for('index'))

    def login(self, username: str, password: str):
        con = self.get_db()
        sql = "SELECT * FROM users WHERE username = ? AND password = ?"
        cur = con.execute(sql, (username, password))
        user = cur.fetchone()
        if user:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid username or password.")
        
    def logout(self):
        session.pop('username', None)
        return redirect(url_for('index'))