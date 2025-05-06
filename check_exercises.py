import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from gym_app import create_app
from gym_app.models import Exercise, db
from sqlalchemy import inspect

app = create_app()

with app.app_context():
    # Count total exercises
    total_count = Exercise.query.count()
    print(f"Total exercises in database: {total_count}")
    
    # Get column names from the Exercise model
    inspector = inspect(db.engine)
    columns = inspector.get_columns('exercises')
    column_names = [col['name'] for col in columns]
    print("\nExercise table columns:")
    for col in column_names:
        print(f"- {col}")
    
    # Check how many exercises have empty fields
    incomplete_count = 0
    missing_fields = {
        'description': 0,
        'instructions': 0,
        'tips': 0,
        'secondary_muscle_groups': 0
    }
    
    print("\nSampling exercise data:")
    exercises = Exercise.query.limit(5).all()
    
    for ex in exercises:
        print(f"\n{ex.id}: {ex.name} (Muscle Group: {ex.muscle_group})")
        print(f"  Equipment: {ex.equipment}")
        print(f"  Difficulty: {ex.difficulty}")
        print(f"  Secondary Muscles: {ex.secondary_muscle_groups}")
        print(f"  Description: {(ex.description or '')[:50]}...")
        print(f"  Instructions: {(ex.instructions or '')[:50]}...")
        print(f"  Tips: {(ex.tips or '')[:50]}...")
    
    # Count exercises with missing fields
    for ex in Exercise.query.all():
        if not ex.description or not ex.instructions or not ex.tips or not ex.secondary_muscle_groups:
            incomplete_count += 1
            
        if not ex.description:
            missing_fields['description'] += 1
        if not ex.instructions:
            missing_fields['instructions'] += 1 
        if not ex.tips:
            missing_fields['tips'] += 1
        if not ex.secondary_muscle_groups:
            missing_fields['secondary_muscle_groups'] += 1
    
    print(f"\nExercises with incomplete data: {incomplete_count} out of {total_count}")
    print("Missing field counts:")
    for field, count in missing_fields.items():
        print(f"- {field}: {count} exercises")
    
    # List unique muscle groups
    muscle_groups = db.session.query(Exercise.muscle_group).distinct().all()
    print("\nUnique muscle groups:")
    for mg in muscle_groups:
        print(f"- {mg[0]}")
