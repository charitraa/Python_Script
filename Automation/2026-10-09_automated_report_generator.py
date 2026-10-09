"""
This script generates a simple HTML report from data provided in a CSV file.
It reads item details (Item, Quantity, Price), calculates total sales value,
and summarizes the data in an easy-to-read HTML format.

The generated report includes:
- A title with the current date and time.
- Summary statistics (total items, total sales value).
- A table displaying all items with their quantities, unit prices, and line totals.

The script is designed to be beginner-friendly, practical, and fully self-contained.
It only uses standard Python libraries.
"""

import csv
import datetime
import os # Used to create a dummy CSV file for the example


def generate_report(csv_file_path, output_html_path):
    """
    Reads data from a CSV file, performs basic analysis, and generates an HTML report.

    Args:
        csv_file_path (str): The path to the input CSV file.
        output_html_path (str): The path where the generated HTML report will be saved.
    """
    items_data = []
    total_sales_value = 0.0
    total_distinct_items = 0

    # Attempt to read the CSV file
    try:
        with open(csv_file_path, mode='r', newline='', encoding='utf-8') as csv_file:
            # Use csv.DictReader to read rows as dictionaries,
            # which makes accessing columns by name easier.
            reader = csv.DictReader(csv_file)
            
            # Check if required headers exist
            required_headers = ['Item', 'Quantity', 'Price']
            if not all(header in reader.fieldnames for header in required_headers):
                print(f"Error: CSV file must contain headers: {', '.join(required_headers)}")
                return

            for row in reader:
                try:
                    item_name = row['Item']
                    # Convert Quantity and Price to numeric types for calculations
                    quantity = int(row['Quantity'])
                    price = float(row['Price'])
                    
                    # Calculate the total value for this specific item row
                    line_total = quantity * price
                    
                    items_data.append({
                        'item': item_name,
                        'quantity': quantity,
                        'price': price,
                        'line_total': line_total
                    })
                    
                    total_sales_value += line_total

                except ValueError as e:
                    print(f"Skipping row due to data conversion error: {row} - {e}")
                except KeyError as e:
                    print(f"Skipping row due to missing column: {row} - {e}")

    except FileNotFoundError:
        print(f"Error: The CSV file '{csv_file_path}' was not found.")
        return
    except Exception as e:
        print(f"An unexpected error occurred while reading the CSV: {e}")
        return

    # Calculate total distinct items (count unique item names)
    # A set is used to store unique item names
    distinct_item_names = {item['item'] for item in items_data}
    total_distinct_items = len(distinct_item_names)
    
    # Get current date and time for the report
    report_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Start building the HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sales Report - {report_date}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f4; color: #333; }}
            .container {{ max-width: 900px; margin: auto; background: #fff; padding: 25px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            h1 {{ color: #0056b3; text-align: center; margin-bottom: 20px; }}
            h2 {{ color: #0056b3; border-bottom: 1px solid #eee; padding-bottom: 10px; margin-top: 30px; }}
            .summary p {{ font-size: 1.1em; line-height: 1.6; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
            th {{ background-color: #f2f2f2; color: #333; }}
            .footer {{ text-align: center; margin-top: 40px; font-size: 0.9em; color: #777; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Automated Sales Report</h1>
            <p style="text-align: center; color: #666;">Generated on: {report_date}</p>

            <h2>Summary Statistics</h2>
            <div class="summary">
                <p><strong>Total Distinct Items Sold:</strong> {total_distinct_items}</p>
                <p><strong>Total Sales Value:</strong> ${total_sales_value:,.2f}</p>
            </div>

            <h2>Detailed Item List</h2>
            <table>
                <thead>
                    <tr>
                        <th>Item Name</th>
                        <th>Quantity</th>
                        <th>Unit Price</th>
                        <th>Line Total</th>
                    </tr>
                </thead>
                <tbody>
    """

    # Add each item row to the HTML table
    if not items_data:
        html_content += """
                    <tr>
                        <td colspan="4" style="text-align: center;">No data available to display.</td>
                    </tr>
        """
    else:
        for item in items_data:
            html_content += f"""
                    <tr>
                        <td>{item['item']}</td>
                        <td>{item['quantity']}</td>
                        <td>${item['price']:,.2f}</td>
                        <td>${item['line_total']:,.2f}</td>
                    </tr>
            """

    # Close the HTML tags
    html_content += f"""
                </tbody>
            </table>

            <div class="footer">
                <p>&copy; {datetime.datetime.now().year} Automated Report Generator</p>
            </div>
        </div>
    </body>
    </html>
    """

    # Save the HTML content to the output file
    try:
        with open(output_html_path, mode='w', encoding='utf-8') as html_file:
            html_file.write(html_content)
        print(f"Report successfully generated at: {output_html_path}")
    except IOError as e:
        print(f"Error: Could not write the HTML report to '{output_html_path}'. {e}")
    except Exception as e:
        print(f"An unexpected error occurred while writing the HTML file: {e}")


if __name__ == "__main__":
    # --- Example Usage ---

    # Define the names for our input CSV and output HTML files
    input_csv_file = "sales_data.csv"
    output_html_file = "sales_report.html"

    # 1. Create a dummy CSV file for demonstration purposes.
    # In a real scenario, this file would already exist.
    sample_data = [
        ['Item', 'Quantity', 'Price'],
        ['Laptop', 1, 1200.50],
        ['Mouse', 5, 25.00],
        ['Keyboard', 2, 75.00],
        ['Monitor', 1, 300.00],
        ['Webcam', 3, 50.00],
        ['Speaker', 2, 80.00],
        ['Headphones', 4, 45.00],
        ['USB Drive', 10, 15.00],
        # Example of a row with bad data (will be skipped by error handling)
        ['Invalid Item', 'abc', 100.00],
        ['Another Item', 1, 'xyz'],
        # Example of a valid row
        ['Desk Lamp', 3, 35.00],
    ]

    print(f"Creating dummy CSV file: {input_csv_file}...")
    try:
        with open(input_csv_file, mode='w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerows(sample_data)
        print("Dummy CSV file created successfully.")
    except Exception as e:
        print(f"Error creating dummy CSV: {e}")
        # If we can't create the CSV, there's no point proceeding
        exit()

    # 2. Call the report generation function
    print(f"\nGenerating report from '{input_csv_file}' to '{output_html_file}'...")
    generate_report(input_csv_file, output_html_file)

    # 3. Clean up the dummy CSV file after generation (optional)
    # You might want to remove this line if you wish to inspect the CSV.
    if os.path.exists(input_csv_file):
        # os.remove(input_csv_file)
        # print(f"\nCleaned up dummy CSV file: {input_csv_file}")
        pass # Keeping the CSV for user inspection after run

    print("\nTo view the report, open 'sales_report.html' in your web browser.")
