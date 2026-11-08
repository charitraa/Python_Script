# pip install requests beautifulsoup4
# This script requires two third-party libraries: 'requests' for making HTTP requests
# and 'beautifulsoup4' for parsing HTML. You can install them using pip:
# pip install requests beautifulsoup4

import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import re
import os
from urllib.parse import urlparse

"""
E-commerce Price Tracker

This script tracks the price of a specific product on Amazon.com.
It fetches the current price from the product page, stores it along with a timestamp
in a product-specific CSV file, and can optionally notify the user if the price
drops below a specified target price.

Features:
- Fetches product details (currently only price) from a given Amazon URL.
- Stores historical price data in a product-specific CSV file located in a 'price_history' directory.
- Checks if the current price is below a user-defined target.
- Provides a simple command-line output for tracking status and history.

Usage:
1. Ensure 'requests' and 'beautifulsoup4' are installed (`pip install requests beautifulsoup4`).
2. Run the script. The `if __name__ == "__main__":` block provides example usage.
   You should replace the example URLs with actual Amazon product URLs you wish to track.
"""

# --- Configuration ---
# User-Agent header helps mimic a real browser request, reducing chances of being blocked.
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}
# Directory to store price history files
HISTORY_DIR = "price_history"

# --- Helper Functions ---

def get_page_content(url):
    """
    Fetches the HTML content of a given URL.

    Args:
        url (str): The URL of the page to fetch.

    Returns:
        str: The HTML content of the page, or None if an error occurred.
    """
    try:
        # Send a GET request to the URL with specified headers and a timeout
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None

def parse_amazon_price(soup):
    """
    Extracts the product price from an Amazon product page's BeautifulSoup object.
    This function tries to locate the price based on common Amazon HTML structures.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object of the Amazon product page.

    Returns:
        float: The extracted price, or None if the price could not be found.
    """
    # Common elements where Amazon displays prices:
    # 1. Spans with specific IDs (older structure)
    # 2. Spans with class "a-offscreen" (often contains the actual text price, but might appear multiple times)
    # 3. Spans with class "a-price" which usually wraps the price elements.

    # List of potential price elements to check, in order of likelihood/specificity
    price_elements_finders = [
        # New structure for current price
        lambda s: s.find("span", {"class": "a-price aok-align-center"}),
        # General a-offscreen that usually has the full price
        lambda s: s.find("span", {"class": "a-offscreen"}),
        # Older IDs for price blocks
        lambda s: s.find("span", {"id": "priceblock_ourprice"}),
        lambda s: s.find("span", {"id": "priceblock_dealprice"}),
        lambda s: s.find("span", {"id": "priceblock_saleprice"}),
    ]

    for find_func in price_elements_finders:
        element = find_func(soup)
        if element:
            price_text = element.get_text(strip=True)
            # Use regex to find a number that might include commas or periods
            match = re.search(r'\d[\d,\.]*', price_text)
            if match:
                # Remove commas and convert to float
                try:
                    return float(match.group(0).replace(',', ''))
                except ValueError:
                    continue # If conversion fails, try next finder

    # If no specific elements were found, try a more general search for 'a-price' class
    # and then look for `a-offscreen` within it.
    price_span = soup.find("span", class_="a-price")
    if price_span:
        offscreen_span = price_span.find("span", class_="a-offscreen")
        if offscreen_span:
            price_text = offscreen_span.get_text(strip=True)
            match = re.search(r'\d[\d,\.]*', price_text)
            if match:
                try:
                    return float(match.group(0).replace(',', ''))
                except ValueError:
                    pass # Continue if conversion fails

    print("Warning: Could not find price on the page. HTML structure might have changed or element not present.")
    return None

def get_product_identifier(url):
    """
    Generates a simple, clean identifier for a product from its URL.
    For Amazon, this typically extracts the ASIN (e.g., B08WHD2R87).
    This identifier is used to create a unique filename for the price history CSV.
    """
    parsed_url = urlparse(url)
    path_segments = parsed_url.path.split('/')
    
    # Attempt to find the ASIN (10-character alphanumeric string, often after /dp/ or /gp/product/)
    for i, segment in enumerate(path_segments):
        if len(segment) == 10 and segment.isalnum(): # ASINs are 10 alphanumeric chars
            if i > 0 and (path_segments[i-1] == 'dp' or path_segments[i-1] == 'product'):
                return segment
    
    # Fallback: Use a cleaned version of the last non-empty path segment, or the hostname
    if path_segments and path_segments[-1]:
        # Remove special characters from the last path segment to make it filename safe
        return re.sub(r'[^a-zA-Z0-9_-]', '', path_segments[-1]).strip('-')
    
    # Final fallback: use the domain name if no useful path segments
    return parsed_url.hostname.replace('.', '_') if parsed_url.hostname else "unknown_product"


def get_history_filepath(product_url):
    """
    Returns the full path to the CSV file for a given product URL.
    """
    identifier = get_product_identifier(product_url)
    if not os.path.exists(HISTORY_DIR):
        os.makedirs(HISTORY_DIR) # Create the history directory if it doesn't exist
    return os.path.join(HISTORY_DIR, f"{identifier}_price_history.csv")

