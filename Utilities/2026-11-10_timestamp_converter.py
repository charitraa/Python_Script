import datetime
import sys

"""
This script provides functionality to convert between Unix timestamps (seconds since the epoch)
and human-readable datetime strings.

It handles two primary conversions:
1.  Unix Timestamp (UTC) to a local human-readable datetime string.
2.  Local human-readable datetime string to a Unix Timestamp (UTC).

The script uses Python's `datetime` module and is designed to be beginner-friendly.
It includes error handling for invalid inputs and guides the user through the process.
"""

def convert_timestamp_to_local_datetime_string(timestamp, output_format="%Y-%m-%d %H:%M:%S %Z"):
    """
    Converts a Unix timestamp (seconds since the epoch, assumed UTC) into a
    human-readable datetime string in the local timezone.

    Args:
        timestamp (float or int): The Unix timestamp to convert.
        output_format (str, optional): The desired format for the output datetime string.
                                       Defaults to "%Y-%m-%d %H:%M:%S %Z" (e.g., 2023-10-27 10:30:00 CDT).
                                       %Z will include the local timezone abbreviation (e.g., 'CDT', 'GMT').

    Returns:
        str: A string representing the datetime in the local timezone.

    Raises:
        ValueError: If the timestamp is out of the valid range for datetime conversion.
        TypeError: If the timestamp is not a number.
    """
    try:
        # datetime.fromtimestamp() converts a Unix timestamp to a local datetime object.
        # This object is "naive" but strftime will use the system's local timezone for %Z.
        dt_object = datetime.datetime.fromtimestamp(timestamp)
        # Use strftime to format the datetime object into a readable string.
        return dt_object.strftime(output_format)
    except (ValueError, OSError) as e: 
        # ValueError occurs for timestamps out of range, OSError on some systems for extreme values.
        raise ValueError(f"Invalid timestamp value or range error: {e}")
    except TypeError:
        raise TypeError("Timestamp must be a number (integer or float).")

def convert_local_datetime_string_to_timestamp(dt_string, input_format="%Y-%m-%d %H:%M:%S"):
    """
    Converts a human-readable datetime string (assumed to be in the local timezone)
    into a Unix timestamp (seconds since the epoch, UTC).

    Args:
        dt_string (str): The datetime string to convert.
        input_format (str, optional): The format of the input datetime string.
                                      Defaults to "%Y-%m-%d %H:%M:%S".
                                      Ensure this format exactly matches your input string.

    Returns:
        float: The Unix timestamp (UTC) corresponding to the input datetime string.

    Raises:
        ValueError: If the datetime string does not match the input_format.
        TypeError: If the input is not a string.
    """
    try:
        # datetime.strptime() parses a string into a "naive" datetime object
        # (meaning it has no explicit timezone information).
        dt_object = datetime.datetime.strptime(dt_string, input_format)
        # The .timestamp() method on a naive datetime object assumes the datetime
        # is in the local timezone and converts it to a UTC Unix timestamp.
        return dt_object.timestamp()
    except ValueError as e:
        raise ValueError(f"Invalid datetime string or format mismatch. "
                         f"Expected format '{input_format}', got '{dt_string}': {e}")
    except TypeError:
        raise TypeError("Datetime string must be a string.")

if __name__ == "__main__":
    print("Timestamp Converter")
    print("-------------------")
    print("This script converts between Unix timestamps (UTC) and human-readable local datetimes.")
    print("Unix timestamps are always UTC. Datetime strings are interpreted in your local timezone.")
    print("\nExamples:")
    print("  Timestamp to Datetime: Input 1678886400 (which is 2023-03-15 12:00:00 UTC)")
    print("                         Output will be in your local time (e.g., 2023-03-15 08:00:00 EDT if UTC-4).")
    print("  Datetime to Timestamp: Input '2023-10-27 10:30:00' (your local time)")
    print("                         Output will be the equivalent UTC Unix timestamp.")
    print("-------------------\n")

    while True:
        print("Choose an option:")
        print("  1. Convert Unix Timestamp to Local Datetime String")
        print("  2. Convert Local Datetime String to Unix Timestamp")
        print("  3. Exit")

        choice = input("Enter your choice (1, 2, or 3): ").strip()

        if choice == '1':
            while True:
                timestamp_input = input("Enter the Unix timestamp (e.g., 1678886400 or 1678886400.123): ").strip()
                try:
                    # Attempt to convert the input string to a float, allowing for fractional seconds.
                    timestamp = float(timestamp_input)
                    # Call the conversion function with the default output format.
                    formatted_dt = convert_timestamp_to_local_datetime_string(timestamp)
                    print(f"\nResult: {timestamp} (UTC) converts to {formatted_dt} (Local Time)\n")
                    break # Exit the inner loop on successful conversion
                except (ValueError, TypeError) as e:
                    print(f"Error: {e}. Please ensure you enter a valid number for the timestamp.")
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")

        elif choice == '2':
            default_format = "%Y-%m-%d %H:%M:%S"
            while True:
                dt_string_input = input(f"Enter the datetime string (e.g., '2023-10-27 10:30:00' for local time): ").strip()
                
                # Offer the user an option to specify a custom format.
                custom_format_choice = input(f"Use default input format '{default_format}'? (y/n): ").strip().lower()
                input_format = default_format
                if custom_format_choice == 'n':
                    input_format = input("Enter your custom input format (e.g., '%d/%m/%Y %H:%M'): ").strip()
                    if not input_format: # If user enters an empty string, revert to default
                        print(f"No custom format entered. Using default format: '{default_format}'")
                        input_format = default_format

                try:
                    # Call the conversion function.
                    timestamp = convert_local_datetime_string_to_timestamp(dt_string_input, input_format)
                    print(f"\nResult: '{dt_string_input}' (Local Time) with format '{input_format}' converts to {timestamp} (UTC)\n")
                    break # Exit the inner loop on successful conversion
                except (ValueError, TypeError) as e:
                    print(f"Error: {e}. Please ensure your datetime string matches the provided format and is valid.")
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")

        elif choice == '3':
            print("Exiting Timestamp Converter. Goodbye!")
            sys.exit(0) # Exit the script cleanly

        else:
            print("Invalid choice. Please enter '1', '2', or '3'.")
