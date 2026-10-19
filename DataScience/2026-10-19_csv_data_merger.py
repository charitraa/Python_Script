import csv
import os
from collections import defaultdict

def merge_csv_files(input_filepaths, output_filepath):
    """
    Merges multiple CSV files into a single output CSV file.

    It intelligently handles different columns across input files by:
    1. Identifying all unique column names across all input files to form a 'master header'.
    2. For each row in an input file, it maps the data to the master header,
       filling in empty strings for columns that are present in the master
       header but not in the specific input file's row.
    3. The master header columns in the output file are sorted alphabetically
       for consistent output across runs, regardless of input file order.

    Args:
        input_filepaths (list): A list of paths to the CSV files to merge.
        output_filepath (str): The path to the output merged CSV file.
    """

    if not input_filepaths:
        print("No input CSV files provided. Exiting.")
        return

    # --- Step 1: Determine the master header ---
    # This involves reading the headers from all files to find all unique column names.
    master_column_names = set()
    for filepath in input_filepaths:
        try:
            with open(filepath, 'r', newline='', encoding='utf-8') as infile:
                reader = csv.reader(infile)
                header = next(reader)  # Read the first row as header
                # Filter out any empty strings that might appear if a header row has trailing commas
                master_column_names.update(col.strip() for col in header if col.strip())
        except FileNotFoundError:
            print(f"Warning: Input file not found - {filepath}. Skipping.")
        except StopIteration:
            # This means the file is empty or only has an empty header row
            print(f"Warning: Input file is empty or has no header - {filepath}. Skipping.")
        except Exception as e:
            print(f"Error reading header from {filepath}: {e}. Skipping.")

    # Sort the master column names to ensure consistent output column order
    master_header = sorted(list(master_column_names))
    if not master_header:
        print("No valid headers found in any input files. Cannot merge.")
        return

    # --- Step 2: Write the merged data to the output file ---
    try:
        with open(output_filepath, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(master_header) # Write the master header as the first row

            # Process each input file
            for filepath in input_filepaths:
                try:
                    with open(filepath, 'r', newline='', encoding='utf-8') as infile:
                        reader = csv.reader(infile)
                        file_header = next(reader) # Get the header of the current input file

                        # Create a mapping from column name to its index in the current file
                        # This helps in quickly finding the value for a given column name
                        # We strip headers here as well for robustness against whitespace
                        column_to_index = {col.strip(): i for i, col in enumerate(file_header)}

                        # Iterate over the data rows in the current input file
                        for row_data in reader:
                            # Create an output row initialized with empty strings
                            # This ensures all master header columns are present
                            output_row = [''] * len(master_header)

                            # Populate the output row based on the current file's data
                            for i, master_col_name in enumerate(master_header):
                                # If the master column exists in the current file, get its value
                                if master_col_name in column_to_index:
                                    col_index_in_file = column_to_index[master_col_name]
                                    # Ensure the row_data has enough columns to avoid IndexError
                                    if col_index_in_file < len(row_data):
                                        output_row[i] = row_data[col_index_in_file]
                            writer.writerow(output_row) # Write the prepared row to the output file
                except FileNotFoundError:
                    print(f"Warning: Input file not found - {filepath}. Skipping data from this file.")
                except StopIteration:
                    # This means the file is empty or only has a header row
                    print(f"Warning: Input file is empty or has no data rows after header - {filepath}. Skipping.")
                except Exception as e:
                    print(f"Error processing {filepath}: {e}. Skipping data from this file.")

        print(f"Successfully merged {len(input_filepaths)} files into '{output_filepath}'.")

    except IOError as e:
        print(f"Error writing to output file '{output_filepath}': {e}")
    except Exception as e:
        print(f"An unexpected error occurred during merging: {e}")


if __name__ == "__main__":
    # --- Example Usage ---

    # 1. Create some dummy CSV files for demonstration
    # These files have different sets of columns and different orders.

    # File 1: basic info
    dummy_file1_path = "data_file_1.csv"
    with open(dummy_file1_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Age", "City"])
        writer.writerow(["Alice", "30", "New York"])
        writer.writerow(["Bob", "24", "London"])
        writer.writerow(["Charlie", "35", "Paris"])
    print(f"Created dummy file: {dummy_file1_path}")

    # File 2: contact info, some overlap, some new columns
    dummy_file2_path = "data_file_2.csv"
    with open(dummy_file2_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["City", "Email", "Name"]) # Different order, new column
        writer.writerow(["New York", "alice@example.com", "Alice"])
        writer.writerow(["Berlin", "david@example.com", "David"])
        writer.writerow(["Tokyo", "eve@example.com", "Eve"])
    print(f"Created dummy file: {dummy_file2_path}")

    # File 3: product info, completely different columns (except perhaps an implicit ID)
    # This example shows how rows without common columns are handled -
    # they will still be added, but their specific data won't align to other files' columns.
    dummy_file3_path = "data_file_3.csv"
    with open(dummy_file3_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["ProductID", "Price", "Category"])
        writer.writerow(["P101", "10.99", "Electronics"])
        writer.writerow(["P102", "5.00", "Books"])
    print(f"Created dummy file: {dummy_file3_path}")

    # A file with an empty header to test error handling
    dummy_file_empty_header_path = "data_file_empty_header.csv"
    with open(dummy_file_empty_header_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([]) # An empty header
        writer.writerow(["value1", "value2"])
    print(f"Created dummy file: {dummy_file_empty_header_path}")

    # An empty file to test error handling
    dummy_file_empty_path = "data_file_empty.csv"
    open(dummy_file_empty_path, 'a').close() # Create an empty file
    print(f"Created dummy file: {dummy_file_empty_path}")


    # Define the list of input files to merge
    input_files_to_merge = [
        dummy_file1_path,
        dummy_file2_path,
        dummy_file3_path,
        "non_existent_file.csv", # Test file not found error
        dummy_file_empty_header_path,
        dummy_file_empty_path
    ]

    # Define the output file path
    output_merged_csv_path = "merged_output.csv"

    print("\n--- Starting CSV Merger ---")
    merge_csv_files(input_files_to_merge, output_merged_csv_path)
    print("--- CSV Merger Finished ---")

    print(f"\nMerged CSV file '{output_merged_csv_path}' created.")
    print("You can open it with a spreadsheet program or text editor to inspect the result.")

    # Optional: Clean up the dummy files
    # Uncomment the following lines if you want to remove the created files after running.
    # for f_path in [dummy_file1_path, dummy_file2_path, dummy_file3_path, dummy_file_empty_header_path, dummy_file_empty_path, output_merged_csv_path]:
    #     if os.path.exists(f_path):
    #         os.remove(f_path)
    #         print(f"Cleaned up {f_path}")
