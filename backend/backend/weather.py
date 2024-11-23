from flask import Blueprint, request, jsonify
import requests
import os
from dotenv import load_dotenv  # Import dotenv

# Načítanie environmentálnych premenných z boot.txt
load_dotenv('boot.txt')

weather_api = Blueprint('weather_api', __name__)

API_KEY = os.getenv('WEATHER_API_KEY')

def check_extreme_weather(data):
    alerts = []
    temperature = data["main"]["temp"]
    wind_speed = data["wind"]["speed"]
    description = data["weather"][0]["description"].lower()

    if temperature < -10:
        alerts.append("Veľmi nízke teploty! Dbajte na vhodné oblečenie a zostaňte v teple.")
    elif temperature > 35:
        alerts.append("Veľmi vysoké teploty! Hydratujte sa a obmedzte fyzickú aktivitu.")

    if wind_speed > 20:
        alerts.append("Silný vietor! Dbajte na opatrnosť a vyhnite sa vonkajším aktivitám.")

    if "storm" in description:
        alerts.append("Búrka na obzore! Sledujte výstrahy a zostaňte v bezpečí.")

    if "snow" in description:
        alerts.append("Husté sneženie! Počítajte so sťaženými podmienkami na cestách.")

    if "rain" in description:
        alerts.append("Silný dážď! Dbajte na opatrnosť pri pohybe vonku.")

    return alerts

@weather_api.route('', methods=['GET'])
def get_weather():
    city = request.args.get('city')
    lat = request.args.get('lat')
    lon = request.args.get('lon')

    if not city and (not lat or not lon):
        return jsonify({"error": "Zadajte názov mesta alebo GPS súradnice"}), 400

    if city:
        params = {"q": city, "appid": API_KEY, "units": "metric"}
    else:
        params = {"lat": lat, "lon": lon, "appid": API_KEY, "units": "metric"}

    url = "http://api.openweathermap.org/data/2.5/weather"

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if response.status_code != 200:
            return jsonify({"error": data.get("message", "Chyba pri získavaní počasia")}), response.status_code

        alerts = check_extreme_weather(data)

        simplified_data = {
            "city": data.get("name"),
            "country": data["sys"].get("country"),
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"],
            "icon": data["weather"][0]["icon"],
            "wind_speed": data["wind"].get("speed"),
            "humidity": data["main"]["humidity"],
            "alerts": alerts
        }
        return jsonify(simplified_data)

    except Exception as e:
        return jsonify({"error": "Chyba pri pripojení k OpenWeather API"}), 500
