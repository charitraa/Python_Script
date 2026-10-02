# pip install feedparser

"""
A beginner-friendly Python script to fetch and display entries from an RSS feed.

This script uses the 'feedparser' library to parse RSS/Atom feeds,
extracting information like title, link, publication date, and summary for each entry.
It aims to be practical and easy to understand for learners, providing
clear output and handling common scenarios like missing data or parsing errors.
"""

import feedparser
import datetime
import textwrap

def read_rss_feed(feed_url: str):
    """
    Fetches and displays entries from a given RSS feed URL.

    Args:
        feed_url (str): The URL of the RSS or Atom feed to read.
    """
    print(f"--- Attempting to fetch RSS feed from: {feed_url} ---")
    print("-" * (len(feed_url) + 40))

    try:
        # Use feedparser to parse the RSS feed.
        # This function automatically handles fetching the content
        # from the URL and parsing it into a Python object.
        feed = feedparser.parse(feed_url)

        # Check for potential parsing errors or network issues.
        # 'feed.bozo' is True if there were problems.
        if feed.bozo:
            print(f"Warning: Could not parse feed completely. Error: {feed.bozo_exception}")
            # If no entries are found even with a bozo exception, there's nothing to display.
            if not feed.entries:
                print("No entries found, possibly due to severe parsing error or an empty feed.")
                return

        # If no entries are found after parsing (e.g., empty feed or invalid URL content)
        if not feed.entries:
            print("No entries found in the feed. The URL might not be a valid RSS/Atom feed or it's empty.")
            return

        # Display general feed information
        print(f"\nFeed Title: {feed.feed.get('title', 'N/A')}")
        print(f"Feed Link: {feed.feed.get('link', 'N/A')}")
        # 'subtitle' is common for Atom, 'description' for RSS.
        print(f"Feed Description: {feed.feed.get('subtitle', feed.feed.get('description', 'N/A'))}")
        print("\n--- Latest Entries ---")

        # Iterate through each entry in the feed
        for i, entry in enumerate(feed.entries):
            print(f"\nEntry {i + 1}:")

            # Get the title, defaulting to 'No Title' if not present.
            # Strip whitespace for cleaner display.
            title = entry.get('title', 'No Title').strip()
            # Wrap the title for better readability on narrow terminals.
            # The 'initial_indent' is empty because we prepend "  Title: " outside textwrap.
            print("  Title: " + textwrap.fill(title, initial_indent='', subsequent_indent='         ', width=70))

            # Get the link, defaulting to 'No Link'.
            link = entry.get('link', 'No Link')
            print(f"  Link: {link}")

            # Get and format the published date.
            # feedparser provides 'published' (raw string) and 'parsed_published' (time.struct_time).
            # We convert 'parsed_published' to a datetime object for easy custom formatting.
            published_date_str = "N/A"
            if 'parsed_published' in entry and entry.parsed_published:
                try:
                    dt_object = datetime.datetime(*entry.parsed_published[:6])
                    published_date_str = dt_object.strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    # Fallback if datetime conversion fails for some reason
                    published_date_str = entry.get('published', 'N/A')
            else:
                published_date_str = entry.get('published', 'N/A')
            print(f"  Published: {published_date_str}")

            # Get the summary/description.
            # 'summary_detail.value' often provides a cleaner text without HTML tags,
            # especially if the original 'summary' contains HTML.
            if 'summary_detail' in entry and 'value' in entry.summary_detail:
                summary = entry.summary_detail.value.strip()
            else:
                summary = entry.get('summary', 'No Summary').strip()

            # Truncate long summaries for brevity to avoid overwhelming the output.
            max_summary_length = 300
            if len(summary) > max_summary_length:
                summary = summary[:max_summary_length] + "..."

            # Wrap the summary text with proper indentation for readability.
            wrapped_summary = textwrap.fill(summary, initial_indent='  Summary: ', subsequent_indent='           ', width=70)
            print(wrapped_summary)

    except Exception as e:
        print(f"An unexpected error occurred while processing the feed: {e}")
        print("Please check the URL and your internet connection.")

if __name__ == "__main__":
    # --- Example Usage ---

    # Example 1: A well-known technology news feed (The Verge)
    print("--- Reading The Verge RSS Feed ---")
    tech_feed_url = "https://www.theverge.com/rss/index.xml"
    read_rss_feed(tech_feed_url)

    print("\n" + "="*80 + "\n") # Separator for readability

    # Example 2: A general news feed (NPR Top Stories)
    print("--- Reading NPR Top Stories RSS Feed ---")
    news_feed_url = "https://feeds.npr.org/1001/rss.xml"
    read_rss_feed(news_feed_url)

    print("\n" + "="*80 + "\n") # Separator

    # Example 3: An intentionally invalid URL to demonstrate error handling
    print("--- Reading an Invalid URL (expecting error) ---")
    invalid_feed_url = "http://www.example.com/not-an-rss-feed.xml"
    read_rss_feed(invalid_feed_url)

    print("\n" + "="*80 + "\n") # Separator

    # Example 4: A valid URL that might not contain an RSS feed (e.g., a simple HTML page)
    # This often results in a 'bozo' exception but might still try to parse.
    print("--- Reading a Regular Website (expecting issues or no entries) ---")
    regular_website_url = "https://www.python.org"
    read_rss_feed(regular_website_url)
