import os
import sys
import re
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from gym_app import create_app
from gym_app.models import Exercise, db

# Primary muscle groups
MUSCLE_GROUPS = {
    'chest': ['chest', 'pecs', 'pectoral', 'bench press', 'push up', 'pushup', 'fly', 'decline', 'incline'],
    'back': ['back', 'lats', 'latissimus', 'row', 'pulldown', 'pull-down', 'pull up', 'pullup', 'deadlift', 'trap', 
             'rhomboid', 'erector'],
    'legs': ['legs', 'quads', 'quadriceps', 'hamstring', 'glutes', 'glute', 'calf', 'calves', 'squat', 'lunge', 
             'leg press', 'leg extension', 'leg curl', 'thigh', 'hack squat', 'deadlift', 'hip thrust'],
    'shoulders': ['shoulder', 'delt', 'deltoid', 'press', 'lateral raise', 'front raise', 'rear delt', 'military', 
                 'overhead press', 'upright row', 'shrug'],
    'arms': ['arms', 'biceps', 'triceps', 'curl', 'extension', 'pushdown', 'preacher', 'hammer', 'concentration', 
             'skull crusher', 'kickback', 'dip', 'forearm', 'wrist', 'chin up', 'chinup'],
    'abs': ['abs', 'abdominal', 'core', 'crunch', 'sit up', 'situp', 'plank', 'russian twist', 'leg raise', 
            'oblique', 'stomach', 'v-up', 'v up', 'mountain climber'],
    'cardio': ['cardio', 'run', 'sprint', 'jog', 'bike', 'cycle', 'cycling', 'rowing', 'elliptical', 'stair', 
              'jumping jack', 'jump rope', 'burpee', 'treadmill', 'hiit', 'interval', 'aerobic'],
    'full body': ['full body', 'compound', 'functional', 'crossfit', 'cross fit', 'circuit', 'kettlebell', 
                 'battle rope', 'sled', 'clean', 'snatch', 'jerk']
}

def determine_muscle_group(exercise_name, description=None, secondary_muscles=None):
    """Determine the most likely muscle group based on name and description."""
    # Convert everything to lowercase for comparison
    name = exercise_name.lower() if exercise_name else ""
    desc = description.lower() if description else ""
    secondary = secondary_muscles.lower() if secondary_muscles else ""
    
    # Combine text to search through
    text = f"{name} {desc} {secondary}"
    
    # Score each muscle group based on keyword matches
    scores = {}
    for muscle_group, keywords in MUSCLE_GROUPS.items():
        score = 0
        for keyword in keywords:
            # Look for whole word matches using regex
            pattern = r'\b' + re.escape(keyword) + r'\b'
            matches = re.findall(pattern, text)
            
            # Name matches are worth more
            name_matches = re.findall(pattern, name)
            
            # Calculate score: name matches * 3 + other matches
            score += len(name_matches) * 3 + (len(matches) - len(name_matches))
            
        scores[muscle_group] = score
    
    # Find the muscle group with the highest score
    best_match = max(scores.items(), key=lambda x: x[1])
    
    # If no significant match found, default to full body
    if best_match[1] == 0:
        return 'full body'
    
    return best_match[0]

def refine_muscle_groups():
    """Assign specific muscle groups to exercises based on names and descriptions."""
    app = create_app()
    
    with app.app_context():
        print("Starting muscle group assignment...")
        
        # Get all exercises
        exercises = Exercise.query.all()
        print(f"Found {len(exercises)} exercises")
        
        # Track statistics
        updated_count = 0
        muscle_group_counts = {}
        
        # Process each exercise
        for exercise in exercises:
            # Skip exercises that already have specific muscle groups
            if exercise.muscle_group and exercise.muscle_group.lower() != 'full body':
                muscle_group_counts[exercise.muscle_group.lower()] = muscle_group_counts.get(exercise.muscle_group.lower(), 0) + 1
                continue
                
            # Determine the most appropriate muscle group
            muscle_group = determine_muscle_group(
                exercise.name, 
                exercise.description, 
                exercise.secondary_muscle_groups
            )
            
            # Set the new muscle group
            exercise.muscle_group = muscle_group
            updated_count += 1
            
            # Track statistics
            muscle_group_counts[muscle_group] = muscle_group_counts.get(muscle_group, 0) + 1
            
            if updated_count % 50 == 0:
                print(f"Updated {updated_count} exercises so far")
        
        # Commit changes if any were made
        if updated_count > 0:
            db.session.commit()
            print(f"Successfully updated {updated_count} exercises with specific muscle groups")
        else:
            print("No exercises needed muscle group assignments")
            
        # Print final distribution
        print("\nFinal muscle group distribution:")
        for muscle_group, count in sorted(muscle_group_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"- {muscle_group}: {count} exercises")

if __name__ == "__main__":
    refine_muscle_groups()
