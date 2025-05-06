from gym_app import create_app, db
from gym_app.models import User, Exercise, Workout, WorkoutExercise
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random
import requests

def seed_exercises():
    """Add comprehensive exercises to the database."""
    exercises = [
        # Chest
        {
            'name': 'Bench Press', 
            'muscle_group': 'chest', 
            'secondary_muscle_groups': 'triceps, shoulders',
            'equipment': 'barbell, bench',
            'difficulty': 'intermediate',
            'description': 'A compound upper-body exercise that involves pressing a weight upwards while lying on a bench.',
            'instructions': '1. Lie on a flat bench with feet on the ground\n2. Grip the bar slightly wider than shoulder width\n3. Lower the bar to your mid-chest\n4. Press the bar back to starting position with elbows fully extended',
            'tips': 'Keep your wrists straight and elbows at a 45-degree angle to your body to protect your shoulders.',
            'is_compound': True,
            'calories_per_hour': 400
        },
        {
            'name': 'Incline Press', 
            'muscle_group': 'chest', 
            'secondary_muscle_groups': 'shoulders, triceps',
            'equipment': 'barbell, incline bench',
            'difficulty': 'intermediate',
            'description': 'A variation of the bench press performed on an inclined bench to target the upper chest.',
            'instructions': '1. Lie on an incline bench set to 30-45 degrees\n2. Grip the bar slightly wider than shoulder width\n3. Lower the bar to your upper chest\n4. Press the bar back to starting position',
            'is_compound': True,
            'calories_per_hour': 380
        },
        {
            'name': 'Chest Fly', 
            'muscle_group': 'chest', 
            'secondary_muscle_groups': 'shoulders',
            'equipment': 'dumbbells, bench',
            'difficulty': 'beginner',
            'description': 'An isolation exercise that targets the pectoral muscles by moving weights in an arc-like motion.',
            'instructions': '1. Lie on a flat bench holding dumbbells above your chest\n2. Slightly bend your elbows\n3. Lower the weights in an arc motion until you feel a stretch\n4. Bring the weights back together in an arc',
            'tips': 'Keep a slight bend in your elbows throughout the movement to reduce stress on the joints.',
            'is_compound': False,
            'calories_per_hour': 280
        },
        {
            'name': 'Push-ups', 
            'muscle_group': 'chest', 
            'secondary_muscle_groups': 'triceps, shoulders, core',
            'equipment': 'bodyweight',
            'difficulty': 'beginner',
            'description': 'A classic bodyweight exercise for developing upper body strength.',
            'instructions': '1. Start in a plank position with hands slightly wider than shoulders\n2. Keep your body in a straight line\n3. Lower your chest to the floor by bending your elbows\n4. Push back up to starting position',
            'tips': 'Keep your core engaged throughout the movement to maintain proper form.',
            'is_compound': True,
            'calories_per_hour': 300
        },
        {
            'name': 'Dumbbell Chest Press', 
            'muscle_group': 'chest', 
            'secondary_muscle_groups': 'triceps, shoulders',
            'equipment': 'dumbbells, bench',
            'difficulty': 'beginner',
            'description': 'A variation of the bench press using dumbbells for greater range of motion.',
            'instructions': '1. Lie on a flat bench with a dumbbell in each hand\n2. Position dumbbells at shoulder level\n3. Press weights upward until arms are extended\n4. Lower weights back to starting position',
            'is_compound': True,
            'calories_per_hour': 350
        },
        
        # Back
        {
            'name': 'Pull-ups', 
            'muscle_group': 'back', 
            'secondary_muscle_groups': 'biceps, shoulders',
            'equipment': 'pull-up bar',
            'difficulty': 'intermediate',
            'description': 'A challenging upper body exercise that builds back and arm strength.',
            'instructions': '1. Hang from a pull-up bar with hands shoulder-width apart\n2. Pull your body up until your chin clears the bar\n3. Lower yourself with control back to hanging position',
            'tips': 'Start with assisted pull-ups if you cannot do full pull-ups.',
            'is_compound': True,
            'calories_per_hour': 450
        },
        {
            'name': 'Deadlift', 
            'muscle_group': 'back', 
            'secondary_muscle_groups': 'legs, glutes, core',
            'equipment': 'barbell',
            'difficulty': 'advanced',
            'description': 'A compound movement that works nearly the entire body with focus on the posterior chain.',
            'instructions': '1. Stand with feet hip-width apart, barbell over mid-foot\n2. Bend at hips and knees to grip the bar\n3. Lift the bar by extending hips and knees\n4. Return the weight to the floor with control',
            'tips': 'Keep your back straight and core engaged throughout the movement.',
            'is_compound': True,
            'calories_per_hour': 500
        },
        {
            'name': 'Bent Over Row', 
            'muscle_group': 'back', 
            'secondary_muscle_groups': 'biceps, shoulders',
            'equipment': 'barbell',
            'difficulty': 'intermediate',
            'description': 'A compound exercise that targets the middle back muscles and requires stability.',
            'instructions': '1. Bend at your hips until torso is almost parallel to floor\n2. Grip barbell with hands shoulder-width apart\n3. Pull the bar to your lower ribcage\n4. Lower the bar with control',
            'is_compound': True,
            'calories_per_hour': 400
        },
        {
            'name': 'Lat Pulldown', 
            'muscle_group': 'back', 
            'secondary_muscle_groups': 'biceps, shoulders',
            'equipment': 'cable machine',
            'difficulty': 'beginner',
            'description': 'A machine exercise that simulates pull-ups to build back width.',
            'instructions': '1. Sit at a lat pulldown machine with thighs secured\n2. Grip the bar wider than shoulder width\n3. Pull the bar down to your upper chest\n4. Slowly return to starting position',
            'is_compound': True,
            'calories_per_hour': 350
        },
        {
            'name': 'Single-Arm Dumbbell Row', 
            'muscle_group': 'back', 
            'secondary_muscle_groups': 'biceps, shoulders',
            'equipment': 'dumbbell, bench',
            'difficulty': 'beginner',
            'description': 'A unilateral back exercise that helps correct imbalances and builds thickness.',
            'instructions': '1. Place one knee and hand on a bench\n2. Hold a dumbbell in the opposite hand hanging down\n3. Pull the dumbbell up to your hip\n4. Lower with control and repeat',
            'is_compound': True,
            'calories_per_hour': 380
        },
        
        # Shoulders
        {
            'name': 'Overhead Press', 
            'muscle_group': 'shoulders', 
            'secondary_muscle_groups': 'triceps, upper chest',
            'equipment': 'barbell or dumbbells',
            'difficulty': 'intermediate',
            'description': 'A fundamental strength movement that builds shoulder size and strength.',
            'instructions': '1. Stand with feet shoulder-width apart\n2. Hold weight at shoulder level\n3. Press weight overhead until arms are fully extended\n4. Lower weight back to shoulders',
            'is_compound': True,
            'calories_per_hour': 400
        },
        {
            'name': 'Lateral Raise', 
            'muscle_group': 'shoulders', 
            'secondary_muscle_groups': 'upper traps',
            'equipment': 'dumbbells',
            'difficulty': 'beginner',
            'description': 'An isolation exercise that targets the lateral deltoids for broader shoulders.',
            'instructions': '1. Stand holding dumbbells at your sides\n2. Raise arms out to sides until parallel to floor\n3. Pause briefly at the top\n4. Lower dumbbells with control',
            'tips': 'Keep a slight bend in your elbows and avoid using momentum.',
            'is_compound': False,
            'calories_per_hour': 300
        },
        {
            'name': 'Front Raise', 
            'muscle_group': 'shoulders', 
            'secondary_muscle_groups': 'upper chest',
            'equipment': 'dumbbells, barbell, or plate',
            'difficulty': 'beginner',
            'description': 'An isolation exercise that targets the anterior deltoids.',
            'instructions': '1. Stand holding weights in front of thighs\n2. Raise weights forward and up to shoulder height\n3. Pause briefly\n4. Lower with control',
            'is_compound': False,
            'calories_per_hour': 280
        },
        {
            'name': 'Face Pull', 
            'muscle_group': 'shoulders', 
            'secondary_muscle_groups': 'upper back, rotator cuff',
            'equipment': 'cable machine, rope attachment',
            'difficulty': 'beginner',
            'description': 'A corrective exercise that strengthens the rear deltoids and rotator cuff.',
            'instructions': '1. Stand facing a cable machine with rope attachment\n2. Pull the rope towards your face, separating hands at the end\n3. Squeeze shoulder blades together\n4. Return to starting position with control',
            'tips': 'Focus on external rotation of the shoulders at the end of the movement.',
            'is_compound': False,
            'calories_per_hour': 250
        },
        {
            'name': 'Arnold Press', 
            'muscle_group': 'shoulders', 
            'secondary_muscle_groups': 'triceps',
            'equipment': 'dumbbells',
            'difficulty': 'intermediate',
            'description': 'A dynamic shoulder press that rotates the arms during the movement.',
            'instructions': '1. Sit with dumbbells at shoulder height, palms facing you\n2. Press upward while rotating palms away from you\n3. At the top, your arms should be extended with palms facing forward\n4. Reverse the motion when lowering',
            'is_compound': True,
            'calories_per_hour': 350
        },
        
        # Arms
        {
            'name': 'Bicep Curl', 
            'muscle_group': 'arms', 
            'secondary_muscle_groups': 'forearms',
            'equipment': 'dumbbells or barbell',
            'difficulty': 'beginner',
            'description': 'A fundamental exercise for building bicep size and strength.',
            'instructions': '1. Stand holding weights with arms fully extended\n2. Curl the weights toward your shoulders\n3. Squeeze your biceps at the top\n4. Lower with control to starting position',
            'tips': 'Keep your elbows close to your body throughout the movement.',
            'is_compound': False,
            'calories_per_hour': 280
        },
        {
            'name': 'Tricep Extension', 
            'muscle_group': 'arms', 
            'secondary_muscle_groups': '',
            'equipment': 'dumbbells, cable, or rope',
            'difficulty': 'beginner',
            'description': 'An isolation exercise for the triceps that extends the elbow joint.',
            'instructions': '1. Stand or sit holding weight overhead\n2. Lower the weight behind your head by bending elbows\n3. Extend arms back to starting position\n4. Keep upper arms stationary throughout',
            'is_compound': False,
            'calories_per_hour': 250
        },
        {
            'name': 'Hammer Curl', 
            'muscle_group': 'arms', 
            'secondary_muscle_groups': 'forearms',
            'equipment': 'dumbbells',
            'difficulty': 'beginner',
            'description': 'A variation of the bicep curl that emphasizes the brachialis and forearms.',
            'instructions': '1. Stand holding dumbbells with palms facing each other\n2. Curl the weights while maintaining neutral grip\n3. Squeeze at the top\n4. Lower with control',
            'is_compound': False,
            'calories_per_hour': 280
        },
        {
            'name': 'Skull Crusher', 
            'muscle_group': 'arms', 
            'secondary_muscle_groups': '',
            'equipment': 'barbell, EZ bar, or dumbbells',
            'difficulty': 'intermediate',
            'description': 'A tricep exercise performed lying down with weight lowered toward the forehead.',
            'instructions': '1. Lie on a bench holding weight above your chest\n2. Bend elbows to lower weight toward your forehead\n3. Extend arms back to starting position\n4. Keep upper arms stationary',
            'tips': 'Use a spotter or lighter weights when first learning this exercise.',
            'is_compound': False,
            'calories_per_hour': 300
        },
        {
            'name': 'Dips', 
            'muscle_group': 'arms', 
            'secondary_muscle_groups': 'chest, shoulders',
            'equipment': 'parallel bars or bench',
            'difficulty': 'intermediate',
            'description': 'A compound pushing exercise that heavily targets the triceps.',
            'instructions': '1. Support your body on parallel bars with arms extended\n2. Lower your body by bending your elbows\n3. Push back up to starting position\n4. Keep elbows close to body for more tricep focus',
            'is_compound': True,
            'calories_per_hour': 400
        },
        
        # Legs
        {
            'name': 'Squat', 
            'muscle_group': 'legs', 
            'secondary_muscle_groups': 'glutes, lower back, core',
            'equipment': 'barbell or bodyweight',
            'difficulty': 'intermediate',
            'description': 'A fundamental compound lower body exercise that builds overall strength.',
            'instructions': '1. Stand with feet shoulder-width apart\n2. Bend knees and hips to lower your body\n3. Keep chest up and back straight\n4. Return to standing by extending knees and hips',
            'tips': 'Aim to reach at least parallel depth for full muscle development.',
            'is_compound': True,
            'calories_per_hour': 500
        },
        {
            'name': 'Leg Press', 
            'muscle_group': 'legs', 
            'secondary_muscle_groups': 'glutes',
            'equipment': 'leg press machine',
            'difficulty': 'beginner',
            'description': 'A machine-based compound leg exercise with reduced stabilization requirements.',
            'instructions': '1. Sit on leg press machine with feet on platform\n2. Release safety and lower platform by bending knees\n3. Press back to starting position without locking knees\n4. Control the movement throughout',
            'is_compound': True,
            'calories_per_hour': 450
        },
        {
            'name': 'Lunges', 
            'muscle_group': 'legs', 
            'secondary_muscle_groups': 'glutes, core',
            'equipment': 'bodyweight, dumbbells, or barbell',
            'difficulty': 'beginner',
            'description': 'A unilateral exercise that builds leg strength, balance, and coordination.',
            'instructions': '1. Stand with feet hip-width apart\n2. Step forward with one leg and lower your body\n3. Both knees should bend to approximately 90 degrees\n4. Push through front foot to return to starting position',
            'is_compound': True,
            'calories_per_hour': 400
        },
        {
            'name': 'Leg Extension', 
            'muscle_group': 'legs', 
            'secondary_muscle_groups': '',
            'equipment': 'leg extension machine',
            'difficulty': 'beginner',
            'description': 'An isolation exercise that targets the quadriceps muscles.',
            'instructions': '1. Sit on machine with pads on lower shins\n2. Extend knees to lift weight\n3. Pause briefly at the top\n4. Lower with control',
            'tips': 'Avoid using momentum and focus on quad contraction.',
            'is_compound': False,
            'calories_per_hour': 250
        },
        {
            'name': 'Romanian Deadlift', 
            'muscle_group': 'legs', 
            'secondary_muscle_groups': 'glutes, lower back',
            'equipment': 'barbell or dumbbells',
            'difficulty': 'intermediate',
            'description': 'A hip-hinge movement that targets the hamstrings and posterior chain.',
            'instructions': '1. Stand holding weight in front of thighs\n2. Push hips back while maintaining slight knee bend\n3. Lower weight along legs until you feel hamstring stretch\n4. Return to starting position by driving hips forward',
            'tips': 'Keep back straight and core engaged throughout the movement.',
            'is_compound': True,
            'calories_per_hour': 450
        },
        
        # Core
        {
            'name': 'Plank', 
            'muscle_group': 'core', 
            'secondary_muscle_groups': 'shoulders',
            'equipment': 'bodyweight',
            'difficulty': 'beginner',
            'description': 'An isometric core exercise that builds total core stability.',
            'instructions': '1. Start in a push-up position on forearms\n2. Keep body in straight line from head to heels\n3. Engage core and hold position\n4. Breathe normally throughout',
            'tips': 'Don\'t let your hips sag or pike up; maintain a neutral spine.',
            'is_compound': False,
            'calories_per_hour': 300
        },
        {
            'name': 'Sit-ups', 
            'muscle_group': 'core', 
            'secondary_muscle_groups': 'hip flexors',
            'equipment': 'bodyweight',
            'difficulty': 'beginner',
            'description': 'A classic exercise that targets the rectus abdominis (six-pack muscles).',
            'instructions': '1. Lie on back with knees bent and feet flat\n2. Place hands behind head or across chest\n3. Curl upper body toward knees\n4. Lower back down with control',
            'is_compound': False,
            'calories_per_hour': 280
        },
        {
            'name': 'Russian Twist', 
            'muscle_group': 'core', 
            'secondary_muscle_groups': 'obliques',
            'equipment': 'bodyweight or weight',
            'difficulty': 'beginner',
            'description': 'A rotational exercise that targets the obliques and improves core stability.',
            'instructions': '1. Sit with knees bent and feet elevated\n2. Lean back slightly to engage core\n3. Twist torso to one side, then the other\n4. Add weight for increased difficulty',
            'is_compound': False,
            'calories_per_hour': 300
        },
        {
            'name': 'Leg Raise', 
            'muscle_group': 'core', 
            'secondary_muscle_groups': 'hip flexors',
            'equipment': 'bodyweight',
            'difficulty': 'intermediate',
            'description': 'An exercise that targets the lower abdominals and hip flexors.',
            'instructions': '1. Lie flat on back with legs extended\n2. Keep back pressed to the floor\n3. Raise legs to vertical position\n4. Lower legs with control without touching the floor',
            'tips': 'For easier variation, bend knees during the movement.',
            'is_compound': False,
            'calories_per_hour': 320
        },
        {
            'name': 'Mountain Climbers', 
            'muscle_group': 'core', 
            'secondary_muscle_groups': 'shoulders, chest, quads',
            'equipment': 'bodyweight',
            'difficulty': 'beginner',
            'description': 'A dynamic exercise that combines core strength with cardiovascular benefits.',
            'instructions': '1. Start in a push-up position\n2. Alternate bringing knees toward chest in running motion\n3. Keep hips down and core engaged\n4. Move at desired speed based on goals',
            'is_compound': True,
            'calories_per_hour': 400
        },
        
        # Cardio
        {
            'name': 'Running', 
            'muscle_group': 'cardio', 
            'secondary_muscle_groups': 'legs, core',
            'equipment': 'none or treadmill',
            'difficulty': 'beginner',
            'description': 'A fundamental cardio exercise for improving endurance and burning calories.',
            'instructions': '1. Maintain good posture with slight forward lean\n2. Land midfoot with feet under hips\n3. Use a comfortable stride length\n4. Breathe rhythmically',
            'tips': 'Start with walk/run intervals if you\'re a beginner.',
            'is_compound': True,
            'calories_per_hour': 600
        },
        {
            'name': 'Cycling', 
            'muscle_group': 'cardio', 
            'secondary_muscle_groups': 'legs',
            'equipment': 'bicycle or stationary bike',
            'difficulty': 'beginner',
            'description': 'A low-impact cardio option that builds leg strength and endurance.',
            'instructions': '1. Adjust seat height so legs are nearly extended at bottom of pedal stroke\n2. Maintain steady cadence\n3. Mix intensity levels for best results\n4. Keep upper body relatively stable',
            'is_compound': True,
            'calories_per_hour': 500
        },
        {
            'name': 'Jumping Rope', 
            'muscle_group': 'cardio', 
            'secondary_muscle_groups': 'calves, shoulders',
            'equipment': 'jump rope',
            'difficulty': 'beginner',
            'description': 'A highly effective cardio exercise for coordination and calorie burning.',
            'instructions': '1. Hold handles with rope behind you\n2. Swing rope overhead and jump as it passes under feet\n3. Land softly on balls of feet\n4. Maintain a steady rhythm',
            'tips': 'Start with a slower pace until you master the technique.',
            'is_compound': True,
            'calories_per_hour': 700
        },
        {
            'name': 'Burpees', 
            'muscle_group': 'cardio', 
            'secondary_muscle_groups': 'chest, legs, core',
            'equipment': 'bodyweight',
            'difficulty': 'intermediate',
            'description': 'A full-body exercise that combines strength and cardio elements.',
            'instructions': '1. Start standing, then squat down and place hands on floor\n2. Jump feet back to push-up position\n3. Perform a push-up (optional)\n4. Jump feet forward and explosively jump up with arms overhead',
            'is_compound': True,
            'calories_per_hour': 700
        },
        {
            'name': 'Rowing', 
            'muscle_group': 'cardio', 
            'secondary_muscle_groups': 'back, arms, legs',
            'equipment': 'rowing machine',
            'difficulty': 'beginner',
            'description': 'A full-body cardio exercise with minimal joint impact.',
            'instructions': '1. Sit with feet secured and grip the handle\n2. Push with legs first, then pull with back and arms\n3. Return by extending arms, then hinging at hips, then bending knees\n4. Maintain good posture throughout',
            'tips': 'Focus on power from the legs rather than pulling with arms.',
            'is_compound': True,
            'calories_per_hour': 600
        }
    ]
    
    added_count = 0
    for exercise_data in exercises:
        exercise = Exercise.query.filter_by(name=exercise_data['name']).first()
        if not exercise:
            exercise = Exercise(**exercise_data)
            db.session.add(exercise)
            added_count += 1
    
    db.session.commit()
    print(f"Added {added_count} new exercises to the database")

