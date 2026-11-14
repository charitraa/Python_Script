"""
This script splits a large file into smaller, user-defined chunks.
It's useful for managing very large files that might be too big to
transfer, upload, or process whole. Each chunk is saved as a new
file with a sequential part number.
"""

import os
import sys

def split_file(input_filepath, chunk_size_mb, output_prefix=None):
    """
    Splits a large file into smaller chunks based on a specified size.

    Args:
        input_filepath (str): The path to the large file to be split.
        chunk_size_mb (int): The desired size of each chunk in megabytes (MB).
        output_prefix (str, optional): A prefix for the output chunk filenames.
                                       If None, the base name of the original
                                       file will be used as the prefix.
    """
    # Check if the input file exists
    if not os.path.exists(input_filepath):
        print(f"Error: Input file '{input_filepath}' not found.")
        return

    # Convert chunk size from megabytes (MB) to bytes
    # 1 MB = 1024 KB, 1 KB = 1024 bytes
    chunk_size_bytes = chunk_size_mb * 1024 * 1024

    # Determine the base name for the output part files.
    # If an output_prefix is provided, use that.
    # Otherwise, use the original filename without its extension.
    if output_prefix:
        base_filename_for_parts = output_prefix
    else:
        # Get just the filename from the path
        original_filename = os.path.basename(input_filepath)
        # Split the filename into name and extension, take only the name part
        base_filename_for_parts = os.path.splitext(original_filename)[0]

    part_num = 0        # Counter for the current part file
    total_parts = 0     # Total number of parts created
    total_bytes_read = 0 # Total bytes processed from the input file

    try:
        # Open the input file in binary read mode ('rb')
        with open(input_filepath, 'rb') as infile:
            print(f"Splitting '{input_filepath}' into chunks of {chunk_size_mb} MB...")
            
            # Loop indefinitely until the end of the input file is reached
            while True:
                # Read a chunk of data from the input file
                chunk = infile.read(chunk_size_bytes)
                
                # If no data was read, it means we've reached the end of the file
                if not chunk:
                    break

                part_num += 1
                # Construct the output filename using the base name and a formatted part number
                # For example: 'my_file.part_001', 'my_file.part_002', etc.
                output_filename = f"{base_filename_for_parts}.part_{part_num:03d}"
                
                # Open the output part file in binary write mode ('wb')
                with open(output_filename, 'wb') as outfile:
                    outfile.write(chunk) # Write the chunk data to the part file
                
                bytes_written = len(chunk)
                total_bytes_read += bytes_written
                total_parts += 1
                print(f"  Created '{output_filename}' ({bytes_written / (1024*1024):.2f} MB)")

        print(f"\nSuccessfully split '{input_filepath}' into {total_parts} parts.")
        print(f"Total data processed: {total_bytes_read / (1024*1024):.2f} MB")

    except IOError as e:
        print(f"Error during file operation: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # --- Example Usage ---

    # Define parameters for the dummy file and splitting
    DUMMY_FILENAME = "example_large_file.bin"
    DUMMY_FILE_SIZE_MB = 15  # Create a 15 MB dummy file
    CHUNK_SIZE_MB_DEMO = 4   # Split it into 4 MB chunks

    print(f"--- Creating a dummy file '{DUMMY_FILENAME}' of {DUMMY_FILE_SIZE_MB} MB ---")
    try:
        # Create a dummy large file for demonstration purposes.
        # This file will be filled with repeating 'A' characters to reach the desired size.
        with open(DUMMY_FILENAME, 'wb') as f:
            # Create a 1 MB block of content
            dummy_content_block = b'A' * (1024 * 1024)
            for _ in range(DUMMY_FILE_SIZE_MB):
                f.write(dummy_content_block)
        print(f"Dummy file '{DUMMY_FILENAME}' created successfully.")
    except IOError as e:
        print(f"Error creating dummy file: {e}")
        sys.exit(1) # Exit if we can't create the dummy file for the demo

    print("\n--- Starting file splitting demonstration ---")
    # Call the split_file function with our dummy file and desired chunk size
    split_file(DUMMY_FILENAME, CHUNK_SIZE_MB_DEMO)
    print("--- File splitting complete ---")

    # --- Cleanup ---
    # Remove the dummy file and all its created parts to clean up the environment
    print("\n--- Cleaning up dummy files and parts ---")
    try:
        # Remove the original dummy file
        if os.path.exists(DUMMY_FILENAME):
            os.remove(DUMMY_FILENAME)
            print(f"Removed original dummy file: '{DUMMY_FILENAME}'.")
        
        # Determine the base name that was used for the part files
        # This should match the logic inside the split_file function
        base_name_for_cleanup = os.path.splitext(os.path.basename(DUMMY_FILENAME))[0]
        
        # Iterate through potential part files and remove them
        part_num_to_check = 1
        removed_any_parts = False
        while True:
            # Construct the filename for a potential part file
            part_filename = f"{base_name_for_cleanup}.part_{part_num_to_check:03d}"
            
            if os.path.exists(part_filename):
                os.remove(part_filename)
                print(f"Removed part file: '{part_filename}'.")
                removed_any_parts = True
                part_num_to_check += 1
            else:
                # If a part file is not found, we've likely processed all created parts
                break
        
        if not removed_any_parts:
             print("No part files were found for cleanup (this might indicate an issue if parts were expected).")
             
    except Exception as e:
        print(f"Error during cleanup: {e}")
    
    print("--- Cleanup complete ---")
