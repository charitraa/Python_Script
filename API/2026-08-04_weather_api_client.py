"""
This script acts as a simple weather API client.
It fetches current weather data for a specified city using the OpenWeatherMap API.
Users need to obtain a free API key from OpenWeatherMap (https://openweathermap.org/api)
and replace the 'YOUR_API_KEY' placeholder.

The script takes a city name as input and outputs the current temperature,
weather description, humidity, and wind speed for that city.
It includes basic error handling for API issues and network problems.
"""

import urllib.request # For making HTTP requests
import urllib.parse   # For encoding URL parameters
import json           # For working with JSON data

# --- Configuration ---
# IMPORTANT: Replace 'YOUR_API_KEY' with your actual OpenWeatherMap API key.
# You can get one for free by signing up at https://openweathermap.org/api
API_KEY = "YOUR_API_KEY"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"

def get_weather(city_name: str) -> dict | None:
    """
    Fetches current weather data for a given city from the OpenWeatherMap API.

    Args:
        city_name: The name of the city to get weather for.

    Returns:
        A dictionary containing parsed weather data if successful, None otherwise.
    """
    if API_KEY == "YOUR_API_KEY":
        print("Error: Please replace 'YOUR_API_KEY' in the script with your actual OpenWeatherMap API key.")
        print("You can get one for free from https://openweathermap.org/api")
        return None

    # Encode the city name for use in a URL (e.g., "New York" becomes "New%20York")
    encoded_city_name = urllib.parse.quote(city_name)
    
    # Construct the full API URL with city, API key, and units (metric for Celsius)
    full_url = f"{BASE_URL}q={encoded_city_name}&appid={API_KEY}&units=metric"

    try:
        # Make the HTTP request to the OpenWeatherMap API
        # 'with' statement ensures the connection is properly closed
        with urllib.request.urlopen(full_url) as response:
            # Check if the HTTP status code indicates an error (e.g., 404 Not Found)
            if response.getcode() != 200:
                print(f"Error fetching data: HTTP Status {response.getcode()} for '{city_name}'.")
                return None

            # Read the response body, decode it from bytes to a string, and parse as JSON
            data = response.read().decode('utf-8')
            weather_data = json.loads(data)

            # OpenWeatherMap also returns specific error codes within the JSON
            if weather_data.get("cod") == "404":
                print(f"Error: City '{city_name}' not found.")
                return None
            elif weather_data.get("cod") != 200: # General API error
                 print(f"Error from API: {weather_data.get('message', 'Unknown API error')}")
                 return None

            return weather_data

    except urllib.error.URLError as e:
        # Handles network-related errors (e.g., no internet connection, invalid URL, DNS issues)
        print(f"Network error: Could not connect to the weather service. {e}")
        return None
    except json.JSONDecodeError:
        # Handles cases where the response is not valid JSON
        print("Error: Could not parse weather data (invalid JSON response from API).")
        return None
    except Exception as e:
        # Catch any other unexpected errors during the process
        print(f"An unexpected error occurred: {e}")
        return None

def display_weather(weather_data: dict, city_name: str):
    """
    Prints formatted weather information to the console.

    Args:
        weather_data: A dictionary containing parsed weather data.
        city_name: The name of the city (for display purposes).
    """
    if not weather_data:
        print(f"No weather data available to display for {city_name}.")
        return

    try:
        # Extract relevant information from the nested dictionary structure
        # Use .get() with a default empty dictionary to prevent KeyError if a key is missing
        main_info = weather_data.get("main", {})
        weather_description_list = weather_data.get("weather", [])
        wind_info = weather_data.get("wind", {})

        temperature = main_info.get("temp")
        feels_like = main_info.get("feels_like")
        humidity = main_info.get("humidity")
        
        # Get the first weather description if available, otherwise default to "N/A"
        description = (weather_description_list[0].get("description").capitalize()
                       if weather_description_list else "N/A")
        
        # Wind speed is in meters per second (m/s) for metric units
        wind_speed = wind_info.get("speed") 

        # Print the information in a user-friendly format
        print(f"\n--- Current Weather in {city_name.title()} ---")
        print(f"Temperature: {temperature}°C (feels like {feels_like}°C)")
        print(f"Description: {description}")
        print(f"Humidity:    {humidity}%")
        print(f"Wind Speed:  {wind_speed} m/s")
        print("--------------------------------------")

    except KeyError as e:
        # Catch if a critical key is missing during extraction
        print(f"Error: Missing expected data in weather response: {e}")
    except IndexError:
        # Catch if weather_description_list is empty and we try to access [0]
        print("Error: No weather description found in API response.")
    except Exception as e:
        # Catch any other unexpected errors during display
        print(f"An error occurred while displaying weather data: {e}")


if __name__ == "__main__":
    # --- Example Usage ---

    # Prompt the user to enter a city name
    user_city = input("Enter a city name to get its current weather: ")

    # Call the function to fetch weather data for the specified city
    current_weather = get_weather(user_city)

    # If weather data was successfully fetched (not None), display it
    if current_weather:
        display_weather(current_weather, user_city)
    else:
        # This message will be shown if get_weather returned None,
        # indicating an error already printed by get_weather.
        print("Failed to retrieve weather data. Please review messages above.")

    # --- You can uncomment the following section to test with predefined cities ---
    # print("\n--- Testing with pre-defined cities ---")
    #
    # cities_to_test = ["London", "Paris", "Tokyo", "InvalidCityNameXYZ", "New York"]
    # for city in cities_to_test:
    #     print(f"\nAttempting to get weather for {city}...")
    #     weather_data_test = get_weather(city)
    #     display_weather(weather_data_test, city)
