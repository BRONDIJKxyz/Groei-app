from gym_app import create_app, db
from sqlalchemy import Column, String, Text, Boolean, Integer
import traceback

# Create the Flask app context
app = create_app()

def update_database_schema():
    """Add missing columns to the exercises table without risking data loss."""
    with app.app_context():
        # Get a connection from the engine
        conn = db.engine.connect()
        transaction = conn.begin()
        
        try:
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
            
            # First check if the exercises table exists
            print("Checking if exercises table exists...")
            try:
                result = conn.execute("SELECT 1 FROM exercises LIMIT 1")
                print("Exercises table exists!")
            except Exception as e:
                print(f"Error accessing exercises table: {str(e)}")
                print("Exercises table might not exist or be accessible.")
                transaction.rollback()
                return False
                
            # Now try to add each column
            for column_name, column_type in columns_to_add:
                try:
                    # Try to add the column
                    print(f"Adding column {column_name} ({column_type})...")
                    conn.execute(f"ALTER TABLE exercises ADD COLUMN {column_name} {column_type}")
                    print(f"Successfully added column {column_name}")
                except Exception as e:
                    # If column already exists or other error
                    print(f"Could not add column {column_name}: {str(e)}")
            
            # Commit the transaction
            transaction.commit()
            print("Schema update completed successfully!")
            return True
            
        except Exception as e:
            # If any error occurs, rollback the transaction
            transaction.rollback()
            print(f"Error updating schema: {str(e)}")
            traceback.print_exc()
            return False
        finally:
            # Close the connection
            conn.close()

if __name__ == "__main__":
    success = update_database_schema()
    if success:
        print("Schema updated successfully! Now you can run seed_data.py to restore data.")
    else:
        print("Schema update failed. Please check the errors above.")
