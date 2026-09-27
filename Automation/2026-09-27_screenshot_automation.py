"""
This script provides a simple and complete solution for automating full-screen
screenshots on Windows and macOS using the Pillow library.

It includes a function to capture a screenshot and save it with a timestamped
filename in a specified directory, automatically creating the directory if it
doesn't exist.

The script is designed to be beginner-friendly, practical, and fully self-contained.
"""

# pip install Pillow
from PIL import ImageGrab # Used for capturing screenshots
import datetime           # Used for generating unique filenames with timestamps
import os                 # Used for creating directories and path manipulation
import time               # Used for pausing the script in the example

def take_screenshot(directory="screenshots", filename=None):
    """
    Captures a full-screen screenshot and saves it to a specified directory.

    Args:
        directory (str): The path to the directory where the screenshot will be saved.
                         If the directory does not exist, it will be created.
                         Defaults to "screenshots".
        filename (str, optional): The name of the screenshot file (e.g., "my_capture.png").
                                  If None, a timestamp-based filename will be generated
                                  (e.g., "screenshot_2023-10-27_10-30-00.png").
                                  If an extension is not provided, '.png' will be added.
                                  Defaults to None.

    Returns:
        str: The full path to the saved screenshot file, or None if an error occurred.
    """
    # Ensure the output directory exists
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: '{directory}'")

    # Generate a filename if not provided
    if filename is None:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"screenshot_{timestamp}.png"
    elif not any(filename.lower().endswith(ext) for ext in ('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
        # Append .png if no common image extension is provided
        filename = f"{filename}.png"

    # Construct the full path for the screenshot file
    file_path = os.path.join(directory, filename)

    try:
        # Capture the full screen
        # On Windows and macOS, ImageGrab.grab() captures the entire screen.
        # On Linux, ImageGrab.grab() might require a backend like 'scrot' or 'gnome-screenshot'
        # to be installed and accessible. For robust cross-platform support (including Linux
        # without external tools), the 'mss' library is often preferred.
        screenshot = ImageGrab.grab()

        # Save the screenshot
        screenshot.save(file_path)
        print(f"Screenshot saved successfully: '{file_path}'")
        return file_path
    except Exception as e:
        print(f"Error taking screenshot: {e}")
        print("Please ensure you have the necessary permissions and Pillow is correctly installed.")
        print("On some systems (especially Linux), additional tools or libraries might be needed.")
        return None

if __name__ == "__main__":
    # --- Example 1: Take a single screenshot with a default timestamped filename ---
    print("--- Example 1: Taking a single screenshot ---")
    take_screenshot() # Saves to "screenshots/screenshot_YYYY-MM-DD_HH-MM-SS.png"
    print("\n")

    # --- Example 2: Take a screenshot with a custom filename ---
    print("--- Example 2: Taking a screenshot with a custom filename ---")
    take_screenshot(filename="my_specific_capture") # '.png' will be added automatically
    print("\n")

    # --- Example 3: Take multiple screenshots with a delay ---
    print("--- Example 3: Taking multiple screenshots with a delay ---")
    custom_dir = "my_automated_captures"
    num_captures = 3
    delay_seconds = 2

    print(f"Preparing to take {num_captures} screenshots in directory '{custom_dir}' "
          f"with a {delay_seconds}-second delay between each.")
    for i in range(num_captures):
        print(f"Taking screenshot {i+1} of {num_captures}...")
        # Custom filenames for each capture in the loop
        take_screenshot(directory=custom_dir, filename=f"capture_{i+1}.png")
        if i < num_captures - 1: # Don't wait after the last capture
            time.sleep(delay_seconds) # Wait before the next capture
    print("Multiple screenshot capture process complete.")
