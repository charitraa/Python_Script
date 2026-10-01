# pip install requests

import requests
import re
import urllib.parse
import sys

"""
This script checks all internal and external hyperlinks found on a given URL.
It fetches the HTML content of the target URL, extracts all 'href' attributes
from anchor tags (<a>), resolves relative URLs, and then attempts to make an
HTTP GET request to each unique link found. It reports the status (working or broken)
for each link, along with its HTTP status code.

It requires the 'requests' library to be installed: `pip install requests`
"""

def check_link(url: str, timeout: int = 5) -> tuple[int, str, bool]:
    """
    Attempts to make an HTTP GET request to a given URL to check its status.

    Args:
        url (str): The URL to check.
        timeout (int): Maximum seconds to wait for a response.

    Returns:
        tuple[int, str, bool]: A tuple containing:
            - HTTP status code (or 0 for network errors)
            - A descriptive reason/status text
            - True if the link is considered broken, False otherwise.
    """
    try:
        # Send a GET request to the URL. We set a timeout to prevent
        # the script from hanging indefinitely on unresponsive servers.
        # allow_redirects=True by default, which is usually desired for link checking.
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        # Using requests.head() is often faster as it only fetches headers, not the full content.
        # If HEAD is not allowed/supported, fall back to GET.
        if response.status_code >= 400 or response.status_code < 200:
            response = requests.get(url, timeout=timeout, allow_redirects=True)
            # Raise an exception for HTTP errors (4xx or 5xx)
            response.raise_for_status()
        
        # If status code is 2xx, the link is generally considered working.
        is_broken = not (200 <= response.status_code < 300)
        return response.status_code, response.reason, is_broken
    except requests.exceptions.HTTPError as e:
        # HTTP errors (e.g., 404 Not Found, 500 Internal Server Error)
        return e.response.status_code, e.response.reason, True
    except requests.exceptions.ConnectionError:
        # Network-related errors (e.g., DNS failure, refused connection)
        return 0, "Connection Error", True
    except requests.exceptions.Timeout:
        # Request timed out
        return 0, "Timeout", True
    except requests.exceptions.RequestException as e:
        # Any other requests-related exception
        return 0, f"Request Failed: {e}", True
    except Exception as e:
        # Catch any other unexpected errors
        return 0, f"Unexpected Error: {e}", True

def get_all_links(base_url: str, html_content: str) -> set[str]:
    """
    Extracts all unique absolute URLs from the HTML content of a page.

    Args:
        base_url (str): The base URL of the page being scanned, used to
                        resolve relative links into absolute ones.
        html_content (str): The full HTML content of the page as a string.

    Returns:
        set[str]: A set of unique, absolute HTTP/HTTPS URLs found on the page.
    """
    # Regex to find href attributes in <a> tags.
    # It captures the URL within double or single quotes.
    # re.IGNORECASE makes it case-insensitive for 'a' and 'href'.
    # re.DOTALL allows '.' to match newlines, important for multi-line attributes.
    # The non-greedy '.*?' ensures it stops at the first quote.
    link_pattern = re.compile(r'<a\s+(?:[^>]*?\s+)?href=["\'](.*?)(?=["\'])', re.IGNORECASE | re.DOTALL)
    
    found_links = set()
    for match in link_pattern.finditer(html_content):
        link = match.group(1).strip() # Get the captured URL and strip whitespace

        # Skip empty links or fragment identifiers for the same page
        if not link or link.startswith('#'):
            continue

        # Resolve relative URLs to absolute URLs using the base URL
        # e.g., "/about" becomes "https://example.com/about"
        absolute_link = urllib.parse.urljoin(base_url, link)

        # Parse the absolute link to check its scheme and strip fragments
        parsed_link = urllib.parse.urlparse(absolute_link)

        # Only process HTTP and HTTPS links.
        # Filter out mailto:, javascript:, ftp:, etc.
        if parsed_link.scheme in ['http', 'https']:
            # Construct the URL without the fragment part (#section) for checking,
            # as fragments don't affect the HTTP request itself.
            cleaned_link = urllib.parse.urlunparse(parsed_link._replace(fragment=''))
            found_links.add(cleaned_link)
            
    return found_links

def main(target_url: str):
    """
    Main function to orchestrate the link checking process.
    Fetches the target URL, extracts links, and checks each one.
    """
    print(f"Starting link check on: {target_url}\n")
    print("Fetching initial page content...")

    try:
        # Fetch the HTML content of the target URL
        response = requests.get(target_url, timeout=10)
        response.raise_for_status() # Raise an exception for 4xx/5xx HTTP errors
        html_content = response.text
        print(f"Successfully fetched {target_url}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the target URL '{target_url}': {e}")
        return
    
    # Extract all unique links from the fetched HTML
    extracted_links = get_all_links(target_url, html_content)
    
    if not extracted_links:
        print("No hyperlinks (<a> tags with href) found on the page.")
        return

    print(f"\nFound {len(extracted_links)} unique hyperlinks to check.")
    print("-" * 50)

    broken_links_count = 0
    total_checked = 0

    # Iterate through each extracted link, check its status, and report.
    # Sorting the links provides a consistent output order.
    for link in sorted(list(extracted_links)):
        total_checked += 1
        status_code, reason, is_broken = check_link(link)
        
        if is_broken:
            broken_links_count += 1
            print(f"[BROKEN] ({status_code} {reason}) -> {link}")
        # else:
            # print(f"[OK] ({status_code} {reason}) -> {link}") # Uncomment for verbose output

    print("-" * 50)
    if broken_links_count == 0:
        print(f"All {total_checked} links checked are working. Good job!")
    else:
        print(f"Found {broken_links_count} broken link(s) out of {total_checked} checked.")

if __name__ == "__main__":
    # Example usage:
    # You can change this URL to any website you want to check.
    # A simple page like 'http://example.com' or a local test page is good for beginners.
    # For testing broken links, you might need a page that deliberately contains one.
    
    # Example of a URL that might contain some links
    default_url = "https://www.python.org" 
    
    # Check if a URL was provided as a command-line argument
    if len(sys.argv) > 1:
        target_url_from_args = sys.argv[1]
        print(f"Using URL from command line: {target_url_from_args}")
        main(target_url_from_args)
    else:
        print(f"No URL provided. Using default: {default_url}")
        print("To specify a URL, run the script like: python link_checker.py https://your-website.com")
        main(default_url)

    print("\nScript finished.")
