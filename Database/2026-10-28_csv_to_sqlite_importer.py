"""
This script provides a simple and beginner-friendly way to import data from a CSV file
into an SQLite database table. It automatically creates the table based on the CSV's
header row, treating all columns as TEXT for maximum compatibility.

Key Features:
- Reads a specified CSV file.
- Connects to or creates an SQLite database file.
- Creates a new table (or drops an existing one if specified) using CSV headers as column names.
- Inserts all rows from the CSV into the new SQLite table.
- Handles basic error conditions like file not found or database errors.
- All columns are imported as TEXT data type for simplicity and broad compatibility.
"""

import csv
import sqlite3
import os
import sys

def import_csv_to_sqlite(csv_filepath, db_filepath, table_name, drop_if_exists=True):
    """
    Imports data from a CSV file into an SQLite database table.

    The function creates a new table in the specified SQLite database based on
    the CSV header. All columns are created as TEXT type for simplicity.
    If the table already exists, it can optionally be dropped before creation.

    Args:
        csv_filepath (str): The path to the input CSV file.
        db_filepath (str): The path to the SQLite database file.
        table_name (str): The name of the table to create/update in the database.
        drop_if_exists (bool): If True, drops the table if it already exists
                                before creating a new one. If False and the
                                table exists, an sqlite3.OperationalError will
                                occur when trying to create it with the same name.

    Returns:
        bool: True if the import was successful, False otherwise.
    """
    if not os.path.exists(csv_filepath):
        print(f"Error: CSV file not found at '{csv_filepath}'", file=sys.stderr)
        return False

    conn = None # Initialize conn to None for proper cleanup in finally block
    try:
        # Connect to the SQLite database. If the file doesn't exist, it will be created.
        conn = sqlite3.connect(db_filepath)
        cursor = conn.cursor()

        # Open and read the CSV file
        # 'newline=''' is important to prevent issues with different line endings
        # 'encoding='utf-8'' is standard for handling various characters
        with open(csv_filepath, 'r', newline='', encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile)

            # Read the header row to determine column names
            try:
                header = next(csv_reader)
            except StopIteration:
                print(f"Error: CSV file '{csv_filepath}' is empty or has no header.", file=sys.stderr)
                return False

            # Sanitize column names:
            # - Strip leading/trailing whitespace.
            # - Replace spaces, dots, and hyphens with underscores for valid SQL identifiers.
            # - If a column name becomes empty after sanitization, assign a generic name.
            # - Quote identifiers to handle cases with special characters or SQL keywords.
            sanitized_header = []
            for i, col_name in enumerate(header):
                sanitized_name = col_name.strip().replace(' ', '_').replace('.', '_').replace('-', '_')
                if not sanitized_name:
                    sanitized_name = f"column_{i + 1}" # Fallback for empty names
                sanitized_header.append(f'"{sanitized_name}"') # Quote for safety

            # Prepare the SQL for table creation. All columns are set to TEXT type
            # for maximum compatibility and simplicity in a beginner-friendly script.
            columns_with_types = ", ".join([f"{col} TEXT" for col in sanitized_header])
            
            # If 'drop_if_exists' is True, remove the table if it already exists
            if drop_if_exists:
                drop_table_sql = f"DROP TABLE IF EXISTS {table_name}"
                cursor.execute(drop_table_sql)
                print(f"Info: Dropped existing table '{table_name}' (if it existed).")

            # Create the new table
            create_table_sql = f"CREATE TABLE {table_name} ({columns_with_types})"
            cursor.execute(create_table_sql)
            print(f"Info: Created table '{table_name}' with schema: ({columns_with_types}).")

            # Prepare the INSERT statement
            # The '?' placeholders prevent SQL injection and properly handle data types.
            placeholders = ", ".join(["?" for _ in sanitized_header])
            insert_sql = f"INSERT INTO {table_name} VALUES ({placeholders})"

            # Insert data row by row
            rows_imported = 0
            for row in csv_reader:
                # Basic validation: check if the number of columns matches the header
                if len(row) != len(sanitized_header):
                    print(f"Warning: Skipping row due to column count mismatch. Expected {len(sanitized_header)}, got {len(row)}: {row}", file=sys.stderr)
                    continue
                cursor.execute(insert_sql, row)
                rows_imported += 1

        # Commit the changes to the database
        conn.commit()
        print(f"Success: Imported {rows_imported} rows into table '{table_name}' from '{csv_filepath}'.")
        return True

    except FileNotFoundError:
        print(f"Error: CSV file not found at '{csv_filepath}'", file=sys.stderr)
        return False
    except csv.Error as e:
        print(f"Error reading CSV file '{csv_filepath}': {e}", file=sys.stderr)
        return False
    except sqlite3.Error as e:
        print(f"Error importing to SQLite database '{db_filepath}': {e}", file=sys.stderr)
        return False
    except Exception as e:
        # Catch any other unexpected errors
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        return False
    finally:
        # Ensure the database connection is closed even if an error occurs
        if conn:
            conn.close()
            # print("Info: Database connection closed.") # Uncomment for verbose debugging

