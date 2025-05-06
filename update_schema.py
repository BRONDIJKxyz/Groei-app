from gym_app import create_app, db
from sqlalchemy import Column, String, Text, Boolean, Integer

# Create the Flask app context
app = create_app()

def update_database_schema():
    """Add missing columns to the exercises table."""
    with app.app_context():
        # Get a connection from the engine
        conn = db.engine.connect()
        
        # Check if columns exist and add them if they don't
        # We'll execute direct ALTER TABLE statements
        columns_to_add = [
            ("secondary_muscle_groups", "TEXT"),
            ("equipment", "TEXT"),
            ("difficulty", "TEXT"),
            ("instructions", "TEXT"),
            ("tips", "TEXT"),
            ("video_url", "TEXT"),
            ("is_compound", "BOOLEAN"),
            ("calories_per_hour", "INTEGER")
        ]
        
        for column_name, column_type in columns_to_add:
            try:
                # Try to add the column
                print(f"Adding column {column_name} ({column_type})...")
                conn.execute(f"ALTER TABLE exercises ADD COLUMN {column_name} {column_type}")
                print(f"Successfully added column {column_name}")
            except Exception as e:
                # If column already exists or other error
                print(f"Could not add column {column_name}: {str(e)}")
        
        print("Schema update completed!")

if __name__ == "__main__":
    update_database_schema()
