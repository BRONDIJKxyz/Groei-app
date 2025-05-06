import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from gym_app import create_app
from gym_app.models import Exercise, db
import random

# Exercise data templates by muscle group
EXERCISE_TEMPLATES = {
    "chest": {
        "descriptions": [
            "A compound pushing exercise that targets the chest muscles.",
            "An isolation exercise focusing on pectoral development.",
            "A classic chest builder that also engages the shoulders and triceps."
        ],
        "instructions": [
            "1. Position yourself on the bench with feet flat on the floor\n2. Grip the weight with proper form\n3. Lower with control to chest level\n4. Push the weight away from your body\n5. Maintain proper breathing throughout",
            "1. Set up in the proper position\n2. Keep your chest up and shoulders back\n3. Perform the movement with controlled tempo\n4. Focus on squeezing the chest at peak contraction"
        ],
        "tips": [
            "Focus on chest contraction rather than just moving weight.",
            "Keep your elbows at a 45-degree angle to protect your shoulders.",
            "Maintain a slight arch in your lower back for proper form."
        ],
        "secondary_muscles": "triceps, shoulders"
    },
    "back": {
        "descriptions": [
            "A pulling exercise that targets the latissimus dorsi and middle back.",
            "A rowing movement that builds back thickness and strength.",
            "A compound back exercise that improves posture and back definition."
        ],
        "instructions": [
            "1. Maintain a neutral spine throughout the movement\n2. Initiate the pull with your back muscles\n3. Squeeze your shoulder blades together\n4. Lower the weight with control\n5. Repeat with proper form",
            "1. Set up with proper body alignment\n2. Pull using your back, not your arms\n3. Keep your chest up throughout\n4. Control the negative portion"
        ],
        "tips": [
            "Think about pulling with your elbows, not your hands.",
            "Keep your core engaged to protect your lower back.",
            "Focus on full range of motion rather than heavy weight."
        ],
        "secondary_muscles": "biceps, rear delts"
    },
    "legs": {
        "descriptions": [
            "A compound lower body exercise targeting the quadriceps, hamstrings, and glutes.",
            "A fundamental leg movement that builds overall lower body strength.",
            "A functional exercise that improves lower body power and mobility."
        ],
        "instructions": [
            "1. Position feet shoulder-width apart\n2. Keep your chest up and back straight\n3. Bend at the knees and hips\n4. Lower until thighs are parallel to floor\n5. Drive through heels to return to starting position",
            "1. Maintain proper alignment of knees over toes\n2. Control the descent\n3. Engage your core throughout\n4. Push through your heels on the way up"
        ],
        "tips": [
            "Focus on proper depth rather than weight.",
            "Keep your knees tracking over your toes, not caving inward.",
            "Breathe out during the exertion phase of the movement."
        ],
        "secondary_muscles": "core, lower back"
    },
    "shoulders": {
        "descriptions": [
            "An isolation exercise targeting the deltoid muscles.",
            "A shoulder movement that builds strength and stability in the shoulder joint.",
            "A compound exercise that develops all three heads of the deltoid muscle."
        ],
        "instructions": [
            "1. Keep a slight bend in the elbows\n2. Raise the weights with controlled motion\n3. Hold briefly at the top\n4. Lower slowly back to starting position\n5. Maintain proper posture throughout",
            "1. Position yourself with proper body alignment\n2. Control the weight throughout the movement\n3. Focus on the shoulder muscles doing the work\n4. Avoid using momentum"
        ],
        "tips": [
            "Use lighter weights with perfect form rather than heavier weights with poor technique.",
            "Keep your core engaged to prevent arching your lower back.",
            "Avoid shrugging your shoulders during the movement."
        ],
        "secondary_muscles": "trapezius, triceps"
    },
    "arms": {
        "descriptions": [
            "An isolation exercise targeting the biceps muscles.",
            "A focused movement to develop the triceps.",
            "A compound arm exercise that builds overall arm strength and definition."
        ],
        "instructions": [
            "1. Keep your elbows close to your body\n2. Curl/extend with controlled movement\n3. Squeeze the muscle at peak contraction\n4. Lower slowly to starting position\n5. Repeat with proper form",
            "1. Maintain strict form throughout\n2. Focus on the mind-muscle connection\n3. Use a full range of motion\n4. Control the negative portion"
        ],
        "tips": [
            "Focus on feeling the target muscle working, not just moving weight.",
            "Keep your wrists in a neutral position to prevent strain.",
            "Avoid using momentum - slower is often better for arm training."
        ],
        "secondary_muscles": "shoulders, forearms"
    },
    "abs": {
        "descriptions": [
            "A core exercise focusing on the abdominal muscles.",
            "An exercise that targets the entire core region.",
            "A movement that develops core strength and stability."
        ],
        "instructions": [
            "1. Start in a proper position with lower back supported\n2. Contract your abdominals to initiate movement\n3. Exhale during the contraction\n4. Return to starting position with control\n5. Maintain tension throughout the set",
            "1. Keep your neck neutral throughout\n2. Focus on using your abs, not hip flexors\n3. Control the entire movement\n4. Breathe rhythmically during the exercise"
        ],
        "tips": [
            "Quality of movement is more important than quantity for abs.",
            "Keep your lower back pressed into the floor/mat to protect your spine.",
            "Focus on slow, controlled movements rather than speed."
        ],
        "secondary_muscles": "lower back, obliques"
    },
    "cardio": {
        "descriptions": [
            "A cardiovascular exercise that improves heart health and endurance.",
            "A fat-burning workout that elevates your heart rate.",
            "An endurance-building exercise that improves overall fitness."
        ],
        "instructions": [
            "1. Start with a proper warm-up\n2. Maintain good posture throughout\n3. Keep a consistent pace\n4. Control your breathing\n5. Cool down properly afterward",
            "1. Begin at a comfortable intensity\n2. Increase effort gradually\n3. Focus on proper form to prevent injury\n4. Monitor your heart rate if possible"
        ],
        "tips": [
            "Listen to your body and adjust intensity as needed.",
            "Stay hydrated before, during, and after cardio sessions.",
            "Mix high and low intensity for optimal results."
        ],
        "secondary_muscles": "full body"
    }
}

