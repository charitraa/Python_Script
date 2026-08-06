# Required third-party package: Pillow
# You can install it using pip:
# pip install Pillow

import os
from PIL import Image, ImageDraw, ImageFont

"""
This script provides a simple and beginner-friendly way to resize images.

It uses the Pillow library (a well-known image processing package) to open an
image, calculate new dimensions based on either a maximum size or a scaling
factor, and then save the resized image to a new file.

The script includes an example usage block that creates a dummy image if one
doesn't exist, resizes it in two different ways, and then cleans up the dummy
files.
"""

def resize_image(input_path, output_path, max_size=None, scale_factor=None):
    """
    Resizes an image and saves it to a new file.

    The function can resize an image based on a maximum dimension (maintaining
    aspect ratio) or a scaling factor. You must provide either `max_size`
    or `scale_factor`, but not both.

    Args:
        input_path (str): The file path of the input image.
        output_path (str): The file path where the resized image will be saved.
        max_size (tuple, optional): A tuple (width, height) representing the
                                    maximum dimensions. The image will be
                                    resized to fit within these dimensions
                                    while preserving its aspect ratio.
        scale_factor (float, optional): A factor by which to scale the image.
                                        For example, 0.5 for half size, 2.0
                                        for double size.

    Returns:
        bool: True if the image was resized successfully, False otherwise.
    """
    # Ensure exactly one of max_size or scale_factor is provided
    if (max_size is None and scale_factor is None) or \
       (max_size is not None and scale_factor is not None):
        print("Error: You must provide either 'max_size' or 'scale_factor', but not both.")
        return False

    try:
        # Open the image using Pillow
        with Image.open(input_path) as img:
            original_width, original_height = img.size

            new_width, new_height = original_width, original_height # Initialize with original size

            if max_size:
                # Calculate new dimensions based on max_size while maintaining aspect ratio
                max_width, max_height = max_size
                
                # Calculate the ratio needed to fit both dimensions
                width_ratio = max_width / original_width
                height_ratio = max_height / original_height
                
                # Use the smaller ratio to ensure the image fits entirely within
                # the max_width and max_height, preserving its aspect ratio.
                scale_ratio = min(width_ratio, height_ratio)
                
                new_width = int(original_width * scale_ratio)
                new_height = int(original_height * scale_ratio)

            elif scale_factor:
                # Calculate new dimensions based on the provided scale_factor
                new_width = int(original_width * scale_factor)
                new_height = int(original_height * scale_factor)

            # Resize the image using the calculated dimensions
            # Image.LANCZOS is a high-quality filter often used for downsampling.
            resized_img = img.resize((new_width, new_height), Image.LANCZOS)

            # Save the resized image to the specified output path
            # Pillow automatically infers the output format from the file extension.
            resized_img.save(output_path)
            print(f"Successfully resized '{input_path}' to '{output_path}' ({new_width}x{new_height}).")
            return True

    except FileNotFoundError:
        print(f"Error: Input file '{input_path}' not found.")
        return False
    except IOError as e:
        # This catches errors like the file not being a valid image format
        print(f"Error: Could not open or process image file '{input_path}'. Details: {e}")
        return False
    except Exception as e:
        # Catch any other unexpected errors
        print(f"An unexpected error occurred during resizing: {e}")
        return False

if __name__ == "__main__":
    # --- Example Usage ---

    # Define paths for the dummy input and output images
    input_dummy_image = "original_dummy_image.png"
    output_resized_max_size = "resized_by_max_size.png"
    output_resized_scale_factor = "resized_by_scale_factor.png"

    # 1. Create a dummy image for testing if it doesn't exist
    # This makes the script fully runnable out-of-the-box.
    if not os.path.exists(input_dummy_image):
        print(f"Creating a dummy image '{input_dummy_image}' for demonstration...")
        try:
            # Create a large red square image (e.g., 1200x800 pixels)
            dummy_size = (1200, 800)
            # 'RGB' mode for color, (255, 0, 0) for red
            dummy_img = Image.new('RGB', dummy_size, color = (255, 0, 0))
            draw = ImageDraw.Draw(dummy_img)
            
            # Add some text to the dummy image for better illustration
            try:
                # Try to use a common system font (e.g., Arial), size 60
                font = ImageFont.truetype("arial.ttf", 60)
            except IOError:
                # Fallback to the default PIL font if the specified font isn't found
                font = ImageFont.load_default()
            
            # Draw white text on the red background
            draw.text((100, 350), "Original Image (1200x800)", font=font, fill=(255, 255, 255))
            
            dummy_img.save(input_dummy_image)
            print(f"Dummy image '{input_dummy_image}' created successfully ({dummy_size[0]}x{dummy_size[1]}).")
        except Exception as e:
            print(f"Error creating dummy image: {e}")
            print("Please ensure you have write permissions in the current directory, or manually provide an image file.")
            exit() # Exit if we cannot create the necessary dummy image

    print("\n--- Starting Image Resizing Examples ---")

    # Example 1: Resize by maximum dimensions
    # Resize the image to fit within a 300x200 pixel bounding box.
    # The aspect ratio will be maintained, so the output dimensions will be
    # at most 300 pixels wide and at most 200 pixels high.
    print(f"\nAttempting to resize '{input_dummy_image}' to fit within 300x200 pixels...")
    success1 = resize_image(input_dummy_image, output_resized_max_size, max_size=(300, 200))
    if success1:
        print(f"Resized image saved as '{output_resized_max_size}'.")
    else:
        print("Resizing by max dimensions failed.")

    # Example 2: Resize by a scaling factor
    # Resize the image to 50% (half) of its original size.
    print(f"\nAttempting to resize '{input_dummy_image}' to 50% of its original size...")
    success2 = resize_image(input_dummy_image, output_resized_scale_factor, scale_factor=0.5)
    if success2:
        print(f"Resized image saved as '{output_resized_scale_factor}'.")
    else:
        print("Resizing by scale factor failed.")

    print("\n--- Image Resizing Examples Finished ---")

    # --- Clean up dummy files ---
    print("\nCleaning up dummy files created during demonstration...")
    if os.path.exists(input_dummy_image):
        os.remove(input_dummy_image)
        print(f"Removed '{input_dummy_image}'.")
    if os.path.exists(output_resized_max_size):
        os.remove(output_resized_max_size)
        print(f"Removed '{output_resized_max_size}'.")
    if os.path.exists(output_resized_scale_factor):
        os.remove(output_resized_scale_factor)
        print(f"Removed '{output_resized_scale_factor}'.")

    print("Cleanup complete. Script finished.")
