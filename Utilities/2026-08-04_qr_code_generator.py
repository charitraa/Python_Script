"""
This script generates a QR code from user-provided text or a URL and saves it as an image file.
It requires the 'qrcode' package, which can be installed via pip.
"""

# To install the required package, open your terminal or command prompt and run:
# pip install qrcode

import qrcode
import os
import sys

def generate_qr_code(data: str, filename: str):
    """
    Generates a QR code for the given data and saves it to the specified filename.

    Args:
        data (str): The text or URL to encode in the QR code. This cannot be empty.
        filename (str): The name of the file to save the QR code image (e.g., "my_qrcode.png").
                        The file format (e.g., PNG, JPEG) is inferred from the extension.
                        This cannot be empty.

    Raises:
        ValueError: If 'data' or 'filename' is empty.
        Exception: For any other errors during QR code generation or saving.
    """
    if not data:
        raise ValueError("Data to encode cannot be empty. Please provide text or a URL.")
    if not filename:
        raise ValueError("Filename cannot be empty. Please provide a name for the output file.")

    # Create a QR code instance.
    # qrcode.make() is a convenience function that automatically handles
    # optimal QR code version (size) and error correction level based on the data length.
    # It returns a PIL Image object.
    img = qrcode.make(data)

    # Save the generated image to the specified file.
    # The file format (e.g., PNG, JPEG) is determined by the filename extension.
    img.save(filename)

if __name__ == "__main__":
    print("--- Simple QR Code Generator ---")
    print("This script will help you create a QR code from any text or URL you provide.")
    print("The QR code will be saved as an image file in the current directory.")

    # Prompt the user for the data to encode in the QR code
    data_to_encode = input("\nEnter the text or URL you want to encode in the QR code: ")

    # Prompt the user for the desired output filename
    output_filename = input("Enter the desired output filename (e.g., my_qrcode.png): ")

    # Basic validation for the filename
    if not output_filename.strip():
        print("Error: Filename cannot be empty. Using 'default_qrcode.png' as a fallback.")
        output_filename = "default_qrcode.png"
    # Ensure the filename has a common image extension if it's missing one
    elif not (output_filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp"))):
        print(f"Warning: Filename '{output_filename}' does not end with a common image extension (like .png or .jpg). Appending '.png'.")
        output_filename += ".png"

    try:
        # Call the function to generate and save the QR code
        generate_qr_code(data_to_encode, output_filename)
        print(f"\nSuccess! QR code has been generated and saved as '{output_filename}'")
        print(f"You can find the image file in the current directory: {os.getcwd()}")
    except ValueError as ve:
        # Catch specific validation errors raised by generate_qr_code
        print(f"\nError: {ve}")
        sys.exit(1) # Exit with a non-zero status code to indicate an error
    except Exception as e:
        # Catch any other unexpected errors during the process
        print(f"\nAn unexpected error occurred: {e}")
        sys.exit(1) # Exit with a non-zero status code
