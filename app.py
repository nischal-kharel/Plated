from flask import Flask, render_template
import pymysql
from config import DB_CONFIG, SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY

def get_db():
    return pymysql.connect(
        **DB_CONFIG,
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/recipes')
def recipe_page():
    return render_template('recipes_page.html')

@app.route('/meals')
def meal_page():
    return render_template('meal_page.html')

if __name__ == '__main__':
    app.run(debug=True)