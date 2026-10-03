# To install the required third-party library, run:
# pip install requests

"""
CLI Weather Dashboard Script

This script fetches current weather information for a specified city using the OpenWeatherMap API
and displays it in a simple, human-readable format in the command line.

To use this script:
1. You need an API key from OpenWeatherMap.
   - Go to https://openweathermap.org/api
   - Sign up for a free account.
   - Once logged in, go to your API keys section (usually under your profile settings)
     and generate a new key if you don't have one.
2. Replace 'YOUR_API_KEY_HERE' in this script with your actual OpenWeatherMap API key.
3. Run the script from your terminal, optionally providing a city name as an argument.

Example Usage:
    python weather_dashboard.py
    python weather_dashboard.py "New York"
    python weather_dashboard.py Paris
"""

import requests
import json
import sys

# --- Configuration ---
# Replace 'YOUR_API_KEY_HERE' with your actual OpenWeatherMap API key.
# Get one for free at https://openweathermap.org/api
API_KEY = "YOUR_API_KEY_HERE"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

def get_weather_data(city_name, api_key):
    """
    Fetches weather data for a given city from the OpenWeatherMap API.

    Args:
        city_name (str): The name of the city to get weather for.
        api_key (str): Your OpenWeatherMap API key.

    Returns:
        dict: A dictionary containing parsed weather data, or None if an error occurs.
    """
    params = {
        'q': city_name,
        'appid': api_key,
        'units': 'metric'  # Use 'imperial' for Fahrenheit, 'metric' for Celsius
    }

    try:
        # Make the GET request to the OpenWeatherMap API
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)

        # Parse the JSON response
        weather_data = response.json()
        return weather_data

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP errors
        if response.status_code == 401:
            print(f"Error: Invalid API Key. Please check your '{API_KEY}' in the script.")
        elif response.status_code == 404:
            print(f"Error: City '{city_name}' not found. Please check the spelling.")
        else:
            print(f"HTTP Error: {e}")
        return None
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the internet. Please check your connection.")
        return None
    except requests.exceptions.Timeout:
        print("Error: Request timed out. The server took too long to respond.")
        return None
    except requests.exceptions.RequestException as e:
        # Catch all other requests-related errors
        print(f"An error occurred during the API request: {e}")
        return None
    except json.JSONDecodeError:
        print("Error: Could not decode JSON response from the API.")
        return None

def display_weather_dashboard(weather_data):
    """
    Prints a formatted weather dashboard to the console using the provided weather data.

    Args:
        weather_data (dict): A dictionary containing parsed weather information.
                             Expected keys: 'name', 'main' (temp, feels_like, humidity, pressure),
                             'weather' (description, icon), 'wind' (speed).
    """
    if not weather_data:
        print("No weather data to display.")
        return

    # Extract relevant information
    city = weather_data.get('name')
    main_weather = weather_data.get('main', {})
    current_temp = main_weather.get('temp')
    feels_like_temp = main_weather.get('feels_like')
    humidity = main_weather.get('humidity')
    pressure = main_weather.get('pressure')

    # 'weather' is a list of dictionaries, we usually take the first one
    weather_description = weather_data.get('weather', [{}])[0].get('description')
    
    wind_data = weather_data.get('wind', {})
    wind_speed = wind_data.get('speed') # Speed is in m/s if units='metric'

    # --- Print the Dashboard ---
    print("\n" + "="*40)
    print(f"{'Weather Dashboard':^40}")
    print("="*40)

    if city:
        print(f"City: {city}")
    if current_temp is not None:
        print(f"Temperature: {current_temp:.1f}°C")
    if feels_like_temp is not None:
        print(f"Feels Like: {feels_like_temp:.1f}°C")
    if weather_description:
        # Capitalize the first letter of the description for better readability
        print(f"Conditions: {weather_description.capitalize()}")
    if humidity is not None:
        print(f"Humidity: {humidity}%")
    if wind_speed is not None:
        # Convert m/s to km/h for easier understanding if metric
        wind_speed_kmh = wind_speed * 3.6
        print(f"Wind Speed: {wind_speed_kmh:.1f} km/h")
    if pressure is not None:
        print(f"Pressure: {pressure} hPa")

    print("="*40 + "\n")

def main():
    """
    Main function to run the CLI weather dashboard.
    It checks for a city argument or uses a default.
    """
    # Check if an API key has been set
    if API_KEY == "YOUR_API_KEY_HERE":
        print("Error: Please replace 'YOUR_API_KEY_HERE' with your actual OpenWeatherMap API key.")
        print("Refer to the script's docstring for instructions.")
        sys.exit(1) # Exit with an error code

    # Get city name from command line arguments or use a default
    if len(sys.argv) > 1:
        city_name = " ".join(sys.argv[1:]) # Allows for multi-word city names like "New York"
    else:
        city_name = "London" # Default city

    print(f"Fetching weather for: {city_name}...")
    weather_data = get_weather_data(city_name, API_KEY)
    if weather_data:
        display_weather_dashboard(weather_data)

if __name__ == "__main__":
    main()
