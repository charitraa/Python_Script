"""
This script is a simple log file analyzer.

It reads a specified log file, counts occurrences of different log levels
(e.g., ERROR, WARNING, INFO), identifies unique error messages, and
reports the most frequent log entries. It's designed to be beginner-friendly
and provide a quick overview of a log file's contents.
"""

import argparse
import re
from collections import Counter
import os
import sys

def analyze_log_file(filepath):
    """
    Analyzes a log file to extract insights like log level counts,
    unique error messages, and most frequent log lines.

    Args:
        filepath (str): The path to the log file to be analyzed.

    Returns:
        dict: A dictionary containing the analysis results, including:
              - 'total_lines': Total number of lines processed.
              - 'log_level_counts': A Counter object with counts for each log level.
              - 'unique_errors': A list of unique error messages found.
              - 'most_frequent_lines': A list of (count, line) tuples for the top N frequent lines.
    """
    total_lines = 0
    log_level_counts = Counter()
    unique_errors = set()  # Use a set to automatically handle uniqueness of error messages
    all_lines = Counter()  # To count frequency of exact lines

    # Regex to find common log levels at the start of a line or after a timestamp/date pattern.
    # It looks for words like ERROR, WARNING, INFO, DEBUG, CRITICAL, FATAL.
    # The \b ensures whole word matching. re.IGNORECASE makes it case-insensitive.
    log_level_pattern = re.compile(
        r'\b(ERROR|WARNING|INFO|DEBUG|CRITICAL|FATAL)\b', re.IGNORECASE
    )

    try:
        # Open the file, using 'utf-8' encoding and 'errors='ignore'' for robustness
        # in case of malformed characters in log files.
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                total_lines += 1
                stripped_line = line.strip()
                if not stripped_line:
                    continue  # Skip empty lines

                all_lines[stripped_line] += 1  # Count frequency of this exact line

                match = log_level_pattern.search(stripped_line)
                if match:
                    # Get the matched log level and convert it to uppercase for consistency
                    level = match.group(1).upper()
                    log_level_counts[level] += 1

                    # If it's an error, critical, or fatal message, store it as a unique error.
                    if level in ['ERROR', 'CRITICAL', 'FATAL']:
                        # Extract the message part: everything after the log level word and any separator.
                        # This is a simple heuristic; more complex log formats might need custom parsing.
                        message_start_index = match.end()
                        message = stripped_line[message_start_index:].strip()
                        # Clean up common separators (e.g., ':', '-', ' ') at the beginning of the message
                        message = re.sub(r'^[ :\-]+', '', message)
                        # Add to unique_errors. If message is empty after stripping, use the full line.
                        unique_errors.add(message if message else stripped_line)
                else:
                    # If no recognizable log level is found, categorize it as 'UNKNOWN'.
                    log_level_counts['UNKNOWN'] += 1
    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while reading the file: {e}")
        return None

    # Get the top 10 most frequent lines. Change the number to see more or fewer.
    most_frequent_lines = all_lines.most_common(10)

    # Convert the set of unique errors to a sorted list for consistent output.
    sorted_unique_errors = sorted(list(unique_errors))

    return {
        'total_lines': total_lines,
        'log_level_counts': log_level_counts,
        'unique_errors': sorted_unique_errors,
        'most_frequent_lines': most_frequent_lines,
    }

