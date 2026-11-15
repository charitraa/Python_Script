"""
This script fetches and displays information about a movie using the OMDb API.

Users need to obtain a free API key from the OMDb website (www.omdbapi.com)
and enter it when prompted. Without a valid API key, the script will not
be able to fetch movie data.

The script is beginner-friendly, fully self-contained, and uses only Python's
standard library modules (urllib.request for HTTP requests and json for
parsing the API response).
"""

import urllib.request
import urllib.parse
import json
import sys

def fetch_movie_info(title: str, api_key: str) -> dict:
    """
    Fetches movie information from the OMDb API for a given title.

    Args:
        title (str): The title of the movie to search for.
        api_key (str): Your OMDb API key.

    Returns:
        dict: A dictionary containing movie information if found, or an
              empty dictionary if the movie is not found or an error occurs.
    """
    if not api_key:
        print("Error: OMDb API key is missing. Please obtain one from www.omdbapi.com.", file=sys.stderr)
        return {}

    # Encode the title for URL to handle spaces and special characters correctly
    encoded_title = urllib.parse.quote(title)
    
    # Construct the API URL. The 't' parameter is for title search.
    url = f"http://www.omdbapi.com/?t={encoded_title}&apikey={api_key}"

    try:
        # Make the HTTP GET request to the OMDb API
        with urllib.request.urlopen(url) as response:
            # Read the response body, which is in bytes, then decode it to a UTF-8 string
            data = response.read().decode('utf-8')
            # Parse the JSON string into a Python dictionary
            movie_data = json.loads(data)

            # The OMDb API returns "Response": "False" if the movie is not found
            # or if there's an issue with the API key.
            if movie_data.get("Response") == "False":
                print(f"Error from OMDb API: {movie_data.get('Error', 'Unknown API error')}", file=sys.stderr)
                return {}
            
            return movie_data

    except urllib.error.URLError as e:
        # Catches network-related errors (e.g., no internet connection, invalid URL)
        print(f"Network error or invalid URL: {e}", file=sys.stderr)
        return {}
    except json.JSONDecodeError as e:
        # Catches errors if the response is not valid JSON
        print(f"Error decoding JSON response from API: {e}", file=sys.stderr)
        return {}
    except Exception as e:
        # Catches any other unexpected errors during the process
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        return {}

def display_movie_details(movie_data: dict):
    """
    Prints selected details of a movie in a human-readable format.

    Args:
        movie_data (dict): A dictionary containing movie information,
                           expected to be the output from fetch_movie_info.
    """
    if not movie_data:
        print("No movie data to display.")
        return

    print("\n--- Movie Details ---")
    # Using .get() with a default value 'N/A' to safely access dictionary keys
    # without crashing if a key is missing.
    print(f"Title:        {movie_data.get('Title', 'N/A')}")
    print(f"Year:         {movie_data.get('Year', 'N/A')}")
    print(f"Rated:        {movie_data.get('Rated', 'N/A')}")
    print(f"Released:     {movie_data.get('Released', 'N/A')}")
    print(f"Runtime:      {movie_data.get('Runtime', 'N/A')}")
    print(f"Genre:        {movie_data.get('Genre', 'N/A')}")
    print(f"Director:     {movie_data.get('Director', 'N/A')}")
    print(f"Writer:       {movie_data.get('Writer', 'N/A')}")
    print(f"Actors:       {movie_data.get('Actors', 'N/A')}")
    print(f"Plot:         {movie_data.get('Plot', 'N/A')}")
    print(f"Language:     {movie_data.get('Language', 'N/A')}")
    print(f"Country:      {movie_data.get('Country', 'N/A')}")
    print(f"Awards:       {movie_data.get('Awards', 'N/A')}")
    print(f"IMDb Rating:  {movie_data.get('imdbRating', 'N/A')}")
    print(f"Box Office:   {movie_data.get('BoxOffice', 'N/A')}")
    print("---------------------\n")

if __name__ == "__main__":
    print("Welcome to the Movie Info Fetcher!")
    print("This script uses the OMDb API (www.omdbapi.com) to get movie details.")
    print("You need a free API key to use it. Please register on their website to obtain one.")

    # Prompt the user for their API key
    omdb_api_key = input("Enter your OMDb API key: ").strip()

    if not omdb_api_key:
        print("API key cannot be empty. Exiting.", file=sys.stderr)
        sys.exit(1) # Exit the script with an error code

    print("\nReady to fetch movie information. Type 'exit' to quit at any time.")

    # Loop indefinitely, allowing the user to search for multiple movies
    while True:
        # Prompt the user for a movie title
        movie_title = input("\nEnter a movie title: ").strip()

        # Check for the exit command
        if movie_title.lower() == 'exit':
            print("Exiting Movie Info Fetcher. Goodbye!")
            break # Exit the while loop

        if not movie_title:
            print("Movie title cannot be empty. Please try again.", file=sys.stderr)
            continue # Skip to the next iteration of the loop

        print(f"Fetching info for '{movie_title}'...")
        
        # Call the function to fetch movie information
        info = fetch_movie_info(movie_title, omdb_api_key)

        # If movie information was successfully retrieved, display it
        if info:
            display_movie_details(info)
        else:
            print(f"Failed to retrieve details for '{movie_title}'. Please ensure the title is correct and your API key is valid.")
        
        print("=" * 60) # A separator for visual clarity between searches
