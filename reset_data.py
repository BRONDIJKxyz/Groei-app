from gym_app import create_app, db
from gym_app.models import User, Exercise, Workout, WorkoutExercise
from seed_data import create_demo_user, seed_exercises, import_exercise_dataset, create_sample_workouts
import os

app = create_app()

def reset_database():
    """Reset the database and reseed it with demo data."""
    with app.app_context():
        try:
            # Ensure tables are created
            print("Ensuring all tables are created...")
            db.create_all()

            # Selectively delete data from tables
            print("Deleting old data from Exercise and WorkoutExercise tables...")
            # Execute delete statements. The order might matter due to foreign keys.
            # If WorkoutExercise has a foreign key to Exercise, delete from WorkoutExercise first.
            db.session.execute(WorkoutExercise.__table__.delete())
            db.session.execute(Exercise.__table__.delete())
            # If you want to reset workouts for the demo user as well, you could do:
            # demo_user_to_reset = User.query.filter_by(email='demo@example.com').first()
            # if demo_user_to_reset:
            #     Workout.query.filter_by(user_id=demo_user_to_reset.id).delete()
            db.session.commit()
            print("Old exercise data deleted.")
            
            # Seed database with exercises and demo user
            print("Seeding exercises...")
            seed_exercises()
            print("Importing exercise dataset...")
            import_exercise_dataset()
            print("Creating/Verifying demo user...")
            demo_user = create_demo_user()
            print("Creating sample workouts for demo user (if needed)...")
            create_sample_workouts(demo_user, force_recreate=True) # force_recreate might need adjustment if it also deletes user's workouts
            
            print("Database reseeded successfully (users preserved)!")
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
