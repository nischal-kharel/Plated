from flask import Flask, render_template, redirect, url_for, session, flash
from config import SECRET_KEY
from routes.auth import auth_bp
from routes.social import social_bp
from routes.lists import lists_bp
from routes.meals import meals_bp
from routes.recipes import recipes_bp
from routes.profile import profile_bp, get_user_by_id

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.register_blueprint(auth_bp)
app.register_blueprint(social_bp)
app.register_blueprint(lists_bp)
app.register_blueprint(meals_bp)
app.register_blueprint(recipes_bp)
app.register_blueprint(profile_bp)

@app.context_processor
def inject_nav_user():
    user_id = session.get('user_id')
    if not user_id:
        return {'nav_user': None}
    return {'nav_user': get_user_by_id(user_id)}

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/home')
def home():
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in first.')
        return redirect(url_for('auth.login'))
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)
