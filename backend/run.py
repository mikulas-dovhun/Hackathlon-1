from flask import Flask
from flask_cors import CORS
import os
import subprocess
import sys

def install_requirements():
    """
    Ensure all dependencies are installed before starting the app.
    """
    try:
        print("Checking and installing dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        sys.exit(1)

# Install requirements before starting
install_requirements()

from backend.weather import weather_api
from backend.forecast import forecast_api
from backend.search import search_api
from backend.favorites import favorites_api
from openai_routes import openai_api  # Import your openai API blueprint

# Inicializácia Flask aplikácie
app = Flask(__name__)
CORS(app)  # Povolenie CORS

# Registrácia Blueprintov
app.register_blueprint(weather_api, url_prefix='/api/weather')
app.register_blueprint(forecast_api, url_prefix='/api/forecast')
app.register_blueprint(search_api, url_prefix='/api/search')
app.register_blueprint(favorites_api, url_prefix='/api/favorites')
app.register_blueprint(openai_api, url_prefix='/api/openai')

if __name__ == '__main__':
    app.run(debug=True)



