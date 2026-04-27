from flask import Blueprint, request, redirect, url_for, session, flash
from db import get_db

social_bp = Blueprint('social', __name__)

@social_bp.route('/follow/<int:user_id>', methods=['POST'])
def follow_user(user_id):
    current_user_id = session.get('user_id')

    if not current_user_id:
        flash('Please log in first.')
        return redirect(url_for('auth.login'))

    return_profile_id = request.form.get('return_profile_id', type=int)

    if current_user_id == user_id:
        flash('You cannot follow yourself.')
        if return_profile_id:
            if return_profile_id == current_user_id:
                return redirect(url_for('profile.profile'))
            return redirect(url_for('profile.view_profile', user_id=return_profile_id))
        return redirect(url_for('profile.view_profile', user_id=user_id))

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
            return redirect(url_for('profile.profile'))
        return redirect(url_for('profile.view_profile', user_id=return_profile_id))

    return redirect(url_for('profile.view_profile', user_id=user_id))

@social_bp.route('/unfollow/<int:user_id>', methods=['POST'])
def unfollow_user(user_id):
    current_user_id = session.get('user_id')

    if not current_user_id:
        flash('Please log in first.')
        return redirect(url_for('auth.login'))

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
            return redirect(url_for('profile.profile'))
        return redirect(url_for('profile.view_profile', user_id=return_profile_id))

    return redirect(url_for('profile.view_profile', user_id=user_id))
