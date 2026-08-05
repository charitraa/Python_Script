# pip install pypdf

import os
from pypdf import PdfWriter, PdfReader

def merge_pdfs(input_pdf_paths, output_pdf_path):
    """
    Merges multiple PDF files into a single output PDF file.

    Args:
        input_pdf_paths (list): A list of strings, where each string is the path to an input PDF file.
        output_pdf_path (str): The path where the merged PDF file will be saved.
    """
    # Create a PdfWriter object which will be used to add pages
    # from input PDFs and then write them to the output file.
    merger = PdfWriter()

    print(f"Attempting to merge the following PDFs: {input_pdf_paths}")

    # Iterate through each PDF path provided in the input list
    for pdf_path in input_pdf_paths:
        # Check if the file exists before trying to open it
        if not os.path.exists(pdf_path):
            print(f"Warning: Input PDF file not found at '{pdf_path}'. Skipping this file.")
            continue
        
        try:
            # Add all pages from the current PDF to the merger object.
            # PdfReader is used to read an existing PDF.
            merger.append(pdf_path)
            print(f"Added '{pdf_path}' to the merger.")
        except Exception as e:
            print(f"Error processing '{pdf_path}': {e}. Skipping this file.")
            continue

    # After adding all desired PDFs, write the merged content to an output file.
    if merger.pages: # Check if any pages were actually added
        try:
            with open(output_pdf_path, "wb") as output_file:
                merger.write(output_file)
            print(f"\nSuccessfully merged PDFs into '{output_pdf_path}'")
        except Exception as e:
            print(f"Error writing merged PDF to '{output_pdf_path}': {e}")
    else:
        print("\nNo PDF files were successfully added for merging. No output file was created.")

    # Close the merger object to release resources
    merger.close()

if __name__ == "__main__":
    # --- Example Usage ---

    # 1. Define dummy PDF filenames for demonstration
    dummy_pdf_names = ["dummy_doc1.pdf", "dummy_doc2.pdf", "dummy_doc3.pdf"]
    output_merged_pdf = "merged_output.pdf"

    # 2. Create simple dummy PDF files for testing
    # This ensures the script is fully runnable even without existing PDFs.
    print("Creating dummy PDF files for demonstration...")
    for i, fname in enumerate(dummy_pdf_names):
        writer = PdfWriter()
        # Add a blank page to each dummy PDF
        writer.add_blank_page(width=72, height=72) # A small page
        # You could also add text or more complex content, but for simplicity, a blank page is enough.
        # For a more realistic dummy, one could add a TextStringObject.
        # page = writer.get_page(0)
        # page.add_text("This is Page {i+1} from {fname}") # Requires more advanced usage for placement

        try:
            with open(fname, "wb") as f:
                writer.write(f)
            print(f"Created '{fname}'")
        except Exception as e:
            print(f"Error creating dummy PDF '{fname}': {e}")
            # If dummy files cannot be created, the rest of the script might fail.
            # Handle by exiting or skipping. For this example, we'll let it proceed
            # and the merge_pdfs function will report it.
        writer.close()

    # 3. Call the merge_pdfs function with the dummy files
    print("\n--- Starting PDF Merger ---")
    merge_pdfs(dummy_pdf_names, output_merged_pdf)
    print("--- PDF Merger Finished ---")

    # 4. Clean up the dummy PDF files and the merged output file
    print("\nCleaning up dummy files and merged output...")
    files_to_clean = dummy_pdf_names + [output_merged_pdf]
    for f in files_to_clean:
        if os.path.exists(f):
            try:
                os.remove(f)
                print(f"Removed '{f}'")
            except Exception as e:
                print(f"Error removing '{f}': {e}")
        else:
            print(f"File '{f}' not found, no need to remove.")
    print("Cleanup complete.")