def import_exercise_dataset():
    """Import exercises from the Free Exercise DB dataset."""
    import json
    
    print("Downloading exercise dataset from Free Exercise DB...")
    # Download the dataset from GitHub
    url = "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/dist/exercises.json"
    response = requests.get(url)
    exercises_data = response.json()
    
    print(f"Processing {len(exercises_data)} exercises from dataset...")
    
    added_count = 0
    skipped_count = 0
    
    for ex_data in exercises_data:
        # Check if exercise already exists
        existing = Exercise.query.filter_by(name=ex_data['name']).first()
        if existing:
            skipped_count += 1
            continue
        
        # Map the primary muscle group to our categories
        primary_muscle = ''
        if 'primary' in ex_data and ex_data['primary']:
            muscle = ex_data['primary'].lower()
            # Map to our standardized categories
            if any(x in muscle for x in ['chest', 'pectoral']):
                primary_muscle = 'chest'
            elif any(x in muscle for x in ['back', 'lat', 'trap', 'rhomboid']):
                primary_muscle = 'back'
            elif any(x in muscle for x in ['shoulder', 'delt']):
                primary_muscle = 'shoulders'
            elif any(x in muscle for x in ['bicep', 'tricep', 'arm', 'forearm']):
                primary_muscle = 'arms'
            elif any(x in muscle for x in ['quad', 'hamstring', 'calf', 'glute', 'leg']):
                primary_muscle = 'legs'
            elif any(x in muscle for x in ['ab', 'core', 'oblique']):
                primary_muscle = 'core'
            elif any(x in muscle for x in ['cardio', 'heart']):
                primary_muscle = 'cardio'
            else:
                # Default to closest match if none of the above
                primary_muscle = 'core'  # Default for most isolation exercises
        
        # Determine difficulty level
        difficulty = 'beginner'
        if 'level' in ex_data:
            level = ex_data['level'].lower()
            if 'beginner' in level:
                difficulty = 'beginner'
            elif 'intermediate' in level:
                difficulty = 'intermediate'
            elif 'advanced' in level or 'expert' in level:
                difficulty = 'advanced'
        
        # Create the exercise object
        exercise = Exercise(
            name=ex_data['name'],
            muscle_group=primary_muscle,
            secondary_muscle_groups=', '.join(ex_data.get('secondary', [])) if 'secondary' in ex_data else '',
            equipment=ex_data.get('equipment', ''),
            difficulty=difficulty,
            description=ex_data.get('description', ''),
            instructions='\n'.join(ex_data.get('steps', [])) if 'steps' in ex_data else '',
            image_url=ex_data.get('image', ''),
            is_compound='compound' in ex_data.get('attributes', [])
        )
        
        db.session.add(exercise)
        added_count += 1
        
        # Commit in batches to avoid memory issues
        if added_count % 50 == 0:
            db.session.commit()
            print(f"Added {added_count} exercises so far...")
    
    db.session.commit()
    print(f"Completed: Added {added_count} new exercises from the dataset (skipped {skipped_count} existing exercises)")

