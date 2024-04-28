#!/bin/bash

# Define the log file
LOGFILE="/home/b2b_user/b2b/deploy_logfile.log"

# Function to add timestamps to log entries
log() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$LOGFILE"

  # If the last command had a non-zero exit code, mark as error
  if [[ $? -ne 0 ]]; then
    echo "  [ERROR]" | tee -a "$LOGFILE"
  fi
}

# Navigate to your project directory on the server
cd /home/b2b_user/b2b || { log "Failed to navigate to project directory"; exit 1; }

# activate the virtual environment
source env/bin/activate 

# Pull the latest changes from your GitHub repository
git pull origin main || { log "Failed to pull from GitHub"; exit 1; }

# Install any required dependencies
pip install -r requirements.txt -v || { log "Failed to install dependencies. See below for detailed output:" && pip install -r requirements.txt -v; exit 1; }

# If you have Tailwind CSS or similar build processes:
npx tailwindcss -i ./static/dist/input.css -o ./static/dist/output.css --watch || { log "Failed to build Tailwind CSS"; exit 1; }

# Collect static files for Django
python manage.py collectstatic --noinput || { log "Failed to collect static files"; exit 1; }

# Apply database migrations 
python manage.py migrate || { log "Failed to apply database migrations"; exit 1; }

# Restart Gunicorn (assuming systemd)
sudo systemctl restart gunicorn || { log "Failed to restart Gunicorn"; exit 1; }

# Signal Nginx to reload configuration (optional, but recommended)
sudo nginx -s reload || { log "Failed to reload Nginx configuration"; exit 1; }

# Deactivate virtual environment
deactivate
