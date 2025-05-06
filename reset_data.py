from gym_app import create_app, db
from gym_app.models import User, Exercise, Workout, WorkoutExercise
from seed_data import create_demo_user, seed_exercises, import_exercise_dataset, create_sample_workouts
import os

app = create_app()

def reset_database():
    """Reset the database and reseed it with demo data."""
    with app.app_context():
        try:
            # Check if the database file exists
            db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            
            print(f"Database path: {db_path}")
            
            # Drop all tables and recreate them
            print("Dropping all tables...")
            db.drop_all()
            print("Creating all tables...")
            db.create_all()
            
            # Seed database with exercises and demo user
            print("Seeding exercises...")
            seed_exercises()
            print("Importing exercise dataset...")
            import_exercise_dataset()
            print("Creating demo user...")
            demo_user = create_demo_user()
            print("Creating sample workouts...")
            create_sample_workouts(demo_user, force_recreate=True)
            
            print("Database reset and reseeded successfully!")
            return True
        except Exception as e:
            print(f"Error resetting database: {str(e)}")
            return False

if __name__ == "__main__":
    success = reset_database()
    if success:
        print("Database reset completed. Your app should now work properly!")
    else:
        print("Database reset failed. Please check the errors above.")
