"""
A useful, complete, standalone Python script for formatting JSON data.

This script reads JSON input from a specified file or standard input (stdin),
pretty-prints it with a configurable indentation level, and writes the
formatted JSON to a specified output file or standard output (stdout).

It's designed to be beginner-friendly, handling common use cases and errors
such as invalid JSON or file not found.

Usage examples from the command line:

1. Format JSON from a file and print to console (default indent of 2 spaces):
   python json_formatter.py my_data.json

2. Format JSON from stdin (piped input) and print to console:
   echo '{"name": "Alice", "age": 30}' | python json_formatter.py

3. Format JSON from a file with 4-space indentation:
   python json_formatter.py my_data.json --indent 4

4. Format JSON from a file and save the output to another file:
   python json_formatter.py my_data.json -o formatted_data.json

5. Format JSON from stdin and save to a file:
   cat my_data.json | python json_formatter.py -o formatted_data.json

6. Run interactively, paste JSON and press Ctrl+D (or Ctrl+Z on Windows)
   when done:
   python json_formatter.py
"""

import sys
import json
import argparse
import os

def main():
    """
    Main function to parse command-line arguments, read JSON, format it,
    and write the output.
    """
    parser = argparse.ArgumentParser(
        description="Pretty-prints JSON data from a file or standard input."
    )
    parser.add_argument(
        "input_file",
        nargs="?",  # Makes the argument optional
        help="Path to the JSON input file. If omitted, reads from standard input (stdin)."
    )
    parser.add_argument(
        "-i", "--indent",
        type=int,
        default=2,
        help="Number of spaces to use for indentation. Default is 2."
    )
    parser.add_argument(
        "-o", "--output-file",
        help="Path to the output file. If omitted, prints to standard output (stdout)."
    )

    args = parser.parse_args()

    json_data = None # Initialize json_data outside try block for scope

    try:
        # Determine input source
        if args.input_file:
            # If an input file is specified, open and load JSON from it
            with open(args.input_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
        else:
            # Otherwise, read from standard input.
            # If stdin is an interactive terminal (not piped/redirected),
            # prompt the user to paste JSON.
            if sys.stdin.isatty():
                print("Reading from standard input. Paste JSON and press Ctrl+D (or Ctrl+Z on Windows) when done:", file=sys.stderr)
            
            # json.load expects a file-like object. It will read until EOF.
            json_data = json.load(sys.stdin)

        # Pretty-print the JSON data with the specified indentation
        formatted_json = json.dumps(json_data, indent=args.indent)

        # Determine output destination
        if args.output_file:
            # Write the formatted JSON to the specified output file
            with open(args.output_file, 'w', encoding='utf-8') as f:
                f.write(formatted_json + "\n") # Add newline at the end for clean files
            print(f"Formatted JSON successfully written to '{args.output_file}'", file=sys.stderr)
        else:
            # Print the formatted JSON to standard output
            print(formatted_json)

    except FileNotFoundError:
        print(f"Error: Input file '{args.input_file}' not found.", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        # Handle cases where the input is not valid JSON
        print(f"Error: Invalid JSON input. {e}", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        # Catch other potential errors during file operations (e.g., permissions)
        print(f"Error reading or writing file: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        # Catch any other unexpected errors during execution
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    # --- Programmatic example of core JSON formatting logic ---
    # This block demonstrates how the `json` module can be used directly
    # for formatting, separate from the command-line interface.
    
    print("--- Demonstrating core JSON formatting logic ---", file=sys.stderr)
    sample_json_string = '{"product": "Smartphone", "price": 899.99, "features": ["5G", "OLED Display"], "available": true, "reviews": null}'
    print(f"Original JSON string:\n{sample_json_string}\n", file=sys.stderr)
    
    try:
        # Parse the JSON string into a Python dictionary/list
        parsed_data = json.loads(sample_json_string)
        # Pretty-print the data with 4-space indentation for this example
        formatted_output = json.dumps(parsed_data, indent=4) 
        print(f"Formatted JSON (indent=4):\n{formatted_output}\n", file=sys.stderr)
    except json.JSONDecodeError as e:
        print(f"Error parsing sample JSON: {e}", file=sys.stderr)
    
    # --- Guidance for command-line usage ---
    # This script is primarily designed to be run from the command line.
    # The `main()` function will be called here, allowing you to interact
    # with the script using its command-line arguments as described in the docstring.
    print("--- You can also run this script from your command line ---", file=sys.stderr)
    print("Try these commands in your terminal (create a file named `temp_data.json` first):", file=sys.stderr)
    print("  echo '{\"city\": \"New York\", \"population\": 8_000_000}' > temp_data.json", file=sys.stderr)
    print("  python json_formatter.py temp_data.json", file=sys.stderr)
    print("  echo '{\"country\": \"Canada\"}' | python json_formatter.py -i 4", file=sys.stderr)
    
    # Optionally clean up the temporary file if it was created programmatically
    # For this example, we're assuming the user creates it manually.

    print("\nRunning main() function for command-line execution...", file=sys.stderr)
    main()
