# pip install Pillow

"""
This script reads and displays EXIF (Exchangeable Image File Format) metadata
from a given image file. EXIF data includes information about the camera,
date/time, location (GPS), and other details captured when a photo is taken.

It is beginner-friendly and uses the widely adopted Pillow library for image
processing, which provides robust EXIF parsing capabilities.
"""

import sys
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def read_exif_metadata(image_path):
    """
    Reads and displays EXIF metadata from a given image file.

    Args:
        image_path (str): The path to the image file.
    """
    print(f"--- Attempting to read EXIF data for: {image_path} ---")
    try:
        # Open the image file using Pillow
        with Image.open(image_path) as img:
            # The _getexif() method returns EXIF data as a dictionary,
            # or None if no EXIF data is found.
            exif_data = img._getexif()

            if exif_data is None:
                print("No EXIF metadata found in this image.")
                return

            print("\nEXIF Metadata:")
            # Iterate through the EXIF data dictionary
            for tag_id, value in exif_data.items():
                # Use TAGS dictionary from PIL.ExifTags to get human-readable
                # names for the EXIF tags. If a tag ID is not found,
                # use the ID itself.
                tag_name = TAGS.get(tag_id, tag_id)

                # Special handling for 'GPSInfo' tag, as its value is another
                # dictionary containing GPS-specific tags.
                if tag_name == 'GPSInfo':
                    print(f"  {tag_name}:")
                    # Iterate through the GPS sub-tags
                    for gps_tag_id, gps_value in value.items():
                        # Use GPSTAGS for human-readable GPS tag names
                        gps_tag_name = GPSTAGS.get(gps_tag_id, gps_tag_id)
                        print(f"    {gps_tag_name}: {gps_value}")
                else:
                    # Print other EXIF tags and their values directly
                    print(f"  {tag_name}: {value}")

    except FileNotFoundError:
        print(f"Error: The file '{image_path}' was not found.")
    except Image.UnidentifiedImageError:
        # This error occurs if the file is not a valid image format
        # or is corrupted.
        print(f"Error: '{image_path}' is not a valid image file or its format is unsupported.")
    except Exception as e:
        # Catch any other unexpected errors during processing
        print(f"An unexpected error occurred: {e}")
    finally:
        print("---------------------------------------")


if __name__ == "__main__":
    # This block runs when the script is executed directly.

    # Check if an image file path was provided as a command-line argument.
    if len(sys.argv) > 1:
        # If an argument is provided, use it as the image path.
        image_file_path = sys.argv[1]
        read_exif_metadata(image_file_path)
    else:
        # If no argument is provided, print usage instructions.
        print("Usage: python exif_reader.py <path_to_image_file>")
        print("\nExample:")
        print("  python exif_reader.py my_vacation_photo.jpg")
        print("  python exif_reader.py C:\\Users\\MyUser\\Pictures\\IMG_0001.JPG")
        print("\nPlease replace '<path_to_image_file>' with the actual path to your image file.")
        print("\nNote: Make sure the image file exists and contains EXIF data (e.g., a photo taken with a digital camera).")
        print("If you don't have one, you can use any photo from your phone or digital camera.")
