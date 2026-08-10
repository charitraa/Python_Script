"""
This script provides a simple CSV reader and analyzer.
It reads a specified CSV file, displays its header and the first few data rows (the "head"),
identifies which columns are numeric, and then calculates basic statistics
(count, mean, median, minimum, and maximum) for those numeric columns.

If no CSV file is provided as a command-line argument, it creates a dummy
'sample_data.csv' file for demonstration purposes and analyzes it.
"""

import csv
import statistics
import os
import sys

def analyze_csv(filepath: str, head_rows: int = 5):
    """
    Reads a CSV file, displays its header and first few rows,
    and calculates basic statistics (mean, median, min, max) for numeric columns.

    Args:
        filepath (str): The path to the CSV file.
        head_rows (int): The number of initial data rows to display as "head".
                         Defaults to 5.
    """
    # Check if the file exists
    if not os.path.exists(filepath):
        print(f"Error: File not found at '{filepath}'")
        return

    data = []      # List to store all data rows
    header = []    # List to store the header row
    
    try:
        # Open the CSV file. `newline=''` prevents extra blank rows.
        # `encoding='utf-8'` is a common and robust encoding.
        with open(filepath, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            
            # Attempt to read the header row
            try:
                header = next(reader)
            except StopIteration:
                print(f"Error: CSV file '{filepath}' is empty or only contains a header.")
                return

            # Read all subsequent data rows
            for row in reader:
                data.append(row)

    except Exception as e:
        # Catch any errors during file reading
        print(f"Error reading CSV file '{filepath}': {e}")
        return

    print(f"\n--- CSV Analysis for: {filepath} ---")
    print(f"\nTotal rows (including header): {len(data) + 1}")
    print(f"Total data rows (excluding header): {len(data)}")
    print(f"Total columns: {len(header)}")

    # --- Display Header ---
    print("\n--- Header ---")
    print(", ".join(header))

    # --- Display Head (first few data rows) ---
    print(f"\n--- Head ({min(head_rows, len(data))} data rows) ---")
    if not data:
        print("No data rows found.")
    else:
        for i, row in enumerate(data):
            if i >= head_rows:
                break
            # Ensure row has enough columns to avoid IndexError
            print(", ".join(row[:len(header)])) 

    # --- Identify Numeric Columns and Prepare Data for Statistics ---
    numeric_columns = {} # Stores {column_name: [list_of_float_values]}
    column_types = {}    # Stores {column_name: 'numeric' or 'string'}

    # Iterate through each column by its index
    for col_idx, col_name in enumerate(header):
        current_column_numeric_values = []
        is_col_numeric = True
        
        # Check if all non-empty values in this column can be converted to float
        for row in data:
            # Ensure the row has a value for this column index
            if col_idx < len(row): 
                value_str = row[col_idx].strip() # Remove leading/trailing whitespace
                if value_str: # Only try to convert non-empty strings
                    try:
                        current_column_numeric_values.append(float(value_str))
                    except ValueError:
                        # If conversion fails for any non-empty value, the column is not numeric
                        is_col_numeric = False
                        break # Stop checking this column
            # If a row is shorter than the header, the value for this column is implicitly missing
        
        # If all non-empty values converted successfully AND there was at least one numeric value
        if is_col_numeric and current_column_numeric_values:
            numeric_columns[col_name] = current_column_numeric_values
            column_types[col_name] = 'numeric'
        else:
            # Treat as 'string' if not fully numeric or no numeric values found
            column_types[col_name] = 'string' 

    # --- Display Column Types ---
    print("\n--- Column Data Types ---")
    for col_name, col_type in column_types.items():
        print(f"  {col_name}: {col_type}")

    # --- Calculate and Display Basic Statistics for Numeric Columns ---
    print("\n--- Basic Statistics for Numeric Columns ---")
    if not numeric_columns:
        print("No numeric columns found for statistics.")
    else:
        for col_name, values in numeric_columns.items():
            if values: # Ensure there are values to calculate statistics
                try:
                    mean_val = statistics.mean(values)
                    median_val = statistics.median(values)
                    min_val = min(values)
                    max_val = max(values)
                    
                    print(f"\n  Column: {col_name}")
                    print(f"    Count:  {len(values)}")
                    print(f"    Mean:   {mean_val:.2f}")   # Format to 2 decimal places
                    print(f"    Median: {median_val:.2f}") # Format to 2 decimal places
                    print(f"    Min:    {min_val:.2f}")    # Format to 2 decimal places
                    print(f"    Max:    {max_val:.2f}")    # Format to 2 decimal places
                except statistics.StatisticsError as se:
                    # This error would typically only happen if `values` was empty,
                    # which is already checked by `if values:`.
                    print(f"\n  Column: {col_name}")
                    print(f"    Could not calculate statistics: {se}")
            else:
                print(f"\n  Column: {col_name}")
                print(f"    No numeric values found in this column to calculate statistics.")


if __name__ == "__main__":
    # Define a default CSV file name for demonstration
    demo_csv_filename = "sample_data.csv"

    # If no command-line argument is provided, create a dummy CSV file
    # and use it for analysis.
    if len(sys.argv) < 2:
        print(f"No CSV file specified. Creating a dummy '{demo_csv_filename}' for demonstration.")
        print("You can run this script with your own CSV like: python {os.path.basename(__file__)} my_data.csv")
        
        # Dummy data for the CSV file, including mixed types, empty cells, and non-numeric numbers
        dummy_data = [
            ["ID", "Name", "Age", "Score", "City", "Grade"],
            ["1", "Alice", "24", "88.5", "New York", "A"],
            ["2", "Bob", "30", "75.2", "London", "B"],
            ["3", "Charlie", "22", "92.1", "Paris", "A"],
            ["4", "David", "35", "64.0", "Tokyo", "C"],
            ["5", "Eve", "28", "95.8", "Sydney", "A"],
            ["6", "Frank", "40", "70.0", "Berlin", "B"],
            ["7", "Grace", "", "81.3", "Rome", "A"], # Missing age
            ["8", "Heidi", "29", "text", "Madrid", "B"], # 'Score' column becomes string due to 'text'
            ["9", "Ivan", "26", "77.7", "", "C"], # Missing city
            ["10", "Judy", "33", "89.0", "New York", "A"],
            ["11", "Kelly", "27", "", "London", "B"] # Missing score
        ]

        try:
            # Create the dummy CSV file
            with open(demo_csv_filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(dummy_data)
            print(f"Dummy file '{demo_csv_filename}' created successfully.")
            csv_to_analyze = demo_csv_filename
        except IOError as e:
            print(f"Error creating dummy CSV file: {e}")
            sys.exit(1) # Exit if we can't create the demo file
    else:
        # Use the CSV file path provided as a command-line argument
        csv_to_analyze = sys.argv[1]

    # Run the analysis function with the determined CSV file
    analyze_csv(csv_to_analyze)

    # Clean up the dummy file if it was created by the script for demonstration
    if len(sys.argv) < 2 and os.path.exists(demo_csv_filename):
        try:
            os.remove(demo_csv_filename)
            print(f"\nCleaned up dummy file '{demo_csv_filename}'.")
        except OSError as e:
            print(f"Error cleaning up dummy file '{demo_csv_filename}': {e}")
