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
        workouts = Workout.query.filter_by(user_id=current_user.id).order_by(Workout.date.desc()).all()
        return render_template('dashboard.html', workouts=workouts)
    
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
        
        workout.completed = True
        db.session.commit()
        
        flash('Workout completed successfully!')
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
