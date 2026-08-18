# pip install requests
import requests
import time
import datetime

"""
Website Uptime Checker

This script periodically checks the availability of a list of websites.
It sends an HTTP GET request to each URL and reports its status (UP or DOWN)
along with the HTTP status code or an error message. The checks are performed
at a specified interval, making it useful for basic website monitoring.
"""

def check_website(url: str, timeout: int = 10) -> tuple[bool, str]:
    """
    Checks if a website is reachable and returns its status.

    Args:
        url (str): The URL of the website to check.
        timeout (int): The maximum number of seconds to wait for a response.

    Returns:
        tuple[bool, str]: A tuple where the first element is True if the
                         website is up (HTTP status 200-299), False otherwise.
                         The second element is a string indicating the
                         HTTP status code or an error message.
    """
    try:
        # Send an HTTP GET request to the URL with a specified timeout.
        # allow_redirects=True means it will follow any redirects (e.g., HTTP to HTTPS).
        # verify=True means it will verify SSL certificates, which is good practice.
        response = requests.get(url, timeout=timeout, allow_redirects=True, verify=True)

        # Check if the HTTP status code indicates success (200-299 range)
        if 200 <= response.status_code < 300:
            return True, f"Status Code: {response.status_code}"
        else:
            # For non-success status codes (e.g., 404 Not Found, 500 Internal Server Error)
            return False, f"Status Code: {response.status_code}"

    except requests.exceptions.ConnectionError:
        # This exception occurs for network-related problems:
        # - DNS resolution failure (website address can't be found)
        # - Host refused connection (server is down or blocking connection)
        # - No route to host (network path to server doesn't exist)
        return False, "Error: Connection refused or host unreachable."
    except requests.exceptions.Timeout:
        # This exception occurs if the server does not send any data
        # within the specified `timeout` duration.
        return False, f"Error: Request timed out after {timeout} seconds."
    except requests.exceptions.RequestException as e:
        # This is a general catch-all for any other requests-related errors
        # (e.g., too many redirects, invalid URL format, etc.).
        return False, f"Error: {e}"
    except Exception as e:
        # Catch any other unexpected errors that might occur during the check.
        return False, f"An unexpected error occurred: {e}"


def main():
    """
    Main function to run the website uptime checker.
    Configures URLs and checking interval, then starts the monitoring loop.
    """
    # List of websites to check. You can add or remove URLs here.
    # It's good to include a mix of known good sites, and potentially
    # a non-existent one or one that returns an error for testing purposes.
    websites_to_check = [
        "https://www.google.com",
        "https://www.python.org",
        "https://example.com",
        "https://thisisafakewebsitefordemo123.com", # Example of a likely down/unreachable website
        "http://httpbin.org/status/500"            # Example of a website returning a 500 Internal Server Error
    ]

    # How often to check the websites (in seconds).
    # For demonstration, a short interval like 60 seconds is used.
    # In a real-world scenario, this might be 300 (5 minutes), 600 (10 minutes), etc.
    check_interval_seconds = 60

    print("Starting website uptime checker...")
    print(f"Monitoring the following websites every {check_interval_seconds} seconds:")
    for url in websites_to_check:
        print(f"- {url}")
    print("-" * 50)

    # Loop indefinitely to perform checks until the script is manually stopped.
    while True:
        # Get the current timestamp for logging purposes.
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n--- Checking websites at {current_time} ---")

        # Iterate through each website in the list and check its status.
        for url in websites_to_check:
            is_up, status_info = check_website(url)
            status_emoji = "✅ UP" if is_up else "❌ DOWN"
            print(f"[{status_emoji}] {url} - {status_info}")

        # Calculate the approximate time for the next check.
        next_check_time = datetime.datetime.now() + datetime.timedelta(seconds=check_interval_seconds)
        print(f"\nNext check in {check_interval_seconds} seconds (approx. {next_check_time.strftime('%H:%M:%S')}). Press Ctrl+C to exit.")
        
        # Wait for the specified interval before performing the next round of checks.
        try:
            time.sleep(check_interval_seconds)
        except KeyboardInterrupt:
            # Handle Ctrl+C (KeyboardInterrupt) to allow the user to gracefully stop the script.
            print("\nWebsite uptime checker stopped by user.")
            break  # Exit the infinite loop


if __name__ == "__main__":
    # This block ensures that `main()` is called only when the script is
    # executed directly, not when it's imported as a module into another script.
    main()
