from flask_login import UserMixin
from gym_app import db
from datetime import datetime
import json

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    workouts = db.relationship('Workout', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.name}>'

class Exercise(db.Model):
    __tablename__ = 'exercises'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    muscle_group = db.Column(db.String(50), nullable=False)
    secondary_muscle_groups = db.Column(db.String(200), nullable=True)  # Comma-separated list
    equipment = db.Column(db.String(100), nullable=True)
    difficulty = db.Column(db.String(20), nullable=True)  # beginner, intermediate, advanced
    description = db.Column(db.Text, nullable=True)
    instructions = db.Column(db.Text, nullable=True)
    tips = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(200), nullable=True)
    video_url = db.Column(db.String(200), nullable=True)
    is_compound = db.Column(db.Boolean, default=False)  # Is it a compound movement?
    calories_per_hour = db.Column(db.Integer, nullable=True)  # Estimated calories burned per hour
    
    workout_exercises = db.relationship('WorkoutExercise', backref='exercise', lazy=True)
    
    def __repr__(self):
        return f'<Exercise {self.name}>'
        
    @property
    def muscle_groups_list(self):
        """Return secondary muscle groups as a list."""
        if not self.secondary_muscle_groups:
            return []
        return [mg.strip() for mg in self.secondary_muscle_groups.split(',')]

class Workout(db.Model):
    __tablename__ = 'workouts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    name = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    
    exercises = db.relationship('WorkoutExercise', backref='workout', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Workout {self.id} on {self.date}>'

class WorkoutExercise(db.Model):
    __tablename__ = 'workout_exercises'
    
    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workouts.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
    _sets_data = db.Column('sets_data', db.Text, default='[]')
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    @property
    def sets_data(self):
        return json.loads(self._sets_data)
    
    @sets_data.setter
    def sets_data(self, value):
        self._sets_data = json.dumps(value)
    
    def __repr__(self):
        return f'<WorkoutExercise {self.id}>'
    
    @property
    def total_weight(self):
        """Calculate total weight lifted for this exercise in this workout."""
        sets = self.sets_data
        return sum(s['weight'] * s['reps'] for s in sets)
    
    @property
    def last_set_weight(self):
        """Get the weight from the last set."""
        sets = self.sets_data
        if sets:
            return sets[-1]['weight']
        return 0
        
    @property
    def last_set_reps(self):
        """Get the reps from the last set."""
        sets = self.sets_data
        if sets:
            return sets[-1]['reps']
        return 8  # Default to 8 reps if no previous set
