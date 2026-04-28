from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
import os
import uuid
from db import get_db
from routes.recipes import get_favorite_recipes_by_user
from routes.meals import get_recent_meals_by_user

profile_bp = Blueprint('profile', __name__)

def get_user_by_id(user_id):
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                'SELECT user_id, username, email, profile_pic, bio FROM users WHERE user_id = %s',
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
                'SELECT 1 FROM follows WHERE follower_id = %s AND following_id = %s',
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
                            SELECT 1 FROM follows viewer_follows
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
                            SELECT 1 FROM follows viewer_follows
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

@profile_bp.route('/profile')
def profile():
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in first.')
        return redirect(url_for('auth.login'))

    user = get_user_by_id(user_id)
    return render_template(
        'profile.html',
        user=user,
        follower_count=get_follower_count(user_id),
        following_count=get_following_count(user_id),
        followers=get_followers(user_id, user_id),
        following=get_following(user_id, user_id),
        favorite_recipes=get_favorite_recipes_by_user(user_id),
        recent_activity=get_recent_activity(user_id),
        current_user_id=user_id,
        following_status=False
    )

@profile_bp.route('/profile/<int:user_id>')
def view_profile(user_id):
    current_user_id = session.get('user_id')
    if not current_user_id:
        flash('Please log in first.')
        return redirect(url_for('auth.login'))

    user = get_user_by_id(user_id)
    if user is None:
        flash('User not found.')
        return redirect(url_for('home'))

    following_status = False
    if current_user_id != user_id:
        following_status = is_following(current_user_id, user_id)

    return render_template(
        'profile.html',
        user=user,
        follower_count=get_follower_count(user_id),
        following_count=get_following_count(user_id),
        followers=get_followers(user_id, current_user_id),
        following=get_following(user_id, current_user_id),
        favorite_recipes=get_favorite_recipes_by_user(user_id),
        recent_activity=get_recent_activity(user_id),
        current_user_id=current_user_id,
        following_status=following_status
    )

@profile_bp.route('/profile/upload_picture', methods=['POST'])
def upload_profile_picture():
    user_id = session.get('user_id')
    if not user_id:
        return {'success': False, 'error': 'Please log in first.'}, 401

    photo = request.files.get('profile_pic')
    if not photo or not photo.filename:
        return {'success': False, 'error': 'No file selected.'}, 400

    ext = os.path.splitext(photo.filename)[1].lower()
    if ext not in {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg'}:
        return {'success': False, 'error': 'Unsupported file type.'}, 400

    filename = uuid.uuid4().hex + ext
    upload_folder = os.path.join(current_app.root_path, 'static', 'media', 'profileimages')
    os.makedirs(upload_folder, exist_ok=True)
    photo.save(os.path.join(upload_folder, filename))
    profile_pic_path = 'media/profileimages/' + filename

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                'UPDATE users SET profile_pic = %s WHERE user_id = %s',
                (profile_pic_path, user_id)
            )
        db.commit()
    except Exception as e:
        return {'success': False, 'error': str(e)}, 500
    finally:
        db.close()

    return {'success': True, 'profile_pic': url_for('static', filename=profile_pic_path)}

@profile_bp.route('/profile/<int:user_id>/reviews')
def user_reviews(user_id):
    current_user_id = session.get('user_id')
    if not current_user_id:
        flash('Please log in first.')
        return redirect(url_for('auth.login'))

    user = get_user_by_id(user_id)
    if not user:
        flash('User not found.')
        return redirect(url_for('home'))

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute('''
                SELECT
                    rr.review_id, rr.body, rr.score, rr.created_at,
                    r.recipe_id, r.recipe_name, r.recipe_pic,
                    COUNT(rl.user_id) AS like_count,
                    MAX(CASE WHEN rl.user_id = %s THEN 1 ELSE 0 END) AS user_liked
                FROM recipe_reviews rr
                JOIN recipes r ON rr.recipe_id = r.recipe_id
                LEFT JOIN review_likes rl ON rl.review_id = rr.review_id
                WHERE rr.user_id = %s
                GROUP BY rr.review_id, rr.body, rr.score, rr.created_at,
                         r.recipe_id, r.recipe_name, r.recipe_pic
                ORDER BY rr.created_at DESC
            ''', (current_user_id, user_id))
            reviews = cursor.fetchall()
    finally:
        db.close()

    for r in reviews:
        r['score'] = float(r['score']) if r['score'] else None
        r['like_count'] = int(r['like_count'])
        r['user_liked'] = bool(r['user_liked'])
        r['created_at'] = r['created_at'].strftime('%b %d, %Y')

    return render_template(
        'user_reviews.html',
        user=user,
        reviews=reviews,
        current_user_id=current_user_id
    )

def get_recent_activity(user_id, limit=5):
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute('''
                SELECT * FROM (
                    SELECT recipe_id AS item_id, recipe_name AS item_name,
                           recipe_pic AS item_pic, created_at, 'recipe' AS item_type
                    FROM recipes WHERE user_id = %s
                    ORDER BY created_at DESC LIMIT 5
                ) recipes_sub
                UNION ALL
                SELECT * FROM (
                    SELECT journal_id, journal_name, journal_pic, created_at, 'meal'
                    FROM journal_posts WHERE user_id = %s
                    ORDER BY created_at DESC LIMIT 5
                ) meals_sub
                ORDER BY created_at DESC
                LIMIT %s
            ''', (user_id, user_id, limit))
            return cursor.fetchall()
    finally:
        db.close()

@profile_bp.route('/users')
def users():
    current_user_id = session.get('user_id')
    if not current_user_id:
        flash('Please log in first.')
        return redirect(url_for('auth.login'))
    return render_template('users.html', users=get_all_users(), current_user_id=current_user_id)

@profile_bp.route('/change_bio', methods=['POST'])
def change_bio():
    current_user_id = session.get('user_id')
    if not current_user_id:
        flash('Please log in first.')
        return redirect(url_for('auth.login'))

    new_bio = request.form.get('profile-bio')
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                'UPDATE users SET bio = %s WHERE user_id = %s',
                (new_bio, current_user_id)
            )
        db.commit()
    finally:
        db.close()

    return redirect(url_for('profile.view_profile', user_id=current_user_id))
