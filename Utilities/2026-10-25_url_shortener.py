# pip install requests

"""
A simple URL shortener script that uses the TinyURL service to convert long URLs
into shorter, more manageable links.

This script demonstrates:
- Making a GET request to a public web API.
- Handling potential network and API-specific errors.
- Basic input/output for user interaction.

Note: This script relies on the TinyURL API (https://tinyurl.com).
"""

import requests
import sys

def shorten_url(long_url: str) -> str | None:
    """
    Shortens a given long URL using the TinyURL service.

    Args:
        long_url (str): The original URL to be shortened.

    Returns:
        str | None: The shortened URL if successful, otherwise None.
    """
    # TinyURL's simple API endpoint for creating short URLs.
    # It expects the long URL as a query parameter and returns the shortened URL as plain text.
    api_endpoint = "https://tinyurl.com/api-create.php"

    try:
        # Send a GET request to the TinyURL API.
        # The 'params' dictionary automatically handles URL encoding for the 'url' parameter.
        print(f"Attempting to shorten: {long_url}")
        response = requests.get(api_endpoint, params={"url": long_url}, timeout=10) # Added a timeout

        # Raise an HTTPError for bad responses (4xx or 5xx status codes).
        # This checks if the request itself was successful at the HTTP level.
        response.raise_for_status()

        # TinyURL returns the shortened URL as plain text if successful.
        # If there's an error from the TinyURL service itself (e.g., invalid input format),
        # it typically returns an error message as plain text.
        shortened_url = response.text.strip()

        # TinyURL's service might return an error message starting with "Error:".
        # We perform a basic check to differentiate a valid shortened URL from an error.
        # A valid shortened URL from TinyURL will always start with "http".
        if shortened_url.lower().startswith("error:") or not shortened_url.startswith("http"):
            print(f"Error from TinyURL service: {shortened_url}")
            return None
        
        return shortened_url

    except requests.exceptions.Timeout:
        # Catch specific timeout errors during the request.
        print(f"Error: The request to TinyURL timed out after 10 seconds.")
        return None
    except requests.exceptions.ConnectionError as e:
        # Catch connection-related errors (e.g., no internet, DNS failure).
        print(f"Error: Could not connect to TinyURL. Please check your internet connection. ({e})")
        return None
    except requests.exceptions.HTTPError as e:
        # Catch HTTP errors (e.g., 404, 500 status codes from the server).
        print(f"Error: HTTP request failed with status code {e.response.status_code}. ({e})")
        return None
    except requests.exceptions.RequestException as e:
        # Catch any other request-related errors (e.g., invalid URL format within requests).
        print(f"An unexpected error occurred during the API request: {e}")
        return None
    except Exception as e:
        # Catch any other unexpected errors that were not specifically handled.
        print(f"An unexpected error occurred: {e}")
        return None


if __name__ == "__main__":
    # --- Example Usage ---

    print("--- TinyURL Shortener ---")
    print("This script uses TinyURL (https://tinyurl.com) to shorten URLs.")
    print("-------------------------")

    # Get URL from user input or use a default if running directly without input
    input_url = input("Enter a long URL to shorten (or press Enter for a default example): ").strip()

    if not input_url:
        # Default example URL if user doesn't provide one
        long_url_to_shorten = "https://www.google.com/search?q=python+url+shortener+script+example&oq=python+url+shortener+script+example&aqs=chrome..69i57j0i22i30l9.8000j0j7&sourceid=chrome&ie=UTF-8"
        print(f"Using default example URL: {long_url_to_shorten}")
    else:
        long_url_to_shorten = input_url

    # Basic validation for the URL format
    if not (long_url_to_shorten.startswith("http://") or long_url_to_shorten.startswith("https://")):
        print("Error: Please enter a valid URL starting with 'http://' or 'https://'.")
        sys.exit(1) # Exit with an error code if the URL format is invalid

    print(f"\nOriginal URL: {long_url_to_shorten}")

    # Call the shortening function
    short_url = shorten_url(long_url_to_shorten)

    if short_url:
        print(f"Shortened URL: {short_url}")
        print("\nTry pasting the shortened URL into your browser!")
    else:
        print("Failed to shorten the URL. Please check the URL and your internet connection.")

    print("\n--- End of Script ---")

    # --- You can uncomment the following lines to test more examples manually ---
    # print("\n--- More Examples ---")
    #
    # # Example with a different valid long URL
    # another_long_url = "https://docs.python.org/3/library/functions.html#open"
    # print(f"\nOriginal: {another_long_url}")
    # another_short_url = shorten_url(another_long_url)
    # if another_short_url:
    #     print(f"Shortened: {another_short_url}")
    # else:
    #     print("Failed to shorten the URL.")
    #
    # # Example with a URL that might not be valid for TinyURL (e.g., a non-existent domain)
    # invalid_domain_url = "https://this-domain-definitely-does-not-exist-123xyz.com"
    # print(f"\nOriginal: {invalid_domain_url}")
    # invalid_domain_short_url = shorten_url(invalid_domain_url)
    # if invalid_domain_short_url:
    #     print(f"Shortened: {invalid_domain_short_url}")
    # else:
    #     print("Failed to shorten the URL (expected for a non-existent domain).")
    #
    # # Example of deliberately malformed input that might cause a TinyURL internal error
    # malformed_url = "http://bad url format!"
    # print(f"\nOriginal: {malformed_url}")
    # malformed_short_url = shorten_url(malformed_url)
    # if malformed_short_url:
    #     print(f"Shortened: {malformed_short_url}")
    # else:
    #     print("Failed to shorten the URL (expected for malformed input).")
