"""
This script extracts all Markdown links from a given string of text.
It identifies links in the format `[Link Text](URL)` and returns
a list of tuples, where each tuple contains the link text and its corresponding URL.
"""

import re

def extract_markdown_links(markdown_text):
    """
    Extracts all Markdown links from the given text.

    Args:
        markdown_text (str): The string containing Markdown content.

    Returns:
        list: A list of tuples, where each tuple contains (link_text, url).
              Returns an empty list if no links are found.
    """
    # Regular expression to find Markdown links.
    # It looks for:
    # \[        - a literal opening square bracket
    # (.*?)     - a non-greedy capture group for the link text (anything)
    # \]        - a literal closing square bracket
    # \(        - a literal opening parenthesis
    # (.*?)     - a non-greedy capture group for the URL (anything)
    # \)        - a literal closing parenthesis
    # re.findall finds all non-overlapping matches of the pattern.
    link_pattern = re.compile(r'\[(.*?)\]\((.*?)\)')
    
    # Find all matches in the markdown_text
    found_links = link_pattern.findall(markdown_text)
    
    return found_links

if __name__ == "__main__":
    # Example Markdown text with various types of links
    example_markdown = """
Here is a [simple link](https://www.example.com).
This is a link to my [blog](http://myblog.org/articles/post1).
You can also find more info on [Google](https://www.google.com "Google's Homepage").
Sometimes links are on different lines:
[Another Example](
    https://example.net/page
).
No link here.
A link without a scheme: [Relative Link](/path/to/page).
An image is not a link: ![Alt Text](image.jpg)
A link with spaces in the URL (which should be URL-encoded in practice, but regex still finds it): [Link with spaces](https://example.com/my awesome page)
"""

    print("--- Markdown Link Extractor ---")
    print("\nOriginal Markdown Text:")
    print(example_markdown)

    # Extract the links
    links = extract_markdown_links(example_markdown)

    print("\nExtracted Links:")
    if links:
        for i, (text, url) in enumerate(links):
            print(f"{i+1}. Link Text: '{text}', URL: '{url}'")
    else:
        print("No Markdown links found in the text.")

    print("\n--- End of Script ---")

    # Another example with no links
    no_links_text = "This text has no links at all. Just plain words."
    print("\n--- Testing with text containing no links ---")
    print("\nOriginal Markdown Text:")
    print(no_links_text)
    no_links = extract_markdown_links(no_links_text)
    print("\nExtracted Links:")
    if no_links:
        for i, (text, url) in enumerate(no_links):
            print(f"{i+1}. Link Text: '{text}', URL: '{url}'")
    else:
        print("No Markdown links found in the text.")
