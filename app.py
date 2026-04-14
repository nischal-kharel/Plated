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

def get_followers(user_id, current_user_id=None):
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                '''
                SELECT 
                    u.user_id,
                    u.username,
                    CASE 
                        WHEN u.user_id = %s THEN TRUE
                        ELSE EXISTS (
                            SELECT 1
                            FROM follows viewer_follows
                            WHERE viewer_follows.follower_id = %s
                              AND viewer_follows.following_id = u.user_id
                        )
                    END AS is_followed_by_current_user
                FROM follows f
                JOIN users u ON f.follower_id = u.user_id
                WHERE f.following_id = %s
                ORDER BY u.username ASC
                ''',
                (current_user_id, current_user_id, user_id)
            )
            followers = cursor.fetchall()

            for user in followers:
                user['is_current_user'] = (user['user_id'] == current_user_id)

            return followers
    finally:
        db.close()


def get_following(user_id, current_user_id=None):
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                '''
                SELECT 
                    u.user_id,
                    u.username,
                    CASE 
                        WHEN u.user_id = %s THEN TRUE
                        ELSE EXISTS (
                            SELECT 1
                            FROM follows viewer_follows
                            WHERE viewer_follows.follower_id = %s
                              AND viewer_follows.following_id = u.user_id
                        )
                    END AS is_followed_by_current_user
                FROM follows f
                JOIN users u ON f.following_id = u.user_id
                WHERE f.follower_id = %s
                ORDER BY u.username ASC
                ''',
                (current_user_id, current_user_id, user_id)
            )
            following = cursor.fetchall()

            for user in following:
                user['is_current_user'] = (user['user_id'] == current_user_id)

            return following
    finally:
        db.close()

def get_all_users():
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute('SELECT user_id, username, email FROM users')
            return cursor.fetchall()
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
    followers = get_followers(user_id, user_id)
    following = get_following(user_id, user_id)

    return render_template(
        'profile.html',
        user=user,
        follower_count=follower_count,
        following_count=following_count,
        followers=followers,
        following=following,
        current_user_id=user_id,
        following_status=False
    )

@app.route('/profile/<int:user_id>')
def view_profile(user_id):
    current_user_id = session.get('user_id')

    if not current_user_id:
        flash('Please log in first.')
        return redirect(url_for('login'))
    
    user = get_user_by_id(user_id)

    if user is None:
        flash('User not found.')
        return redirect(url_for('home'))

    follower_count = get_follower_count(user_id)
    following_count = get_following_count(user_id)
    followers = get_followers(user_id, current_user_id)
    following = get_following(user_id, current_user_id)

    following_status = False
    if current_user_id != user_id:
        following_status = is_following(current_user_id, user_id)
    
    return render_template(
        'profile.html',
        user=user,
        follower_count=follower_count,
        following_count=following_count,
        followers=followers,
        following=following,
        current_user_id=current_user_id,
        following_status=following_status
    )

@app.route('/users')
def users():
    current_user_id = session.get('user_id')

    if not current_user_id:
        flash('Please log in first.')
        return redirect(url_for('login'))

    all_users = get_all_users()
    return render_template('users.html', users=all_users, current_user_id=current_user_id)

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

@app.route('/follow/<int:user_id>', methods=['POST'])
def follow_user(user_id):
    current_user_id = session.get('user_id')

    if not current_user_id:
        flash('Please log in first.')
        return redirect(url_for('login'))
    
    return_profile_id = request.form.get('return_profile_id', type=int)

    if current_user_id == user_id:
        flash('You cannot follow yourself.')
        if return_profile_id:
            if return_profile_id == current_user_id:
                return redirect(url_for('profile'))
            return redirect(url_for('view_profile', user_id=return_profile_id))
        return redirect(url_for('view_profile', user_id=user_id))

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                '''
                INSERT IGNORE INTO follows (follower_id, following_id)
                VALUES (%s, %s)
                ''',
                (current_user_id, user_id)
            )
        db.commit()
    finally:
        db.close()

    if return_profile_id:
        if return_profile_id == current_user_id:
            return redirect(url_for('profile'))
        return redirect(url_for('view_profile', user_id=return_profile_id))

    return redirect(url_for('view_profile', user_id=user_id))

@app.route('/unfollow/<int:user_id>', methods=['POST'])
def unfollow_user(user_id):
    current_user_id = session.get('user_id')

    if not current_user_id:
        flash('Please log in first.')
        return redirect(url_for('login'))
    
    return_profile_id = request.form.get('return_profile_id', type=int)
    
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                '''
                DELETE FROM follows
                WHERE follower_id = %s AND following_id = %s
                ''',
                (current_user_id, user_id)
            )
        db.commit()
    finally:
        db.close()

    if return_profile_id:
        if return_profile_id == current_user_id:
            return redirect(url_for('profile'))
        return redirect(url_for('view_profile', user_id=return_profile_id))

    return redirect(url_for('view_profile', user_id=user_id))

@app.route('/mylists')
def mylists():
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in first.')
        return redirect(url_for('login'))

    # test 
    user_lists_names = [
        {'id': 1, 'name': 'Want to Make'},
        {'id': 2, 'name': 'Favorites'},
        {'id': 3, 'name': 'Vegetarian'}
    ]
    return render_template('mylists.html', list_names=user_lists_names)

# Create new user list
@app.route('/createlist', methods=['POST'])
def createlist():
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in first.')
        return redirect(url_for('login'))
    
    list_name = request.form.get('list-name')
    # check if list name is taken, then show error message and redirect
    # otherwise create new empty list and reload with new list template
    return redirect(url_for('mylists'))

# Delete User List
@app.route('/delete', methods=['POST'])
def delete_list():
    list_id = request.form.get('list_id')
    if list_id:
        db = get_db()
        try:
            with db.cursor() as cursor:
                # table doesn't exist yet
                cursor.execute("DELETE FROM lists WHERE id = %s", (list_id,))
            db.commit()
        finally:
            db.close()
    return redirect(url_for('mylists'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('landing'))

if __name__ == '__main__':
    app.run(debug=True)