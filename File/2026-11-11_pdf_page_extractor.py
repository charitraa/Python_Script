"""
This script provides a function to extract specific pages from a PDF file
and save them into a new PDF file.

It utilizes the PyPDF2 library for PDF manipulation. If you don't have it installed,
you can install it using pip:
pip install PyPDF2
"""

import os
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.errors import PdfReadError

def extract_pdf_pages(input_pdf_path: str, output_pdf_path: str, pages_to_extract: list[int]):
    """
    Extracts specified pages from an input PDF file and saves them to a new output PDF file.

    Args:
        input_pdf_path (str): The file path to the input PDF.
        output_pdf_path (str): The file path where the new PDF with extracted pages will be saved.
        pages_to_extract (list[int]): A list of 1-based page numbers to extract.
                                      For example, [1, 3, 5] to extract the 1st, 3rd, and 5th pages.
    """
    try:
        # Check if the input PDF file exists
        if not os.path.exists(input_pdf_path):
            print(f"Error: Input PDF file not found at '{input_pdf_path}'")
            return

        print(f"Attempting to extract pages {pages_to_extract} from '{input_pdf_path}'...")

        # Open the input PDF in binary read mode
        with open(input_pdf_path, 'rb') as infile:
            reader = PdfReader(infile)
            writer = PdfWriter()

            # Get the total number of pages in the input PDF
            total_pages = len(reader.pages)

            # Validate requested page numbers
            valid_pages_to_extract = []
            for page_num in pages_to_extract:
                if 1 <= page_num <= total_pages:
                    valid_pages_to_extract.append(page_num)
                else:
                    print(f"Warning: Page {page_num} is out of range (1-{total_pages}). It will be skipped.")
            
            if not valid_pages_to_extract:
                print("No valid pages to extract after validation. Exiting.")
                return

            # Add each specified page to the writer.
            # Sorting ensures the output PDF pages are in the requested numerical order.
            for page_num in sorted(valid_pages_to_extract):
                # PyPDF2 uses 0-based indexing for pages, so we subtract 1 from the 1-based page number.
                page_index = page_num - 1
                writer.add_page(reader.pages[page_index])
                print(f"  Added page {page_num}...")

            # Write the new PDF to the output file in binary write mode
            with open(output_pdf_path, 'wb') as outfile:
                writer.write(outfile)

        print(f"Successfully extracted pages to '{output_pdf_path}'")

    except PdfReadError as e:
        print(f"Error reading PDF file '{input_pdf_path}'. It might be corrupted or encrypted: {e}")
    except FileNotFoundError:
        print(f"Error: The file '{input_pdf_path}' was not found. Please check the path.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # --- Example Usage ---

    # Define paths for the input and output PDF files
    input_pdf_filename = "example_input.pdf"
    output_pdf_filename = "extracted_pages.pdf"

    # Define the 1-based page numbers you want to extract.
    # For instance, [1, 3, 5] would extract the first, third, and fifth pages.
    # Try different combinations, e.g., [2, 4], [1, 5], or even [1, 1, 2] to duplicate pages.
    pages_to_get = [1, 3, 5]

    # --- Create a dummy input PDF for demonstration purposes ---
    # This part ensures the example is runnable even if you don't have an existing PDF.
    # In a real scenario, you would replace 'input_pdf_filename' with the path to your actual PDF file.
    if not os.path.exists(input_pdf_filename):
        print(f"Creating a dummy PDF '{input_pdf_filename}' with 5 pages for demonstration...")
        dummy_writer = PdfWriter()
        # Create 5 blank pages of standard Letter size (8.5x11 inches, which is 612x792 points)
        for i in range(5):
            dummy_writer.add_blank_page(width=612, height=792) 
        
        with open(input_pdf_filename, 'wb') as f:
            dummy_writer.write(f)
        print(f"Dummy PDF '{input_pdf_filename}' created successfully. You can open it to see 5 blank pages.")
    else:
        print(f"Using existing PDF '{input_pdf_filename}' for demonstration.")

    # Call the function to extract pages
    extract_pdf_pages(input_pdf_filename, output_pdf_filename, pages_to_get)

    # Optional: Clean up the dummy input PDF after the example runs.
    # Uncomment the following lines if you want the script to remove the generated dummy PDF.
    # if os.path.exists(input_pdf_filename) and input_pdf_filename == "example_input.pdf":
    #     print(f"Cleaning up dummy input PDF: '{input_pdf_filename}'")
    #     os.remove(input_pdf_filename)
    #     print(f"'{input_pdf_filename}' removed.")
