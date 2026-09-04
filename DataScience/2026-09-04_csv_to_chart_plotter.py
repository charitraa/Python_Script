# To run this script, you need to install matplotlib:
# pip install matplotlib

import csv
import matplotlib.pyplot as plt
import argparse
import sys
import os

"""
csv_chart_plotter.py

A Python script that reads data from a CSV file, plots it using Matplotlib,
and can either display the chart or save it to an image file.

It allows specifying the CSV file path, the names of the columns to use for
the X and Y axes, an optional chart title, and an optional output file path
to save the generated chart.

The script is designed to be beginner-friendly, handling common issues like
missing files, invalid column names, and non-numeric data gracefully by
skipping problematic rows and providing informative messages.
"""

def plot_csv_data(
    csv_filepath: str,
    x_column_name: str,
    y_column_name: str,
    title: str = "CSV Data Chart",
    output_filepath: str = None,
    show_plot: bool = True
):
    """
    Reads data from a CSV file, extracts specified columns, and plots a chart.

    Args:
        csv_filepath (str): The path to the input CSV file.
        x_column_name (str): The name of the column to use for the X-axis.
        y_column_name (str): The name of the column to use for the Y-axis.
        title (str, optional): The title of the chart. Defaults to "CSV Data Chart".
        output_filepath (str, optional): If provided, the chart will be saved
                                        to this file path. The file extension
                                        (e.g., .png, .jpg) determines the format.
                                        Defaults to None (chart is not saved).
        show_plot (bool, optional): If True, the chart will be displayed in
                                    a new window. Defaults to True.
    """
    x_data = []
    y_data = []
    
    try:
        with open(csv_filepath, mode='r', newline='', encoding='utf-8') as csvfile:
            # csv.DictReader reads each row as a dictionary where keys are column headers.
            reader = csv.DictReader(csvfile)
            
            # Check if the specified columns exist in the CSV header
            if x_column_name not in reader.fieldnames:
                print(f"Error: X-axis column '{x_column_name}' not found in CSV headers.")
                print(f"Available columns: {', '.join(reader.fieldnames)}")
                return
            if y_column_name not in reader.fieldnames:
                print(f"Error: Y-axis column '{y_column_name}' not found in CSV headers.")
                print(f"Available columns: {', '.join(reader.fieldnames)}")
                return
            
            # Iterate through each row and extract data
            rows_processed = 0
            for i, row in enumerate(reader):
                rows_processed += 1
                try:
                    # Convert data to float. If conversion fails, skip this row.
                    x_val = float(row[x_column_name])
                    y_val = float(row[y_column_name])
                    x_data.append(x_val)
                    y_data.append(y_val)
                except ValueError:
                    print(f"Warning: Skipping row {i+2} due to non-numeric data in "
                          f"'{x_column_name}' ('{row[x_column_name]}') or "
                          f"'{y_column_name}' ('{row[y_column_name]}').")
                except KeyError as e:
                    # This should ideally be caught by fieldnames check at the start,
                    # but included for robustness against malformed rows.
                    print(f"Error: Column '{e}' not found in row {i+2}. This might indicate "
                          "a malformed CSV row after the header check.")
                    return
            
            if not x_data or not y_data:
                print("Error: No valid numeric data found for plotting after processing the CSV.")
                return

    except FileNotFoundError:
        print(f"Error: CSV file not found at '{csv_filepath}'")
        return
    except Exception as e:
        print(f"An unexpected error occurred while reading the CSV file: {e}")
        return

    # --- Plotting with Matplotlib ---
    
    plt.figure(figsize=(10, 6)) # Set the figure size for better readability (width, height)
    # Create a simple line plot with circular markers for each data point
    plt.plot(x_data, y_data, marker='o', linestyle='-', markersize=4, label=f'{x_column_name} vs {y_column_name}')
    
    plt.xlabel(x_column_name) # Label the X-axis with the column name
    plt.ylabel(y_column_name) # Label the Y-axis with the column name
    plt.title(title)           # Set the chart title
    plt.grid(True)             # Add a grid for easier data reading
    plt.legend()               # Display the legend for the plot
    
    plt.tight_layout() # Adjust plot to prevent labels from overlapping
                       # and ensures all elements fit within the figure area.

    # Save the plot if an output path is provided
    if output_filepath:
        try:
            plt.savefig(output_filepath)
            print(f"Chart saved successfully to '{output_filepath}'")
        except Exception as e:
            print(f"Error: Could not save chart to '{output_filepath}': {e}")
            
    # Display the plot if requested
    if show_plot:
        print("Displaying chart...")
        plt.show()

