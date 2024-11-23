from flask import Blueprint, request, jsonify
import requests
import os
from dotenv import load_dotenv  # Import dotenv

load_dotenv('boot.txt')

forecast_api = Blueprint('forecast_api', __name__)
API_KEY = os.getenv('WEATHER_API_KEY')

@forecast_api.route('', methods=['GET'])
def get_forecast():
    city = request.args.get('city')
    if not city:
        return jsonify({"error": "Zadajte názov mesta"}), 400

    url = f"http://api.openweathermap.org/data/2.5/forecast"
    params = {"q": city, "appid": API_KEY, "units": "metric"}

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if response.status_code != 200:
            return jsonify({"error": data.get("message", "Chyba pri získavaní predpovede")}), response.status_code

        forecast_data = [
            {
                "description": item["weather"][0]["description"],
                "humidity": item["main"]["humidity"],
                "icon": item["weather"][0]["icon"],
                "temperature": item["main"]["temp"],
                "wind_speed": item["wind"]["speed"]
            }
            for index, item in enumerate(data["list"]) if index % 5 == 0  # Každý 5. záznam
        ]

        return jsonify({"city": data["city"]["name"], "forecast": forecast_data})

    except Exception as e:
        return jsonify({"error": "Chyba pri pripojení k OpenWeather API"}), 500
