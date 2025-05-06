from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required
from gym_app.models import Workout
from datetime import datetime, timedelta

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
    # Get all workouts ordered by date
    workouts = Workout.query.filter_by(user_id=current_user.id).order_by(Workout.date.desc()).all()
    
    # Calculate workouts this month
    now = datetime.now()
    current_month_workouts = [w for w in workouts if w.date.month == now.month and w.date.year == now.year]
    
    # Calculate current streak
    streak = 0
    if workouts:
        # Start from yesterday to check for streak
        check_date = now.date() - timedelta(days=1)
        for i in range(30):  # Check up to 30 days back
            day_workouts = [w for w in workouts if w.date.date() == check_date and w.completed]
            if day_workouts:
                streak += 1
                check_date -= timedelta(days=1)
            else:
                break
    
    # Find favorite exercise
    exercise_counts = {}
    for workout in workouts:
        for exercise in workout.exercises:
            exercise_name = exercise.exercise.name
            if exercise_name in exercise_counts:
                exercise_counts[exercise_name] += 1
            else:
                exercise_counts[exercise_name] = 1
    
    favorite_exercise = "None yet"
    if exercise_counts:
        favorite_exercise = max(exercise_counts, key=exercise_counts.get)
    
    return render_template('dashboard.html', 
                          workouts=workouts,
                          current_month_workouts=current_month_workouts,
                          streak=streak,
                          favorite_exercise=favorite_exercise,
                          now=now)
