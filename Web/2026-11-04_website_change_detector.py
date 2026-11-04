"""
Website Change Detector

This script monitors a specified website for changes in its content.
It works by fetching the website's HTML content, calculating a cryptographic hash (MD5) of that content,
and comparing it to the hash from the previous check.

The last known hash for each monitored URL is stored in a local file, allowing the script
to remember the website's state across multiple runs.

If a change is detected, it prints a notification. It then continues to monitor
the website at a specified interval.

Features:
- Monitors a single URL.
- Stores the last known website hash locally (in a file named `website_content_hash_<url_md5>.txt`).
- Reports changes detected.
- Checks at a configurable interval.
- Handles basic network errors.
"""

import urllib.request
import urllib.error
import hashlib
import os
import time
import sys

# Define the directory to store hash files (current directory by default)
HASH_FILE_DIR = "."

def _get_hash_filename(url):
    """Generates a unique filename for storing the hash based on the URL."""
    # Create an MD5 hash of the URL itself to use in the filename.
    # This ensures a unique, filesystem-safe name for each URL.
    url_md5 = hashlib.md5(url.encode('utf-8')).hexdigest()
    return os.path.join(HASH_FILE_DIR, f"website_content_hash_{url_md5}.txt")

def get_website_content(url):
    """Fetches the content of a given URL."""
    try:
        # Open the URL and read its content.
        # User-Agent header is added to mimic a web browser, which can help avoid
        # some websites blocking automated requests.
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            # Decode the content to UTF-8. 'errors=ignore' handles potential
            # decoding issues gracefully by ignoring un-decodable characters.
            return response.read().decode('utf-8', errors='ignore')
    except urllib.error.HTTPError as e:
        print(f"Error fetching {url}: HTTP Error {e.code} - {e.reason}", file=sys.stderr)
    except urllib.error.URLError as e:
        print(f"Error fetching {url}: URL Error {e.reason}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred while fetching {url}: {e}", file=sys.stderr)
    return None

def save_hash(hash_value, filename):
    """Saves a hash value to a specified file."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(hash_value)
    except IOError as e:
        print(f"Error saving hash to {filename}: {e}", file=sys.stderr)

def load_hash(filename):
    """Loads a hash value from a specified file."""
    if not os.path.exists(filename):
        return None  # File doesn't exist, meaning no previous hash was saved.
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except IOError as e:
        print(f"Error loading hash from {filename}: {e}", file=sys.stderr)
        return None

def detect_website_change(url, check_interval_seconds=3600):
    """
    Monitors a website for content changes.

    Args:
        url (str): The URL of the website to monitor.
        check_interval_seconds (int): The time in seconds to wait between checks.
                                      Defaults to 3600 seconds (1 hour).
    """
    print(f"Starting website change detector for: {url}")
    print(f"Checking every {check_interval_seconds} seconds.")

    hash_filename = _get_hash_filename(url)
    last_known_hash = load_hash(hash_filename)

    # Perform an initial check before starting the continuous loop
    print("\n--- Initial Check ---")
    current_content = get_website_content(url)
    if current_content is None:
        print("Failed to fetch content during initial check. Exiting.", file=sys.stderr)
        sys.exit(1)

    current_hash = hashlib.md5(current_content.encode('utf-8')).hexdigest()

    if last_known_hash is None:
        print(f"First check for this URL. Storing current website state (hash: {current_hash}).")
        save_hash(current_hash, hash_filename)
        last_known_hash = current_hash # Update for the loop
    elif current_hash != last_known_hash:
        print(f"Website content has changed since the last known state! New hash: {current_hash}")
        save_hash(current_hash, hash_filename)
        last_known_hash = current_hash # Update for the loop
    else:
        print(f"Website content is unchanged from the last known state (hash: {current_hash}).")

    print("--- Starting continuous monitoring ---")

    while True:
        try:
            print(f"\n[{time.ctime()}] Waiting {check_interval_seconds} seconds before next check...")
            time.sleep(check_interval_seconds)

            print(f"[{time.ctime()}] Performing check for {url}...")
            new_content = get_website_content(url)

            if new_content is None:
                print(f"[{time.ctime()}] Failed to fetch content. Retrying next interval.")
                continue # Skip this check, keep the old hash, and try again later.

            new_hash = hashlib.md5(new_content.encode('utf-8')).hexdigest()

            if new_hash != last_known_hash:
                print(f"\n!!! WEBSITE CHANGE DETECTED on {time.ctime()} !!!")
                print(f"Old hash: {last_known_hash}")
                print(f"New hash: {new_hash}")
                save_hash(new_hash, hash_filename)
                last_known_hash = new_hash
            else:
                print(f"[{time.ctime()}] Website content unchanged. Hash: {new_hash}")

        except KeyboardInterrupt:
            print("\nWebsite change detector stopped by user.")
            break
        except Exception as e:
            print(f"An unexpected error occurred in the monitoring loop: {e}", file=sys.stderr)
            print("Attempting to continue monitoring after a brief pause...")
            time.sleep(60) # Wait a bit longer before retrying after an unexpected error.

if __name__ == "__main__":
    # --- EXAMPLE USAGE ---
    # You can change these values to monitor a different website or change the check frequency.
    # For testing, use a URL you control or one that changes frequently (e.g., a news site).
    # Be mindful of the check_interval_seconds to avoid hammering websites too frequently.

    TARGET_URL = "https://www.example.com"  # Replace with the URL you want to monitor
    # Note: Some websites may block requests that are too frequent or don't have a valid User-Agent.
    # Use a high interval for public websites to be respectful of their servers.

    CHECK_INTERVAL_SECONDS = 300  # Check every 5 minutes (for testing purposes)
                                  # For real-world use, consider 3600 (1 hour) or more.

    # Ensure the HASH_FILE_DIR exists, if it's not the current directory
    if HASH_FILE_DIR != "." and not os.path.exists(HASH_FILE_DIR):
        os.makedirs(HASH_FILE_DIR)

    detect_website_change(TARGET_URL, CHECK_INTERVAL_SECONDS)
