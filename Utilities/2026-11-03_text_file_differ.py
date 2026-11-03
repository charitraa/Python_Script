"""
This script compares two text files and prints their differences in a unified diff format.
It can be run with two file paths as command-line arguments, or it will execute a
self-contained example if no arguments are provided.

The unified diff format is a standard way to show changes, where:
- Lines starting with '---' and '+++' indicate the original and new file paths.
- Lines starting with '@@' indicate the chunk header, showing line numbers and counts.
- Lines starting with '-' indicate content removed from the first file.
- Lines starting with '+' indicate content added to the second file.
- Lines starting with ' ' indicate common content (context).
"""

import difflib
import sys
import os

def compare_files(file1_path, file2_path):
    """
    Compares two text files and prints their unified differences to standard output.

    Args:
        file1_path (str): The path to the first text file.
        file2_path (str): The path to the second text file.
    """
    # Check if both files exist before attempting to open them.
    if not os.path.exists(file1_path):
        print(f"Error: File not found: {file1_path}", file=sys.stderr)
        return
    if not os.path.exists(file2_path):
        print(f"Error: File not found: {file2_path}", file=sys.stderr)
        return

    # Read the content of the first file.
    # The 'with' statement ensures the file is properly closed even if errors occur.
    # 'encoding='utf-8'' is good practice for handling various characters.
    try:
        with open(file1_path, 'r', encoding='utf-8') as f1:
            # Read all lines into a list. difflib expects a list of strings,
            # where each string represents a line including its newline character.
            file1_lines = f1.readlines()
    except IOError as e:
        print(f"Error reading {file1_path}: {e}", file=sys.stderr)
        return

    # Read the content of the second file.
    try:
        with open(file2_path, 'r', encoding='utf-8') as f2:
            file2_lines = f2.readlines()
    except IOError as e:
        print(f"Error reading {file2_path}: {e}", file=sys.stderr)
        return

    # Generate the unified diff using difflib.
    # 'fromfile' and 'tofile' are labels that will appear in the diff header.
    # 'lineterm=''' is crucial: it prevents difflib from adding an extra newline
    # to each line of output, as the lines read from files already contain them.
    diff_generator = difflib.unified_diff(
        file1_lines,
        file2_lines,
        fromfile=file1_path,
        tofile=file2_path,
        lineterm=''
    )

    # Print the differences.
    diff_found = False
    for line in diff_generator:
        # Use sys.stdout.write instead of print() to avoid print adding
        # another newline character, as 'line' already includes one.
        sys.stdout.write(line)
        diff_found = True

    # If the diff_generator was empty, it means no differences were found.
    if not diff_found:
        print(f"No differences found between {file1_path} and {file2_path}.")

if __name__ == "__main__":
    # This block determines whether to run a self-contained example or
    # process files provided via command-line arguments.

    # Check if command-line arguments (file paths) were provided.
    # sys.argv[0] is the script name itself, so we expect 3 arguments in total:
    # script_name.py file1.txt file2.txt
    if len(sys.argv) == 3:
        print(f"Comparing files from command line arguments: '{sys.argv[1]}' and '{sys.argv[2]}'\n")
        # Call the comparison function with the provided file paths.
        compare_files(sys.argv[1], sys.argv[2])
    elif len(sys.argv) > 1:
        # If an incorrect number of arguments was provided.
        print("Usage: python text_file_differ.py <file1_path> <file2_path>", file=sys.stderr)
        sys.exit(1)
    else:
        # If no command-line arguments, run the self-contained example.
        print("No file paths provided. Running self-contained example.\n")

        # Define temporary file names for the example.
        temp_file1_name = "example_file1.txt"
        temp_file2_name = "example_file2.txt"

        # Content for the first example file.
        content1 = """Line 1: Hello World.
Line 2: This is the first file.
Line 3: It has some unique content.
Line 4: This line is common.
Line 5: Another common line.
Line 6: And a final line.
"""

        # Content for the second example file, with intentional differences.
        content2 = """Line 1: Hello Python.
Line 2: This is the second file.
Line 3: It has some unique content.
Line 3.5: A new line inserted here.
Line 4: This line is common.
Line 5: Another common line.
Line 7: The final line was changed.
"""

        try:
            # Create and write content to the first temporary file.
            print(f"Creating temporary file: {temp_file1_name}")
            with open(temp_file1_name, 'w', encoding='utf-8') as f:
                f.write(content1)

            # Create and write content to the second temporary file.
            print(f"Creating temporary file: {temp_file2_name}")
            with open(temp_file2_name, 'w', encoding='utf-8') as f:
                f.write(content2)

            print("\n--- Comparing example files with differences ---")
            # Call the comparison function with the temporary files.
            compare_files(temp_file1_name, temp_file2_name)
            print("--- Comparison complete ---\n")

            # Demonstrate comparison of identical files (expected: no diff).
            print(f"\n--- Comparing '{temp_file1_name}' with itself (no diff expected) ---")
            compare_files(temp_file1_name, temp_file1_name)
            print("--- Comparison complete ---\n")

        finally:
            # Clean up: remove the temporary files created for the example.
            print(f"Cleaning up: removing {temp_file1_name}")
            if os.path.exists(temp_file1_name):
                os.remove(temp_file1_name)
            print(f"Cleaning up: removing {temp_file2_name}")
            if os.path.exists(temp_file2_name):
                os.remove(temp_file2_name)
"""
Expected output for the self-contained example:

No file paths provided. Running self-contained example.

Creating temporary file: example_file1.txt
Creating temporary file: example_file2.txt

--- Comparing example files with differences ---
--- example_file1.txt
+++ example_file2.txt
@@ -1,6 +1,7 @@
-Line 1: Hello World.
-Line 2: This is the first file.
+Line 1: Hello Python.
+Line 2: This is the second file.
 Line 3: It has some unique content.
+Line 3.5: A new line inserted here.
 Line 4: This line is common.
 Line 5: Another common line.
-Line 6: And a final line.
+Line 7: The final line was changed.
--- Comparison complete ---


--- Comparing 'example_file1.txt' with itself (no diff expected) ---
No differences found between example_file1.txt and example_file1.txt.
--- Comparison complete ---

Cleaning up: removing example_file1.txt
Cleaning up: removing example_file2.txt
"""
