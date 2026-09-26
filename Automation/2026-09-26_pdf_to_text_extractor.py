# To install the required library, run: pip install pypdf

"""
PDF to Text Extractor Script

This script provides a function to extract all text content from a given PDF file
and a simple command-line interface example to use it. It leverages the 'pypdf'
library, which is a powerful and widely used tool for PDF manipulation in Python.

Usage:
1. Make sure you have the 'pypdf' library installed (`pip install pypdf`).
2. Replace 'example.pdf' in the `if __name__ == "__main__":` block with the
   path to your target PDF file.
3. Run the script: `python your_script_name.py`
4. The extracted text will be printed to the console and saved to 'extracted_text.txt'.
"""

import sys
from pypdf import PdfReader, errors

def extract_text_from_pdf(pdf_path: str) -> str | None:
    """
    Extracts all text content from a specified PDF file.

    Args:
        pdf_path (str): The file path to the PDF document.

    Returns:
        str: A single string containing all extracted text from the PDF,
             or None if an error occurs during processing.
    """
    try:
        # Create a PdfReader object to read the PDF file.
        # This opens the file in binary read mode ('rb').
        reader = PdfReader(pdf_path)

        # Initialize an empty list to store text from each page.
        full_text_pages = []

        # Iterate through each page in the PDF document.
        # reader.pages provides access to all page objects.
        for page_num, page in enumerate(reader.pages):
            try:
                # Extract text from the current page.
                # The extract_text() method attempts to pull all readable text.
                page_text = page.extract_text()
                if page_text:
                    full_text_pages.append(f"--- Page {page_num + 1} ---\n{page_text}\n\n")
                else:
                    # Handle cases where a page might be empty or unreadable
                    full_text_pages.append(f"--- Page {page_num + 1} (No readable text found) ---\n\n")
            except Exception as e:
                # Catch any page-specific extraction errors
                sys.stderr.write(f"Warning: Could not extract text from page {page_num + 1}: {e}\n")
                full_text_pages.append(f"--- Page {page_num + 1} (Extraction Error) ---\n\n")

        # Join all collected page texts into a single string.
        return "".join(full_text_pages)

    except FileNotFoundError:
        sys.stderr.write(f"Error: The PDF file '{pdf_path}' was not found.\n")
        return None
    except errors.PdfReadError as e:
        sys.stderr.write(f"Error: Could not read PDF file '{pdf_path}'. It might be corrupted or encrypted: {e}\n")
        return None
    except Exception as e:
        sys.stderr.write(f"An unexpected error occurred: {e}\n")
        return None

if __name__ == "__main__":
    # --- Example Usage ---
    # Define the path to your input PDF file.
    # IMPORTANT: Replace 'example.pdf' with the actual path to your PDF.
    # You can create a simple PDF with some text (e.g., from a word processor)
    # and save it as 'example.pdf' in the same directory as this script,
    # or provide a full path like '/home/user/documents/my_report.pdf'.
    input_pdf_path = "example.pdf"

    # Define the path where the extracted text will be saved.
    output_text_file_path = "extracted_text.txt"

    print(f"Attempting to extract text from: {input_pdf_path}")

    # Call the function to extract text.
    extracted_content = extract_text_from_pdf(input_pdf_path)

    if extracted_content:
        # If extraction was successful, print the first 500 characters and save to a file.
        print("\n--- Extracted Text (first 500 chars) ---")
        print(extracted_content[:500])
        if len(extracted_content) > 500:
            print("...")
        print("------------------------------------------")

        # Save the full extracted text to a .txt file.
        try:
            with open(output_text_file_path, "w", encoding="utf-8") as f:
                f.write(extracted_content)
            print(f"\nSuccessfully extracted text and saved to '{output_text_file_path}'")
        except IOError as e:
            sys.stderr.write(f"Error: Could not write to output file '{output_text_file_path}': {e}\n")
    else:
        # If extracted_content is None, an error occurred during extraction.
        print("\nText extraction failed. Please check the error messages above.")
        print(f"Make sure '{input_pdf_path}' exists and is a valid, unencrypted PDF.")
        print("You can try creating a simple PDF (e.g., from a text editor or word processor) and naming it 'example.pdf' in the same directory as this script.")
