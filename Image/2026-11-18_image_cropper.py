# To run this script, you'll need the Pillow library. Install it using pip:
# pip install Pillow

import os
from PIL import Image

def crop_image(input_path: str, output_path: str, left: int, upper: int, right: int, lower: int) -> bool:
    """
    Crops an image based on specified coordinates and saves the cropped image.

    Args:
        input_path (str): The file path of the input image.
        output_path (str): The file path where the cropped image will be saved.
        left (int): The x-coordinate of the upper-left corner of the crop box.
        upper (int): The y-coordinate of the upper-left corner of the crop box.
        right (int): The x-coordinate of the lower-right corner of the crop box.
        lower (int): The y-coordinate of the lower-right corner of the crop box.

    Returns:
        bool: True if the image was successfully cropped and saved, False otherwise.
    """
    if not os.path.exists(input_path):
        print(f"Error: Input file not found at '{input_path}'")
        return False

    try:
        # Open the image file
        with Image.open(input_path) as img:
            img_width, img_height = img.size

            # Validate crop coordinates
            if not (0 <= left < right <= img_width and 0 <= upper < lower <= img_height):
                print(f"Error: Invalid crop coordinates for image size ({img_width}x{img_height}).")
                print(f"Crop box: left={left}, upper={upper}, right={right}, lower={lower}")
                return False

            # Define the cropping box as a tuple (left, upper, right, lower)
            crop_box = (left, upper, right, lower)

            # Perform the crop operation
            cropped_img = img.crop(crop_box)

            # Save the cropped image to the specified output path
            cropped_img.save(output_path)
            print(f"Successfully cropped '{input_path}' to '{output_path}'")
            print(f"Crop dimensions: {right-left}x{lower-upper}")
            return True

    except FileNotFoundError:
        print(f"Error: Input file not found at '{input_path}'")
        return False
    except Exception as e:
        print(f"An error occurred during image cropping: {e}")
        return False

if __name__ == "__main__":
    # --- Example Usage ---

    # 1. Create a dummy image for demonstration if it doesn't exist
    dummy_input_image = "example_image.png"
    if not os.path.exists(dummy_input_image):
        print(f"Creating a dummy image '{dummy_input_image}' for demonstration...")
        try:
            # Create a new RGB image with a solid color
            # The size will be 400x300 pixels
            # The color will be a light blue (R=100, G=150, B=200)
            dummy_img = Image.new('RGB', (400, 300), color=(100, 150, 200))
            dummy_img.save(dummy_input_image)
            print(f"Dummy image '{dummy_input_image}' (400x300 pixels) created.")
        except Exception as e:
            print(f"Could not create dummy image. Please ensure Pillow is installed: {e}")
            print("You might need to provide your own 'example_image.png' to run the script.")
            exit()

    # Define paths
    input_image_path = dummy_input_image
    output_cropped_image_path = "cropped_example.png"
    output_cropped_image_path_invalid = "cropped_example_invalid.png"

    # Define cropping coordinates
    # For a 400x300 image, this crops a 150x100 rectangle starting at (50, 100)
    # left: x-coordinate of the upper-left corner
    # upper: y-coordinate of the upper-left corner
    # right: x-coordinate of the lower-right corner
    # lower: y-coordinate of the lower-right corner
    crop_coords = {
        "left": 50,
        "upper": 100,
        "right": 200,  # 50 + 150
        "lower": 200   # 100 + 100
    }

    # Perform a valid crop
    print("\n--- Performing a valid crop ---")
    success = crop_image(
        input_image_path,
        output_cropped_image_path,
        crop_coords["left"],
        crop_coords["upper"],
        crop_coords["right"],
        crop_coords["lower"]
    )

    if success:
        print(f"You can now find the cropped image at '{output_cropped_image_path}'.")
    else:
        print("Valid crop failed.")

    # Demonstrate an invalid crop (coordinates outside image bounds)
    print("\n--- Attempting an invalid crop (out of bounds) ---")
    invalid_crop_coords = {
        "left": 300,
        "upper": 250,
        "right": 500,  # Out of bounds (image width is 400)
        "lower": 350   # Out of bounds (image height is 300)
    }
    success_invalid = crop_image(
        input_image_path,
        output_cropped_image_path_invalid,
        invalid_crop_coords["left"],
        invalid_crop_coords["upper"],
        invalid_crop_coords["right"],
        invalid_crop_coords["lower"]
    )

    if not success_invalid:
        print("Invalid crop correctly prevented.")
    else:
        print("Invalid crop unexpectedly succeeded.")

    # Clean up the dummy image after demonstration
    if os.path.exists(dummy_input_image):
        print(f"\nCleaning up dummy image '{dummy_input_image}'.")
        os.remove(dummy_input_image)
    if os.path.exists(output_cropped_image_path_invalid):
        os.remove(output_cropped_image_path_invalid) # Remove if it was accidentally created
