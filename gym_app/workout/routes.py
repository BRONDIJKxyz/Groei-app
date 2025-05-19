from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, session as flask_session
from flask_login import current_user, login_required
from datetime import datetime
from gym_app.models import Exercise, Workout, WorkoutExercise
from gym_app import db
from sqlalchemy import or_, and_, func

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

    # Pop potential PR value stored in session by add_set
    pr_exercise = flask_session.pop('pr_exercise', None)
    
    return render_template('workout/session.html', 
                          workout=workout, 
                          exercises=exercises,
                          all_exercises=all_exercises,
                          pr_exercise=pr_exercise)

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
    """Mark workout as completed (similar to a git commit). Prevent finishing if there are open exercises."""
    workout = Workout.query.get_or_404(workout_id)
    
    if workout.user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('main.dashboard'))

    # Check for any exercises that are not completed yet
    open_exercises = WorkoutExercise.query.filter_by(workout_id=workout_id).filter(or_(WorkoutExercise.completed == None, WorkoutExercise.completed == False)).all()
    if open_exercises:
        flash('You still have uncompleted exercises in this workout. Mark them as completed before finishing.', 'warning')
        return redirect(url_for('workout.session', workout_id=workout_id))

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

    # ------------------------------------------------------
    # Personal record detection (exclude first ever attempt)
    # ------------------------------------------------------
    new_total = workout_exercise.total_weight
    # Previous best for this exercise (completed workouts only)
    prev_exercises = (
        WorkoutExercise.query.join(Workout)
        .filter(
            Workout.user_id == current_user.id,
            WorkoutExercise.exercise_id == exercise_id,
            Workout.id != workout_id,
            WorkoutExercise.completed == True
        ).all()
    )
    prev_best = max([we.total_weight for we in prev_exercises], default=0)
    if prev_exercises and new_total > prev_best:
        # Store exercise name in session so next load shows confetti
        flask_session['pr_exercise'] = workout_exercise.exercise.name

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

@workout_bp.route('/<int:workout_id>/exercise/<int:exercise_id>/complete', methods=['POST'])
@login_required
def complete_exercise(workout_id, exercise_id):
    """Mark an individual exercise as completed within a workout."""
    try:
        workout = Workout.query.get_or_404(workout_id)
        
        if workout.user_id != current_user.id:
            flash('Access denied', 'danger')
            return redirect(url_for('main.dashboard'))
        
        workout_exercise = WorkoutExercise.query.filter_by(
            workout_id=workout_id, 
            exercise_id=exercise_id
        ).first_or_404()
        
        # Mark the exercise as completed
        workout_exercise.completed = True
        workout_exercise.completed_at = datetime.now()
        
        db.session.commit()
        
        flash(f'Exercise completed successfully!', 'success')
        return redirect(url_for('workout.session', workout_id=workout_id))
    except Exception as e:
        db.session.rollback()
        flash(f"Error completing exercise: {str(e)}", "error")
        return redirect(url_for('workout.session', workout_id=workout_id))

# -------------------------------------------------------------------
# Set deletion route
# -------------------------------------------------------------------
@workout_bp.route('/<int:workout_id>/exercise/<int:exercise_id>/set/<int:set_index>/delete', methods=['POST'])
@login_required
def delete_set(workout_id, exercise_id, set_index):
    """Remove a set by its 1-based index from an exercise within a workout."""
    try:
        workout = Workout.query.get_or_404(workout_id)
        if workout.user_id != current_user.id:
            flash('Access denied', 'error')
            return redirect(url_for('main.dashboard'))

        workout_exercise = WorkoutExercise.query.filter_by(workout_id=workout_id, exercise_id=exercise_id).first_or_404()
        sets = workout_exercise.sets_data or []
        idx = set_index - 1  # Convert to 0-based
        if 0 <= idx < len(sets):
            removed_set = sets.pop(idx)
            workout_exercise.sets_data = sets
            db.session.commit()
            flash(f"Removed set {set_index}: {removed_set['reps']} reps @ {removed_set['weight']}kg", 'success')
        else:
            flash('Invalid set index', 'error')
        return redirect(url_for('workout.session', workout_id=workout_id))
    except Exception as e:
        db.session.rollback()
        flash(f"Error removing set: {str(e)}", 'error')
        return redirect(url_for('workout.session', workout_id=workout_id))

