from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_required
from datetime import datetime
from gym_app.models import Exercise, Workout, WorkoutExercise
from gym_app import db

workout_bp = Blueprint('workout', __name__, url_prefix='/workout')

@workout_bp.route('/exercises')
@login_required
def exercise_list():
    """List all exercises, filterable by muscle group."""
    muscle_group = request.args.get('muscle_group', None)
    
    if muscle_group:
        exercises = Exercise.query.filter_by(muscle_group=muscle_group).all()
    else:
        exercises = Exercise.query.all()
    
    return render_template('workout/exercises.html', exercises=exercises)

@workout_bp.route('/new')
@login_required
def new_workout():
    """Start a new workout session."""
    workout = Workout(user_id=current_user.id, date=datetime.now())
    db.session.add(workout)
    db.session.commit()
    
    return redirect(url_for('workout.session', workout_id=workout.id))

@workout_bp.route('/<int:workout_id>')
@login_required
def session(workout_id):
    """Ongoing workout session page."""
    workout = Workout.query.get_or_404(workout_id)
    
    # Make sure user can only access their own workouts
    if workout.user_id != current_user.id:
        flash('Access denied')
        return redirect(url_for('main.dashboard'))
    
    exercises = WorkoutExercise.query.filter_by(workout_id=workout_id).all()
    all_exercises = Exercise.query.all()
    
    return render_template('workout/session.html', 
                          workout=workout, 
                          exercises=exercises,
                          all_exercises=all_exercises)

@workout_bp.route('/<int:workout_id>/add', methods=['POST'])
@login_required
def add_exercise(workout_id):
    """Add an exercise to current workout."""
    exercise_id = request.form.get('exercise_id')
    
    workout_exercise = WorkoutExercise(
        workout_id=workout_id,
        exercise_id=exercise_id
    )
    
    db.session.add(workout_exercise)
    db.session.commit()
    
    return redirect(url_for('workout.session', workout_id=workout_id))

@workout_bp.route('/<int:workout_id>/complete', methods=['POST'])
@login_required
def complete_workout(workout_id):
    """Mark workout as completed (similar to a git commit)."""
    workout = Workout.query.get_or_404(workout_id)
    
    if workout.user_id != current_user.id:
        flash('Access denied')
        return redirect(url_for('main.dashboard'))
    
    workout.completed = True
    db.session.commit()
    
    flash('Workout committed successfully!')
    return redirect(url_for('main.dashboard'))

@workout_bp.route('/<int:workout_id>/exercise/<int:exercise_id>/set', methods=['POST'])
@login_required
def add_set(workout_id, exercise_id):
    """Add a set to an exercise in the current workout."""
    workout_exercise = WorkoutExercise.query.filter_by(
        workout_id=workout_id, 
        exercise_id=exercise_id
    ).first_or_404()
    
    weight = float(request.form.get('weight', 0))
    reps = int(request.form.get('reps', 0))
    
    # Store the set data (simplified for now, could be a separate model)
    sets_data = workout_exercise.sets_data or []
    sets_data.append({'weight': weight, 'reps': reps})
    workout_exercise.sets_data = sets_data
    
    db.session.commit()
    
    return redirect(url_for('workout.session', workout_id=workout_id))

# API Routes for AJAX functionality
@workout_bp.route('/api/exercises')
@login_required
def api_exercises():
    """API endpoint for exercises."""
    muscle_group = request.args.get('muscle_group', None)
    
    if muscle_group:
        exercises = Exercise.query.filter_by(muscle_group=muscle_group).all()
    else:
        exercises = Exercise.query.all()
    
    return jsonify([{
        'id': e.id, 
        'name': e.name, 
        'muscle_group': e.muscle_group,
        'description': e.description
    } for e in exercises])

@workout_bp.route('/api/<int:workout_id>/totals')
@login_required
def api_workout_totals(workout_id):
    """Get the total weight lifted for each exercise in a workout."""
    exercises = WorkoutExercise.query.filter_by(workout_id=workout_id).all()
    
    totals = []
    for ex in exercises:
        total_weight = 0
        sets = ex.sets_data or []
        
        for s in sets:
            total_weight += s['weight'] * s['reps']
        
        totals.append({
            'exercise_id': ex.exercise_id,
            'exercise_name': ex.exercise.name,
            'total_weight': total_weight,
            'sets_count': len(sets)
        })
    
    return jsonify(totals)