def load_price_history(product_url):
    """
    Loads historical price data for a product from its CSV file.

    Args:
        product_url (str): The URL of the product.

    Returns:
        list: A list of dictionaries, where each dictionary contains 'timestamp' (datetime object)
              and 'price' (float). Returns an empty list if the file doesn't exist or is unreadable.
    """
    filepath = get_history_filepath(product_url)
    history = []
    if os.path.exists(filepath):
        try:
            with open(filepath, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        history.append({
                            'timestamp': datetime.fromisoformat(row['timestamp']),
                            'price': float(row['price'])
                        })
                    except (ValueError, KeyError) as e:
                        print(f"Skipping malformed row in history file {filepath}: {row} - {e}")
            # Sort by timestamp to ensure chronological order, important for latest price check
            history.sort(key=lambda x: x['timestamp'])
        except Exception as e:
            print(f"Error reading history file {filepath}: {e}")
            history = [] # Reset history if file is corrupted
    return history

def save_price_data(product_url, current_price):
    """
    Saves the current price and timestamp to the product's CSV history file.

    Args:
        product_url (str): The URL of the product.
        current_price (float): The current price of the product.
    """
    filepath = get_history_filepath(product_url)
    
    # Check if file exists to determine if headers are needed
    file_exists = os.path.exists(filepath) and os.stat(filepath).st_size > 0
    
    with open(filepath, mode='a', newline='', encoding='utf-8') as file:
        fieldnames = ['timestamp', 'price']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        if not file_exists: # Write header only if file is new or empty
            writer.writeheader()
        
        writer.writerow({
            'timestamp': datetime.now().isoformat(), # Store timestamp in ISO format for easy parsing
            'price': current_price
        })
    print(f"Price data saved to {filepath}")

def display_history(history):
    """
    Prints the historical price data to the console in a readable format.
    """
    if not history:
        print("No historical data available yet.")
        return

    print("\n--- Price History ---")
    # Display up to the last 10 entries for brevity, or all if less than 10
    display_count = min(len(history), 10) 
    for entry in history[-display_count:]: # Show most recent entries
        print(f"  {entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}: ${entry['price']:.2f}")
    if len(history) > display_count:
        print(f"  ... (showing last {display_count} of {len(history)} entries)")
    print("---------------------\n")

# --- Main Tracking Function ---

def track_product_price(product_url, target_price=None):
    """
    Main function to track a product's price.
    Fetches the price, saves it, and checks against a target price.

    Args:
        product_url (str): The URL of the Amazon product to track.
        target_price (float, optional): A target price to check against.
                                         If the current price is at or below this,
                                         a notification is printed. Defaults to None.
    """
    print(f"\nTracking price for: {product_url}")

    # 1. Fetch page content
    html_content = get_page_content(product_url)
    if not html_content:
        print("Failed to retrieve product page. Cannot track price.")
        return

    # 2. Parse price from HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    current_price = parse_amazon_price(soup)

    if current_price is None:
        print("Could not extract current price from the page. Cannot track price.")
        return

    print(f"Current price: ${current_price:.2f}")

    # 3. Load existing history and save current price if it's different
    history = load_price_history(product_url)
    
    # Only save if the price has changed from the last recorded entry
    if not history or history[-1]['price'] != current_price:
        save_price_data(product_url, current_price)
        # Reload history to include the just-saved price for accurate display
        history = load_price_history(product_url) 
    else:
        print("Price has not changed since the last recorded check. Not saving duplicate entry.")

    # 4. Check against target price if provided
    if target_price is not None:
        if current_price <= target_price:
            print(f"*** PRICE ALERT! Price (${current_price:.2f}) is AT or BELOW your target price (${target_price:.2f})! ***")
        else:
            print(f"Price (${current_price:.2f}) is still ABOVE your target price (${target_price:.2f}).")

    # 5. Display historical data
    display_history(history)

# --- Example Usage ---

if __name__ == "__main__":
    # Ensure the history directory exists at the script's start
    if not os.path.exists(HISTORY_DIR):
        os.makedirs(HISTORY_DIR)
        print(f"Created directory: {HISTORY_DIR}")

    # --- Example 1: Track a product with a target price ---
    print("--- Running Example 1: Product with a target price ---")
    # IMPORTANT: Replace this with a real Amazon product URL you want to track.
    # The example URL below is illustrative and might not be valid or stable over time.
    # Find an Amazon URL that is directly a product page, not a search result.
    example_product_url_1 = "https://www.amazon.com/dp/B08WHD2R87" # Example: A popular electronics item or book
    example_target_price_1 = 15.00 # Set your desired target price here

    # To see the historical data accumulate, you would typically run this script
    # multiple times over a period (e.g., daily, hourly).
    track_product_price(example_product_url_1, target_price=example_target_price_1)
    
    print("\n" + "="*50 + "\n")

    # --- Example 2: Track another product without a specific target price initially ---
    print("--- Running Example 2: Product without an initial target price ---")
    example_product_url_2 = "https://www.amazon.com/dp/B0C39694Q5" # Another example product
    
    track_product_price(example_product_url_2)

    # Simulate checking again later with a target price to see the alert feature.
    # In a real scenario, you would run the script again after some time.
    # For this example, we're simply calling the function again immediately.
    print("\n--- Simulating a later check for Example 2 product, now with a target price ---")
    simulated_target_price_2 = 50.00 # A target price for the second product
    track_product_price(example_product_url_2, target_price=simulated_target_price_2)
    
    print("\nScript finished. Check the 'price_history' directory for CSV files containing detailed history.")
