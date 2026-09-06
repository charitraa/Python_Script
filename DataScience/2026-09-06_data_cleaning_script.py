# pip install pandas

import pandas as pd
import os

def clean_data(input_filepath: str, output_filepath: str):
    """
    Performs common data cleaning operations on a CSV file and saves the cleaned data.

    This function takes a CSV file, loads it into a pandas DataFrame, and applies
    several cleaning steps:
    1. Standardizes column names (strips whitespace, converts to lowercase, replaces spaces with underscores).
    2. Handles missing values:
       - Fills numerical columns (Age, Income) with their median.
       - Fills categorical columns (Name, City) with 'Unknown'.
    3. Removes duplicate rows.
    4. Standardizes text data in string columns (strips whitespace, converts to lowercase).
    5. Corrects data types for numerical columns (Age, Income), converting non-numeric
       entries to NaN and then filling those NaNs with the median.

    Args:
        input_filepath (str): The path to the input CSV file that needs cleaning.
        output_filepath (str): The path where the cleaned data will be saved as a CSV file.
    """
    print(f"Loading data from: {input_filepath}")
    try:
        df = pd.read_csv(input_filepath)
        print("Data loaded successfully.")
        print("\n--- Original Data Info ---")
        df.info()
        print("\nMissing values before cleaning:\n", df.isnull().sum())
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_filepath}")
        return
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return

    # --- Step 1: Standardize Column Names ---
    # Strip whitespace, convert to lowercase, and replace spaces with underscores
    original_columns = df.columns.tolist()
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    if original_columns != df.columns.tolist():
        print("\n--- Standardizing Column Names ---")
        print(f"Original: {original_columns}")
        print(f"Cleaned:  {df.columns.tolist()}")

    # --- Step 2: Handle Missing Values & Correct Data Types ---
    # Convert 'Age' and 'Income' to numeric, coercing errors to NaN
    # Then fill these NaNs (and original NaNs) with the median for numerical columns
    # Fill string columns with 'Unknown'
    print("\n--- Handling Missing Values and Correcting Data Types ---")
    for col in ['age', 'income']:
        if col in df.columns:
            # Attempt to convert to numeric, turning non-convertible values into NaN
            df[col] = pd.to_numeric(df[col], errors='coerce')
            # Fill NaN values with the median of the column
            # We calculate median *after* coercing non-numeric to NaN
            median_val = df[col].median()
            if pd.isna(median_val): # If all values are NaN, median is NaN, default to 0 or leave NaN
                 median_val = 0 # Fallback for entirely missing numeric column
            df[col] = df[col].fillna(median_val)
            print(f"Filled missing '{col}' values with median: {median_val}")
            # Ensure age is integer if applicable (after filling)
            if col == 'age':
                df[col] = df[col].astype(int)

    for col in ['name', 'city']:
        if col in df.columns:
            # Fill string NaNs with 'Unknown'
            df[col] = df[col].fillna('Unknown')
            print(f"Filled missing '{col}' values with 'Unknown'")

    # --- Step 3: Remove Duplicate Rows ---
    initial_rows = len(df)
    df.drop_duplicates(inplace=True)
    rows_removed = initial_rows - len(df)
    if rows_removed > 0:
        print(f"\n--- Removing Duplicates ---")
        print(f"Removed {rows_removed} duplicate rows.")
    else:
        print("\nNo duplicate rows found.")


    # --- Step 4: Standardize Text Data ---
    print("\n--- Standardizing Text Data ---")
    string_columns = df.select_dtypes(include='object').columns
    for col in string_columns:
        df[col] = df[col].str.strip().str.lower()
        print(f"Standardized text in column: '{col}'")

    print("\n--- Cleaned Data Info ---")
    df.info()
    print("\nMissing values after cleaning:\n", df.isnull().sum())

    # --- Step 5: Save Cleaned Data ---
    df.to_csv(output_filepath, index=False)
    print(f"\nCleaned data saved to: {output_filepath}")


if __name__ == "__main__":
    # Define file paths
    input_csv_filename = "dirty_data.csv"
    output_csv_filename = "cleaned_data.csv"

    # --- Create a dummy CSV file with dirty data for demonstration ---
    dummy_data = """Name,Age,City,Income,Product_ID
Alice ,25,New York,50000,101
Bob, 30 , London , 60000,102
Charlie,NaN,Paris,75000,103
David,22,New York,NaN,104
Eve,35,London,80000,105
Frank,28,Paris,65000,106
George,,Berlin,90000,107
Hannah,40,New York,70000,108
Alice,25,New York,50000,101  # Exact duplicate of the first row
Jack,32,,72000,109
Karen,invalid,London,55000,110
Liam,29,Paris,68000,111
Mia,30,London,60000,112
Noah,,Berlin,invalid,113
Oliver,26,New York,,114
"""
    with open(input_csv_filename, "w") as f:
        f.write(dummy_data)
    print(f"Created '{input_csv_filename}' with example dirty data.\n")

    # --- Run the data cleaning script ---
    clean_data(input_csv_filename, output_csv_filename)

    # --- Display a sample of the cleaned data ---
    print(f"\n--- Displaying head of '{output_csv_filename}' ---")
    try:
        cleaned_df = pd.read_csv(output_csv_filename)
        print(cleaned_df.head(10).to_string())
    except Exception as e:
        print(f"Could not read cleaned data: {e}")

    # --- Optional: Clean up the dummy files ---
    # uncomment the lines below if you want to remove the generated CSV files
    # print(f"\nCleaning up generated files: {input_csv_filename}, {output_csv_filename}")
    # os.remove(input_csv_filename)
    # os.remove(output_csv_filename)
    # print("Files removed.")
