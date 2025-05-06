from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import current_user, login_required
from gym_app.models import Workout, WorkoutExercise, Exercise
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
    """User dashboard with stats and recent workouts."""
    try:
        # Get the current date
        now = datetime.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Get all user workouts
        workouts = Workout.query.filter_by(user_id=current_user.id).order_by(Workout.date.desc()).all()
        
        # Calculate workout streak and monthly workout count
        streak = 0
        monthly_workouts = 0
        last_workout_date = None
        
        # Enhanced workout data with total weight information
        workout_data = []
        
        for workout in workouts:
            # Format for workout heatmap
            workout_date = workout.date.strftime('%Y-%m-%d')
            
            # Calculate total weight lifted for this workout
            total_weight = 0
            workout_exercises = WorkoutExercise.query.filter_by(workout_id=workout.id).all()
            
            # Track muscle groups for this workout
            muscle_group_counts = {}
            
            for we in workout_exercises:
                # Get exercise data
                exercise = Exercise.query.get(we.exercise_id)
                if exercise and exercise.muscle_group:
                    if exercise.muscle_group in muscle_group_counts:
                        muscle_group_counts[exercise.muscle_group] += 1
                    else:
                        muscle_group_counts[exercise.muscle_group] = 1
                
                # Sum up weight × reps for all sets
                sets_data = we.sets_data
                for set_data in sets_data:
                    if 'weight' in set_data and 'reps' in set_data:
                        total_weight += float(set_data['weight']) * int(set_data['reps'])
            
            # Determine primary muscle group (most exercises)
            primary_muscle_group = max(muscle_group_counts.items(), key=lambda x: x[1])[0] if muscle_group_counts else "General"
            
            # Add to workout data
            workout_data.append({
                'date': workout_date,
                'total_weight': total_weight,
                'primary_muscle_group': primary_muscle_group,
                'workout': workout
            })
            
            # Calculate monthly workouts
            if workout.date >= start_of_month:
                monthly_workouts += 1
            
            # Calculate streak (consecutive days with workouts)
            workout_day = workout.date.date()
            if last_workout_date is None:
                streak = 1
                last_workout_date = workout_day
            elif (last_workout_date - workout_day).days == 1:
                streak += 1
                last_workout_date = workout_day
            elif (last_workout_date - workout_day).days > 1:
                break
        
        # Get favorite exercise (based on frequency)
        exercise_counts = {}
        for workout in workouts:
            for we in workout.exercises:
                exercise = Exercise.query.get(we.exercise_id)
                if exercise:
                    if exercise.name in exercise_counts:
                        exercise_counts[exercise.name] += 1
                    else:
                        exercise_counts[exercise.name] = 1
        
        favorite_exercise = max(exercise_counts.items(), key=lambda x: x[1])[0] if exercise_counts else "None"
        
        return render_template('dashboard.html', 
                               workouts=workouts,
                               workout_data=workout_data,
                               now=now,
                               streak=streak,
                               monthly_workouts=monthly_workouts,
                               favorite_exercise=favorite_exercise)
    except Exception as e:
        # Log the error
        print(f"Error in dashboard route: {str(e)}")
        flash(f"An error occurred: {str(e)}", "error")
        return render_template('dashboard.html', 
                              workouts=[],
                              workout_data=[],
                              now=datetime.now(),
                              streak=0,
                              monthly_workouts=0,
                              favorite_exercise="None")
