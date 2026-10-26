# pip install pytz

import datetime
import pytz

def convert_timezone(dt_obj, source_tz_str, target_tz_str):
    """
    Converts a datetime object from a source timezone to a target timezone.

    This function takes a naive datetime object (without timezone information)
    and assumes it represents a time in the specified `source_tz_str`.
    It then converts this time to the equivalent time in the `target_tz_str`.

    Args:
        dt_obj (datetime.datetime): A naive datetime object (e.g., datetime.datetime(2023, 10, 27, 10, 30, 0)).
                                    This object should *not* have timezone information attached to it.
        source_tz_str (str): The string name of the source timezone (e.g., "America/New_York", "Europe/London", "UTC").
        target_tz_str (str): The string name of the target timezone (e.g., "Asia/Tokyo", "Australia/Sydney", "UTC").

    Returns:
        datetime.datetime: An aware datetime object in the target timezone,
                           or None if any timezone string is invalid.
    """
    try:
        # Get the timezone objects for source and target using pytz.
        # pytz provides a database of timezone information, including daylight saving rules.
        source_tz = pytz.timezone(source_tz_str)
        target_tz = pytz.timezone(target_tz_str)
    except pytz.exceptions.UnknownTimeZoneError as e:
        # Handle cases where an invalid timezone string is provided.
        print(f"Error: Invalid timezone string provided. Please check: {e}")
        return None

    # Localize the input naive datetime object to the source timezone.
    # This step attaches the source timezone information to the datetime object,
    # making it an "aware" datetime object. It assumes the naive_dt is expressed
    # *as if* it were already in the source timezone.
    aware_dt_source = source_tz.localize(dt_obj)

    # Convert the aware datetime object from the source timezone to the target timezone.
    # The .astimezone() method performs the actual conversion, taking into account
    # differences in UTC offsets and daylight saving times between the two timezones.
    aware_dt_target = aware_dt_source.astimezone(target_tz)

    return aware_dt_target

if __name__ == "__main__":
    # --- Example Usage ---

    print("--- Timezone Converter Script ---")

    # 1. Define an initial naive datetime object.
    # This represents a specific date and time without any timezone context.
    # For instance, 10:30 AM on October 27, 2023.
    naive_dt_example = datetime.datetime(2023, 10, 27, 10, 30, 0)
    print(f"\nOriginal Naive Datetime (time before conversion): {naive_dt_example}")

    # 2. Define the source and target timezones using their string identifiers.
    # You can find a comprehensive list of valid timezone strings in `pytz.all_timezones`
    # or `pytz.common_timezones`.
    source_tz_example = "America/New_York"
    target_tz_example = "Europe/London"

    print(f"Source Timezone: {source_tz_example}")
    print(f"Target Timezone: {target_tz_example}")

    # 3. Perform the timezone conversion using the function.
    converted_dt_result = convert_timezone(naive_dt_example, source_tz_example, target_tz_example)

    if converted_dt_result:
        print(f"\nConverted Datetime: {converted_dt_result}")
        print(f"  Date: {converted_dt_result.date()}")
        print(f"  Time: {converted_dt_result.time()}")
        # Display additional details for clarity, showing the timezone name and UTC offset
        print(f"  Timezone Name: {converted_dt_result.tzinfo.tzname(converted_dt_result)}")
        print(f"  UTC Offset: {converted_dt_result.utcoffset()}")
        print(f"  Is DST active in target timezone?: {converted_dt_result.tzinfo.dst(converted_dt_result) != datetime.timedelta(0)}")

    print("\n" + "="*40 + "\n")

    # --- Another Example: Converting from New York to Tokyo ---
    print("--- Another Conversion Example (New York to Tokyo) ---")

    naive_dt_another = datetime.datetime(2023, 10, 27, 18, 0, 0) # 6:00 PM on Oct 27, 2023
    source_tz_another = "America/New_York"
    target_tz_another = "Asia/Tokyo"

    print(f"\nOriginal Naive Datetime: {naive_dt_another}")
    print(f"Source Timezone: {source_tz_another}")
    print(f"Target Timezone: {target_tz_another}")

    converted_dt_another = convert_timezone(naive_dt_another, source_tz_another, target_tz_another)

    if converted_dt_another:
        print(f"\nConverted Datetime: {converted_dt_another}")
        print(f"  Date: {converted_dt_another.date()}")
        print(f"  Time: {converted_dt_another.time()}")
        print(f"  Timezone Name: {converted_dt_another.tzinfo.tzname(converted_dt_another)}")

    print("\n" + "="*40 + "\n")

    # --- Example with an Invalid Timezone String ---
    print("--- Example with Invalid Timezone String ---")

    naive_dt_invalid = datetime.datetime(2023, 1, 1, 12, 0, 0)
    invalid_source_tz = "NonExistent/Timezone" # This will cause an error
    valid_target_tz = "Europe/Berlin"

    print(f"\nAttempting to convert from '{invalid_source_tz}' to '{valid_target_tz}'...")
    invalid_conversion_result = convert_timezone(naive_dt_invalid, invalid_source_tz, valid_target_tz)

    if invalid_conversion_result is None:
        print("Conversion failed as expected due to an invalid timezone string.")
    else:
        print(f"Unexpected success: {invalid_conversion_result}")

    # For beginners: You can inspect available timezones by uncommenting the lines below.
    # print("\n--- First 10 Common Timezones (for reference) ---")
    # for i, tz in enumerate(pytz.common_timezones[:10]):
    #     print(f"  {i+1}. {tz}")
    # print(f"  ...and {len(pytz.common_timezones) - 10} more.")
