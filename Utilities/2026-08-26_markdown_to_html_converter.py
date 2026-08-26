# pip install markdown

"""
This script provides a simple command-line utility to convert Markdown text to HTML.
It leverages the well-known 'markdown' third-party library for robust conversion.
Users can input Markdown content as a string, and the script will output the
corresponding HTML. It's designed to be beginner-friendly, showcasing a practical
use case for converting commonly used Markdown syntax into web-ready HTML.
"""

import markdown # Import the markdown library for conversion.

def convert_markdown_to_html(markdown_text: str) -> str:
    """
    Converts a given Markdown string into an HTML string.

    This function uses the 'markdown' library to parse the Markdown input
    and render it as HTML. It supports a wide range of Markdown features
    including headings, paragraphs, lists, links, images, code blocks, etc.

    Args:
        markdown_text (str): The input string containing Markdown content.

    Returns:
        str: The converted HTML string.
    """
    # The markdown.markdown() function is the core of the conversion.
    # It takes a Markdown string and returns an HTML string.
    html_output = markdown.markdown(markdown_text)
    return html_output

if __name__ == "__main__":
    print("--- Markdown to HTML Converter Example ---")
    print("\n----------------------------------------")
    print("Example 1: Basic Markdown features")
    print("----------------------------------------")

    sample_markdown_1 = """
# Welcome to Markdown

This is a **simple** example of Markdown conversion.
You can use *italics* and `inline code`.

## Features
-   Paragraphs
-   Headings
-   **Bold** and *Italic* text
-   [Links](https://www.python.org)

Here's a quick code snippet:
```python
def hello_world():
    print("Hello, Markdown!")
```
"""
    print("\n--- Original Markdown 1 ---")
    # .strip() is used here to remove any leading/trailing blank lines that might
    # result from the way the multiline string is defined, making the output cleaner.
    print(sample_markdown_1.strip())

    # Convert the Markdown to HTML
    converted_html_1 = convert_markdown_to_html(sample_markdown_1)

    print("\n--- Converted HTML 1 ---")
    print(converted_html_1)

    print("\n----------------------------------------")
    print("Example 2: Another set of Markdown features")
    print("----------------------------------------")

    sample_markdown_2 = """
A paragraph with a [link to Google](https://www.google.com).

This is a second paragraph. It can be quite long and span
multiple lines. We can even add a line break using two spaces
at the end of a line.  
Like this.

-   Unordered list item 1
-   Unordered list item 2
    -   Nested item A
    -   Nested item B
1.  Ordered list item 1
2.  Ordered list item 2

> This is a blockquote.
> It can span multiple lines.

---

End of document.
"""
    print("\n--- Original Markdown 2 ---")
    print(sample_markdown_2.strip())

    converted_html_2 = convert_markdown_to_html(sample_markdown_2)

    print("\n--- Converted HTML 2 ---")
    print(converted_html_2)
    print("\n----------------------------------------")
