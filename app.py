from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
from config import DB_CONFIG, SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY

def get_db():
    return pymysql.connect(
        **DB_CONFIG,
        cursorclass=pymysql.cursors.DictCursor
    )

def get_user_by_id(user_id):
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                'SELECT user_id, username, email FROM users WHERE user_id = %s',
                (user_id,)
            )
            return cursor.fetchone()
    finally:
        db.close()

def get_follower_count(user_id):
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                'SELECT COUNT(*) AS count FROM follows WHERE following_id = %s',
                (user_id,)
            )
            return cursor.fetchone()['count']
    finally:
        db.close()

def get_following_count(user_id):
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                'SELECT COUNT(*) AS count FROM follows WHERE follower_id = %s',
                (user_id,)
            )
            return cursor.fetchone()['count']
    finally:
        db.close()

def is_following(follower_id, following_id):
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                '''
                SELECT 1
                FROM follows
                WHERE follower_id = %s AND following_id = %s
                ''',
                (follower_id, following_id)
            )
            return cursor.fetchone() is not None
    finally:
        db.close()

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/profile')
def profile():
    user_id = session.get('user_id')
    
    if not user_id:
        flash('Please log in first.')
        return redirect(url_for('login'))
    
    user = get_user_by_id(user_id)
    follower_count = get_follower_count(user_id)
    following_count = get_following_count(user_id)

    return render_template(
        'profile.html',
        user = user,
        follower_count = follower_count,
        following_count = following_count
    )

@app.route('/recipes')
def recipe_page():
    return render_template('recipes_page.html')

@app.route('/meals')
def meal_page():
    return render_template('meal_page.html')

# Auth Routes:

# Register 
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    username = request.form['username']
    email    = request.form['email']
    password = request.form['password']
    confirm  = request.form['confirm-password']

    # Basic validation
    if password != confirm:
        flash('Passwords do not match.')
        return redirect(url_for('register'))

    if len(username) > 20:
        flash('Username must be 20 characters or fewer.')
        return redirect(url_for('register'))

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
        # username or email already taken
        flash('Username or email is already in use.')
        return redirect(url_for('register'))
    finally:
        db.close()

    return redirect(url_for('login'))

#Login
@app.route('/login', methods=['GET', 'POST'])
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
        return redirect(url_for('login'))

    # Store user_id in the session so we know who is logged in
    session['user_id'] = user['user_id']
    return redirect(url_for('home'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('landing'))

if __name__ == '__main__':
    app.run(debug=True)