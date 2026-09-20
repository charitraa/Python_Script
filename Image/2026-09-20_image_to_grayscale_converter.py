# pip install Pillow

"""
A Python script to convert a given image file to grayscale.

This script takes an input image path, converts the image to its grayscale
representation, and saves the result to a specified output path. It leverages
the Pillow library for image processing, which is a widely used and powerful
image manipulation tool in Python.

The script includes error handling for common issues like file not found or
problems during image processing. It also provides a self-contained example
in the `if __name__ == "__main__":` block that creates a dummy color image,
converts it, and then cleans up the temporary input file.
"""

import os
import sys
from PIL import Image

def convert_to_grayscale(input_image_path, output_image_path):
    """
    Converts a given image file to grayscale and saves it to a new file.

    Args:
        input_image_path (str): The file path of the input image (e.g., 'my_photo.jpg').
        output_image_path (str): The file path where the grayscale image will be saved
                                 (e.g., 'my_photo_grayscale.png').
                                 The format is inferred from the extension.

    Returns:
        bool: True if the conversion was successful, False otherwise.
    """
    try:
        # Open the image file using Pillow's Image.open() function.
        # The 'with' statement ensures the image file is properly closed
        # after it's no longer needed, even if errors occur.
        with Image.open(input_image_path) as img:
            print(f"Opened image: {input_image_path} (Format: {img.format}, Mode: {img.mode}, Size: {img.size})")

            # Convert the image to grayscale.
            # 'L' mode (Luminance) is used to represent grayscale images.
            # In 'L' mode, each pixel is represented by a single 8-bit value
            # (0-255), where 0 is black and 255 is white.
            grayscale_img = img.convert('L')
            print(f"Converted image to grayscale. New mode: {grayscale_img.mode}")

            # Save the grayscale image to the specified output path.
            # Pillow automatically determines the output format (e.g., PNG, JPEG)
            # based on the file extension provided in 'output_image_path'.
            grayscale_img.save(output_image_path)
            print(f"Successfully saved grayscale image to: {output_image_path}")
            return True

    except FileNotFoundError:
        # Handle cases where the input image file does not exist.
        print(f"Error: Input file not found at '{input_image_path}'", file=sys.stderr)
        return False
    except IOError as e:
        # Handle general I/O errors, such as corrupt image files,
        # or issues with writing the output file.
        print(f"Error: Could not open or save image. Details: {e}", file=sys.stderr)
        return False
    except Exception as e:
        # Catch any other unexpected errors during the process.
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    # --- Working Example Usage ---
    # This block demonstrates how to use the convert_to_grayscale function.
    # It first creates a simple dummy color image, then converts it to grayscale,
    # and finally cleans up the temporary input image to leave no trace.

    example_input_filename = "example_color_image.png"
    example_output_filename = "example_grayscale_image.png"

    # 1. Create a dummy color image for demonstration purposes.
    # This makes the example fully runnable without needing an existing image file.
    try:
        # Image.new(mode, size, color) creates a new image.
        # 'RGB' mode for a full-color image.
        # (200, 150) specifies the width and height in pixels.
        # (255, 0, 0) specifies a solid red color (R, G, B values).
        dummy_image = Image.new('RGB', (200, 150), (255, 0, 0))
        dummy_image.save(example_input_filename)
        print(f"Created a dummy color image: {example_input_filename}")
    except IOError as e:
        print(f"Error: Could not create dummy image '{example_input_filename}'. Details: {e}", file=sys.stderr)
        sys.exit(1) # Exit if we cannot even prepare the input for the example.

    # 2. Attempt to convert the dummy image to grayscale.
    print(f"\nAttempting to convert '{example_input_filename}' to grayscale...")
    success = convert_to_grayscale(example_input_filename, example_output_filename)

    if success:
        print(f"\nExample conversion completed successfully!")
        print(f"You can now find '{example_input_filename}' (original color image) and")
        print(f"'{example_output_filename}' (grayscale version) in the current directory.")
    else:
        print(f"\nExample conversion failed.")

    # 3. Clean up the dummy input image.
    # It's good practice to remove temporary files created by the example.
    if os.path.exists(example_input_filename):
        try:
            os.remove(example_input_filename)
            print(f"\nCleaned up dummy input image: {example_input_filename}")
        except OSError as e:
            print(f"Warning: Could not remove dummy input image '{example_input_filename}'. Details: {e}", file=sys.stderr)

    # Note: The output grayscale image ('example_grayscale_image.png') is left
    # for the user to inspect.