@workout_bp.route('/api/exercises')
@login_required
def api_exercises():
    """API endpoint to get all exercises."""
    try:
        # Sort by muscle group, then by name
        exercises = Exercise.query.all()
        
        # Serialize
        result = []
        for exercise in exercises:
            result.append({
                'id': exercise.id,
                'name': exercise.name,
                'muscle_group': exercise.muscle_group,
                'equipment': exercise.equipment,
                'is_compound': exercise.is_compound,
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)})

@workout_bp.route('/api/exercises/with-progress')
@login_required
def api_exercises_with_progress():
    """API endpoint to get only exercises with progress data (completed sets)."""
    try:
        # Get exercise IDs that have completed workout data
        exercise_ids_with_progress = db.session.query(WorkoutExercise.exercise_id)\
            .join(Workout)\
            .filter(
                Workout.user_id == current_user.id,
                WorkoutExercise.completed == True,
                WorkoutExercise._sets_data != '[]'  # Only exercises with sets data
            )\
            .distinct()\
            .all()
        
        # Convert to flat list
        exercise_ids = [id[0] for id in exercise_ids_with_progress]
        
        # Get the full exercise details for these IDs
        exercises = Exercise.query.filter(Exercise.id.in_(exercise_ids)).all()
        
        # Serialize
        result = []
        for exercise in exercises:
            result.append({
                'id': exercise.id,
                'name': exercise.name,
                'muscle_group': exercise.muscle_group,
                'equipment': exercise.equipment,
                'is_compound': exercise.is_compound,
            })
        
        return jsonify(result)
    except Exception as e:
        print(f"Error fetching exercises with progress: {str(e)}")
        return jsonify({'error': str(e)})

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

@workout_bp.route('/api/exercise/<int:exercise_id>/history')
@login_required
def api_exercise_history(exercise_id):
    """Return recent history (last 10 completed workouts) for an exercise."""
    history_records = (
        WorkoutExercise.query.join(Workout)
        .filter(
            Workout.user_id == current_user.id,
            WorkoutExercise.exercise_id == exercise_id,
            WorkoutExercise.completed == True
        )
        .order_by(Workout.date.desc())
        .limit(10)
        .all()
    )
    history = [
        {
            'date': we.workout.date.strftime('%Y-%m-%d'),
            'total_weight': we.total_weight,
            'sets': we.sets_data,
        }
        for we in history_records
    ]
    return jsonify(history)

@workout_bp.route('/api/exercise/<int:exercise_id>/progress')
@login_required
def api_exercise_progress(exercise_id):
    """Return detailed progress history for a specific exercise with max weights over time."""
    try:
        # Fetch exercise
        exercise = Exercise.query.get_or_404(exercise_id)
        
        # Get all workout sessions for this exercise (only completed ones)
        # Don't limit to 10 so we can see full progress history
        workout_exercises = (
            WorkoutExercise.query
            .join(Workout)
            .filter(
                WorkoutExercise.exercise_id == exercise_id,
                Workout.user_id == current_user.id,
                WorkoutExercise.completed == True
            )
            .order_by(Workout.date.asc())  # Ascending for timeline chart
            .all()
        )
        
        # Format results for API
        results = []
        for we in workout_exercises:
            # Skip entries with no sets
            if not we.sets_data:
                continue
                
            # Get the workout date
            workout_date = we.workout.date.strftime('%Y-%m-%d')
            
            # Calculate max weight for this exercise session
            max_weight = max([s.get('weight', 0) for s in we.sets_data])
            
            results.append({
                'workout_id': we.workout_id,
                'date': workout_date,
                'formatted_date': we.workout.date.strftime('%b %d, %Y'),
                'total_weight': we.total_weight,
                'max_weight': max_weight
            })
        
        return jsonify({
            'success': True,
            'exercise': {
                'id': exercise.id,
                'name': exercise.name,
                'muscle_group': exercise.muscle_group
            },
            'progress': results
        })
    except Exception as e:
        print(f"Error fetching exercise progress: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })
