from flask import Blueprint, request, jsonify
import pandas as pd
import os
from loguru import logger
import openai
import matplotlib
matplotlib.use('Agg')  # Use a thread-safe backend
import matplotlib.pyplot as plt

# Set OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Path to the datasets directory
DATASETS_PATH = os.path.abspath('./datasets')

# Path to the Staty.csv file
STATY_FILE = os.path.join(DATASETS_PATH, 'Staty.csv')

# Create Blueprint
weatherquery_api = Blueprint('weatherquery_api', __name__)

# Helper function to set white elements in graphs
def set_white_theme(ax):
    """
    Customize the plot to have white grid, ticks, spines, and outlines.
    """
    ax.spines['top'].set_color('white')
    ax.spines['right'].set_color('white')
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    ax.yaxis.label.set_color('white')
    ax.xaxis.label.set_color('white')
    ax.title.set_color('white')
    ax.grid(color='white', linestyle='--', linewidth=0.5)  # Dashed white grid lines

# Helper function to save plots with transparent background
def save_plot_to_file(filename):
    """
    Save the current matplotlib plot to a file with a transparent background and release resources.
    """
    output_directory = './generated_graphs'
    os.makedirs(output_directory, exist_ok=True)
    file_path = os.path.join(output_directory, filename)
    try:
        plt.savefig(file_path, format='png', bbox_inches='tight', transparent=True)
    except Exception as e:
        logger.error(f"Error saving plot {filename}: {e}")
    finally:
        plt.close('all')  # Ensure all figures are closed
    return file_path

# Fetch region file and country folder for a city
def get_file_and_country_for_city(city):
    logger.info(f"Looking for region and country for city: {city}")
    if not os.path.exists(STATY_FILE):
        logger.error(f"File {STATY_FILE} does not exist!")
        return None, None, f"CSV file with city, region, and country data '{STATY_FILE}' does not exist."

    try:
        df = pd.read_csv(STATY_FILE, delimiter=';', encoding='utf-8')
        city_row = df[df['City'].str.lower() == city.lower()]
        if city_row.empty:
            return None, None, f"City '{city}' not found in Staty.csv."

        region_file = city_row['Region'].iloc[0] + ".csv"
        country_folder = city_row['Country'].iloc[0]
        return region_file, country_folder, None
    except Exception as e:
        logger.error(f"Error processing file '{STATY_FILE}': {e}")
        return None, None, f"Error reading data from '{STATY_FILE}': {e}"

# Fetch city data from region file
def get_city_data(city, region_file, country_folder):
    csv_path = os.path.join(DATASETS_PATH, country_folder, region_file)
    logger.info(f"Looking for file: {csv_path}")

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

# Main weather query endpoint
@weatherquery_api.route('/weatherquery', methods=['POST'])
def weather_query():
    """
    Handle user query, fetch data from the relevant CSV file, process data, and generate graphs.
    """
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    try:
        # Extract city name using OpenAI
        openai_prompt = f"Extract the city name from the following question: '{user_message}'. Please respond only with the city name."
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts city names from text."},
                {"role": "user", "content": openai_prompt}
            ],
            max_tokens=50,
            temperature=0
        )
        city = response['choices'][0]['message']['content'].strip()

        if not city:
            return jsonify({"response": "Could not identify the city from the question.", "available": False})

        logger.info(f"Identified city: {city}")

        # Fetch the region file and country folder
        region_file, country_folder, error = get_file_and_country_for_city(city)
        if error:
            return jsonify({"response": error, "available": False})

        # Fetch the city data
        city_data, error = get_city_data(city, region_file, country_folder)
        if error:
            return jsonify({"response": error, "available": False})

        # Prepare the data
        city_data['Date'] = pd.to_datetime(city_data['Date'], format='%d.%m.%Y')
        city_data.rename(columns={'Temperature (�C)': 'Temperature (°C)'}, inplace=True)

        required_columns = ['Temperature (°C)', 'Humidity (%)', 'Wind Direction', 'Date']
        missing_columns = [col for col in required_columns if col not in city_data.columns]

        if missing_columns:
            return jsonify({
                "response": f"The dataset is missing required columns: {', '.join(missing_columns)}.",
                "available": False
            })

        filtered_data = city_data.tail(28)  # Last 4 weeks
        if filtered_data.empty:
            return jsonify({"response": f"No recent data found for {city}.", "available": False})

        # Generate graphs
        graph_images = {}

        # 1. Temperature Trend
        plt.figure(figsize=(10, 6))
        ax = plt.gca()
        plt.plot(filtered_data['Date'], filtered_data['Temperature (°C)'], marker='o', color='blue', linewidth=2)
        plt.title(f'Temperature Trend in {city} (Last 4 Weeks)')
        plt.xlabel('Date')
        plt.ylabel('Temperature (°C)')
        set_white_theme(ax)
        graph_images['temperature_trend'] = save_plot_to_file(f"{city}_temperature_trend.png")

        # 2. Humidity Trend
        plt.figure(figsize=(10, 6))
        ax = plt.gca()
        plt.plot(filtered_data['Date'], filtered_data['Humidity (%)'], marker='o', color='orange', linewidth=2)
        plt.title(f'Humidity Trend in {city} (Last 4 Weeks)')
        plt.xlabel('Date')
        plt.ylabel('Humidity (%)')
        set_white_theme(ax)
        graph_images['humidity_trend'] = save_plot_to_file(f"{city}_humidity_trend.png")

        # 3. Wind Direction Pie Chart
        plt.figure(figsize=(8, 8))
        wind_directions = filtered_data['Wind Direction'].value_counts()
        plt.pie(wind_directions, labels=wind_directions.index, autopct='%1.1f%%', startangle=140,
                textprops={'color': 'white'})
        plt.title(f'Wind Directions in {city}', color='white')
        graph_images['wind_directions'] = save_plot_to_file(f"{city}_wind_directions.png")

        # 4. Pressure Trend (Optional)
        if 'Pressure (hPa)' in filtered_data.columns:
            plt.figure(figsize=(10, 6))
            ax = plt.gca()
            plt.plot(filtered_data['Date'], filtered_data['Pressure (hPa)'], marker='o', color='green', linewidth=2)
            plt.title(f'Pressure Trend in {city} (Last 4 Weeks)')
            plt.xlabel('Date')
            plt.ylabel('Pressure (hPa)')
            set_white_theme(ax)
            graph_images['pressure_trend'] = save_plot_to_file(f"{city}_pressure_trend.png")

        # Send data and question to OpenAI
        city_data_json = city_data.to_dict(orient='records')
        data_prompt = f"Here is the weather data for {city}: {city_data_json}\n\n"
        full_prompt = f"{data_prompt}Based on the above data, answer the following question: '{user_message}'."
        final_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a weather assistant who answers based on provided data."},
                {"role": "user", "content": full_prompt}
            ],
            max_tokens=200,
            temperature=0.7
        )
        answer = final_response['choices'][0]['message']['content'].strip()

        # Return response
        return jsonify({
            "response": answer,
            "graphs": graph_images,
            "available": True
        })

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({"error": "An error occurred while processing the request.", "details": str(e)}), 500
