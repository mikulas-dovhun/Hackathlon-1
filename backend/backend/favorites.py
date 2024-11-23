from flask import Blueprint, request, jsonify
import requests
import os
from dotenv import load_dotenv  # Import dotenv

load_dotenv('boot.txt')

favorites_api = Blueprint('favorites_api', __name__)
API_KEY = os.getenv('WEATHER_API_KEY')

@favorites_api.route('', methods=['GET'])
def get_favorites_weather():
    # Zoznam miest z query parametrov
    cities = request.args.getlist('cities')
    if not cities:
        return jsonify({"error": "Zadajte aspoň jedno mesto"}), 400

    results = []  # Zoznam výsledkov
    url = "http://api.openweathermap.org/data/2.5/weather"  # API pre aktuálne počasie

    # Iterácia cez mestá a získanie počasia pre každé z nich
    for city in cities:
        params = {"q": city, "appid": API_KEY, "units": "metric"}
        try:
            response = requests.get(url, params=params)
            data = response.json()

            if response.status_code == 200:  # Úspešná odpoveď
                results.append({
                    "city": data.get("name"),
                    "country": data["sys"].get("country"),
                    "temperature": data["main"]["temp"],
                    "description": data["weather"][0]["description"],
                    "icon": data["weather"][0]["icon"],
                    "wind_speed": data["wind"].get("speed"),
                    "humidity": data["main"].get("humidity"),
                })
            else:  # Chyba zo strany API
                results.append({
                    "city": city,
                    "error": data.get("message", "Neznáma chyba")
                })
        except Exception as e:  # Chyba pri pripojení alebo spracovaní
            results.append({
                "city": city,
                "error": "Chyba pri pripojení k OpenWeather API"
            })

    # Vrátenie zoznamu obľúbených miest s počasiami
    return jsonify({"favorites": results})
