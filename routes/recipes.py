from flask import Blueprint, render_template, request, redirect, url_for, session, current_app
import os
import uuid
from db import get_db

recipes_bp = Blueprint('recipes', __name__)

@recipes_bp.route('/get_recipes')
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

@recipes_bp.route('/get_feed_recipes')
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

@recipes_bp.route('/recipes')
def recipe_page():
    return render_template('recipes_page.html')

@recipes_bp.route('/recipes/new', methods=['GET', 'POST'])
def new_recipe():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    if request.method == 'GET':
        return render_template('instructions.html')

    recipe_name        = request.form.get('recipe_name', '').strip()
    description        = request.form.get('description', '').strip()
    ingredients        = request.form.get('ingredients', '').strip()
    directions         = request.form.get('directions', '').strip()
    meal_types         = request.form.get('meal_types', '').strip()
    dietary_preference = request.form.get('dietary_preference', 'no-restriction').strip()
    prep_time          = int(request.form.get('prep_time'))
    cook_time          = int(request.form.get('cook_time'))
    servings           = int(request.form.get('servings'))

    if not recipe_name or not ingredients or not directions:
        return {'success': False, 'error': 'Missing required fields.'}, 400

    recipe_pic = None
    photo = request.files.get('recipe_pic')
    if photo and photo.filename:
        ext = os.path.splitext(photo.filename)[1].lower()
        filename = uuid.uuid4().hex + ext
        upload_folder = os.path.join(current_app.root_path, 'static', 'media', 'recipe_pics')
        os.makedirs(upload_folder, exist_ok=True)
        photo.save(os.path.join(upload_folder, filename))
        recipe_pic = 'media/recipe_pics/' + filename

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                '''INSERT INTO recipes
                   (user_id, recipe_name, description, ingredients, directions,
                    prep_time, cook_time, servings, dietary_preference, meal_type, recipe_pic)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                (session['user_id'], recipe_name, description, ingredients, directions,
                 prep_time, cook_time, servings, dietary_preference, meal_types, recipe_pic)
            )
        db.commit()
    except Exception as e:
        return {'success': False, 'error': str(e)}, 500
    finally:
        db.close()

    return {'success': True}

@recipes_bp.route('/recipe/<int:recipe_id>')
def recipe_view(recipe_id):
    user_id = session.get('user_id')
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                '''SELECT r.*, u.username, u.profile_pic
                   FROM recipes r
                   JOIN users u ON r.user_id = u.user_id
                   WHERE r.recipe_id = %s''',
                (recipe_id,)
            )
            recipe = cursor.fetchone()
            cursor.execute(
                'SELECT AVG(score) AS avg, COUNT(*) AS count FROM recipe_ratings WHERE recipe_id = %s',
                (recipe_id,)
            )
            rating_data = cursor.fetchone()
            user_rating = None
            user_lists = []
            if user_id:
                cursor.execute(
                    'SELECT score FROM recipe_ratings WHERE user_id = %s AND recipe_id = %s',
                    (user_id, recipe_id)
                )
                ur = cursor.fetchone()
                user_rating = ur['score'] if ur else None
                cursor.execute(
                    'SELECT list_id, list_name FROM mylists WHERE user_id = %s',
                    (user_id,)
                )
                user_lists = cursor.fetchall()
    finally:
        db.close()

    if recipe is None:
        return redirect(url_for('home'))

    avg_rating = round(float(rating_data['avg']), 1) if rating_data['avg'] else 0
    rating_count = rating_data['count']

    return render_template(
        'recipedisplay.html',
        recipe=recipe,
        avg_rating=avg_rating,
        rating_count=rating_count,
        user_rating=user_rating,
        user_lists=user_lists,
        current_user_id=user_id
    )

@recipes_bp.route('/rate/<int:recipe_id>', methods=['POST'])
def rate_recipe(recipe_id):
    user_id = session.get('user_id')
    if not user_id:
        return {'success': False}, 401

    data = request.get_json()
    score = data.get('score')
    if not score or score < 0.5 or score > 5:
        return {'success': False, 'error': 'Invalid score'}, 400

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                '''INSERT INTO recipe_ratings (user_id, recipe_id, score)
                   VALUES (%s, %s, %s)
                   ON DUPLICATE KEY UPDATE score = %s''',
                (user_id, recipe_id, score, score)
            )
            db.commit()
            cursor.execute(
                'SELECT AVG(score) AS avg FROM recipe_ratings WHERE recipe_id = %s',
                (recipe_id,)
            )
            result = cursor.fetchone()
            new_avg = round(float(result['avg']), 1) if result['avg'] else 0
    finally:
        db.close()

    return {'success': True, 'new_avg': new_avg}

@recipes_bp.route('/like/<int:recipe_id>', methods=['POST'])
def like_recipe(recipe_id):
    user_id = session.get('user_id')
    if not user_id:
        return {'success': False}, 401

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                'SELECT 1 FROM recipe_likes WHERE user_id = %s AND recipe_id = %s',
                (user_id, recipe_id)
            )
            if cursor.fetchone():
                cursor.execute(
                    'DELETE FROM recipe_likes WHERE user_id = %s AND recipe_id = %s',
                    (user_id, recipe_id)
                )
                liked = False
            else:
                cursor.execute(
                    'INSERT INTO recipe_likes (user_id, recipe_id) VALUES (%s, %s)',
                    (user_id, recipe_id)
                )
                liked = True
        db.commit()
    finally:
        db.close()

    return {'success': True, 'liked': liked}

@recipes_bp.route('/recipe/<int:recipe_id>/reviews')
def get_reviews(recipe_id):
    user_id = session.get('user_id')
    sort = request.args.get('sort', 'recent')

    db = get_db()
    try:
        with db.cursor() as cursor:
            if sort == 'popular':
                order = 'COUNT(rl.user_id) DESC'
            else:
                order = 'rr.created_at DESC'

            if sort == 'friends' and user_id:
                cursor.execute(f'''
                    SELECT rr.review_id, rr.body, rr.score, rr.created_at,
                           u.user_id, u.username, u.profile_pic,
                           COUNT(rl.user_id) AS like_count,
                           MAX(CASE WHEN rl.user_id = %s THEN 1 ELSE 0 END) AS user_liked
                    FROM recipe_reviews rr
                    JOIN users u ON rr.user_id = u.user_id
                    JOIN follows f ON f.following_id = rr.user_id AND f.follower_id = %s
                    LEFT JOIN review_likes rl ON rl.review_id = rr.review_id
                    WHERE rr.recipe_id = %s
                    GROUP BY rr.review_id, rr.body, rr.score, rr.created_at,
                             u.user_id, u.username, u.profile_pic
                    ORDER BY {order}
                    LIMIT 50
                ''', (user_id, user_id, recipe_id))
            else:
                cursor.execute(f'''
                    SELECT rr.review_id, rr.body, rr.score, rr.created_at,
                           u.user_id, u.username, u.profile_pic,
                           COUNT(rl.user_id) AS like_count,
                           MAX(CASE WHEN rl.user_id = %s THEN 1 ELSE 0 END) AS user_liked
                    FROM recipe_reviews rr
                    JOIN users u ON rr.user_id = u.user_id
                    LEFT JOIN review_likes rl ON rl.review_id = rr.review_id
                    WHERE rr.recipe_id = %s
                    GROUP BY rr.review_id, rr.body, rr.score, rr.created_at,
                             u.user_id, u.username, u.profile_pic
                    ORDER BY {order}
                    LIMIT 50
                ''', (user_id or 0, recipe_id))

            reviews = cursor.fetchall()

        user_review = None
        if user_id:
            with db.cursor() as cursor:
                cursor.execute(
                    'SELECT * FROM recipe_reviews WHERE user_id = %s AND recipe_id = %s',
                    (user_id, recipe_id)
                )
                user_review = cursor.fetchone()
    finally:
        db.close()

    for r in reviews:
        r['created_at'] = r['created_at'].strftime('%b %d, %Y')
        r['score'] = float(r['score']) if r['score'] else None
        r['like_count'] = int(r['like_count'])
        r['user_liked'] = bool(r['user_liked'])

    if user_review:
        user_review['created_at'] = user_review['created_at'].strftime('%b %d, %Y')
        user_review['score'] = float(user_review['score']) if user_review['score'] else None

    return {'reviews': reviews, 'user_review': user_review}

@recipes_bp.route('/recipe/<int:recipe_id>/review', methods=['POST'])
def submit_review(recipe_id):
    user_id = session.get('user_id')
    if not user_id:
        return {'success': False, 'error': 'Login required'}, 401

    data = request.get_json()
    body = data.get('body', '').strip()
    score = data.get('score')

    if not body:
        return {'success': False, 'error': 'Review text required'}, 400

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute('''
                INSERT INTO recipe_reviews (user_id, recipe_id, body, score)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE body = %s, score = %s, updated_at = NOW()
            ''', (user_id, recipe_id, body, score, body, score))
        db.commit()
    except Exception as e:
        return {'success': False, 'error': str(e)}, 500
    finally:
        db.close()

    return {'success': True}

@recipes_bp.route('/review/<int:review_id>/like', methods=['POST'])
def like_review(review_id):
    user_id = session.get('user_id')
    if not user_id:
        return {'success': False}, 401

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                'SELECT 1 FROM review_likes WHERE user_id = %s AND review_id = %s',
                (user_id, review_id)
            )
            if cursor.fetchone():
                cursor.execute(
                    'DELETE FROM review_likes WHERE user_id = %s AND review_id = %s',
                    (user_id, review_id)
                )
                liked = False
            else:
                cursor.execute(
                    'INSERT INTO review_likes (user_id, review_id) VALUES (%s, %s)',
                    (user_id, review_id)
                )
                liked = True
        db.commit()
    finally:
        db.close()

    return {'success': True, 'liked': liked}

@recipes_bp.route('/review/<int:review_id>/delete', methods=['POST'])
def delete_review(review_id):
    user_id = session.get('user_id')
    if not user_id:
        return {'success': False, 'error': 'Login required'}, 401

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                'DELETE FROM recipe_reviews WHERE review_id = %s AND user_id = %s',
                (review_id, user_id)
            )
        db.commit()
    except Exception as e:
        return {'success': False, 'error': str(e)}, 500
    finally:
        db.close()

    return {'success': True}

@recipes_bp.route('/search')
def search_page():
    return render_template('search.html')

@recipes_bp.route('/search/results')
def search_results():
    q          = request.args.get('q', '').strip()
    dietary    = request.args.getlist('dietary')
    cook_times = request.args.getlist('cook_time', type=int)
    meal_types = request.args.getlist('meal_type')
    min_rating = request.args.get('rating', type=float)

    conditions    = []
    where_params  = []
    having_params = []
    order_params  = []

    if q:
        conditions.append('MATCH(r.recipe_name, r.description, r.ingredients) AGAINST(%s IN NATURAL LANGUAGE MODE)')
        where_params.append(q)

    if dietary:
        diet_clauses = ['FIND_IN_SET(%s, r.dietary_preference)' for _ in dietary]
        conditions.append('(' + ' OR '.join(diet_clauses) + ')')
        where_params.extend(dietary)

    if cook_times:
        conditions.append('r.cook_time <= %s')
        where_params.append(max(cook_times))

    if meal_types:
        meal_clauses = ['FIND_IN_SET(%s, r.meal_type)' for _ in meal_types]
        conditions.append('(' + ' OR '.join(meal_clauses) + ')')
        where_params.extend(meal_types)

    where_clause = ('WHERE ' + ' AND '.join(conditions)) if conditions else ''

    having_clause = ''
    if min_rating is not None:
        having_clause = 'HAVING avg_rating >= %s'
        having_params.append(min_rating)

    if q:
        order_clause = 'ORDER BY MATCH(r.recipe_name, r.description, r.ingredients) AGAINST(%s IN NATURAL LANGUAGE MODE) DESC, MAX(r.created_at) DESC'
        order_params.append(q)
    else:
        order_clause = 'ORDER BY MAX(r.created_at) DESC'

    query = '''
        SELECT r.recipe_id, r.recipe_name, r.recipe_pic,
               COALESCE(AVG(rr.score), 0) AS avg_rating
        FROM recipes r
        LEFT JOIN recipe_ratings rr ON r.recipe_id = rr.recipe_id
        ''' + where_clause + '''
        GROUP BY r.recipe_id, r.recipe_name, r.recipe_pic
        ''' + having_clause + '''
        ''' + order_clause + '''
        LIMIT 40
    '''

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(query, where_params + having_params + order_params)
            recipes = cursor.fetchall()
    finally:
        db.close()

    for r in recipes:
        r['avg_rating'] = float(r['avg_rating'])

    return {'recipes': recipes}

def get_favorite_recipes_by_user(user_id, limit=4):
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                '''
                SELECT r.recipe_id, r.recipe_name, r.recipe_pic
                FROM favorite_recipes fr
                JOIN recipes r ON fr.recipe_id = r.recipe_id
                WHERE fr.user_id = %s
                ORDER BY fr.created_at DESC
                LIMIT %s
                ''',
                (user_id, limit)
            )
            return cursor.fetchall()
    finally:
        db.close()
