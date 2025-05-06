from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()

# User loader function
@login_manager.user_loader
def load_user(user_id):
    from gym_app.models import User
    return User.query.get(int(user_id))

def create_app():
    # Initialize Flask app
    app = Flask(__name__, 
                static_folder='../static',  # Use the static folder in the root directory
                static_url_path='/static')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-dev-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///gym_app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Add context processor to make 'now' available in all templates
    @app.context_processor
    def inject_now():
        return {'now': datetime.now()}
    
    with app.app_context():
        # Import and register blueprints
        from gym_app.auth.routes import auth_bp
        from gym_app.workout.routes import workout_bp
        from gym_app.main.routes import main_bp
        
        app.register_blueprint(auth_bp)
        app.register_blueprint(workout_bp)
        app.register_blueprint(main_bp)
        
        # Create database tables
        db.create_all()
        
    return app