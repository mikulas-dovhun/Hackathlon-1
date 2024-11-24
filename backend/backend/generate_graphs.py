from flask import Blueprint, request, jsonify
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
import os
from loguru import logger

# Define Blueprint
graphs_api = Blueprint('graphs_api', __name__)

# Path to the datasets directory
DATASETS_PATH = os.path.abspath('./datasets')


def save_plot_to_file(filename):
    """
    Save the current matplotlib plot to a file with a transparent background.
    """
    file_path = os.path.join('./generated_graphs', filename)
    plt.savefig(file_path, format='png', bbox_inches='tight', transparent=True)
    plt.close()
    return file_path


def get_file_and_country_for_city(city):
    """
    Load the region file and country folder for a given city from Staty.csv.
    """
    staty_file = os.path.join(DATASETS_PATH, 'Staty.csv')
    if not os.path.exists(staty_file):
        logger.error(f"Staty.csv file does not exist in {DATASETS_PATH}")
        return None, None, f"Staty.csv file does not exist."

    try:
        # Read the Staty.csv file
        df = pd.read_csv(staty_file, delimiter=';', encoding='utf-8')
        city_row = df[df['City'].str.lower() == city.lower()]  # Case-insensitive match
        if city_row.empty:
            return None, None, f"City '{city}' not found in Staty.csv."
        region_file = city_row['Region'].iloc[0] + ".csv"
        country_folder = city_row['Country'].iloc[0]
        return region_file, country_folder, None
    except Exception as e:
        logger.error(f"Error processing Staty.csv: {e}")
        return None, None, f"Error reading data from Staty.csv: {e}"


def get_city_data(city, region_file, country_folder):
    """
    Load data for a specific city from the appropriate region CSV file.
    """
    csv_path = os.path.join(DATASETS_PATH, country_folder, region_file)
    if not os.path.exists(csv_path):
        return None, f"CSV file '{region_file}' does not exist in folder '{country_folder}'."

    try:
        df = pd.read_csv(csv_path, delimiter=';', encoding='latin1')
        city_data = df[df['City'].str.lower() == city.lower()]
        if city_data.empty:
            return None, f"No data found for city '{city}' in file '{region_file}'."
        return city_data, None
    except Exception as e:
        logger.error(f"Error processing file '{csv_path}': {e}")
        return None, f"Error reading data from '{csv_path}': {e}"


@graphs_api.route('/generate_graphs', methods=['POST'])
def generate_graphs():
    """
    Generate graphs for a specific city using the last 4 weeks of data, clean outliers, and return them.
    """
    try:
        # Parse the request
        data = request.json
        city = data.get('city')

        if not city:
            return jsonify({"error": "City is required"}), 400

        # Find region and country
        region_file, country_folder, error = get_file_and_country_for_city(city)
        if error:
            return jsonify({"error": error}), 400

        # Load city data
        city_data, error = get_city_data(city, region_file, country_folder)
        if error:
            return jsonify({"error": error}), 400

        # Ensure Date column is in datetime format and clean data
        city_data['Date'] = pd.to_datetime(city_data['Date'], format='%d.%m.%Y')

        # Rename columns to fix encoding issue
        city_data.rename(columns=lambda x: x.strip(), inplace=True)
        city_data.rename(columns={'Temperature (�C)': 'Temperature (°C)'}, inplace=True)

        # Remove outliers in temperature
        city_data = city_data[(city_data['Temperature (°C)'] >= -50) & (city_data['Temperature (°C)'] <= 50)]

        # Determine the last 4 weeks of data
        latest_date = city_data['Date'].max()
        four_weeks_ago = latest_date - pd.Timedelta(weeks=4)
        filtered_data = city_data[city_data['Date'] >= four_weeks_ago]

        if filtered_data.empty:
            return jsonify({"error": f"No valid data found for {city} in the last 4 weeks."}), 400

        # Ensure output directory exists
        output_directory = './generated_graphs'
        os.makedirs(output_directory, exist_ok=True)

        # Initialize graph storage
        graph_images = {}

        # 1. Temperature Trend Graph
        plt.figure(figsize=(10, 6))
        plt.plot(filtered_data['Date'], filtered_data['Temperature (°C)'], marker='o', label='Temperature', color='blue')
        plt.title(f'Temperature Trend in {city} (Last 4 Weeks)')
        plt.xlabel('Date')
        plt.ylabel('Temperature (°C)')
        plt.grid()
        plt.tight_layout()
        graph_images['temperature_trend'] = save_plot_to_file(f"{city}_temperature_trend.png")

        # 2. Histogram of Temperatures
        plt.figure(figsize=(10, 6))
        plt.hist(filtered_data['Temperature (°C)'], bins=15, color='green', edgecolor='black')
        plt.title(f'Temperature Distribution in {city} (Last 4 Weeks)')
        plt.xlabel('Temperature (°C)')
        plt.ylabel('Frequency')
        plt.grid()
        plt.tight_layout()
        graph_images['temperature_histogram'] = save_plot_to_file(f"{city}_temperature_histogram.png")

        # 3. Daily Humidity Trend
        plt.figure(figsize=(10, 6))
        plt.plot(filtered_data['Date'], filtered_data['Humidity (%)'], marker='o', color='orange', label='Humidity')
        plt.title(f'Daily Humidity in {city} (Last 4 Weeks)')
        plt.xlabel('Date')
        plt.ylabel('Humidity (%)')
        plt.grid()
        plt.tight_layout()
        graph_images['humidity_trend'] = save_plot_to_file(f"{city}_humidity_trend.png")

        # 4. Wind Direction Pie Chart
        plt.figure(figsize=(8, 8))
        wind_directions = filtered_data['Wind Direction'].value_counts()
        plt.pie(wind_directions, labels=wind_directions.index, autopct='%1.1f%%', startangle=140)
        plt.title(f'Wind Directions in {city}')
        plt.tight_layout()
        graph_images['wind_directions'] = save_plot_to_file(f"{city}_wind_directions.png")

        return jsonify({"graphs": graph_images})

    except Exception as e:
        logger.error(f"Error generating graphs: {str(e)}")
        return jsonify({"error": "An error occurred while generating graphs.", "details": str(e)}), 500
