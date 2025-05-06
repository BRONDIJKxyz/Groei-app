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
    
    # Get all exercises first
    all_exercises = Exercise.query.all()
    
    # Apply muscle group filter only if specified
    if muscle_group:
        exercises = [ex for ex in all_exercises if ex.muscle_group.lower() == muscle_group.lower()]
    else:
        exercises = all_exercises
    
    # For debugging
    total_count = len(all_exercises)
    muscle_group_counts = {}
    for group in ['chest', 'back', 'shoulders', 'arms', 'legs', 'core', 'cardio']:
        muscle_group_counts[group] = len([ex for ex in all_exercises if ex.muscle_group.lower() == group.lower()])
    
    print(f"Total exercises in database: {total_count}")
    print(f"Exercises being sent to template: {len(exercises)}")
    print(f"Muscle group counts: {muscle_group_counts}")
    
    return render_template('workout/exercises.html', 
                          exercises=exercises, 
                          total_count=total_count,
                          muscle_group_counts=muscle_group_counts)

@workout_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_workout():
    """Start a new workout session."""
    try:
        workout = Workout(
            user_id=current_user.id, 
            date=datetime.now(),
            name=f"Workout on {datetime.now().strftime('%B %d, %Y')}"
        )
        db.session.add(workout)
        db.session.commit()
        
        # If an exercise_id was provided, add it to the new workout
        exercise_id = request.form.get('exercise_id')
        if exercise_id:
            exercise = Exercise.query.get(exercise_id)
            if exercise:
                workout_exercise = WorkoutExercise(
                    workout_id=workout.id,
                    exercise_id=exercise.id
                )
                db.session.add(workout_exercise)
                db.session.commit()
                flash(f'Added {exercise.name} to your workout!', 'success')
        
        return redirect(url_for('workout.session', workout_id=workout.id))
    except Exception as e:
        # Log the error
        print(f"Error creating new workout: {str(e)}")
        db.session.rollback()
        flash("An error occurred while creating your workout. Please try again.", "error")
        return redirect(url_for('main.dashboard'))

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
    try:
        exercise_id = request.form.get('exercise_id')
        if not exercise_id:
            flash('No exercise selected', 'error')
            return redirect(url_for('workout.session', workout_id=workout_id))
        
        # Make sure the workout belongs to the current user
        workout = Workout.query.get_or_404(workout_id)
        if workout.user_id != current_user.id:
            flash('Access denied', 'error')
            return redirect(url_for('main.dashboard'))
            
        # Check if exercise exists
        exercise = Exercise.query.get_or_404(exercise_id)
        
        # Check if exercise is already in the workout
        existing = WorkoutExercise.query.filter_by(
            workout_id=workout_id,
            exercise_id=exercise_id
        ).first()
        
        if existing:
            flash(f'{exercise.name} is already in this workout', 'info')
            return redirect(url_for('workout.session', workout_id=workout_id))
        
        # Add the exercise to the workout
        workout_exercise = WorkoutExercise(
            workout_id=workout_id,
            exercise_id=exercise_id
        )
        
        db.session.add(workout_exercise)
        db.session.commit()
        
        flash(f'Added {exercise.name} to your workout!', 'success')
        return redirect(url_for('workout.session', workout_id=workout_id))
    except Exception as e:
        print(f"Error adding exercise to workout: {str(e)}")
        db.session.rollback()
        flash("An error occurred while adding the exercise. Please try again.", "error")
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

@workout_bp.route('/add-exercise', methods=['POST'])
@login_required
def add_exercise_to_workout():
    """Handle exercise addition from the exercise list page."""
    try:
        # Extract form data
        exercise_id = request.form.get('exercise_id')
        workout_option = request.form.get('workout_option')
        
        if not exercise_id:
            flash('No exercise selected', 'error')
            return redirect(url_for('workout.exercise_list'))
        
        # Get the exercise
        exercise = Exercise.query.get_or_404(exercise_id)
        
        if workout_option == 'new':
            # Create a new workout
            workout = Workout(
                user_id=current_user.id,
                date=datetime.now(),
                name=f"Workout on {datetime.now().strftime('%B %d, %Y')}"
            )
            db.session.add(workout)
            db.session.flush()  # Get the ID without committing
            
            # Add the exercise to the new workout
            workout_exercise = WorkoutExercise(
                workout_id=workout.id,
                exercise_id=exercise_id
            )
            db.session.add(workout_exercise)
            db.session.commit()
            
            flash(f'Created a new workout with {exercise.name}', 'success')
            return redirect(url_for('workout.session', workout_id=workout.id))
        else:
            # Add to existing workout
            workout_id = int(workout_option)
            
            # Verify workout belongs to user
            workout = Workout.query.get_or_404(workout_id)
            if workout.user_id != current_user.id:
                flash('Access denied', 'error')
                return redirect(url_for('workout.exercise_list'))
                
            # Check if exercise is already in workout
            existing = WorkoutExercise.query.filter_by(
                workout_id=workout_id, 
                exercise_id=exercise_id
            ).first()
            
            if existing:
                flash(f'{exercise.name} is already in this workout', 'info')
            else:
                # Add the exercise to the workout
                workout_exercise = WorkoutExercise(
                    workout_id=workout_id,
                    exercise_id=exercise_id
                )
                db.session.add(workout_exercise)
                db.session.commit()
                flash(f'Added {exercise.name} to your workout', 'success')
                
            return redirect(url_for('workout.session', workout_id=workout_id))
            
    except Exception as e:
        db.session.rollback()
        print(f"Error adding exercise: {str(e)}")
        flash('An error occurred while adding the exercise', 'error')
        return redirect(url_for('workout.exercise_list'))

# API Routes for AJAX functionality
@workout_bp.route('/api/exercises')
@login_required
def api_exercises():
    """API endpoint to get all exercises."""
    exercises = Exercise.query.all()
    
    result = []
    for exercise in exercises:
        result.append({
            'id': exercise.id,
            'name': exercise.name,
            'muscle_group': exercise.muscle_group,
            'description': exercise.description,
            'image_url': exercise.image_url
        })
    
    return jsonify({'exercises': result})

@workout_bp.route('/api/exercises/<int:exercise_id>')
@login_required
def api_exercise_detail(exercise_id):
    """API endpoint to get a specific exercise's details."""
    exercise = Exercise.query.get_or_404(exercise_id)
    
    result = {
        'id': exercise.id,
        'name': exercise.name,
        'muscle_group': exercise.muscle_group,
        'secondary_muscle_groups': exercise.secondary_muscle_groups,
        'equipment': exercise.equipment,
        'difficulty': exercise.difficulty,
        'description': exercise.description,
        'instructions': exercise.instructions,
        'tips': exercise.tips,
        'image_url': exercise.image_url,
        'video_url': exercise.video_url,
        'is_compound': exercise.is_compound,
        'calories_per_hour': exercise.calories_per_hour
    }
    
    return jsonify(result)

@workout_bp.route('/api/active-workouts')
@login_required
def api_active_workouts():
    """API endpoint to get user's active (incomplete) workouts."""
    workouts = Workout.query.filter_by(
        user_id=current_user.id,
        completed=False
    ).order_by(Workout.date.desc()).all()
    
    result = []
    for workout in workouts:
        result.append({
            'id': workout.id,
            'date': workout.date.isoformat(),
            'name': workout.name,
        })
    
    return jsonify({'workouts': result})

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
