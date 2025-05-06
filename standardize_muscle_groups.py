import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from gym_app import create_app
from gym_app.models import Exercise, db

# Standard muscle group categories
STANDARD_MUSCLE_GROUPS = [
    'chest', 'back', 'legs', 'shoulders', 'arms', 'abs', 'cardio', 'full body', 'neck', 'calves'
]

# Mapping of common variations to standardized categories
MUSCLE_GROUP_MAPPING = {
    # Chest variations
    'pectorals': 'chest',
    'pecs': 'chest',
    'upper chest': 'chest',
    'lower chest': 'chest',
    'middle chest': 'chest',
    'chest muscles': 'chest',
    'pectoral': 'chest',
    
    # Back variations
    'lats': 'back',
    'upper back': 'back',
    'lower back': 'back',
    'middle back': 'back',
    'latissimus dorsi': 'back',
    'traps': 'back',
    'trapezius': 'back',
    'rhomboids': 'back',
    
    # Legs variations
    'quads': 'legs',
    'quadriceps': 'legs',
    'hamstrings': 'legs',
    'glutes': 'legs',
    'gluteus maximus': 'legs',
    'thighs': 'legs',
    'leg': 'legs',
    'lower body': 'legs',
    
    # Shoulders variations
    'delts': 'shoulders',
    'deltoids': 'shoulders',
    'shoulder': 'shoulders',
    'upper shoulders': 'shoulders',
    'rear delts': 'shoulders',
    'front delts': 'shoulders',
    'side delts': 'shoulders',
    
    # Arms variations
    'biceps': 'arms',
    'triceps': 'arms',
    'forearms': 'arms',
    'arm': 'arms',
    'upper arms': 'arms',
    
    # Abs variations
    'abdominals': 'abs',
    'core': 'abs',
    'stomach': 'abs',
    'midsection': 'abs',
    'obliques': 'abs',
    
    # Cardio variations
    'cardiovascular': 'cardio',
    'aerobic': 'cardio',
    'heart': 'cardio',
    'endurance': 'cardio',
    
    # Other
    'fullbody': 'full body',
    'total body': 'full body',
    'whole body': 'full body',
    'complete body': 'full body',
    'calf': 'calves',
}

def standardize_muscle_groups():
    """Ensure all exercises have standardized muscle group names."""
    app = create_app()
    
    with app.app_context():
        print("Starting muscle group standardization...")
        
        # Get all exercises
        exercises = Exercise.query.all()
        print(f"Found {len(exercises)} exercises")
        
        # Track statistics
        updated_count = 0
        already_standard_count = 0
        unknown_muscle_groups = set()
        
        # Process each exercise
        for exercise in exercises:
            original_muscle_group = exercise.muscle_group.lower() if exercise.muscle_group else None
            
            # Skip if already has a standard muscle group
            if original_muscle_group in STANDARD_MUSCLE_GROUPS:
                already_standard_count += 1
                continue
                
            # Check if we have a mapping for this muscle group
            if original_muscle_group in MUSCLE_GROUP_MAPPING:
                standard_muscle_group = MUSCLE_GROUP_MAPPING[original_muscle_group]
                exercise.muscle_group = standard_muscle_group
                updated_count += 1
                
                if updated_count % 10 == 0:
                    print(f"Updated {updated_count} exercises so far")
            elif original_muscle_group:
                # Keep track of unknown muscle groups
                unknown_muscle_groups.add(original_muscle_group)
            else:
                # If no muscle group is set, set a default value of 'full body'
                exercise.muscle_group = 'full body'
                updated_count += 1
        
        # Commit changes if any were made
        if updated_count > 0:
            db.session.commit()
            print(f"Successfully standardized {updated_count} exercises")
        else:
            print("No exercises needed standardization")
            
        print(f"Already standard: {already_standard_count}")
        
        # Report any unknown muscle groups
        if unknown_muscle_groups:
            print("\nUnknown muscle groups found:")
            for muscle_group in sorted(unknown_muscle_groups):
                print(f"- '{muscle_group}'")
            print("\nConsider adding these to the mapping dictionary.")
        
        # Print current distribution of muscle groups
        muscle_group_counts = {}
        for exercise in exercises:
            muscle_group = exercise.muscle_group.lower() if exercise.muscle_group else 'none'
            muscle_group_counts[muscle_group] = muscle_group_counts.get(muscle_group, 0) + 1
        
        print("\nCurrent muscle group distribution:")
        for muscle_group, count in sorted(muscle_group_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"- {muscle_group}: {count} exercises")

if __name__ == "__main__":
    standardize_muscle_groups()
