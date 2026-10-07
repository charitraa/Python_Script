"""
This script provides a simple command-line file and directory compression/decompression tool.
It uses the standard `zipfile` module to create and extract ZIP archives.

Features:
- Compress a single file into a ZIP archive.
- Compress an entire directory (including subdirectories and files) into a ZIP archive.
- Decompress a ZIP archive into a specified directory.

Usage:
To run this script from the command line, you need to provide arguments for the action,
input path, and output path.

Example Command Line Usage:
# Compress a single file:
python your_script_name.py --action compress --input my_file.txt --output my_file.zip

# Compress an entire directory:
python your_script_name.py --action compress --input my_folder --output my_folder.zip

# Decompress a ZIP archive:
python your_script_name.py --action decompress --input my_archive.zip --output extracted_content
"""

import zipfile
import os
import argparse
import shutil # Used for cleanup in the example

def compress_file_or_directory(input_path, output_zip_path):
    """
    Compresses a file or an entire directory into a ZIP archive.

    Args:
        input_path (str): The path to the file or directory to be compressed.
        output_zip_path (str): The desired path for the output ZIP archive.
    """
    # Ensure the parent directory for the output zip exists
    os.makedirs(os.path.dirname(output_zip_path), exist_ok=True)

    try:
        # Open the ZIP file in write mode
        with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            if os.path.isfile(input_path):
                # If it's a file, just add it to the zip.
                # arcname specifies the name of the file inside the zip,
                # using os.path.basename ensures it's just the file name, not its full path.
                zf.write(input_path, arcname=os.path.basename(input_path))
                print(f"Successfully compressed file '{input_path}' to '{output_zip_path}'")
            elif os.path.isdir(input_path):
                # If it's a directory, walk through it and add all files.
                # os.walk generates the file names in a directory tree by walking the tree top-down.
                for root, _, files in os.walk(input_path):
                    for file in files:
                        full_path = os.path.join(root, file)
                        # Calculate the relative path within the input_path directory.
                        # This ensures the folder structure is maintained inside the zip.
                        # For example, if input_path is 'my_folder' and full_path is 'my_folder/sub/file.txt',
                        # then relative_path will be 'sub/file.txt'.
                        relative_path = os.path.relpath(full_path, input_path)
                        zf.write(full_path, arcname=os.path.join(os.path.basename(input_path), relative_path))
                print(f"Successfully compressed directory '{input_path}' to '{output_zip_path}'")
            else:
                print(f"Error: Input path '{input_path}' is neither a file nor a directory.")
                return False
        return True
    except FileNotFoundError:
        print(f"Error: Input path '{input_path}' not found.")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during compression: {e}")
        return False

def decompress_archive(input_zip_path, output_dir):
    """
    Decompresses a ZIP archive into a specified directory.

    Args:
        input_zip_path (str): The path to the ZIP archive to be decompressed.
        output_dir (str): The directory where the contents will be extracted.
    """
    if not os.path.exists(input_zip_path):
        print(f"Error: ZIP archive '{input_zip_path}' not found.")
        return False

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Open the ZIP file in read mode
        with zipfile.ZipFile(input_zip_path, 'r') as zf:
            # Extract all contents to the specified output directory
            zf.extractall(output_dir)
        print(f"Successfully decompressed '{input_zip_path}' to '{output_dir}'")
        return True
    except zipfile.BadZipFile:
        print(f"Error: '{input_zip_path}' is not a valid ZIP file or it is corrupted.")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during decompression: {e}")
        return False

