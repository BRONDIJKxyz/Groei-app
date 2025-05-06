from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required
from gym_app.models import Workout

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page with workout history visualized like GitHub commits."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """User's dashboard with workout history displayed as a commit-style heatmap."""
    workouts = Workout.query.filter_by(user_id=current_user.id).order_by(Workout.date.desc()).all()
    return render_template('dashboard.html', workouts=workouts)