if __name__ == "__main__":
    # --- Example Usage ---
    print("--- Starting CSV to SQLite Importer Example ---")

    # 1. Define file paths and table name for the example
    sample_csv_filename = "sample_products.csv"
    sample_db_filename = "my_products_database.db"
    sample_table_name = "products"

    # 2. Create a dummy CSV file for demonstration purposes
    print(f"\nCreating a sample CSV file: '{sample_csv_filename}'")
    csv_content = """product_id,product_name,category,price,stock_quantity
1,Laptop,Electronics,1200.00,50
2,Mouse,Electronics,25.50,150
3,Keyboard,Electronics,75.00,80
4,Monitor,Electronics,300.00,30
5,Desk Chair,Furniture,150.00,100
6,Coffee Table,Furniture,80.00,75
"""
    try:
        with open(sample_csv_filename, 'w', newline='', encoding='utf-8') as f:
            f.write(csv_content)
        print("Sample CSV file created successfully.")
    except IOError as e:
        print(f"Error creating sample CSV file: {e}", file=sys.stderr)
        sys.exit(1) # Exit if the sample CSV can't be created

    # 3. Call the import function to move data from CSV to SQLite
    print(f"\nAttempting to import '{sample_csv_filename}' into '{sample_db_filename}' table '{sample_table_name}'...")
    # 'drop_if_exists=True' makes it easy to re-run the script for testing
    success = import_csv_to_sqlite(sample_csv_filename, sample_db_filename, sample_table_name, drop_if_exists=True)

    if success:
        print("\nImport successful! Verifying data...")
        # 4. Verify the imported data by querying the SQLite database
        conn = None
        try:
            conn = sqlite3.connect(sample_db_filename)
            cursor = conn.cursor()

            # Select all data from the imported table
            # Note: Using f-string for table_name here is safe because `table_name`
            # comes from our script's constant, not untrusted user input.
            cursor.execute(f"SELECT * FROM {sample_table_name}")
            rows = cursor.fetchall()

            # Get column names from the cursor description for a nice output
            column_names = [description[0] for description in cursor.description]
            print(f"Data from '{sample_table_name}':")
            print(" | ".join(column_names))
            print("-" * (sum(len(c) for c in column_names) + 3 * (len(column_names) - 1))) # Simple separator
            for row in rows:
                print(" | ".join(map(str, row))) # Convert all values to string for printing

            # Count total rows to confirm
            cursor.execute(f"SELECT COUNT(*) FROM {sample_table_name}")
            count = cursor.fetchone()[0]
            print(f"\nTotal rows in '{sample_table_name}': {count}")

        except sqlite3.Error as e:
            print(f"Error verifying data from SQLite database: {e}", file=sys.stderr)
        finally:
            if conn:
                conn.close()
    else:
        print("\nCSV import failed. Check error messages above.")

    # 5. Clean up: Remove the generated sample CSV and DB files
    print("\nCleaning up generated files...")
    if os.path.exists(sample_csv_filename):
        os.remove(sample_csv_filename)
        print(f"Removed '{sample_csv_filename}'.")
    if os.path.exists(sample_db_filename):
        os.remove(sample_db_filename)
        print(f"Removed '{sample_db_filename}'.")

    print("\n--- CSV to SQLite Importer Example Finished ---")
