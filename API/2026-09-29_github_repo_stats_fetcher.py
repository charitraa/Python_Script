"""
This script fetches and displays various statistics for a specified GitHub repository.
It queries the GitHub API to retrieve details such as star count, fork count,
open issues, last update time, and more, for a given owner and repository name.

This script uses only Python's standard library modules, making it fully self-contained
without requiring any `pip install` commands.
"""

import urllib.request
import urllib.error
import json
import sys
from datetime import datetime

def get_github_repo_stats(owner, repo_name):
    """
    Fetches statistics for a GitHub repository using its API.

    Args:
        owner (str): The username or organization that owns the repository.
        repo_name (str): The name of the repository.

    Returns:
        dict: A dictionary containing key repository statistics if successful,
              otherwise None.
    """
    # Construct the GitHub API URL for the repository
    api_url = f"https://api.github.com/repos/{owner}/{repo_name}"

    try:
        # Create a Request object. It's good practice to include a User-Agent header
        # when making web requests, as some APIs (including GitHub's) may require it
        # or use it for rate limiting and logging purposes.
        headers = {'User-Agent': 'Python Repo Stats Fetcher'}
        req = urllib.request.Request(api_url, headers=headers)

        # Open the URL and send the HTTP GET request
        with urllib.request.urlopen(req) as response:
            # Read the response body, which comes as bytes
            response_body = response.read()
            # Decode the bytes into a string using UTF-8, then parse the JSON
            repo_data = json.loads(response_body.decode('utf-8'))

            # Extract desired statistics from the parsed JSON data
            stats = {
                "name": repo_data.get("name"),
                "full_name": repo_data.get("full_name"),
                "description": repo_data.get("description"),
                "html_url": repo_data.get("html_url"),
                "stargazers_count": repo_data.get("stargazers_count"),
                "forks_count": repo_data.get("forks_count"),
                "open_issues_count": repo_data.get("open_issues_count"),
                "language": repo_data.get("language"),
                "updated_at": repo_data.get("updated_at")
            }
            return stats

    except urllib.error.HTTPError as e:
        # Handle HTTP errors, such as 404 (Not Found) or 403 (Forbidden due to rate limiting)
        if e.code == 404:
            print(f"Error: Repository '{owner}/{repo_name}' not found. Please check the owner and repository name.", file=sys.stderr)
        elif e.code == 403:
            print(f"Error: Access forbidden, potentially due to GitHub API rate limiting (60 requests/hour for unauthenticated). Try again later.", file=sys.stderr)
        else:
            print(f"Error fetching data from GitHub API: HTTP {e.code} - {e.reason}", file=sys.stderr)
        return None
    except urllib.error.URLError as e:
        # Handle network-related errors (e.g., no internet connection, invalid URL)
        print(f"Error: Could not connect to GitHub API. Please check your internet connection or the URL. Reason: {e.reason}", file=sys.stderr)
        return None
    except json.JSONDecodeError:
        # Handle cases where the response from the API is not valid JSON
        print(f"Error: Failed to decode JSON response from GitHub API for '{owner}/{repo_name}'.", file=sys.stderr)
        return None
    except Exception as e:
        # Catch any other unexpected errors that might occur
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        return None

def print_repo_stats(stats):
    """
    Prints the provided repository statistics in a user-friendly, formatted way.

    Args:
        stats (dict): A dictionary containing repository statistics, typically
                      returned by `get_github_repo_stats`.
    """
    if not stats:
        print("No statistics to display.", file=sys.stderr)
        return

    print("\n--- GitHub Repository Statistics ---")
    print(f"Repository:   {stats.get('full_name', 'N/A')}")
    print(f"URL:          {stats.get('html_url', 'N/A')}")
    # Display description, handling cases where it might be empty or None
    description = stats.get('description')
    print(f"Description:  {description if description else '[No description provided]'}")
    print(f"Language:     {stats.get('language', 'N/A')}")
    print(f"Stars:        {stats.get('stargazers_count', 'N/A')}")
    print(f"Forks:        {stats.get('forks_count', 'N/A')}")
    print(f"Open Issues:  {stats.get('open_issues_count', 'N/A')}")

    # Format the 'updated_at' timestamp for better readability
    updated_at_str = stats.get('updated_at')
    if updated_at_str:
        try:
            # GitHub API returns timestamps in ISO 8601 format (e.g., "YYYY-MM-DDTHH:MM:SSZ")
            # Parse it into a datetime object
            dt_object = datetime.strptime(updated_at_str, "%Y-%m-%dT%H:%M:%SZ")
            # Format the datetime object into a more human-readable string
            print(f"Last Updated: {dt_object.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        except ValueError:
            # If the timestamp format is unexpected, print it as is
            print(f"Last Updated: {updated_at_str} (format error)")
    else:
        print(f"Last Updated: N/A")
    print("------------------------------------")


if __name__ == "__main__":
    # This block runs only when the script is executed directly (not imported as a module).
    # It provides an example of how to use the functions defined above.

    # Default values for repository owner and name.
    # These will be used if no command-line arguments are provided.
    default_owner = "pallets"
    default_repo = "flask"

    owner = default_owner
    repo_name = default_repo

    # Check if command-line arguments are provided by the user.
    # sys.argv is a list of command-line arguments; sys.argv[0] is the script name.
    if len(sys.argv) == 3:
        # If two arguments are given, use them as owner and repo_name
        owner = sys.argv[1]
        repo_name = sys.argv[2]
        print(f"Fetching stats for {owner}/{repo_name} (from command-line arguments)...")
    elif len(sys.argv) > 1:
        # If an incorrect number of arguments (more than 1 but not 3) is given,
        # print a usage message and exit.
        print("Usage: python github_repo_stats.py [owner] [repo_name]", file=sys.stderr)
        sys.exit(1) # Exit with an error code
    else:
        # If no arguments are given, use the default owner and repo_name
        print(f"No command-line arguments provided. Fetching stats for default repository: {owner}/{repo_name}...")
        print("To fetch for another repository, run: python github_repo_stats.py <owner> <repo_name>\n")


    # Call the function to fetch repository statistics
    repo_stats = get_github_repo_stats(owner, repo_name)

    # If statistics were successfully fetched, print them
    if repo_stats:
        print_repo_stats(repo_stats)
    else:
        # If `get_github_repo_stats` returned None, an error message would have
        # already been printed, so we just add a general failure message.
        print("Failed to retrieve repository statistics.", file=sys.stderr)
