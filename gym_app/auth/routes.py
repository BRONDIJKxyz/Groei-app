from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from gym_app.models import User
from gym_app import db
import traceback

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page."""
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            password = request.form.get('password')
            remember = True if request.form.get('remember') else False
            
            # Debug information
            print(f"Login attempt for email: {email}")
            
            user = User.query.filter_by(email=email).first()
            
            if not user:
                flash('No account found with that email address')
                return render_template('auth/login.html')
            
            if user and check_password_hash(user.password_hash, password):
                # Successful login
                login_user(user, remember=remember)
                next_page = request.args.get('next')
                print(f"Login successful for user: {user.email}")
                return redirect(next_page or url_for('main.dashboard'))
            else:
                # Failed login - password doesn't match
                print(f"Password verification failed for user: {user.email}")
                flash('Invalid password')
        except Exception as e:
            print(f"Login error: {str(e)}")
            print(traceback.format_exc())
            flash('An error occurred during login. Please try again.')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page."""
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('auth.register'))
        
        # Create new user
        new_user = User(
            email=email,
            name=name,
            password_hash=generate_password_hash(password)
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Logout user."""
    logout_user()
    return redirect(url_for('main.index'))
