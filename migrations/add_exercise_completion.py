from gym_app import create_app, db
from flask_migrate import Migrate
from gym_app.models import WorkoutExercise

app = create_app()
migrate = Migrate(app, db)

with app.app_context():
    # Add the columns if they don't exist
    with db.engine.connect() as conn:
        conn.execute(db.text("PRAGMA table_info(workout_exercises)"))
        columns = conn.fetchall()
        column_names = [col[1] for col in columns]
        
        # Check if completed column exists
        if 'completed' not in column_names:
            print("Adding 'completed' column to workout_exercises table...")
            conn.execute(db.text("ALTER TABLE workout_exercises ADD COLUMN completed BOOLEAN DEFAULT 0"))
        
        # Check if completed_at column exists
        if 'completed_at' not in column_names:
            print("Adding 'completed_at' column to workout_exercises table...")
            conn.execute(db.text("ALTER TABLE workout_exercises ADD COLUMN completed_at DATETIME"))
    
    print("Migration completed successfully!")
