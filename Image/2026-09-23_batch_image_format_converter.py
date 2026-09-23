# To install the required third-party package:
# pip install Pillow

"""
This script provides a beginner-friendly command-line tool for converting batches
of image files from various formats to a specified target format.

It iterates through a given input directory, identifies common image files,
and converts them, saving the results to an output directory.

Supported input formats depend on the Pillow library, which includes most
common image formats like JPEG, PNG, BMP, GIF, TIFF, WebP, etc.

Usage:
  python your_script_name.py -i <input_directory> -o <output_directory> -f <target_format>

Example:
  python batch_converter.py -i images_in -o images_out -f png
  This will convert all images in 'images_in' to PNG format and save them in 'images_out'.
"""

import os
import argparse
from PIL import Image
from PIL import UnidentifiedImageError

def convert_images(input_dir: str, output_dir: str, target_format: str):
    """
    Converts all supported image files in an input directory to a specified
    target format and saves them to an output directory.

    Args:
        input_dir (str): The path to the directory containing input images.
        output_dir (str): The path to the directory where converted images will be saved.
        target_format (str): The desired output format (e.g., 'png', 'jpeg', 'webp').
    """
    # Ensure the output directory exists, create it if it doesn't
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    # Convert the target format to lowercase for consistency
    target_format_lower = target_format.lower()

    print(f"\nStarting image conversion from '{input_dir}' to '{output_dir}' (format: {target_format_lower})...")
    converted_count = 0
    skipped_count = 0
    error_count = 0

    # Iterate over all files in the input directory
    for filename in os.listdir(input_dir):
        input_filepath = os.path.join(input_dir, filename)

        # Check if it's a file and not a directory
        if os.path.isfile(input_filepath):
            try:
                # Open the image file
                with Image.open(input_filepath) as img:
                    # Get the filename without its extension
                    base_name = os.path.splitext(filename)[0]
                    
                    # Construct the output filename with the new format
                    output_filename = f"{base_name}.{target_format_lower}"
                    output_filepath = os.path.join(output_dir, output_filename)

                    # Save the image in the target format
                    # For JPEG, it's often good to specify quality.
                    # 'optimize=True' can help reduce file size.
                    if target_format_lower == 'jpeg' or target_format_lower == 'jpg':
                        # Convert to RGB mode if not already (e.g., for PNGs with alpha channel)
                        # JPEGs do not support alpha channels.
                        if img.mode in ('RGBA', 'P'):
                            img = img.convert('RGB')
                        img.save(output_filepath, quality=90, optimize=True)
                    else:
                        img.save(output_filepath, optimize=True)

                    print(f"  Converted '{filename}' to '{output_filename}'")
                    converted_count += 1

            except UnidentifiedImageError:
                print(f"  Skipped '{filename}': Not a recognized image file.")
                skipped_count += 1
            except Exception as e:
                print(f"  Error converting '{filename}': {e}")
                error_count += 1
        else:
            print(f"  Skipped '{filename}': Not a file (might be a directory).")
            skipped_count += 1

    print("\n--- Conversion Summary ---")
    print(f"Successfully converted: {converted_count} images")
    print(f"Skipped (non-images/directories): {skipped_count} items")
    print(f"Errors encountered: {error_count} items")
    print("------------------------")
    print("Conversion complete!")


if __name__ == "__main__":
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(
        description="Batch Image Format Converter using Pillow.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "-i", "--input",
        type=str,
        default="test_images_input", # Default input directory for easy testing
        help="Path to the directory containing input images."
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="test_images_output", # Default output directory
        help="Path to the directory to save converted images."
    )
    parser.add_argument(
        "-f", "--format",
        type=str,
        default="png", # Default target format
        help="Desired output image format (e.g., 'png', 'jpeg', 'webp', 'bmp', 'gif')."
    )

    args = parser.parse_args()

    # --- Example Usage for Testing ---
    # This block creates dummy images if the input directory doesn't exist,
    # making the script fully runnable for demonstration purposes.
    if not os.path.exists(args.input):
        print(f"Creating example input directory '{args.input}' and dummy images...")
        os.makedirs(args.input)
        try:
            # Create a dummy JPEG image
            img_jpeg = Image.new('RGB', (100, 50), color = 'red')
            img_jpeg.save(os.path.join(args.input, 'example_red.jpg'))
            
            # Create a dummy PNG image with transparency
            img_png = Image.new('RGBA', (100, 50), color = (0, 0, 255, 128)) # Blue with 50% opacity
            img_png.save(os.path.join(args.input, 'example_blue.png'))

            # Create another dummy JPEG to test mixed formats
            img_gif = Image.new('RGB', (80, 80), color = 'green')
            img_gif.save(os.path.join(args.input, 'example_green.gif'))
            
            # Create a non-image file to test skipping
            with open(os.path.join(args.input, 'not_an_image.txt'), 'w') as f:
                f.write("This is not an image file.")

            print("Dummy images and text file created for testing.")
        except Exception as e:
            print(f"Error creating dummy images: {e}")
            print("Please ensure Pillow is installed: 'pip install Pillow'")
            exit(1)

    # Call the conversion function with the parsed arguments
    convert_images(args.input, args.output, args.format)

    print(f"\nCheck the '{args.output}' directory for the converted images.")
    if os.path.exists(args.output):
        print("Files in output directory:")
        for f in os.listdir(args.output):
            print(f"- {f}")
    else:
        print("Output directory was not created (likely due to errors).")
