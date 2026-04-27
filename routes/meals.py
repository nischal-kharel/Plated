from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
import os
import uuid
import json
from db import get_db

meals_bp = Blueprint('meals', __name__)

@meals_bp.route('/meals')
def meal_page():
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in first.')
        return redirect(url_for('auth.login'))
    return render_template('add_meal_page.html')

@meals_bp.route('/meals/save', methods=['POST'])
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

    try:
        tags = json.loads(request.form.get('tags', '[]'))
    except json.JSONDecodeError:
        tags = []

    journal_pic = None
    photo = request.files.get('journal_pic')
    if photo and photo.filename:
        ext = os.path.splitext(photo.filename)[1].lower()
        filename = uuid.uuid4().hex + ext
        upload_folder = os.path.join(current_app.root_path, 'static', 'media', 'journal_pics')
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
                    'INSERT IGNORE INTO journal_tags (journal_id, tag_id) VALUES (%s, %s)',
                    (journal_id, tag_id)
                )
        db.commit()
    except Exception as e:
        return {'success': False, 'error': str(e)}, 500
    finally:
        db.close()

    return {'success': True}

@meals_bp.route('/journal')
def journal_page():
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in first.')
        return redirect(url_for('auth.login'))
    meals = get_journal_posts_by_user(user_id)
    return render_template('journal.html', meals=meals)

@meals_bp.route('/journal/delete/<int:journal_id>', methods=['POST'])
def delete_journal_post(journal_id):
    user_id = session.get('user_id')
    if not user_id:
        return {'success': False, 'error': 'Please log in first.'}, 401

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                'DELETE FROM journal_posts WHERE journal_id = %s AND user_id = %s',
                (journal_id, user_id)
            )
        db.commit()
    except Exception as e:
        return {'success': False, 'error': str(e)}, 500
    finally:
        db.close()

    return {'success': True}

def get_recent_meals_by_user(user_id, limit=4):
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                '''
                SELECT journal_id, journal_name, journal_pic, created_at
                FROM journal_posts
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT %s
                ''',
                (user_id, limit)
            )
            return cursor.fetchall()
    finally:
        db.close()

def get_journal_posts_by_user(user_id):
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                '''
                SELECT
                    jp.journal_id, jp.journal_name, jp.caption,
                    jp.journal_pic, jp.rating, jp.created_at,
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
