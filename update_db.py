import os
import sys

# Add the project directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from gym_app import create_app, db
from gym_app.models import WorkoutExercise
from sqlalchemy import text

app = create_app()

with app.app_context():
    # Check if the columns exist before trying to add them
    connection = db.engine.connect()
    
    # Get the table columns
    result = connection.execute(text("PRAGMA table_info(workout_exercises)"))
    columns = result.fetchall()
    column_names = [col[1] for col in columns]
    
    # Add 'completed' column if it doesn't exist
    if 'completed' not in column_names:
        print("Adding 'completed' column to workout_exercises table...")
        connection.execute(text("ALTER TABLE workout_exercises ADD COLUMN completed BOOLEAN DEFAULT 0"))
    else:
        print("Column 'completed' already exists")
    
    # Add 'completed_at' column if it doesn't exist
    if 'completed_at' not in column_names:
        print("Adding 'completed_at' column to workout_exercises table...")
        connection.execute(text("ALTER TABLE workout_exercises ADD COLUMN completed_at DATETIME"))
    else:
        print("Column 'completed_at' already exists")
    
    connection.close()
    print("Database update completed successfully!")
