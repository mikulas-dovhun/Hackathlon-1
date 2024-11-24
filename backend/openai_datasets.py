from flask import Blueprint, request, jsonify
import pandas as pd
import os
from loguru import logger
import openai

# Set OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Path to the datasets directory
DATASETS_PATH = os.path.abspath('./datasets')

# Path to the Staty.csv file
STATY_FILE = os.path.join(DATASETS_PATH, 'Staty.csv')

# Create Blueprint
weatherquery_api = Blueprint('weatherquery_api', __name__)


def get_file_and_country_for_city(city):
    """
    Load the region file and country folder for a given city from Staty.csv.
    """
    logger.info(f"Looking for region and country for city: {city}")
    if not os.path.exists(STATY_FILE):
        logger.error(f"File {STATY_FILE} does not exist!")
        return None, None, f"CSV file with city, region, and country data '{STATY_FILE}' does not exist."

    try:
        # Read the Staty.csv file
        df = pd.read_csv(STATY_FILE, delimiter=';', encoding='utf-8')
        city_row = df[df['City'].str.lower() == city.lower()]  # Case-insensitive match
        if city_row.empty:
            return None, None, f"City '{city}' not found in Staty.csv."
        region_file = city_row['Region'].iloc[0] + ".csv"
        country_folder = city_row['Country'].iloc[0]
        return region_file, country_folder, None
    except Exception as e:
        logger.error(f"Error processing file '{STATY_FILE}': {e}")
        return None, None, f"Error reading data from '{STATY_FILE}': {e}"


def get_city_data(city, region_file, country_folder):
    """
    Load data for a specific city from the appropriate region CSV file.
    """
    csv_path = os.path.join(DATASETS_PATH, country_folder, region_file)
    if not os.path.exists(csv_path):
        return None, f"CSV file '{region_file}' does not exist."

    try:
        df = pd.read_csv(csv_path, delimiter=';', encoding='latin1')
        city_data = df[df['City'].str.lower() == city.lower()]
        if city_data.empty:
            return None, f"No data found for city '{city}' in file '{region_file}'."
        return city_data, None
    except Exception as e:
        logger.error(f"Error processing file '{csv_path}': {e}")
        return None, f"Error reading data from '{csv_path}': {e}"


@weatherquery_api.route('/weatherquery', methods=['POST'])
def weather_query():
    """
    Handle user query and fetch data from the relevant CSV file, with support for comparisons.
    """
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    try:
        # Use OpenAI to extract cities or regions involved
        openai_prompt = f"Extract the cities or regions mentioned in the following question: '{user_message}'. Provide a list of names separated by commas."
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts city or region names from text."},
                {"role": "user", "content": openai_prompt}
            ],
            max_tokens=100,
            temperature=0
        )
        locations = response['choices'][0]['message']['content'].strip().split(',')

        if not locations or len(locations) == 0:
            return jsonify({"response": "Could not identify locations from the question.", "available": False})

        logger.info(f"Identified locations: {locations}")

        # Process data for each location
        comparison_results = {}
        for location in locations:
            location = location.strip()
            region_file, country_folder, error = get_file_and_country_for_city(location)
            if error:
                comparison_results[location] = {"error": error}
                continue

            city_data, error = get_city_data(location, region_file, country_folder)
            if error:
                comparison_results[location] = {"error": error}
                continue

            # Process city data (e.g., min, max, mean temperatures)
            temp_min = city_data['Temperature (°C)'].min()
            temp_max = city_data['Temperature (°C)'].max()
            temp_mean = city_data['Temperature (°C)'].mean()

            comparison_results[location] = {
                "min_temp": temp_min,
                "max_temp": temp_max,
                "mean_temp": temp_mean
            }

        # Prepare results for comparison
        if len(comparison_results) > 1:
            comparison_summary = f"Comparison results:\n"
            for location, data in comparison_results.items():
                if "error" in data:
                    comparison_summary += f"{location}: {data['error']}\n"
                else:
                    comparison_summary += f"{location}: Min Temp = {data['min_temp']}°C, Max Temp = {data['max_temp']}°C, Avg Temp = {data['mean_temp']}°C\n"
        else:
            comparison_summary = f"Data for {locations[0]}: {comparison_results[locations[0]]}"

        return jsonify({"response": comparison_summary, "available": True})

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({"error": "An error occurred while processing the request.", "details": str(e)}), 500
