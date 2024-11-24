from flask import Blueprint, request, jsonify
import openai
import requests
from loguru import logger
import os

# Function to load keys from the boot.txt file
def load_keys_from_txt(file_path):
    """Read API keys from a .txt file and set them as environment variables."""
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line and '=' in line:  # Ensure it's not an empty line and contains '='
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()  # Set as an environment variable

# Load keys from the boot.txt file
load_keys_from_txt('boot.txt')

# Fetch API keys from environment variables
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Set the OpenAI API key
openai.api_key = OPENAI_API_KEY

# Define Blueprint
openai_api = Blueprint('openai_api', __name__)

@openai_api.route('/chat', methods=['POST'])
def chat_with_weather():
    """Process the user's message and fetch weather data from OpenWeather API."""
    logger.info('Received request on /chat')
    user_message = request.json.get('message')

    if not user_message:
        logger.error("Missing message!")
        return jsonify({"error": "Message is required"}), 400

    try:
        # Send the message to OpenAI to extract the city name
        openai_prompt = f"Extract the name of the city from the following sentence: '{user_message}'. Please respond only with the city name."

        # Correct OpenAI API call for chat model
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant who can extract city names from user messages."},
                {"role": "user", "content": openai_prompt}
            ],
            max_tokens=10,
            temperature=0
        )

        # Extract city name from OpenAI response
        city = response.choices[0].message['content'].strip()

        # Check if city is empty or invalid
        if not city or len(city.split()) > 3:  # Prevents long multi-word responses
            logger.error(f"City extraction failed or is invalid: '{city}'")
            return jsonify({"error": "City not recognized in the message"}), 400

        logger.info(f"Extracted city: {city}")

        # Fetch weather data from OpenWeather API
        weather_url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {"q": city, "appid": WEATHER_API_KEY, "units": "metric"}

        weather_response = requests.get(weather_url, params=params)
        weather_data = weather_response.json()

        if weather_response.status_code != 200:
            logger.error(f"Error from OpenWeather API: {weather_data.get('message', 'Unknown error')}")
            return jsonify({"error": weather_data.get("message", "Error fetching weather data")}), weather_response.status_code

        # Standardized weather information output
        standardized_weather_info = {
            "city": city,
            "temperature": weather_data['main']['temp'],
            "feels_like": weather_data['main']['feels_like'],
            "humidity": weather_data['main']['humidity'],
            "wind_speed": weather_data['wind']['speed'],
            "description": weather_data['weather'][0]['description'].capitalize(),
        }

        # Prepare the final prompt for OpenAI with weather details
        openai_prompt = (
            f"User asked about the weather in {city}. "
            f"Here is the weather data: "
            f"Temperature: {standardized_weather_info['temperature']}°C, "
            f"Feels like: {standardized_weather_info['feels_like']}°C, "
            f"Humidity: {standardized_weather_info['humidity']}%, "
            f"Wind speed: {standardized_weather_info['wind_speed']} m/s, "
            f"Description: {standardized_weather_info['description']}.\n\n"
            f"User's message: {user_message}"
        )

        # Send the weather data and user message to OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant who can provide weather information."},
                {"role": "user", "content": openai_prompt}
            ],
            max_tokens=200,
            temperature=0.7
        )

        # Get response from OpenAI
        ai_response = response['choices'][0]['message']['content'].strip()
        logger.info(f"OpenAI response: {ai_response}")

        # Include standardized weather info in the response
        return jsonify({"response": ai_response, "weather": standardized_weather_info})

    except requests.exceptions.RequestException as e:
        logger.error(f"Connection error with OpenWeather API: {str(e)}")
        return jsonify({"error": "Error fetching weather data"}), 500
    except openai.error.OpenAIError as e:
        logger.error(f"OpenAI API error: {str(e)}")
        return jsonify({"error": "OpenAI API error", "details": str(e)}), 500
    except Exception as e:
        logger.error(f"General error: {str(e)}")
        return jsonify({"error": "An error occurred", "details": str(e)}), 500
