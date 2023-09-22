import sqlite3
from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import re
from werkzeug.security import generate_password_hash

# Initialize the Flask app
app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')

# Configure SQLite database connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

DATABASE = 'database.db'

# Connect to the SQLite database
def create_connection():
    return sqlite3.connect(DATABASE)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

# Create the SQLite database tables
with app.app_context():
    db.create_all()

@app.route('/init_db')
def initialize_database():
    with app.app_context():
        db.create_all()
    return 'Database initialized!'

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get user registration data from the form
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Input validation
        if not re.match(r'^[A-Za-z0-9]+$', username):
            return 'Username should contain only letters and numbers.'
        if not re.match(r'^\S+@\S+\.\S+$', email):
            return 'Invalid email address.'
        if len(password) < 4:
            return 'Password should be at least 4 characters long.'

        # Check if the user with the same username or email already exists
        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()

        if existing_user:
            return 'Username already exists. Please choose a different one.'
        if existing_email:
            return 'Email address is already registered.'

        # Hash the user's password for security
        hashed_password = generate_password_hash(password, method='sha256')

        # Create a new User object and add it to the database
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return 'Registration successful!'

    else:
        return render_template('register.html')