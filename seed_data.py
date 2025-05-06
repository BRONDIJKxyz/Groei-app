from gym_app import create_app, db
from gym_app.models import User, Exercise, Workout, WorkoutExercise
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

def seed_exercises():
    """Add sample exercises to the database."""
    exercises = [
        # Chest
        {'name': 'Bench Press', 'muscle_group': 'chest', 'description': 'Lie on a flat bench and press weight upward.'},
        {'name': 'Incline Press', 'muscle_group': 'chest', 'description': 'Press weight upward while on an inclined bench.'},
        {'name': 'Chest Fly', 'muscle_group': 'chest', 'description': 'Open arms wide with weights and bring together in an arc.'},
        {'name': 'Push-ups', 'muscle_group': 'chest', 'description': 'Classic bodyweight exercise for chest and triceps.'},
        
        # Back
        {'name': 'Pull-ups', 'muscle_group': 'back', 'description': 'Pull yourself up to a bar using your back and arms.'},
        {'name': 'Deadlift', 'muscle_group': 'back', 'description': 'Lift weight from ground with a focus on lower back.'},
        {'name': 'Bent Over Row', 'muscle_group': 'back', 'description': 'Bend over and row weight to your abdomen.'},
        {'name': 'Lat Pulldown', 'muscle_group': 'back', 'description': 'Pull a bar down toward your upper chest.'},
        
        # Shoulders
        {'name': 'Overhead Press', 'muscle_group': 'shoulders', 'description': 'Press weight overhead from shoulder height.'},
        {'name': 'Lateral Raise', 'muscle_group': 'shoulders', 'description': 'Raise weights to sides to target lateral deltoids.'},
        {'name': 'Front Raise', 'muscle_group': 'shoulders', 'description': 'Raise weights in front to target anterior deltoids.'},
        {'name': 'Face Pull', 'muscle_group': 'shoulders', 'description': 'Pull rope attachment toward your face.'},
        
        # Arms
        {'name': 'Bicep Curl', 'muscle_group': 'arms', 'description': 'Curl weight toward your shoulder to work biceps.'},
        {'name': 'Tricep Extension', 'muscle_group': 'arms', 'description': 'Extend weight away from you to work triceps.'},
        {'name': 'Hammer Curl', 'muscle_group': 'arms', 'description': 'Curl with neutral grip to work biceps and forearms.'},
        {'name': 'Skull Crusher', 'muscle_group': 'arms', 'description': 'Lower weight toward your forehead lying down.'},
        
        # Legs
        {'name': 'Squat', 'muscle_group': 'legs', 'description': 'Bend knees and lower body with weight on shoulders.'},
        {'name': 'Leg Press', 'muscle_group': 'legs', 'description': 'Press weight away using legs in a seated position.'},
        {'name': 'Lunges', 'muscle_group': 'legs', 'description': 'Step forward and lower your body to work quads and glutes.'},
        {'name': 'Leg Extension', 'muscle_group': 'legs', 'description': 'Extend legs from seated position to target quads.'},
        
        # Core
        {'name': 'Plank', 'muscle_group': 'core', 'description': 'Hold position similar to push-up start to work core.'},
        {'name': 'Sit-ups', 'muscle_group': 'core', 'description': 'Raise upper body from lying position to work abs.'},
        {'name': 'Russian Twist', 'muscle_group': 'core', 'description': 'Twist torso side to side while seated to work obliques.'},
        {'name': 'Leg Raise', 'muscle_group': 'core', 'description': 'Raise legs while lying down to target lower abs.'},
    ]
    
    for exercise_data in exercises:
        exercise = Exercise.query.filter_by(name=exercise_data['name']).first()
        if not exercise:
            exercise = Exercise(**exercise_data)
            db.session.add(exercise)
    
    db.session.commit()
    print(f"Added {len(exercises)} exercises to the database")

def create_demo_user():
    """Create a demo user account."""
    demo_user = User.query.filter_by(email='demo@example.com').first()
    if not demo_user:
        demo_user = User(
            email='demo@example.com',
            name='Demo User',
            password_hash=generate_password_hash('password123')
        )
        db.session.add(demo_user)
        db.session.commit()
        print("Created demo user: demo@example.com / password123")
    else:
        print("Demo user already exists")
    
    return demo_user

def create_sample_workouts(user, num_workouts=20):
    """Create sample workouts for the demo user."""
    if Workout.query.filter_by(user_id=user.id).count() > 0:
        print("User already has workouts, skipping sample workout creation")
        return
    
    exercises = Exercise.query.all()
    
    # Create workouts over the past few months
    for i in range(num_workouts):
        # Random date in the past 90 days
        days_ago = random.randint(0, 90)
        workout_date = datetime.now() - timedelta(days=days_ago)
        
        workout = Workout(
            user_id=user.id,
            date=workout_date,
            name=f"Workout on {workout_date.strftime('%B %d')}",
            completed=True
        )
        db.session.add(workout)
        db.session.flush()  # To get the workout ID
        
        # Add 3-5 exercises to each workout
        num_exercises = random.randint(3, 5)
        workout_exercises = random.sample(exercises, num_exercises)
        
        for exercise in workout_exercises:
            workout_exercise = WorkoutExercise(
                workout_id=workout.id,
                exercise_id=exercise.id
            )
            db.session.add(workout_exercise)
            
            # Add 3-4 sets for each exercise
            num_sets = random.randint(3, 4)
            sets_data = []
            
            for set_num in range(num_sets):
                weight = random.randint(10, 100)
                reps = random.randint(6, 12)
                sets_data.append({'weight': weight, 'reps': reps})
            
            workout_exercise.sets_data = sets_data
    
    db.session.commit()
    print(f"Created {num_workouts} sample workouts for {user.name}")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Seed with sample data
        seed_exercises()
        demo_user = create_demo_user()
        create_sample_workouts(demo_user)
        
        print("Database seeding completed successfully!")
