from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from db import get_db

lists_bp = Blueprint('lists', __name__)

@lists_bp.route('/mylists')
def mylists():
    current_user_id = session.get('user_id')
    if not current_user_id:
        flash('Please log in first.')
        return redirect(url_for('auth.login'))

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                '''
                SELECT list_id, list_name
                FROM mylists
                WHERE user_id = %s
                ''',
                (current_user_id,)
            )
            user_lists = cursor.fetchall()

            for lst in user_lists:
                cursor.execute(
                    '''
                    SELECT r.recipe_id, r.recipe_name, r.recipe_pic
                    FROM recipes r
                    JOIN mylists_recipes mr ON r.recipe_id = mr.recipe_id
                    WHERE mr.list_id = %s
                    LIMIT 4
                    ''',
                    (lst['list_id'],)
                )
                lst['recipes'] = cursor.fetchall()

        db.commit()
    finally:
        db.close()

    return render_template('mylists.html', list_names=user_lists)

@lists_bp.route('/createlist', methods=['POST'])
def createlist():
    current_user_id = session.get('user_id')
    if not current_user_id:
        flash('Please log in first.')
        return redirect(url_for('auth.login'))

    listname = request.form.get('list-name')
    if not listname or not listname.strip():
        flash('List name is required.')
        return redirect(url_for('lists.mylists'))

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                'SELECT list_id FROM mylists WHERE user_id = %s AND list_name = %s',
                (current_user_id, listname)
            )
            if cursor.fetchone():
                flash('A list with this name already exists.')
                return redirect(url_for('lists.mylists'))

            cursor.execute(
                'INSERT INTO mylists (user_id, list_name) VALUES (%s, %s)',
                (current_user_id, listname)
            )
        db.commit()
    finally:
        db.close()

    return redirect(url_for('lists.mylists'))

@lists_bp.route('/delete_list', methods=['POST'])
def delete_list():
    current_user_id = session.get('user_id')
    if not current_user_id:
        flash('Please log in first.')
        return redirect(url_for('auth.login'))

    listid = request.form.get('list_id')
    if listid:
        db = get_db()
        try:
            with db.cursor() as cursor:
                cursor.execute(
                    'DELETE FROM mylists WHERE list_id = %s AND user_id = %s',
                    (listid, current_user_id)
                )
            db.commit()
        finally:
            db.close()

    return redirect(url_for('lists.mylists'))

@lists_bp.route('/add_to_list', methods=['POST'])
def add_to_list():
    current_user_id = session.get('user_id')
    if not current_user_id:
        flash('Please log in first.')
        return redirect(url_for('auth.login'))

    list_id = request.form.get('list_id')
    recipe_id = request.form.get('recipe_id')

    if not list_id or not recipe_id:
        flash('Invalid request.')
        return redirect(url_for('lists.mylists'))

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                'SELECT list_id FROM mylists WHERE list_id = %s AND user_id = %s',
                (list_id, current_user_id)
            )
            if not cursor.fetchone():
                flash('List not found.')
                return redirect(url_for('home'))

            cursor.execute(
                'SELECT 1 FROM mylists_recipes WHERE list_id = %s AND recipe_id = %s',
                (list_id, recipe_id)
            )
            if cursor.fetchone():
                flash('Recipe is already in this list.')
                return redirect(url_for('recipes.recipe_view', recipe_id=recipe_id))

            cursor.execute(
                'INSERT INTO mylists_recipes (list_id, recipe_id) VALUES (%s, %s)',
                (list_id, recipe_id)
            )
            flash('Recipe added to list.')
        db.commit()
    finally:
        db.close()

    return redirect(url_for('recipes.recipe_view', recipe_id=recipe_id))

@lists_bp.route('/get_list_recipes', methods=['GET'])
def get_list_recipes():
    current_user_id = session.get('user_id')
    if not current_user_id:
        return jsonify([]), 401

    list_id = request.args.get('list')
    if not list_id:
        return jsonify([])

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                '''
                SELECT r.recipe_id, r.recipe_name, r.recipe_pic
                FROM recipes r
                JOIN mylists_recipes mr ON r.recipe_id = mr.recipe_id
                WHERE mr.list_id = %s
                ''',
                (list_id,)
            )
            recipes = cursor.fetchall()
    finally:
        db.close()

    return jsonify(recipes)
