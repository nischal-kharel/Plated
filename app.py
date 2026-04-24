from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
import os
import uuid
import json
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
    user_id = session.get('user_id')

    if not user_id:
        flash('Please log in first.')
        return redirect(url_for('login'))
    return render_template('home.html')

# trending recipes section
@app.route('/get_recipes')
def get_recipes():
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                '''SELECT recipe_id, recipe_name, recipe_pic
                FROM recipes
                ORDER BY created_at DESC 
                LIMIT 20'''
            )
            recipes = cursor.fetchall()
    finally:
        db.close()
    return {'recipes': recipes}

# Friend Activity section, for now it will take all recipes from the database
# will update laterr
@app.route('/get_feed_recipes')
def get_feed_recipes():
    user_id = session.get('user_id')
    if not user_id:
        return {'recipes': []}
    
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                '''SELECT r.recipe_id, r.recipe_name, r.recipe_pic, u.username
                FROM recipes r
                JOIN users u ON r.user_id = u.user_id
                ORDER BY r.created_at DESC
                LIMIT 20'''
            )
            recipes = cursor.fetchall()

    finally:
        db.close()
    return {'recipes': recipes}

@app.route('/recipe/<int:recipe_id>')
def recipe_view(recipe_id):
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute('SELECT * FROM recipes WHERE recipe_id = %s', (recipe_id,))
            recipe = cursor.fetchone()
    finally:
        db.close()
    if recipe is None:
        return redirect(url_for('home'))
    return render_template('recipe_view.html', recipe=recipe)

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

@app.route('/recipes/new', methods=['GET', 'POST'])
def new_recipe():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'GET':
        return render_template('instructions.html')

    recipe_name        = request.form.get('recipe_name', '').strip()
    ingredients        = request.form.get('ingredients', '').strip()
    directions         = request.form.get('directions', '').strip()
    prep_time          = int(request.form.get('prep_time'))
    cook_time          = int(request.form.get('cook_time'))
    servings           = int(request.form.get('servings'))
    dietary_preference = request.form.get('dietary_preference', 'no-restriction')

    if not recipe_name or not ingredients or not directions:
        return {'success': False, 'error': 'Missing required fields.'}, 400

    # handle optional photo upload
    recipe_pic = None
    photo = request.files.get('recipe_pic')
    if photo and photo.filename:
        ext = os.path.splitext(photo.filename)[1].lower()
        filename = uuid.uuid4().hex + ext
        upload_folder = os.path.join(app.root_path, 'static', 'media', 'recipe_pics')
        os.makedirs(upload_folder, exist_ok=True)
        photo.save(os.path.join(upload_folder, filename))
        recipe_pic = 'media/recipe_pics/' + filename

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                '''INSERT INTO recipes
                   (user_id, recipe_name, ingredients, directions,
                    prep_time, cook_time, servings, dietary_preference, recipe_pic)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                (session['user_id'], recipe_name, ingredients, directions,
                 prep_time, cook_time, servings, dietary_preference, recipe_pic)
            )
        db.commit()
    except Exception as e:
        return {'success': False, 'error': str(e)}, 500
    finally:
        db.close()

    return {'success': True}

@app.route('/meals')
def meal_page():
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in first.')
        return redirect(url_for('login'))
    return render_template('add_meal_page.html')

@app.route('/meals/save', methods=['POST'])
def save_meal():
    user_id = session.get('user_id')

    if not user_id:
        return {'success': False, 'error': 'Please log in first.'}, 401

    journal_name = request.form.get('journal_name', '').strip()
    caption = request.form.get('caption', '').strip()
    rating_raw = request.form.get('rating', '').strip()

    if not journal_name:
        return {'success': False, 'error': 'Meal title is required.'}, 400

    rating = None
    if rating_raw:
        try:
            rating = float(rating_raw)
        except ValueError:
            return {'success': False, 'error': 'Invalid rating.'}, 400

    tags_raw = request.form.get('tags', '[]')

    try:
        tags = json.loads(tags_raw)
    except json.JSONDecodeError:
        tags = []

    journal_pic = None
    photo = request.files.get('journal_pic')
    if photo and photo.filename:
        ext = os.path.splitext(photo.filename)[1].lower()
        filename = uuid.uuid4().hex + ext
        upload_folder = os.path.join(app.root_path, 'static', 'media', 'journal_pics')
        os.makedirs(upload_folder, exist_ok=True)
        photo.save(os.path.join(upload_folder, filename))
        journal_pic = 'media/journal_pics/' + filename

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                '''
                INSERT INTO journal_posts (user_id, journal_name, caption, journal_pic, rating)
                VALUES (%s, %s, %s, %s, %s)
                ''',
                (user_id, journal_name, caption, journal_pic, rating)
            )

            journal_id = cursor.lastrowid

            for tag_name in tags:
                clean_tag = tag_name.strip()
                if not clean_tag:
                    continue

                cursor.execute(
                    '''
                    INSERT INTO tags (tag_name)
                    VALUES (%s)
                    ON DUPLICATE KEY UPDATE tag_id = LAST_INSERT_ID(tag_id)
                    ''',
                    (clean_tag,)
                )
                tag_id = cursor.lastrowid

                cursor.execute(
                    '''
                    INSERT IGNORE INTO journal_tags (journal_id, tag_id)
                    VALUES (%s, %s)
                    ''',
                    (journal_id, tag_id)
                )

        db.commit()
    except Exception as e:
        return {'success': False, 'error': str(e)}, 500
    finally:
        db.close()

    return {'success': True}

@app.route('/journal')
def journal_page():
    user_id = session.get('user_id')

    if not user_id:
        flash('Please log in first.')
        return redirect(url_for('login'))

    meals = get_journal_posts_by_user(user_id)
    return render_template('journal.html', meals=meals)

def get_journal_posts_by_user(user_id):
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                '''
                SELECT 
                    jp.journal_id,
                    jp.journal_name,
                    jp.caption,
                    jp.journal_pic,
                    jp.rating,
                    jp.created_at,
                    GROUP_CONCAT(t.tag_name ORDER BY t.tag_name SEPARATOR ', ') AS tags
                FROM journal_posts jp
                LEFT JOIN journal_tags jt ON jp.journal_id = jt.journal_id
                LEFT JOIN tags t ON jt.tag_id = t.tag_id
                WHERE jp.user_id = %s
                GROUP BY jp.journal_id, jp.journal_name, jp.caption, jp.journal_pic, jp.rating, jp.created_at
                ORDER BY jp.created_at DESC
                ''',
                (user_id,)
            )
            return cursor.fetchall()
    finally:
        db.close()

@app.route('/journal/delete/<int:journal_id>', methods=['POST'])
def delete_journal_post(journal_id):
    user_id = session.get('user_id')

    if not user_id:
        return {'success': False, 'error': 'Please log in first.'}, 401

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                '''
                DELETE FROM journal_posts
                WHERE journal_id = %s AND user_id = %s
                ''',
                (journal_id, user_id)
            )
        db.commit()
    except Exception as e:
        return {'success': False, 'error': str(e)}, 500
    finally:
        db.close()

    return {'success': True}

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