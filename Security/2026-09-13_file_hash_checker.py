"""
file_hash_checker.py

This script calculates the cryptographic hash of a given file using a specified algorithm
(e.g., SHA256, MD5, SHA1). It can also compare the calculated hash against an expected hash
value to verify file integrity. This is useful for checking if a downloaded file has been
corrupted or tampered with.

Usage:
    python file_hash_checker.py <file_path> [--algorithm <algorithm>] [--expected-hash <hash_value>]

Examples:
    python file_hash_checker.py my_document.pdf
    python file_hash_checker.py important_archive.zip --algorithm sha1
    python file_hash_checker.py setup.exe --expected-hash d41d8cd98f00b204e9800998ecf8427e
    python file_hash_checker.py download.iso -a sha256 -e abcd123...
"""

import hashlib
import argparse
import os
import sys
import tempfile

def calculate_file_hash(file_path, algorithm='sha256', buffer_size=65536):
    """
    Calculates the hash of a file using the specified algorithm.

    This function reads the file in chunks to efficiently handle large files
    without loading the entire file into memory.

    Args:
        file_path (str): The path to the file.
        algorithm (str): The hashing algorithm to use (e.g., 'md5', 'sha1', 'sha256').
                         Defaults to 'sha256'.
        buffer_size (int): The size of the chunks (in bytes) to read the file in.
                           Larger buffer sizes can be faster for large files, but use
                           more memory temporarily. Default is 64KB.

    Returns:
        str: The hexadecimal digest of the file's hash, or None if the file is not found
             or the algorithm is not supported/reading fails.
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found at '{file_path}'")
        return None
    
    if not os.path.isfile(file_path):
        print(f"Error: '{file_path}' is not a regular file.")
        return None

    try:
        # Create a hash object for the specified algorithm
        # hashlib.new() allows specifying the algorithm name dynamically.
        hasher = hashlib.new(algorithm)
    except ValueError:
        print(f"Error: Unknown or unsupported hash algorithm '{algorithm}'.")
        print(f"Available algorithms: {', '.join(sorted(hashlib.algorithms_available))}")
        return None

    try:
        # Open the file in binary read mode ('rb')
        with open(file_path, 'rb') as f:
            while True:
                # Read file in chunks
                chunk = f.read(buffer_size)
                if not chunk:
                    # End of file reached
                    break
                # Update the hash object with the current chunk
                hasher.update(chunk)
        # Return the hexadecimal representation of the hash
        return hasher.hexdigest()
    except IOError as e:
        print(f"Error reading file '{file_path}': {e}")
        return None

def main():
    """
    Parses command-line arguments and performs the file hash check.
    """
    parser = argparse.ArgumentParser(
        description="Calculates and optionally verifies the hash of a file.",
        formatter_class=argparse.RawTextHelpFormatter # For better formatting of help message
    )
    # Positional argument for the file path
    parser.add_argument(
        "file_path",
        help="The path to the file to hash."
    )
    # Optional argument for the hashing algorithm
    parser.add_argument(
        "-a", "--algorithm",
        default="sha256", # Default algorithm if not specified
        choices=sorted(hashlib.algorithms_available), # Restrict choices to available algorithms
        help=f"The hashing algorithm to use (e.g., md5, sha1, sha256).\n"
             f"Default is sha256.\n"
             f"Available: {', '.join(sorted(hashlib.algorithms_available))}"
    )
    # Optional argument for an expected hash value for comparison
    parser.add_argument(
        "-e", "--expected-hash",
        help="An optional expected hash value for comparison.\n"
             "If provided, the script will compare the calculated hash with this value.\n"
             "Comparison is case-insensitive."
    )

    args = parser.parse_args()

    print(f"--- File Hash Checker ---")
    print(f"File: '{args.file_path}'")
    print(f"Algorithm: {args.algorithm.upper()}")

    # Calculate the hash of the specified file
    calculated_hash = calculate_file_hash(args.file_path, args.algorithm)

    if calculated_hash:
        print(f"Calculated Hash: {calculated_hash}")

        # If an expected hash was provided, perform a comparison
        if args.expected_hash:
            print(f"Expected Hash:   {args.expected_hash}")
            # Perform a case-insensitive comparison
            if calculated_hash.lower() == args.expected_hash.lower():
                print("Status: MATCH - The file's hash matches the expected hash.")
            else:
                print("Status: MISMATCH - The file's hash DOES NOT match the expected hash.")
        else:
            print("Status: No expected hash provided for comparison.")
    else:
        # An error message would have been printed by calculate_file_hash
        print("Status: Failed to calculate hash.")
    print("-------------------------")


if __name__ == "__main__":
    # This block provides working examples when the script is run directly.
    # It demonstrates how to use the script programmatically by modifying sys.argv.
    # In a real-world scenario, you would run these commands from your terminal.

    print("--- Demonstrating File Hash Checker Script ---")

    # Create a temporary directory and file for testing purposes
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file_content = "This is a test file created for the hash checker demonstration.\n" \
                            "It contains some sample text to generate a unique hash."
        test_file_name = "demo_file.txt"
        test_file_path = os.path.join(tmpdir, test_file_name)

        # Write content to the temporary file
        with open(test_file_path, "w") as f:
            f.write(test_file_content)
        print(f"1. Created a temporary test file at: '{test_file_path}'")

        # Manually calculate the SHA256 hash of the content to use as an expected value
        expected_sha256_for_demo = hashlib.sha256(test_file_content.encode('utf-8')).hexdigest()
        print(f"   Its expected SHA256 hash is: {expected_sha256_for_demo}\n")

        # Store original sys.argv to restore later
        original_argv = sys.argv[:]

        # --- Example 1: Calculate SHA256 hash of the demo file ---
        print("\n" + "="*70)
        print("Example 1: Calculating SHA256 hash (default algorithm)")
        print(f"   Command: python file_hash_checker.py \"{test_file_path}\"")
        sys.argv = ['file_hash_checker.py', test_file_path] # Simulate command line arguments
        main()
        print("="*70)

        # --- Example 2: Calculate MD5 hash of the demo file ---
        print("\n" + "="*70)
        print("Example 2: Calculating MD5 hash (--algorithm md5)")
        print(f"   Command: python file_hash_checker.py \"{test_file_path}\" --algorithm md5")
        sys.argv = ['file_hash_checker.py', test_file_path, '--algorithm', 'md5']
        main()
        print("="*70)

        # --- Example 3: Calculate SHA256 hash and compare (MATCH) ---
        print("\n" + "="*70)
        print("Example 3: Calculating SHA256 hash and comparing (Expected MATCH)")
        print(f"   Command: python file_hash_checker.py \"{test_file_path}\" --expected-hash {expected_sha256_for_demo}")
        sys.argv = ['file_hash_checker.py', test_file_path, '--expected-hash', expected_sha256_for_demo]
        main()
        print("="*70)

        # --- Example 4: Calculate SHA256 hash and compare (MISMATCH) ---
        # We'll intentionally provide a slightly incorrect expected hash
        mismatched_hash = expected_sha256_for_demo[:-1] + ('0' if expected_sha256_for_demo[-1] != '0' else '1')
        print("\n" + "="*70)
        print("Example 4: Calculating SHA256 hash and comparing (Expected MISMATCH)")
        print(f"   Command: python file_hash_checker.py \"{test_file_path}\" --expected-hash {mismatched_hash}")
        sys.argv = ['file_hash_checker.py', test_file_path, '--expected-hash', mismatched_hash]
        main()
        print("="*70)

        # --- Example 5: Trying to hash a non-existent file ---
        non_existent_path = os.path.join(tmpdir, "non_existent_file.txt")
        print("\n" + "="*70)
        print("Example 5: Trying to hash a non-existent file")
        print(f"   Command: python file_hash_checker.py \"{non_existent_path}\"")
        sys.argv = ['file_hash_checker.py', non_existent_path]
        main()
        print("="*70)

        # Restore original sys.argv for any subsequent operations in the same Python process
        sys.argv = original_argv

    print("\n--- End of Demonstration ---")
    print("The temporary test file and directory have been removed.")