def create_demo_user():
    """Create a demo user account."""
    demo_user = User.query.filter_by(email='demo@example.com').first()
    if not demo_user:
        demo_user = User(
            email='demo@example.com',
            name='Demo User',
            password_hash=generate_password_hash('password123')
        )
        db.session.add(demo_user)
        db.session.commit()
        print("Created demo user: demo@example.com / password123")
    else:
        print("Demo user already exists")
    
    return demo_user

def create_sample_workouts(user, num_workouts=20, force_recreate=False):
    """Create sample workouts for the demo user."""
    if not force_recreate and Workout.query.filter_by(user_id=user.id).count() > 0:
        print("User already has workouts, skipping sample workout creation")
        return
    
    # If force_recreate is True, remove existing workouts
    if force_recreate:
        existing_workouts = Workout.query.filter_by(user_id=user.id).all()
        for workout in existing_workouts:
            db.session.delete(workout)
        db.session.commit()
        print(f"Removed {len(existing_workouts)} existing workouts for demo user")
    
    exercises = Exercise.query.all()
    
    # Create workouts over the past few months
    for i in range(num_workouts):
        # Random date in the past 90 days
        days_ago = random.randint(0, 90)
        workout_date = datetime.now() - timedelta(days=days_ago)
        
        workout = Workout(
            user_id=user.id,
            date=workout_date,
            name=f"Workout on {workout_date.strftime('%B %d')}",
            completed=True
        )
        db.session.add(workout)
        db.session.flush()  # To get the workout ID
        
        # Add 3-5 exercises to each workout
        num_exercises = random.randint(3, 5)
        workout_exercises = random.sample(exercises, num_exercises)
        
        for exercise in workout_exercises:
            workout_exercise = WorkoutExercise(
                workout_id=workout.id,
                exercise_id=exercise.id
            )
            db.session.add(workout_exercise)
            
            # Add 3-4 sets for each exercise
            num_sets = random.randint(3, 4)
            sets_data = []
            
            for set_num in range(num_sets):
                weight = random.randint(10, 100)
                reps = random.randint(6, 12)
                sets_data.append({'weight': weight, 'reps': reps})
            
            workout_exercise.sets_data = sets_data
    
    db.session.commit()
    print(f"Created {num_workouts} sample workouts for {user.name}")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Seed with sample data
        seed_exercises()
        import_exercise_dataset()
        demo_user = create_demo_user()
        create_sample_workouts(demo_user, force_recreate=True)
        
        print("Database seeding completed successfully!")
