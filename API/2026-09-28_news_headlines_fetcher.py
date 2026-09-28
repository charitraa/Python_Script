"""
This script fetches the latest news headlines and their corresponding links
from a specified RSS feed (e.g., BBC News Top Stories) using only Python's
standard library. It is designed to be beginner-friendly, demonstrating basic
web request handling and XML parsing.
"""

import urllib.request
import xml.etree.ElementTree as ET

def fetch_headlines(rss_feed_url: str) -> list[dict]:
    """
    Fetches news headlines and their links from a given RSS feed URL.

    Args:
        rss_feed_url (str): The URL of the RSS feed to fetch.

    Returns:
        list[dict]: A list of dictionaries, where each dictionary represents
                    a headline and contains 'title' and 'link' keys.
                    Returns an empty list if there's an error or no headlines found.
    """
    headlines = []
    try:
        # Open the URL and read its content.
        # This acts like opening a file on the internet.
        with urllib.request.urlopen(rss_feed_url) as response:
            # Read all the data from the response. It will be in bytes.
            xml_data = response.read()

        # Parse the XML data. ET.fromstring parses XML directly from a string (or bytes).
        # This converts the XML text into a tree structure that we can navigate.
        root = ET.fromstring(xml_data)

        # RSS feeds typically have a 'channel' element which contains 'item' elements.
        # Each 'item' element represents a single news story.
        channel = root.find('channel')
        if channel is None:
            print(f"Error: Could not find 'channel' element in the RSS feed from {rss_feed_url}")
            return []

        # Iterate through all 'item' elements found within the 'channel'.
        for item in channel.findall('item'):
            # Find the 'title' element within the current 'item'.
            title_element = item.find('title')
            # Find the 'link' element within the current 'item'.
            link_element = item.find('link')

            # Ensure both title and link elements exist and have text content.
            if title_element is not None and title_element.text and \
               link_element is not None and link_element.text:
                headlines.append({
                    "title": title_element.text.strip(), # .strip() removes leading/trailing whitespace
                    "link": link_element.text.strip()
                })

    except urllib.error.URLError as e:
        # Handles network-related errors (e.g., hostname not found, connection refused).
        print(f"Error fetching URL '{rss_feed_url}': {e.reason}")
    except ET.ParseError as e:
        # Handles errors if the downloaded content is not well-formed XML.
        print(f"Error parsing XML from '{rss_feed_url}': {e}")
    except Exception as e:
        # Catch any other unexpected errors.
        print(f"An unexpected error occurred: {e}")

    return headlines

if __name__ == "__main__":
    # Example usage: Fetch headlines from BBC News Top Stories RSS feed.
    # You can replace this URL with any other valid RSS feed URL.
    BBC_NEWS_RSS_URL = "http://feeds.bbci.co.uk/news/rss.xml"

    print(f"Fetching headlines from: {BBC_NEWS_RSS_URL}\n")

    # Call the function to get the headlines.
    latest_headlines = fetch_headlines(BBC_NEWS_RSS_URL)

    # Check if any headlines were returned.
    if latest_headlines:
        print("--- Latest News Headlines ---")
        # Iterate through the list of headline dictionaries and print each one.
        for i, headline in enumerate(latest_headlines):
            print(f"{i+1}. Title: {headline['title']}")
            print(f"   Link: {headline['link']}\n")
    else:
        print("No headlines found or an error occurred during fetching.")
        print("Please check the RSS feed URL or your internet connection.")
