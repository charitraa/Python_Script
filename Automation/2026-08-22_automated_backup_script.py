"""
Automated Backup Script

This script creates a timestamped zip archive of a specified source directory
and saves it to a designated destination directory. It's designed to be
beginner-friendly, practical, and suitable for scheduling (e.g., with cron
on Linux/macOS or Task Scheduler on Windows).

It includes basic error handling and logs its actions to the console.

Configuration:
- SOURCE_DIR: The directory you want to back up.
- DESTINATION_DIR: The directory where the backup archives will be stored.

Example Usage (within if __name__ == "__main__": block):
1. Creates a dummy source directory with some files for testing.
2. Runs the backup process using the configured SOURCE_DIR and DESTINATION_DIR.
3. Prints status messages to the console during the process.
4. Cleans up the dummy source directory after the backup demonstration.
"""

import os
import shutil
import datetime
import logging

# --- Configuration Variables ---
# IMPORTANT: Update these paths to match your system.
# The directory you want to back up.
# For example: SOURCE_DIR = "/home/user/my_important_docs" (Linux/macOS)
# For example: SOURCE_DIR = "C:\\Users\\YourUser\\Documents\\MyProject" (Windows)
# Using os.path.expanduser and a hidden directory for a safe testing example:
SOURCE_DIR = os.path.expanduser("~/.my_backup_source_data")

# The directory where you want to store your backup archives.
# This directory must exist and be writable by the script.
# For example: DESTINATION_DIR = "/mnt/backups/daily" (Linux/macOS)
# For example: DESTINATION_DIR = "D:\\Backups" (Windows)
# Using os.path.expanduser and a hidden directory for a safe testing example:
DESTINATION_DIR = os.path.expanduser("~/.my_backups_archives")

# --- Logger Setup ---
# Configure logging to output messages to the console.
logging.basicConfig(
    level=logging.INFO,  # Set to logging.DEBUG for more detailed output
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def perform_backup(source_path: str, destination_path: str) -> None:
    """
    Performs the backup operation.

    Creates a timestamped zip archive of the `source_path` directory
    and saves it to the `destination_path`.

    Args:
        source_path (str): The absolute path to the directory to be backed up.
        destination_path (str): The absolute path to the directory where
                                the backup archive will be stored.
    """
    logger.info(f"Starting backup process...")
    logger.info(f"Source directory: '{source_path}'")
    logger.info(f"Destination directory: '{destination_path}'")

    # --- Validate Source Path ---
    if not os.path.exists(source_path):
        logger.error(f"Error: Source directory '{source_path}' does not exist. Aborting backup.")
        return
    if not os.path.isdir(source_path):
        logger.error(f"Error: Source path '{source_path}' is not a directory. Aborting backup.")
        return

    # --- Prepare Destination Directory ---
    # Ensure the destination directory exists. Create it if it doesn't.
    if not os.path.exists(destination_path):
        logger.info(f"Destination directory '{destination_path}' does not exist. Creating it...")
        try:
            os.makedirs(destination_path, exist_ok=True) # exist_ok=True prevents error if it somehow exists already
        except OSError as e:
            logger.error(f"Error creating destination directory '{destination_path}': {e}. Aborting backup.")
            return
    elif not os.path.isdir(destination_path):
        logger.error(f"Error: Destination path '{destination_path}' is not a directory. Aborting backup.")
        return

    # --- Prepare Archive Name ---
    # Get the name of the source directory (e.g., "my_important_docs")
    source_dir_name = os.path.basename(source_path)
    # Generate a timestamp for the backup file (e.g., "20231027_103000")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    # Construct the base name for the archive (e.g., "my_important_docs_20231027_103000")
    archive_base_name = f"{source_dir_name}_{timestamp}"
    # Construct the full path to the archive without the .zip extension
    output_filepath_no_ext = os.path.join(destination_path, archive_base_name)

    logger.info(f"Attempting to create archive: '{os.path.basename(output_filepath_no_ext)}.zip'")

    # --- Create Archive ---
    try:
        # shutil.make_archive(base_name, format, root_dir=None, base_dir=None)
        # base_name: The full path to the archive file (without the format extension).
        # format: The archive format (e.g., 'zip', 'tar', 'gztar').
        # root_dir: The directory from which to start archiving.
        # base_dir: The directory that will be the top-level directory inside the archive.
        # To archive '/path/to/my_data' and have 'my_data/' as the top-level
        # directory inside the zip:
        # root_dir = '/path/to' (the parent of my_data)
        # base_dir = 'my_data' (the name of the directory itself)
        archive_path = shutil.make_archive(
            output_filepath_no_ext,       # The desired full path and name for the output archive
            'zip',                        # The archive format
            root_dir=os.path.dirname(source_path), # The parent directory of the source_path
            base_dir=source_dir_name      # The name of the source directory itself
        )
        logger.info(f"Backup successful! Archive created at: '{archive_path}'")

    except PermissionError as e:
        logger.error(f"Permission denied: Unable to write to '{destination_path}'. "
                     f"Please check directory permissions. Error: {e}")
    except shutil.Error as e:
        logger.error(f"Shutil error during archive creation: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during backup: {e}", exc_info=True)

# --- Example Usage ---
if __name__ == "__main__":
    logger.info("--- Automated Backup Script Started ---")

    # --- Setup a dummy source directory and files for testing ---
    # This block will create temporary files and directories to demonstrate the script.
    # In a real-world scenario, you would only define SOURCE_DIR and DESTINATION_DIR
    # at the top of the script.
    
    logger.info(f"Setting up dummy source directory at: {SOURCE_DIR}")
    os.makedirs(SOURCE_DIR, exist_ok=True) # Create the dummy source directory

    # Create some dummy files within the source directory
    try:
        with open(os.path.join(SOURCE_DIR, "document1.txt"), "w") as f:
            f.write("This is an important document.\n")
            f.write("It contains valuable information for the backup test.")
        with open(os.path.join(SOURCE_DIR, "notes.md"), "w") as f:
            f.write("# My Backup Notes\n- Item 1\n- Item 2\n- Test data here")

        # Create a subdirectory with another file
        dummy_subdir = os.path.join(SOURCE_DIR, "project_configs")
        os.makedirs(dummy_subdir, exist_ok=True)
        with open(os.path.join(dummy_subdir, "config.ini"), "w") as f:
            f.write("[Settings]\nversion=1.0\nauthor=BackupScript\n")
        logger.info("Dummy files and subdirectories created successfully in the source.")
    except IOError as e:
        logger.error(f"Could not create dummy files in '{SOURCE_DIR}': {e}")
        # The script will still attempt to back up the (possibly empty) directory.

    logger.info(f"Ensuring destination directory exists: {DESTINATION_DIR}")
    os.makedirs(DESTINATION_DIR, exist_ok=True) # Ensure dummy destination exists

    # --- Run the backup process with the defined paths ---
    perform_backup(SOURCE_DIR, DESTINATION_DIR)

    # --- Optional: Cleanup dummy source directory ---
    # In a real-world, scheduled backup scenario, you would NOT clean up
    # your actual source directory! This is strictly for demonstration
    # purposes to leave your system clean after running the example.
    logger.info(f"Cleaning up dummy source directory: {SOURCE_DIR}")
    try:
        shutil.rmtree(SOURCE_DIR)
        logger.info("Dummy source directory removed successfully.")
    except OSError as e:
        logger.error(f"Error removing dummy source directory '{SOURCE_DIR}': {e}")

    logger.info(f"Backup process finished. Please check '{DESTINATION_DIR}' for the created backup archive.")
    logger.info("--- Automated Backup Script Finished ---")
