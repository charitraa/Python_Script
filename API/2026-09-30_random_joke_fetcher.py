"""
This script fetches a random joke from a public API and displays it to the user.

It demonstrates how to make a simple HTTP GET request using Python's standard
library (`urllib.request`), parse JSON responses (`json`), and handle potential
network or API errors. This is a great starting point for understanding how
to interact with web services.
"""

import urllib.request
import urllib.error
import json
import sys

# Define the API endpoint for fetching a random joke.
# We're using the Official Joke API, which provides simple JSON responses
# with a 'setup' and 'punchline'.
JOKE_API_URL = "https://official-joke-api.appspot.com/random_joke"

def fetch_random_joke():
    """
    Fetches a random joke from the configured API endpoint.

    This function attempts to connect to the joke API, retrieve its response,
    and parse the JSON data to extract the joke's setup and punchline.
    It includes error handling for network issues, HTTP errors, and JSON
    parsing problems.

    Returns:
        tuple: A tuple containing (setup, punchline) of the joke if successful.
               Example: ("Why don't scientists trust atoms?", "Because they make up everything!")
        None: If an error occurs during the fetch or parsing process.
    """
    try:
        # Create a Request object. It's good practice to include a User-Agent header
        # when making web requests, as some APIs might block requests without one
        # or use it for logging/analytics.
        req = urllib.request.Request(JOKE_API_URL, headers={'User-Agent': 'Python Joke Fetcher Script'})

        # Open the URL and get the response.
        # The 'with' statement ensures the connection is properly closed even if errors occur.
        # This part might raise urllib.error.URLError (for network problems like no internet)
        # or urllib.error.HTTPError (for server issues like 404, 500).
        with urllib.request.urlopen(req) as response:
            # Read the entire response body. This will be in bytes.
            response_body = response.read()

            # Decode the bytes to a string using UTF-8 encoding, which is standard for JSON.
            json_string = response_body.decode('utf-8')

            # Parse the JSON string into a Python dictionary.
            # This might raise json.JSONDecodeError if the response isn't valid JSON.
            joke_data = json.loads(json_string)

            # Extract the 'setup' and 'punchline' from the parsed dictionary.
            # The API returns an object like: {"id": 123, "type": "general", "setup": "...", "punchline": "..."}
            setup = joke_data.get("setup")
            punchline = joke_data.get("punchline")

            # Check if both setup and punchline were successfully retrieved.
            if setup and punchline:
                return setup, punchline
            else:
                print("Error: Could not find 'setup' or 'punchline' in the API response.")
                print(f"Full API response (for debugging): {joke_data}")
                return None

    except urllib.error.URLError as e:
        # Handles network-related errors (e.g., no internet connection, DNS resolution failure,
        # API server is down or unreachable).
        print(f"Network error: Could not reach the joke API. Reason: {e.reason}")
        return None
    except urllib.error.HTTPError as e:
        # Handles HTTP errors (e.g., 404 Not Found, 500 Internal Server Error, 403 Forbidden).
        print(f"HTTP error: The joke API returned an error. Status: {e.code}, Reason: {e.reason}")
        return None
    except json.JSONDecodeError:
        # Handles cases where the API response is not valid JSON. This can happen if
        # the server returns an error message in plain text, or corrupted data.
        print("Error: Failed to decode JSON from the API response. The response might be malformed.")
        return None
    except Exception as e:
        # Catch any other unexpected errors that might occur during the process.
        print(f"An unexpected error occurred: {e}")
        return None

def main():
    """
    Main function to execute the random joke fetcher.
    It calls the fetch_random_joke function and prints the joke or an error message.
    """
    print("-----------------------------------")
    print("    Random Joke Fetcher (Python)   ")
    print("-----------------------------------")
    print("Fetching a random joke from the web...")

    joke = fetch_random_joke()

    if joke:
        setup, punchline = joke
        print("\n--- Your Random Joke ---")
        print(f"Setup: {setup}")
        print(f"Punchline: {punchline}")
        print("------------------------")
    else:
        print("\nCould not retrieve a joke at this time. Please check your internet")
        print("connection or try again later if the API is temporarily unavailable.")
        sys.exit(1) # Exit with an error code (1) to indicate failure.

if __name__ == "__main__":
    # This block ensures that the main() function is called only when the script
    # is executed directly (e.g., `python your_script_name.py`),
    # and not when it's imported as a module into another Python script.
    main()
