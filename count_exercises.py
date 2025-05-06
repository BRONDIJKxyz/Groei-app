from gym_app import create_app, db
from gym_app.models import Exercise

app = create_app()

with app.app_context():
    count = Exercise.query.count()
    print(f'Total exercises in database: {count}')
    
    # Print a few sample exercises
    sample = Exercise.query.limit(5).all()
    print("\nSample exercises:")
    for ex in sample:
        print(f"- {ex.name} ({ex.muscle_group})")