# Default template for any unmapped muscle groups
DEFAULT_TEMPLATE = {
    "descriptions": [
        "A compound exercise targeting multiple muscle groups.",
        "A focused movement to develop strength and muscular endurance.",
        "An exercise that builds functional strength and stability."
    ],
    "instructions": [
        "1. Set up with proper form and alignment\n2. Perform the movement with controlled tempo\n3. Focus on the target muscles\n4. Complete the full range of motion\n5. Maintain good breathing technique",
        "1. Begin in the correct starting position\n2. Execute the movement with proper technique\n3. Avoid using momentum\n4. Return to the starting position with control"
    ],
    "tips": [
        "Focus on proper form and technique before adding weight.",
        "Maintain a mind-muscle connection throughout the exercise.",
        "Progress gradually to prevent injury and ensure continued improvement."
    ],
    "secondary_muscles": "supporting muscle groups"
}

# Difficulty levels for exercises without specified difficulty
DIFFICULTY_LEVELS = ["beginner", "intermediate", "advanced"]

def update_exercise_data():
    """Update all exercises to ensure complete information."""
    app = create_app()
    
    with app.app_context():
        print("Starting exercise database update...")
        exercises = Exercise.query.all()
        print(f"Found {len(exercises)} exercises in database")
        
        updated_count = 0
        
        for exercise in exercises:
            # Track if we need to update this exercise
            needs_update = False
            
            # Get template based on muscle group or use default
            template = EXERCISE_TEMPLATES.get(exercise.muscle_group.lower(), DEFAULT_TEMPLATE)
            
            # Fill in missing description
            if not exercise.description:
                exercise.description = random.choice(template["descriptions"])
                needs_update = True
            
            # Fill in missing instructions
            if not exercise.instructions:
                exercise.instructions = random.choice(template["instructions"])
                needs_update = True
            
            # Fill in missing tips
            if not exercise.tips:
                exercise.tips = random.choice(template["tips"])
                needs_update = True
            
            # Fill in missing secondary muscle groups
            if not exercise.secondary_muscle_groups:
                exercise.secondary_muscle_groups = template["secondary_muscles"]
                needs_update = True
            
            # Fill in missing difficulty
            if not exercise.difficulty:
                exercise.difficulty = random.choice(DIFFICULTY_LEVELS)
                needs_update = True
            
            # Update database if changes were made
            if needs_update:
                updated_count += 1
                if updated_count % 10 == 0:
                    print(f"Updated {updated_count} exercises so far...")
        
        # Commit all changes
        if updated_count > 0:
            db.session.commit()
            print(f"Successfully updated {updated_count} exercises with missing information")
        else:
            print("All exercises already have complete information!")

if __name__ == "__main__":
    update_exercise_data()
