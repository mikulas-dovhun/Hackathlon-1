from flask import Blueprint, request, jsonify
import requests
import os
from dotenv import load_dotenv  # Import dotenv

load_dotenv('boot.txt')

search_api = Blueprint('search_api', __name__)

# Load API keys from boot.txt (or .env)
API_KEY = os.getenv('WEATHER_API_KEY')

@search_api.route('', methods=['GET'])
def search_city():
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "Zadajte hľadaný výraz"}), 400

    url = f"http://api.openweathermap.org/geo/1.0/direct"
    params = {"q": query, "appid": API_KEY}

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if not data:
            return jsonify({"error": "Mesto nenájdené"}), 404

        cities = [
            {"name": item["name"], "country": item["country"], "lat": item["lat"], "lon": item["lon"]}
            for item in data
        ]

        return jsonify(cities)

    except Exception as e:
        return jsonify({"error": "Chyba pri pripojení k OpenWeather API"}), 500
