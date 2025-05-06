#!/bin/bash

# Update script for Groei-app on PythonAnywhere

# Navigate to the project directory
cd /home/MBron/Groei-app

# Pull the latest changes from GitHub
git pull origin main

# Install any new dependencies
source venv/bin/activate
pip install -r requirements.txt

# Perform database migrations if needed
# Uncomment the lines below if you are using Flask-Migrate
# flask db migrate -m "Auto migration from update script"
# flask db upgrade

# Reload the web app by touching the WSGI file
touch /var/www/MBron_pythonanywhere_com_wsgi.py

echo "Groei-app successfully updated and reloaded!"