def main():
    """
    Parses command-line arguments, analyzes the specified log file,
    and prints the analysis report.
    """
    # Set up argument parsing for the command line.
    parser = argparse.ArgumentParser(
        description="A simple log file analyzer to count log levels, "
                    "find unique errors, and identify frequent log entries."
    )
    parser.add_argument(
        "logfile",
        help="Path to the log file to analyze."
    )
    args = parser.parse_args()

    print(f"Analyzing log file: '{args.logfile}'...\n")

    analysis_results = analyze_log_file(args.logfile)

    if analysis_results:
        print("--- Log Analysis Report ---")
        print(f"Total Lines: {analysis_results['total_lines']}")

        print("\nLog Level Counts:")
        if analysis_results['log_level_counts']:
            # Print log levels sorted by their count in descending order.
            for level, count in analysis_results['log_level_counts'].most_common():
                print(f"  {level:<10}: {count}")
        else:
            print("  No log levels identified.")

        print("\nUnique Error/Critical/Fatal Messages:")
        if analysis_results['unique_errors']:
            # Print each unique error message with an index.
            for i, error in enumerate(analysis_results['unique_errors'], 1):
                print(f"  {i}. {error}")
        else:
            print("  No unique error messages found.")

        print("\nTop 10 Most Frequent Log Lines:")
        if analysis_results['most_frequent_lines']:
            # Print the top 10 most frequent log lines and their counts.
            for count, line in analysis_results['most_frequent_lines']:
                print(f"  ({count}x) {line}")
        else:
            print("  No repetitive log lines found.")
        print("\n--- End of Report ---")
    else:
        print("Log analysis could not be completed due to previous errors.")

if __name__ == "__main__":
    # --- Example Usage ---
    # This block demonstrates how to run the script.
    # It first creates a dummy log file named 'example.log' if it doesn't exist,
    # then simulates running the script with this file as an argument.

    dummy_log_filename = "example.log"

    # Create a dummy log file for demonstration purposes.
    # In a real scenario, you would typically run this script against an existing log file.
    if not os.path.exists(dummy_log_filename):
        print(f"Creating a dummy log file: '{dummy_log_filename}' for demonstration.")
        with open(dummy_log_filename, 'w', encoding='utf-8') as f:
            f.write("2023-10-27 10:00:01 INFO: Application started.\n")
            f.write("2023-10-27 10:00:02 DEBUG: Connecting to database...\n")
            f.write("2023-10-27 10:00:03 INFO: User 'john.doe' logged in.\n")
            f.write("2023-10-27 10:00:04 WARNING: Low disk space on /tmp.\n")
            f.write("2023-10-27 10:00:05 ERROR: Failed to connect to database. Retrying...\n")
            f.write("2023-10-27 10:00:06 INFO: Processing user data.\n")
            f.write("2023-10-27 10:00:07 DEBUG: Data validation successful.\n")
            f.write("2023-10-27 10:00:08 WARNING: Low disk space on /tmp.\n")
            f.write("2023-10-27 10:00:09 ERROR: Failed to connect to database. Retrying...\n")
            f.write("2023-10-27 10:00:10 INFO: Application shutdown.\n")
            f.write("2023-10-27 10:00:11 CRITICAL: System critical error: Out of memory!\n")
            f.write("2023-10-27 10:00:12 DEBUG: Another debug message.\n")
            f.write("2023-10-27 10:00:13 ERROR: Database connection lost permanently.\n")
            f.write("This is a line without a clear log level, so it will be 'UNKNOWN'.\n")
            f.write("2023-10-27 10:00:14 INFO: Processing user data.\n")  # Repeated line
            f.write("2023-10-27 10:00:15 INFO: Processing user data.\n")  # Repeated line
            f.write("2023-10-27 10:00:16 INFO: Processing user data.\n")  # Repeated line
            f.write("2023-10-27 10:00:17 ERROR - Permission denied for user 'guest'.\n")
            f.write("2023-10-27 10:00:18 FATAL: Unrecoverable error.\n")
            f.write("Another line with INFO level: User logged out.\n")
            f.write("2023-10-27 10:00:19 ERROR: Failed to connect to database. Retrying...\n") # Repeated error message
            f.write("2023-10-27 10:00:20 WARNING: Cache limit reached.\n")
            f.write("2023-10-27 10:00:21 WARNING: Cache limit reached.\n") # Repeated warning

    # Modify sys.argv to simulate command-line arguments.
    # This allows the argparse module to function as if the script was run from the terminal.
    # The first element 'log_analyzer.py' is the script name itself.
    sys.argv = [sys.argv[0], dummy_log_filename]

    main()

    # Optional: Clean up the dummy log file after demonstration.
    # Uncomment the following lines if you want the script to remove the dummy file
    # after it runs.
    # if os.path.exists(dummy_log_filename):
    #     os.remove(dummy_log_filename)
    #     print(f"\nCleaned up dummy log file: '{dummy_log_filename}'")