def main():
    """
    Parses command-line arguments and calls the appropriate compression/decompression function.
    """
    parser = argparse.ArgumentParser(
        description="A simple file and directory compression/decompression tool using ZIP."
    )
    # Define an argument for the action to perform (compress or decompress)
    parser.add_argument(
        '--action',
        choices=['compress', 'decompress'],
        required=True,
        help="Action to perform: 'compress' or 'decompress'."
    )
    # Define an argument for the input path
    parser.add_argument(
        '--input',
        required=True,
        help="Path to the file/directory to compress, or ZIP archive to decompress."
    )
    # Define an argument for the output path
    parser.add_argument(
        '--output',
        required=True,
        help="Path for the output ZIP archive (for compress) or output directory (for decompress)."
    )

    args = parser.parse_args()

    if args.action == 'compress':
        compress_file_or_directory(args.input, args.output)
    elif args.action == 'decompress':
        decompress_archive(args.input, args.output)

if __name__ == "__main__":
    # --- Example Usage for Learners ---
    print("--- Running example usage ---")

    # Define paths for demonstration
    example_dir = "example_data"
    example_file = os.path.join(example_dir, "my_document.txt")
    example_subdir = os.path.join(example_dir, "sub_folder")
    example_subdir_file = os.path.join(example_subdir, "report.pdf") # Just a placeholder name
    example_zip_file = "my_document.zip"
    example_zip_dir = "example_data.zip"
    extracted_file_dir = "extracted_file_content"
    extracted_dir_content = "extracted_directory_content"

    # 1. Setup: Create dummy files and directories for the example
    print("\n1. Setting up dummy data...")
    os.makedirs(example_subdir, exist_ok=True)
    with open(example_file, "w") as f:
        f.write("This is a test document.\nIt has multiple lines.")
    with open(example_subdir_file, "w") as f:
        f.write("This is a dummy report inside a subfolder.")
    print(f"Created '{example_file}'")
    print(f"Created '{example_subdir_file}'")

    # 2. Demonstrate compressing a single file
    print("\n2. Compressing a single file...")
    compress_file_or_directory(example_file, example_zip_file)

    # 3. Demonstrate compressing a directory
    print("\n3. Compressing an entire directory...")
    compress_file_or_directory(example_dir, example_zip_dir)

    # 4. Demonstrate decompressing a file ZIP
    print("\n4. Decompressing a file ZIP archive...")
    decompress_archive(example_zip_file, extracted_file_dir)
    # Verify content (optional, for learner understanding)
    if os.path.exists(os.path.join(extracted_file_dir, os.path.basename(example_file))):
        print(f"  Verified: '{os.path.basename(example_file)}' found in '{extracted_file_dir}'")
    else:
        print(f"  Warning: Could not verify '{os.path.basename(example_file)}' in '{extracted_file_dir}'")


    # 5. Demonstrate decompressing a directory ZIP
    print("\n5. Decompressing a directory ZIP archive...")
    decompress_archive(example_zip_dir, extracted_dir_content)
    # Verify content (optional, for learner understanding)
    if os.path.exists(os.path.join(extracted_dir_content, os.path.basename(example_dir), os.path.basename(example_file))):
        print(f"  Verified: '{os.path.basename(example_file)}' found in '{os.path.join(extracted_dir_content, os.path.basename(example_dir))}'")
    else:
        print(f"  Warning: Could not verify '{os.path.basename(example_file)}' in '{os.path.join(extracted_dir_content, os.path.basename(example_dir))}'")


    # 6. Cleanup: Remove all created dummy files and directories
    print("\n6. Cleaning up dummy data and archives...")
    if os.path.exists(example_dir):
        shutil.rmtree(example_dir)
    if os.path.exists(example_zip_file):
        os.remove(example_zip_file)
    if os.path.exists(example_zip_dir):
        os.remove(example_zip_dir)
    if os.path.exists(extracted_file_dir):
        shutil.rmtree(extracted_file_dir)
    if os.path.exists(extracted_dir_content):
        shutil.rmtree(extracted_dir_content)
    print("Cleanup complete.")

    print("\n--- Example usage finished ---")

    # To use the script with command-line arguments directly,
    # comment out or remove the example usage block above and run like:
    # python your_script_name.py --action compress --input path/to/file_or_dir --output path/to/output.zip
    # python your_script_name.py --action decompress --input path/to/archive.zip --output path/to/output_dir
