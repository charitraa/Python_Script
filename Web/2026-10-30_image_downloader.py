# Required third-party packages:
# pip install requests beautifulsoup4

import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, unquote

"""
Python script to download images from a given URL.

This script can operate in two modes:
1.  If the provided URL points directly to an image file (e.g., a .jpg or .png URL),
    it will download that single image.
2.  If the provided URL points to a webpage (e.g., an HTML page), it will attempt
    to scrape the page for all <img> tags, extract their source URLs, and
    download all found images to a specified local folder.

It's designed to be beginner-friendly, practical, and self-contained.
"""

def _download_single_image(image_url, output_folder):
    """
    Helper function to download a single image from a given URL to the specified folder.
    It attempts to extract a meaningful filename from the URL, or generates a unique one.
    Handles filename collisions by appending a counter.
    """
    try:
        # Send a GET request to the image URL with a timeout
        response = requests.get(image_url, stream=True, timeout=10)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

        # Extract filename from the URL path
        parsed_url = urlparse(image_url)
        filename = os.path.basename(parsed_url.path)

        # If filename is empty or doesn't have a clear extension, generate a unique one.
        # This covers cases where URL ends in a slash, is very generic, or unhelpful.
        if not filename or '.' not in filename:
            # Generate a unique name using a hash of the URL and append a common extension.
            # abs(hash()) ensures a positive integer; modulo keeps the number shorter.
            filename = f"image_{abs(hash(image_url)) % 1_000_000}.jpg"
            print(f"  Warning: Filename unclear for '{image_url}'. Saving as '{filename}'")

        # Decode URL-encoded characters in the filename (e.g., %20 becomes space)
        filename = unquote(filename)

        # Construct the full path where the image will be saved
        filepath = os.path.join(output_folder, filename)

        # Handle potential filename collisions by adding a suffix (e.g., image.jpg -> image_1.jpg)
        original_filepath = filepath
        counter = 1
        while os.path.exists(filepath):
            name, ext = os.path.splitext(original_filepath)
            filepath = f"{name}_{counter}{ext}"
            counter += 1
            # Update filename variable for consistent output message
            filename = os.path.basename(filepath)

        # Save the image content to the file in binary write mode
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"  Downloaded: '{filename}'")
        return True # Indicate successful download
    except requests.exceptions.Timeout:
        print(f"  Error: Timeout while downloading '{image_url}'")
        return False
    except requests.exceptions.RequestException as e:
        print(f"  Error downloading '{image_url}': {e}")
        return False
    except IOError as e:
        print(f"  Error saving '{filename}': {e}")
        return False

def download_images(url, output_folder="downloaded_images"):
    """
    Downloads images from a given URL to a specified output folder.

    Parameters:
        url (str): The URL to process. Can be a direct link to an image
                   or a link to a webpage.
        output_folder (str): The directory where downloaded images will be saved.
                             Defaults to "downloaded_images".
    """
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created output folder: '{output_folder}'")

    # Define common image file extensions for direct download detection
    image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp', '.ico')

    # Check if the URL appears to be a direct link to an image file
    # This is a heuristic based on checking if the URL path ends with a known image extension.
    if url.lower().endswith(image_extensions):
        print(f"\nProcessing direct image URL: '{url}'")
        _download_single_image(url, output_folder)
        return # Exit after attempting to download the single image

    print(f"\nAttempting to scrape images from webpage: '{url}'")
    try:
        # Fetch the content of the webpage with a timeout
        response = requests.get(url, timeout=15)
        response.raise_for_status() # Raise an exception for HTTP errors (e.g., 404 Not Found)
    except requests.exceptions.Timeout:
        print(f"Error: Timeout while accessing webpage '{url}'.")
        return
    except requests.exceptions.RequestException as e:
        print(f"Error accessing webpage '{url}': {e}")
        return

    # Parse the webpage content using Beautiful Soup to find HTML elements
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all <img> tags in the parsed HTML
    img_tags = soup.find_all('img')

    if not img_tags:
        print(f"No <img> tags found on '{url}'.")
        return

    downloaded_count = 0
    print(f"Found {len(img_tags)} potential images. Starting download...")
    for img in img_tags:
        # Get the 'src' attribute. Some websites use 'data-src' for lazy loading.
        img_url = img.get('src') or img.get('data-src')

        if not img_url:
            continue # Skip if no source URL is found in src or data-src

        # Convert relative URLs to absolute URLs.
        # urljoin handles cases like '/path/to/image.jpg' relative to 'http://example.com/page'.
        absolute_img_url = urljoin(url, img_url)

        # Basic validation: ensure the constructed URL starts with http or https
        if not absolute_img_url.startswith(('http://', 'https://')):
            print(f"  Skipping non-HTTP/HTTPS image URL: '{absolute_img_url}'")
            continue

        # Attempt to download the image using the helper function
        if _download_single_image(absolute_img_url, output_folder):
            downloaded_count += 1

    print(f"\nFinished processing '{url}'. Downloaded {downloaded_count} image(s) to '{output_folder}'.")

if __name__ == "__main__":
    # --- Example Usage ---

    # 1. Download images from a sample webpage (e.g., official Python logos page)
    print("--- Example 1: Downloading images from a webpage ---")
    webpage_url_1 = "https://www.python.org/community/logos/"
    download_images(webpage_url_1, "python_logos")

    # 2. Download a single direct image (e.g., a specific Python logo)
    print("\n--- Example 2: Downloading a single direct image ---")
    direct_image_url = "https://www.python.org/static/img/python-logo.png"
    download_images(direct_image_url, "single_image_download")

    # 3. Another webpage example (e.g., a Wikipedia page with many images)
    print("\n--- Example 3: Downloading images from a Wikipedia page ---")
    wikipedia_url = "https://en.wikipedia.org/wiki/Cat"
    download_images(wikipedia_url, "wiki_cat_images")

    # 4. Example testing error handling: a URL that likely does not exist
    print("\n--- Example 4: Testing error handling (non-existent webpage) ---")
    non_existent_url = "https://example.com/non_existent_page_12345.html"
    download_images(non_existent_url, "error_test_non_existent")

    # 5. Example testing error handling: a valid page that has no <img> tags
    print("\n--- Example 5: Testing error handling (valid page with no img tags) ---")
    # IANA example.com page is simple and typically has no images.
    no_img_url = "https://www.iana.org/domains/example/"
    download_images(no_img_url, "error_test_no_img")

    print("\nAll example downloads finished. Check the created folders.")
