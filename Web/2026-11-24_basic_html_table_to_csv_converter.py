# pip install beautifulsoup4

import csv
from bs4 import BeautifulSoup

def convert_html_table_to_csv(html_content, output_csv_path=None):
    """
    Parses the first HTML table found in the given HTML content and
    converts its data into a list of lists (representing rows and cells).
    Optionally writes this data to a specified CSV file.

    Args:
        html_content (str): A string containing HTML content with at least one table.
        output_csv_path (str, optional): The path to the CSV file where the
                                         table data should be saved. If None,
                                         the data is only returned, not saved.

    Returns:
        list[list[str]]: A list of lists, where each inner list represents a row
                         of the HTML table, and its elements are the string
                         contents of the cells. Returns an empty list if no
                         table is found.
    """
    # Parse the HTML content using BeautifulSoup.
    # 'html.parser' is a built-in parser that works well for general HTML.
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the first <table> tag in the HTML document.
    # For simplicity, this script targets only the first table it finds.
    table = soup.find('table')

    if not table:
        print("No table found in the provided HTML content.")
        return []

    table_data = []

    # Iterate over each row (<tr> tag) in the found table.
    for row in table.find_all('tr'):
        row_data = []
        # Find all header cells (<th>) and data cells (<td>) within the current row.
        # .get_text(strip=True) extracts the text content and removes leading/trailing whitespace.
        # This handles both <th> and <td> elements in a single pass.
        for cell in row.find_all(['th', 'td']):
            row_data.append(cell.get_text(strip=True))
        table_data.append(row_data)

    # If an output CSV path is provided, write the collected data to the CSV file.
    if output_csv_path:
        try:
            # Open the CSV file in write mode ('w').
            # newline='' is crucial for csv.writer to prevent blank rows.
            with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                csv_writer = csv.writer(csvfile)
                # Write all the collected rows to the CSV file.
                csv_writer.writerows(table_data)
            print(f"Table data successfully written to '{output_csv_path}'")
        except IOError as e:
            print(f"Error writing to CSV file '{output_csv_path}': {e}")
    else:
        print("No output CSV path provided. Table data extracted but not saved to file.")

    return table_data

if __name__ == "__main__":
    # --- Example Usage ---

    # 1. Define a sample HTML string containing a simple table.
    # This HTML includes both table headers (<th>) and data cells (<td>).
    # It also has a colspan in the footer, which for simplicity, will be treated
    # as a single cell containing all its text content.
    sample_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sample Table</title>
        <style>
            table, th, td {
                border: 1px solid black;
                border-collapse: collapse;
            }
            th, td {
                padding: 8px;
                text-align: left;
            }
        </style>
    </head>
    <body>

        <h1>My Awesome Data Table</h1>

        <p>This is some introductory text.</p>

        <table>
            <thead>
                <tr>
                    <th>Header A</th>
                    <th>Header B</th>
                    <th>Header C</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Data 1-A</td>
                    <td>Data 1-B</td>
                    <td>Data 1-C</td>
                </tr>
                <tr>
                    <td>Data 2-A</td>
                    <td>Data 2-B with <br>a line break</td>
                    <td>Data 2-C</td>
                </tr>
                <tr>
                    <td>Data 3-A</td>
                    <td>Data 3-B</td>
                    <td>Data 3-C</td>
                </tr>
            </tbody>
            <tfoot>
                <tr>
                    <td colspan="3">Footer Notes: All data is fictional.</td>
                </tr>
            </tfoot>
        </table>

        <p>End of table content.</p>

        <!-- Another table that will be ignored by default (only first table is processed) -->
        <table>
            <tr><td>Ignored A</td><td>Ignored B</td></tr>
        </table>

    </body>
    </html>
    """

    # 2. Define the output CSV file name.
    output_filename = "sample_table_output.csv"

    print("--- Starting HTML Table to CSV Conversion Example ---")

    # 3. Call the converter function with the sample HTML and output file name.
    # The function will print messages indicating its progress.
    extracted_data = convert_html_table_to_csv(sample_html, output_filename)

    # 4. Print the extracted data to the console for verification.
    print("\n--- Extracted Data (list of lists) ---")
    if extracted_data:
        for row_idx, row in enumerate(extracted_data):
            print(f"Row {row_idx + 1}: {row}")
    else:
        print("No data extracted.")

    # 5. Example of converting without saving to a file.
    print("\n--- Example: Converting without saving to file ---")
    temp_html = "<table><tr><th>Name</th><td>Alice</td></tr><tr><th>Age</th><td>30</td></tr></table>"
    in_memory_data = convert_html_table_to_csv(temp_html) # No output_csv_path means not saved
    print("\n--- In-memory Extracted Data ---")
    for row_idx, row in enumerate(in_memory_data):
        print(f"Row {row_idx + 1}: {row}")

    print("\n--- Conversion Example Finished ---")
