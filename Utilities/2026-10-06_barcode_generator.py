# pip install python-barcode Pillow

import barcode
from barcode.writer import ImageWriter
import os

"""
This script generates various types of barcodes (e.g., EAN-13, Code 128)
and saves them as image files (PNG by default).

It leverages the 'python-barcode' library for encoding barcode data
and 'Pillow' (PIL) for image generation.
"""

def generate_barcode(
    data: str,
    output_filename: str,
    barcode_type: str = 'ean13',
    options: dict = None
) -> str:
    """
    Generates a barcode image and saves it to a file.

    Args:
        data (str): The data to encode in the barcode.
                    - For 'ean13', this should be a 12-digit number string.
                      The 13th checksum digit is calculated automatically.
                    - For 'ean8', this should be a 7-digit number string.
                    - For 'code128', this can be any string.
        output_filename (str): The base name for the output file (e.g., "my_barcode").
                               The script will append the correct extension (e.g., ".png").
        barcode_type (str, optional): The type of barcode to generate.
                                      Common types include 'ean13', 'code128', 'ean8'.
                                      Defaults to 'ean13'.
        options (dict, optional): A dictionary of options to customize the barcode image.
                                  These options are passed to the ImageWriter.save() method.
                                  Common options include:
                                  - 'module_height': Height of the bars in mm.
                                  - 'font_size': Size of the text below the barcode.
                                  - 'text_distance': Distance between the barcode and the text.
                                  - 'quiet_zone': Width of the quiet zone (empty space) around the barcode.
                                  - 'write_text': Boolean to enable/disable text below the barcode.
                                  - 'dpi': Dots per inch for image resolution.
                                  Defaults to None, using ImageWriter's defaults.

    Returns:
        str: The full path to the generated barcode image file, or None if an error occurred.

    Raises:
        ValueError: If the data is invalid for the specified barcode type (e.g., EAN-13 requires 12 digits).
        barcode.errors.BarcodeError: For other issues during barcode generation by the library.
    """
    # Ensure options is a dictionary, even if None was passed
    options = options if options is not None else {}

    try:
        # Perform basic validation for common fixed-length barcode types
        if barcode_type == 'ean13':
            if not (data.isdigit() and len(data) == 12):
                raise ValueError(f"EAN-13 barcode requires a 12-digit number string, got '{data}' (length {len(data)})")
        elif barcode_type == 'ean8':
            if not (data.isdigit() and len(data) == 7):
                raise ValueError(f"EAN-8 barcode requires a 7-digit number string, got '{data}' (length {len(data)})")
        # For other types like Code 128, data length is more flexible and handled by the library itself.

        # Get the barcode class for the specified type
        # The 'writer=ImageWriter()' tells the barcode library to use Pillow (PIL)
        # to render the barcode as an image.
        BarcodeClass = barcode.get(barcode_type)
        barcode_instance = BarcodeClass(data, writer=ImageWriter())

        # Save the barcode image to a file.
        # The save method will append the appropriate file extension (e.g., .png)
        # and return the full path to the saved file.
        full_path = barcode_instance.save(output_filename, options=options)

        # Return the absolute path for clarity in output
        return os.path.abspath(full_path)

    except ValueError as e:
        print(f"Error: Invalid data for barcode type '{barcode_type}': {e}")
        return None
    except barcode.errors.BarcodeError as e:
        # Catch errors specifically from the barcode library (e.g., illegal characters)
        print(f"Error generating barcode '{barcode_type}' with data '{data}': {e}")
        return None
    except Exception as e:
        # Catch any other unexpected errors
        print(f"An unexpected error occurred during barcode generation: {e}")
        return None

if __name__ == "__main__":
    print("--- Barcode Generator Script ---")
    print("This script will generate sample barcode images in the current directory.")

    # --- Example 1: Generate a simple EAN-13 barcode ---
    # EAN-13 is commonly used for retail products. It requires 12 digits for input.
    ean13_data = "123456789012"
    ean13_filename = "product_ean13_barcode"
    print(f"\nAttempting to generate EAN-13 barcode for data: {ean13_data}")
    generated_file_ean13 = generate_barcode(ean13_data, ean13_filename, barcode_type='ean13')
    if generated_file_ean13:
        print(f"Successfully generated EAN-13 barcode: {generated_file_ean13}")

    # --- Example 2: Generate a Code 128 barcode with custom options ---
    # Code 128 is versatile, can encode alphanumeric data, often used in logistics.
    code128_data = "Hello World! 123 ABC"
    code128_filename = "shipping_code128_barcode"
    custom_options = {
        'module_height': 10,  # Shorter bars in millimeters
        'font_size': 8,       # Smaller text size below the barcode
        'text_distance': 3,   # Reduced distance between barcode and text
        'quiet_zone': 4,      # Smaller empty space around the barcode
        'write_text': True,   # Explicitly ensure human-readable text is written
        'dpi': 300            # Higher resolution for better print quality
    }
    print(f"\nAttempting to generate Code 128 barcode for data: '{code128_data}' with custom options")
    generated_file_code128 = generate_barcode(code128_data, code128_filename, barcode_type='code128', options=custom_options)
    if generated_file_code128:
        print(f"Successfully generated Code 128 barcode: {generated_file_code128}")

    # --- Example 3: Generate an EAN-8 barcode ---
    # EAN-8 is a shorter version of EAN-13, used for small products. Requires 7 digits.
    ean8_data = "9876543"
    ean8_filename = "small_product_ean8_barcode"
    print(f"\nAttempting to generate EAN-8 barcode for data: {ean8_data}")
    generated_file_ean8 = generate_barcode(ean8_data, ean8_filename, barcode_type='ean8')
    if generated_file_ean8:
        print(f"Successfully generated EAN-8 barcode: {generated_file_ean8}")

    # --- Example 4: Demonstrate error handling for invalid EAN-13 data ---
    invalid_ean13_data = "12345" # This data is too short for EAN-13
    invalid_ean13_filename = "invalid_ean13_barcode"
    print(f"\nAttempting to generate EAN-13 barcode with invalid data: '{invalid_ean13_data}'")
    generated_file_invalid = generate_barcode(invalid_ean13_data, invalid_ean13_filename, barcode_type='ean13')
    if not generated_file_invalid:
        print("Barcode generation failed as expected for invalid EAN-13 data (too short).")

    print("\nScript finished. Check your current directory for generated barcode images (e.g., .png files).")
