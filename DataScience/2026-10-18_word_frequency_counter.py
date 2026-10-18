"""
This script counts the frequency of words in a given text file.

It takes a file path as a command-line argument, reads the content,
cleans the text (converts to lowercase, removes punctuation and numbers),
counts the occurrences of each unique word, and then prints the top N
most frequent words to the console.
"""

import collections # Provides the Counter class for efficient word counting
import re          # Provides regular expression operations for text cleaning
import sys         # Provides access to command-line arguments and system-specific parameters
import os          # Provides a way to interact with the operating system, used for example file cleanup

def clean_and_tokenize(text):
    """
    Cleans the input text by converting it to lowercase, removing punctuation
    and numbers, and then splitting it into a list of individual words.

    Args:
        text (str): The raw input text.

    Returns:
        list: A list of cleaned words.
    """
    # Convert all text to lowercase to ensure "The" and "the" are counted as the same word.
    text = text.lower()

    # Use a regular expression to find all sequences of letters (a-z).
    # This effectively removes punctuation, numbers, and splits the text into words.
    # For example, "Hello, world! 123" becomes ["hello", "world"].
    # re.findall returns a list of all non-overlapping matches.
    words = re.findall(r'[a-z]+', text)

    return words

def count_word_frequencies(words):
    """
    Counts the frequency of each word in a list of words.

    Args:
        words (list): A list of words.

    Returns:
        collections.Counter: A Counter object mapping words to their frequencies.
    """
    # collections.Counter is a dictionary subclass specifically designed for counting
    # hashable objects. It's perfect for this task as it automatically handles counting
    # occurrences of items in an iterable.
    return collections.Counter(words)

def display_top_words(word_counts, num_words=10):
    """
    Displays the top N most frequent words and their counts.

    Args:
        word_counts (collections.Counter): A Counter object with word frequencies.
        num_words (int): The number of top words to display. Defaults to 10.
    """
    print(f"\n--- Top {num_words} most frequent words ---")

    # Check if there are any words to display.
    if not word_counts:
        print("No words found to display.")
        return

    # most_common(N) returns a list of the N most common elements and their counts,
    # from the most common to the least.
    for word, count in word_counts.most_common(num_words):
        print(f"'{word}': {count}")

def main():
    """
    Main function to orchestrate the word frequency counting process.
    It expects a file path as a command-line argument, reads the file,
    processes its content, and displays the word frequencies.
    """
    # Check if a file path argument was provided by the user.
    # sys.argv is a list of command-line arguments. sys.argv[0] is the script name itself.
    if len(sys.argv) < 2:
        print("Usage: python word_frequency_counter.py <file_path>")
        print("Example: python word_frequency_counter.py my_document.txt")
        sys.exit(1) # Exit with an error code, indicating incorrect usage

    file_path = sys.argv[1] # Get the file path from the command-line arguments

    try:
        # Open the file for reading. 'r' stands for read mode.
        # 'utf-8' is a common character encoding that handles a wide range of characters.
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read() # Read the entire content of the file into a single string.
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        sys.exit(1) # Exit with an error code for a missing file
    except Exception as e:
        print(f"An unexpected error occurred while reading the file: {e}")
        sys.exit(1) # Exit with an error code for other file reading issues

    # If the file is empty or contains only whitespace, 'content.strip()' will be an empty string.
    if not content.strip():
        print(f"The file '{file_path}' appears to be empty or contains only whitespace. No words to count.")
        sys.exit(0) # Exit successfully, as there's no error, just no data to process

    # Clean the text and tokenize it into a list of words.
    words = clean_and_tokenize(content)

    # Check if any valid words were extracted after cleaning (e.g., if the file only had punctuation).
    if not words:
        print(f"No valid words found in '{file_path}' after cleaning (e.g., only punctuation or numbers were present).")
        sys.exit(0) # Exit successfully, as there's no error, just no words found

    # Count the frequency of each word.
    word_counts = count_word_frequencies(words)

    # Display the top 10 most frequent words.
    display_top_words(word_counts)

if __name__ == "__main__":
    # This block of code runs only when the script is executed directly (e.g., `python script.py`),
    # not when it's imported as a module into another script.
    # It provides a self-contained example of how to use the script.

    # Define a temporary file name for the example.
    temp_file_name = "sample_text_for_word_counter.txt"
    example_text = """
    This is a sample text for counting word frequencies.
    It includes various words, some repeated, and also punctuation!
    Hello world, hello Python. Python is great. Is it not?
    Let's count words. Let's make sure the counter works.
    The quick brown fox jumps over the lazy dog. Fox and dog.
    """

    print(f"--- Running example with a temporary file: '{temp_file_name}' ---")

    try:
        # Create and write the example text to the temporary file.
        with open(temp_file_name, 'w', encoding='utf-8') as f:
            f.write(example_text)

        # Temporarily modify sys.argv to simulate command-line arguments.
        # This makes the main() function believe it was called with `python script.py temp_file_name`.
        original_argv = sys.argv
        sys.argv = [original_argv[0], temp_file_name]

        # Call the main function.
        main()

    finally:
        # This block ensures that the temporary file is cleaned up, even if an error occurred
        # during the execution of the main() function.
        if os.path.exists(temp_file_name):
            os.remove(temp_file_name)
            print(f"\n--- Cleaned up temporary file: '{temp_file_name}' ---")

        # Restore the original sys.argv. This is good practice in case other parts of the
        # program (if this were a larger application) rely on the original arguments.
        sys.argv = original_argv
