from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
from db import get_db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    username = request.form['username']
    email    = request.form['email']
    password = request.form['password']
    confirm  = request.form['confirm-password']

    if password != confirm:
        flash('Passwords do not match.')
        return redirect(url_for('auth.register'))

    if len(username) > 20:
        flash('Username must be 20 characters or fewer.')
        return redirect(url_for('auth.register'))

    password_hash = generate_password_hash(password)

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                'INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)',
                (username, email, password_hash)
            )
        db.commit()
    except pymysql.err.IntegrityError:
        flash('Username or email is already in use.')
        return redirect(url_for('auth.register'))
    finally:
        db.close()

    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form['username']
    password = request.form['password']

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                'SELECT user_id, password_hash FROM users WHERE username = %s',
                (username,)
            )
            user = cursor.fetchone()
    finally:
        db.close()

    if user is None or not check_password_hash(user['password_hash'], password):
        flash('Invalid username or password.')
        return redirect(url_for('auth.login'))

    session['user_id'] = user['user_id']
    return redirect(url_for('home'))

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('landing'))
