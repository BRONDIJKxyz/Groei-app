from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    # Initialize Flask app
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-dev-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///gym_app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    
    # Import models here to avoid circular imports
    from models import User, Exercise, Workout, WorkoutExercise
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Routes
    @app.route('/')
    def index():
        """Home page with workout history visualized like GitHub commits."""
        if current_user.is_authenticated:
            return render_template('dashboard.html')
        return render_template('index.html')
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Login page."""
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            
            user = User.query.filter_by(email=email).first()
            
            if user and check_password_hash(user.password_hash, password):
                login_user(user)
                return redirect(url_for('dashboard'))
            
            flash('Invalid email or password')
        
        return render_template('login.html')
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """Registration page."""
        if request.method == 'POST':
            email = request.form.get('email')
            name = request.form.get('name')
            password = request.form.get('password')
            
            # Check if user already exists
            if User.query.filter_by(email=email).first():
                flash('Email already registered')
                return redirect(url_for('register'))
            
            # Create new user
            new_user = User(
                email=email,
                name=name,
                password_hash=generate_password_hash(password)
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            flash('Registration successful! Please log in.')
            return redirect(url_for('login'))
        
        return render_template('register.html')
    
    @app.route('/logout')
    @login_required
    def logout():
        """Logout user."""
        logout_user()
        return redirect(url_for('index'))
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        """User's dashboard with workout history."""
        # Get all user workouts
        workouts = Workout.query.filter_by(user_id=current_user.id).order_by(Workout.date.desc()).all()
        
        # Calculate monthly workouts (current month)
        current_month = datetime.now().month
        current_year = datetime.now().year
        month_start = datetime(current_year, current_month, 1)
        
        if current_month == 12:
            month_end = datetime(current_year + 1, 1, 1)
        else:
            month_end = datetime(current_year, current_month + 1, 1)
            
        monthly_workouts = Workout.query.filter(
            Workout.user_id == current_user.id,
            Workout.date >= month_start,
            Workout.date < month_end
        ).count()
        
        # Calculate streak (simplified)
        streak = 0
        # Simple streak logic could be added here later
        
        # Find favorite exercise (most used)
        favorite_exercise = "None yet"
        # More complex favorite exercise logic could be added here later
        
        # Prepare detailed workout data for the calendar view
        workout_data = []
        
        print(f"Processing {len(workouts)} workouts for user {current_user.id}")
        
        for workout in workouts:
            try:
                # Format date as ISO string for JavaScript
                # Make sure we're using local timezone date to match the user's calendar view
                workout_date = workout.date.strftime('%Y-%m-%d')
                print(f"Processing workout with date: {workout.date} -> formatted as {workout_date}")
                
                # Get all exercises for this workout
                workout_exercises = WorkoutExercise.query.filter_by(workout_id=workout.id).all()
                print(f"Workout {workout.id} has {len(workout_exercises)} exercises")
                
                # Calculate total weight for this workout
                total_weight = 0
                exercise_details = []
                
                # Primary muscle group tracking
                muscle_groups = {}
                
                for we in workout_exercises:
                    # Get the exercise info
                    exercise = Exercise.query.get(we.exercise_id)
                    
                    if not exercise:
                        print(f"Exercise {we.exercise_id} not found")
                        continue
                        
                    # Count muscle groups for determining primary
                    if exercise.muscle_group:
                        muscle_groups[exercise.muscle_group] = muscle_groups.get(exercise.muscle_group, 0) + 1
                    
                    # Calculate weight for this exercise
                    exercise_weight = 0
                    sets = we.sets_data or []
                    
                    for s in sets:
                        if 'weight' in s and 'reps' in s:
                            exercise_weight += float(s.get('weight', 0)) * int(s.get('reps', 0))
                    
                    total_weight += exercise_weight
                    
                    # Add exercise details
                    exercise_details.append({
                        'exercise_id': we.exercise_id,
                        'exercise_name': exercise.name,
                        'sets': we.sets_data,
                        'total_weight': exercise_weight
                    })
                
                # Determine primary muscle group (most used in this workout)
                primary_muscle_group = "general"
                if muscle_groups:
                    try:
                        primary_muscle_group = max(muscle_groups.items(), key=lambda x: x[1])[0]
                    except (ValueError, KeyError) as e:
                        print(f"Error determining primary muscle group: {e}")
                
                # Create workout data entry
                workout_entry = {
                    'date': workout_date,
                    'workout': {
                        'id': workout.id,
                        'name': workout.name or f"Workout {workout.id}",
                        'date': workout_date,
                        'completed': bool(workout.completed)
                    },
                    'total_weight': float(total_weight),
                    'primary_muscle_group': primary_muscle_group,
                    'workout_exercises': exercise_details
                }
                
                workout_data.append(workout_entry)
                print(f"Added workout data for {workout_date}, total weight: {total_weight}")
                
            except Exception as e:
                print(f"Error processing workout {workout.id}: {str(e)}")
        
        # Update stats based on processed data
        if workout_data and len(workout_data) > 0:
            monthly_workouts = sum(1 for w in workout_data if w['date'][:7] == f"{current_year}-{current_month:02d}")
        
        # Create a JSON-safe version of the workout data
        import json
        try:
            workout_data_json = json.dumps(workout_data)
        except TypeError as e:
            print(f"JSON serialization error: {e}")
            # Fallback to a simplified version if full serialization fails
            simplified_data = []
            for wd in workout_data:
                try:
                    # Create a fully serializable copy with simpler structure
                    wd_copy = {
                        'date': wd['date'],
                        'total_weight': float(wd['total_weight']),
                        'primary_muscle_group': str(wd['primary_muscle_group']),
                        'workout': {
                            'id': wd['workout']['id'],
                            'name': str(wd['workout']['name']),
                            'date': wd['workout']['date'],
                            'completed': bool(wd['workout']['completed'])
                        },
                        'workout_exercises': []
                    }
                    
                    # Simplify exercise data
                    for ex in wd['workout_exercises']:
                        ex_copy = {
                            'exercise_id': ex['exercise_id'],
                            'exercise_name': str(ex['exercise_name']),
                            'total_weight': float(ex['total_weight']),
                            'sets': []
                        }
                        
                        # Copy sets data with explicit type conversion
                        if 'sets' in ex and ex['sets']:
                            for s in ex['sets']:
                                if isinstance(s, dict):
                                    # Make a simple set dict with only the needed fields
                                    set_copy = {
                                        'weight': float(s.get('weight', 0)),
                                        'reps': int(s.get('reps', 0))
                                    }
                                    ex_copy['sets'].append(set_copy)
                        
                        wd_copy['workout_exercises'].append(ex_copy)
                    
                    simplified_data.append(wd_copy)
                except Exception as e:
                    print(f"Error simplifying workout data: {e}")
            
            # Try to serialize the simplified data
            try:
                workout_data_json = json.dumps(simplified_data)
                # Replace workout_data with the simplified version that works
                workout_data = simplified_data
            except TypeError as e:
                print(f"Still can't serialize simplified data: {e}")
                workout_data_json = '[]'  # Last resort fallback to empty array
        
        return render_template('dashboard.html', 
                              workouts=workouts,
                              workout_data=workout_data,
                              workout_data_json=workout_data_json,  # Add the serialized JSON data
                              monthly_workouts=monthly_workouts,
                              streak=streak,
                              favorite_exercise=favorite_exercise)
    
    @app.route('/exercises')
    @login_required
    def exercise_list():
        """List all exercises, filterable by muscle group."""
        muscle_group = request.args.get('muscle_group', None)
        
        if muscle_group:
            exercises = Exercise.query.filter_by(muscle_group=muscle_group).all()
        else:
            exercises = Exercise.query.all()
        
        return render_template('exercises.html', exercises=exercises)
    
    @app.route('/workout/new')
    @login_required
    def new_workout():
        """Start a new workout session."""
        workout = Workout(user_id=current_user.id, date=datetime.now())
        db.session.add(workout)
        db.session.commit()
        
        return redirect(url_for('workout_session', workout_id=workout.id))
    
    @app.route('/workout/<int:workout_id>')
    @login_required
    def workout_session(workout_id):
        """Ongoing workout session page."""
        workout = Workout.query.get_or_404(workout_id)
        
        # Make sure user can only access their own workouts
        if workout.user_id != current_user.id:
            flash('Access denied')
            return redirect(url_for('dashboard'))
        
        exercises = WorkoutExercise.query.filter_by(workout_id=workout_id).all()
        all_exercises = Exercise.query.all()
        
        return render_template('workout_session.html', 
                              workout=workout, 
                              exercises=exercises,
                              all_exercises=all_exercises)
    
    @app.route('/workout/<int:workout_id>/add', methods=['POST'])
    @login_required
    def add_exercise_to_workout(workout_id):
        """Add an exercise to current workout."""
        exercise_id = request.form.get('exercise_id')
        
        workout_exercise = WorkoutExercise(
            workout_id=workout_id,
            exercise_id=exercise_id
        )
        
        db.session.add(workout_exercise)
        db.session.commit()
        
        return redirect(url_for('workout_session', workout_id=workout_id))
    
    @app.route('/workout/<int:workout_id>/complete', methods=['POST'])
    @login_required
    def complete_workout(workout_id):
        """Mark workout as completed."""
        workout = Workout.query.get_or_404(workout_id)
        
        if workout.user_id != current_user.id:
            flash('Access denied')
            return redirect(url_for('dashboard'))
        
        # Mark as completed and save    
        workout.completed = True
        
        # Make sure we have a name if none was provided
        if not workout.name:
            # Use the date as a default name if none is set
            workout.name = f"Workout on {workout.date.strftime('%B %d, %Y')}"
        
        db.session.commit()
        
        # Provide clear feedback
        flash('Workout committed successfully!')
        return redirect(url_for('dashboard'))
    
    @app.route('/workout/<int:workout_id>/exercise/<int:exercise_id>/set', methods=['POST'])
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
        
        return redirect(url_for('workout_session', workout_id=workout_id))
    
    # API Routes for AJAX functionality
    @app.route('/api/exercises')
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
    
    @app.route('/api/workout/<int:workout_id>/totals')
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
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