def main():
    """
    Parses command-line arguments and calls the plot_csv_data function.
    """
    parser = argparse.ArgumentParser(
        description="Plot data from a CSV file using specified columns."
    )
    parser.add_argument("csv_file", type=str,
                        help="Path to the input CSV file.")
    parser.add_argument("x_column", type=str,
                        help="Name of the column for the X-axis.")
    parser.add_argument("y_column", type=str,
                        help="Name of the column for the Y-axis.")
    parser.add_argument("--title", type=str, default="CSV Data Chart",
                        help="Optional: Title for the chart.")
    parser.add_argument("--output", type=str,
                        help="Optional: Path to save the generated chart "
                             "(e.g., 'my_chart.png'). If not provided, "
                             "the chart is only displayed unless --no-show is used.")
    parser.add_argument("--no-show", action="store_true",
                        help="Optional: Do not display the chart window. "
                             "Useful when only saving the chart using --output.")

    args = parser.parse_args()

    # Call the plotting function with the parsed arguments
    plot_csv_data(
        csv_filepath=args.csv_file,
        x_column_name=args.x_column,
        y_column_name=args.y_column,
        title=args.title,
        output_filepath=args.output,
        show_plot=not args.no_show # If --no-show is true, then show_plot is False
    )

if __name__ == "__main__":
    # --- Example Usage ---
    # This block demonstrates how to use the script programmatically
    # by creating a dummy CSV and then calling the main function with
    # simulated command-line arguments.

    sample_csv_filename = "sample_data.csv"
    sample_output_filename = "sample_chart.png"

    # Create a dummy CSV file for demonstration
    print(f"Creating a sample CSV file: {sample_csv_filename}")
    with open(sample_csv_filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Time (s)', 'Temperature (C)', 'Humidity (%)', 'Sensor_Status'])
        writer.writerow(['1', '0', '20.5', '60.1', 'OK'])
        writer.writerow(['2', '10', '21.0', '60.5', 'OK'])
        writer.writerow(['3', '20', '21.3', '60.2', 'OK'])
        writer.writerow(['4', '30', '22.1', '61.0', 'OK'])
        writer.writerow(['5', '40', '22.5', 'Error', 'Faulty']) # Introduce bad data in Humidity
        writer.writerow(['6', '50', '23.0', '61.5', 'OK'])
        writer.writerow(['7', '60', 'bad_temp', '61.8', 'OK']) # Another bad data point in Temperature
        writer.writerow(['8', '70', '23.5', '62.0', 'OK'])

    # Save the original sys.argv so we can restore it later
    original_argv = sys.argv[:]

    # --- Example 1: Plotting 'Time (s)' vs 'Temperature (C)' and saving to a file ---
    print("\n--- Running example 1: Plotting 'Time (s)' vs 'Temperature (C)' ---")
    print(f"Chart will be saved to '{sample_output_filename}'")
    sys.argv = [
        "csv_chart_plotter.py",  # Script name (argparse ignores it, but it's conventional)
        sample_csv_filename,     # Required: path to CSV
        "Time (s)",              # Required: X-axis column
        "Temperature (C)",       # Required: Y-axis column
        "--title", "Time vs Temperature Readings (C)", # Optional: Chart title
        "--output", sample_output_filename,           # Optional: Output file path
        # "--no-show" # Uncomment this line if you don't want the plot window to appear
    ]
    main() # Run the main function with simulated arguments

    # Clean up the created CSV and image file for this example
    print(f"\nCleaning up example 1 files...")
    if os.path.exists(sample_output_filename):
        os.remove(sample_output_filename)
        print(f"Removed '{sample_output_filename}'")
    # CSV will be re-created for next example or removed at the very end

    # --- Example 2: Plotting 'Time (s)' vs 'Humidity (%)' (with bad data handling) ---
    print("\n--- Running example 2: Plotting 'Time (s)' vs 'Humidity (%)' ---")
    print("This example will demonstrate skipping rows with non-numeric data.")
    sys.argv = [
        "csv_chart_plotter.py",
        sample_csv_filename,
        "Time (s)",
        "Humidity (%)",
        "--title", "Time vs Humidity Readings (%) (Skipping Errors)",
        # No --output, so it will only display (unless --no-show is active)
    ]
    main() # Run the main function with simulated arguments

    # --- Example 3: Running with an invalid column name to show error handling ---
    print("\n--- Running example 3: Plotting with an invalid column name ---")
    sys.argv = [
        "csv_chart_plotter.py",
        sample_csv_filename,
        "NonExistentColumn",  # This column does not exist in the CSV
        "Temperature (C)",
        "--no-show" # Don't try to display an empty plot
    ]
    main() # Run the main function with simulated arguments
    
    # Restore original sys.argv after all examples
    sys.argv = original_argv

    # Final cleanup of the sample CSV file
    print(f"\nFinal cleanup: removing '{sample_csv_filename}'")
    if os.path.exists(sample_csv_filename):
        os.remove(sample_csv_filename)
        print(f"Removed '{sample_csv_filename}'")

    print("\nAll example usages complete.")
