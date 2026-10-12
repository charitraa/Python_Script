# pip install requests
"""
IP Address Lookup Tool

This script allows you to look up details for a given IP address or domain name
using a public API (ip-api.com). It can provide information such as country,
city, ISP, and geographic coordinates.

You can provide an IP address or domain as a command-line argument,
or it will prompt you for input if none is provided.
If you input 'me', it will look up your own public IP address.
"""

import requests
import sys
import json

def lookup_ip(query: str) -> dict | None:
    """
    Looks up IP address details using the ip-api.com service.

    Args:
        query (str): The IP address (e.g., "8.8.8.8"), domain name (e.g., "google.com"),
                     or "me" to look up your own public IP.

    Returns:
        dict | None: A dictionary containing IP details if the lookup is successful,
                     otherwise None.
    """
    api_url = f"http://ip-api.com/json/{query}"

    try:
        # Make a GET request to the IP lookup API
        response = requests.get(api_url)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)

        data = response.json()

        # The ip-api.com service includes a 'status' field in its JSON response
        if data.get("status") == "success":
            return data
        else:
            # Handle API-specific errors, e.g., private range, invalid query
            print(f"Error: API reported status '{data.get('status', 'unknown')}'")
            print(f"Message: {data.get('message', 'No specific message provided.')}")
            return None
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error occurred: {e}")
        print(f"Response content: {e.response.text}")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"Connection Error: Could not connect to the API server. Check your internet connection.")
        print(f"Details: {e}")
        return None
    except requests.exceptions.Timeout as e:
        print(f"Timeout Error: The request to the API timed out.")
        print(f"Details: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"An unexpected Request Error occurred: {e}")
        return None
    except json.JSONDecodeError:
        print("Error: Could not decode JSON response from the API.")
        return None

def display_ip_info(ip_data: dict):
    """
    Prints the IP address information in a user-friendly format.

    Args:
        ip_data (dict): A dictionary containing IP details.
    """
    print("\n--- IP Lookup Results ---")
    # Iterate through the dictionary and print key-value pairs
    # Use .get() to safely access keys, providing a default if not present
    print(f"Query IP/Domain: {ip_data.get('query', 'N/A')}")
    print(f"Status:          {ip_data.get('status', 'N/A')}")
    print(f"Country:         {ip_data.get('country', 'N/A')} ({ip_data.get('countryCode', 'N/A')})")
    print(f"Region:          {ip_data.get('regionName', 'N/A')} ({ip_data.get('region', 'N/A')})")
    print(f"City:            {ip_data.get('city', 'N/A')}")
    print(f"ZIP Code:        {ip_data.get('zip', 'N/A')}")
    print(f"Timezone:        {ip_data.get('timezone', 'N/A')}")
    print(f"ISP:             {ip_data.get('isp', 'N/A')}")
    print(f"Organization:    {ip_data.get('org', 'N/A')}")
    print(f"AS:              {ip_data.get('as', 'N/A')}")
    print(f"Coordinates:     Lat {ip_data.get('lat', 'N/A')}, Lon {ip_data.get('lon', 'N/A')}")
    print("\n--- Raw Data (JSON) ---")
    # Pretty print the entire JSON response for full details
    print(json.dumps(ip_data, indent=2))
    print("-----------------------\n")


if __name__ == "__main__":
    # Check if an IP/domain was provided as a command-line argument
    if len(sys.argv) > 1:
        ip_query = sys.argv[1]
    else:
        # If no argument, prompt the user for input
        print("Enter an IP address, domain name (e.g., 8.8.8.8, google.com), or 'me' for your own IP:")
        ip_query = input(">>> ").strip()

    if not ip_query:
        print("No input provided. Exiting.")
    else:
        print(f"Looking up details for: {ip_query}...")
        ip_details = lookup_ip(ip_query)

        if ip_details:
            display_ip_info(ip_details)
        else:
            print(f"Could not retrieve details for '{ip_query}'. Please check the input or your connection.")
