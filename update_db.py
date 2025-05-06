import os
import sys
import traceback

# Add the project directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

print("Starting database update...")

try:
    from sqlalchemy import text, inspect
    from gym_app import create_app, db
    from gym_app.models import WorkoutExercise

    app = create_app()

    with app.app_context():
        print("Checking if tables and columns exist...")
        connection = db.engine.connect()
        inspector = inspect(db.engine)
        
        # First check if the table exists
        if 'workout_exercises' not in inspector.get_table_names():
            print("Table 'workout_exercises' does not exist. Creating all tables...")
            db.create_all()
            print("All tables created successfully!")
        else:
            print("Table 'workout_exercises' exists. Checking for columns...")
            columns = inspector.get_columns('workout_exercises')
            column_names = [col['name'] for col in columns]
            
            # Check if 'completed' column exists and add it if not
            if 'completed' not in column_names:
                print("Adding 'completed' column to workout_exercises table...")
                try:
                    connection.execute(text("ALTER TABLE workout_exercises ADD COLUMN completed BOOLEAN DEFAULT 0"))
                    print("Column 'completed' added successfully!")
                except Exception as e:
                    print(f"Error adding 'completed' column: {e}")
            else:
                print("Column 'completed' already exists.")
            
            # Check if 'completed_at' column exists and add it if not
            if 'completed_at' not in column_names:
                print("Adding 'completed_at' column to workout_exercises table...")
                try:
                    connection.execute(text("ALTER TABLE workout_exercises ADD COLUMN completed_at DATETIME"))
                    print("Column 'completed_at' added successfully!")
                except Exception as e:
                    print(f"Error adding 'completed_at' column: {e}")
            else:
                print("Column 'completed_at' already exists.")
        
        connection.close()
        db.session.commit()  # Commit any pending changes
        print("Database update completed successfully!")
except Exception as e:
    print(f"Error during database update: {e}")
    traceback.print_exc()
    print("Try manually executing these SQL commands in your database:")
    print("ALTER TABLE workout_exercises ADD COLUMN completed BOOLEAN DEFAULT 0;")
    print("ALTER TABLE workout_exercises ADD COLUMN completed_at DATETIME;")
