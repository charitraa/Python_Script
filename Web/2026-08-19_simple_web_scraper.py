# pip install requests beautifulsoup4

import requests
from bs4 import BeautifulSoup

"""
simple_web_scraper.py

A simple web scraper script designed to fetch the content of a given URL,
parse its HTML, and extract all hyperlinks along with their text.

This script demonstrates basic web scraping principles using the `requests`
library to make HTTP requests and `BeautifulSoup` for HTML parsing. It's
intended to be beginner-friendly, showing how to get started with fetching
web pages and extracting specific elements (in this case, links).
"""

def scrape_links(url: str) -> list[dict]:
    """
    Fetches the HTML content from the given URL, parses it, and extracts
    all hyperlinks (<a> tags) along with their visible text.

    Args:
        url (str): The URL of the web page to scrape.

    Returns:
        list[dict]: A list of dictionaries, where each dictionary represents
                    a link and contains 'text' and 'href' keys. Returns an
                    empty list if no links are found or an error occurs.
    """
    print(f"Attempting to scrape: {url}")
    try:
        # Send an HTTP GET request to the specified URL
        # The timeout parameter prevents the script from hanging indefinitely
        response = requests.get(url, timeout=10)
        
        # Raise an HTTPError for bad responses (4xx or 5xx status codes)
        response.raise_for_status()
    
    except requests.exceptions.HTTPError as http_err:
        # Handle HTTP errors (e.g., 404 Not Found, 500 Server Error)
        print(f"HTTP error occurred: {http_err} - Status Code: {response.status_code}")
        return []
    except requests.exceptions.ConnectionError as conn_err:
        # Handle network connection errors (e.g., no internet, DNS failure)
        print(f"Connection error occurred: {conn_err} - Is the URL correct? Are you online?")
        return []
    except requests.exceptions.Timeout as timeout_err:
        # Handle request timeout errors
        print(f"Timeout error occurred: {timeout_err} - The server took too long to respond.")
        return []
    except requests.exceptions.RequestException as req_err:
        # Handle any other general request-related errors
        print(f"An unexpected request error occurred: {req_err}")
        return []
    except Exception as e:
        # Catch any other unexpected errors during the request phase
        print(f"An unexpected error occurred during request: {e}")
        return []

    # Parse the HTML content of the page using BeautifulSoup
    # 'html.parser' is a built-in parser that comes with Python
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all <a> tags (hyperlinks) in the parsed HTML
    # The find_all method returns a list of all matching tags
    all_links = soup.find_all('a')

    extracted_data = []
    # Iterate through each found link tag
    for link in all_links:
        # Get the 'href' attribute which contains the URL the link points to
        href = link.get('href')
        # Get the visible text content of the link
        # strip=True removes leading/trailing whitespace from the text
        text = link.get_text(strip=True)

        # Only store valid links that have both a text and an href attribute
        # Also, ignore empty or fragment links (like '#top' which refer to parts of the same page)
        if href and text and not href.startswith('#'):
            extracted_data.append({
                'text': text,
                'href': href
            })

    print(f"Found {len(extracted_data)} unique and valid links.")
    return extracted_data

if __name__ == "__main__":
    # --- Example Usage ---

    # 1. Scrape links from a well-known, public Wikipedia page about Python
    # This URL is generally stable and accessible for scraping.
    target_url = "https://en.wikipedia.org/wiki/Python_(programming_language)"

    print("\n--- Scraping Valid URL ---")
    # Call the scraping function
    links = scrape_links(target_url)

    # Print the extracted links in a readable format
    if links:
        print("\n--- Extracted Links (top 20 for brevity) ---")
        for i, link in enumerate(links[:20]): # Print only the top 20 links to keep output manageable
            print(f"{i+1}. Text: {link['text']}")
            print(f"   URL:  {link['href']}\n")
        if len(links) > 20:
            print(f"... and {len(links) - 20} more links (showing only top 20 for brevity).\n")
    else:
        print("No links were extracted or an error occurred from the valid URL.")

    # 2. Demonstrate error handling with a URL that does not exist
    print("\n--- Demonstrating Error Handling with a Non-Existent Domain ---")
    bad_domain_url = "https://this-is-not-a-real-website-123456789.com"
    bad_domain_links = scrape_links(bad_domain_url)
    if not bad_domain_links:
        print("Result: Successfully handled the non-existent domain URL request (expected ConnectionError).")

    # 3. Demonstrate error handling with a valid domain but a non-existent path (likely 404)
    print("\n--- Demonstrating Error Handling with a Bad Path on a Real Website ---")
    bad_path_url = "https://en.wikipedia.org/wiki/NonExistentPage123456789"
    bad_path_links = scrape_links(bad_path_url)
    if not bad_path_links:
        print("Result: Successfully handled the bad path URL request (expected HTTPError 404 Not Found).")
