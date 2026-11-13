"""
Color Code Converter Script

This script provides functions to convert between common color code formats:
Hexadecimal (HEX) and Red, Green, Blue (RGB).

Functions included:
- hex_to_rgb(hex_color): Converts a HEX color string (e.g., "#RRGGBB" or "RRGGBB")
  into an RGB tuple (R, G, B).
- rgb_to_hex(r, g, b): Converts Red, Green, Blue integer values (0-255 each)
  into a HEX color string (e.g., "#RRGGBB").

The script includes basic input validation and error handling for common issues
like invalid HEX format or RGB values out of range.
"""

def hex_to_rgb(hex_color):
    """
    Converts a hexadecimal color string to an RGB tuple.

    Args:
        hex_color (str): A string representing a hex color, e.g., "#RRGGBB" or "RRGGBB".
                         The '#' prefix is optional.

    Returns:
        tuple: A tuple of three integers (R, G, B), where each value is between 0 and 255.

    Raises:
        ValueError: If the hex_color string is not a valid 6-digit hexadecimal format,
                    contains non-hexadecimal characters, or is not a string.
    """
    # Ensure the input is a string
    if not isinstance(hex_color, str):
        raise ValueError("Input for hex_to_rgb must be a string.")

    # Remove '#' if present and convert to uppercase for consistency in hex digits
    hex_color = hex_color.lstrip('#').upper()

    # Validate the length of the hex string (must be 6 characters for RRGGBB)
    if not len(hex_color) == 6:
        raise ValueError(
            f"Invalid HEX color format. Expected 6 hexadecimal characters, got {len(hex_color)}."
        )

    try:
        # Convert each 2-character hex pair (RR, GG, BB) to an integer (0-255)
        # `int(string, 16)` interprets the string as a base-16 (hexadecimal) number.
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return (r, g, b)
    except ValueError:
        # Catch errors if characters are not valid hexadecimal digits (e.g., "GG")
        raise ValueError(
            "Invalid HEX color format. Contains non-hexadecimal characters."
        )

def rgb_to_hex(r, g, b):
    """
    Converts Red, Green, Blue integer values to a hexadecimal color string.

    Args:
        r (int): The red component (0-255).
        g (int): The green component (0-255).
        b (int): The blue component (0-255).

    Returns:
        str: A string representing the hex color, e.g., "#RRGGBB".

    Raises:
        ValueError: If any RGB component is not an integer or is outside the 0-255 range.
    """
    # Validate that inputs are integers
    if not all(isinstance(comp, int) for comp in [r, g, b]):
        raise ValueError("RGB components must be integers.")

    # Validate that inputs are within the 0-255 range
    if not all(0 <= comp <= 255 for comp in [r, g, b]):
        raise ValueError("RGB components must be between 0 and 255.")

    # Convert each integer to a 2-digit hexadecimal string, padded with leading zero if needed.
    # The f-string format `f"{value:02X}"` achieves this:
    # `#`         - literal '#' character prefix for hex codes.
    # `:02X`      - format an integer as uppercase hex (`X`), padding with a leading zero (`0`)
    #               to ensure it is exactly two characters wide (`2`).
    hex_color = f"#{r:02X}{g:02X}{b:02X}"
    return hex_color

if __name__ == "__main__":
    print("--- Color Code Converter Examples ---")
    print("-----------------------------------")

    # Example 1: HEX to RGB conversion
    print("\nConverting HEX to RGB:")
    hex_color_1 = "#FF0000" # Pure Red
    hex_color_2 = "00FF00"   # Pure Green (without '#')
    hex_color_3 = "#0000FF" # Pure Blue
    hex_color_4 = "#FFFFFF" # White
    hex_color_5 = "000000"   # Black
    hex_color_6 = "#1A2B3C" # A custom dark gray-blue

    try:
        print(f"HEX: {hex_color_1:<8} -> RGB: {hex_to_rgb(hex_color_1)}")
        print(f"HEX: {hex_color_2:<8} -> RGB: {hex_to_rgb(hex_color_2)}")
        print(f"HEX: {hex_color_3:<8} -> RGB: {hex_to_rgb(hex_color_3)}")
        print(f"HEX: {hex_color_4:<8} -> RGB: {hex_to_rgb(hex_color_4)}")
        print(f"HEX: {hex_color_5:<8} -> RGB: {hex_to_rgb(hex_color_5)}")
        print(f"HEX: {hex_color_6:<8} -> RGB: {hex_to_rgb(hex_color_6)}")
    except ValueError as e:
        print(f"Error during HEX to RGB conversion: {e}")

    # Example 2: RGB to HEX conversion
    print("\nConverting RGB to HEX:")
    rgb_color_1 = (255, 0, 0)   # Pure Red
    rgb_color_2 = (0, 255, 0)   # Pure Green
    rgb_color_3 = (0, 0, 255)   # Pure Blue
    rgb_color_4 = (255, 255, 255) # White
    rgb_color_5 = (0, 0, 0)     # Black
    rgb_color_6 = (26, 43, 60)  # A custom dark gray-blue (matches #1A2B3C)

    try:
        # The `*` operator unpacks the tuple into separate arguments for the function
        print(f"RGB: {str(rgb_color_1):<15} -> HEX: {rgb_to_hex(*rgb_color_1)}")
        print(f"RGB: {str(rgb_color_2):<15} -> HEX: {rgb_to_hex(*rgb_color_2)}")
        print(f"RGB: {str(rgb_color_3):<15} -> HEX: {rgb_to_hex(*rgb_color_3)}")
        print(f"RGB: {str(rgb_color_4):<15} -> HEX: {rgb_to_hex(*rgb_color_4)}")
        print(f"RGB: {str(rgb_color_5):<15} -> HEX: {rgb_to_hex(*rgb_color_5)}")
        print(f"RGB: {str(rgb_color_6):<15} -> HEX: {rgb_to_hex(*rgb_color_6)}")
    except ValueError as e:
        print(f"Error during RGB to HEX conversion: {e}")

    # Example 3: Error handling for HEX to RGB
    print("\nError handling examples (HEX to RGB):")
    invalid_hex_1 = "#GGGGGG"   # Contains non-hexadecimal characters
    invalid_hex_2 = "#FF00"     # Too short (expected 6 hex chars)
    invalid_hex_3 = "FF00000"   # Too long (expected 6 hex chars)
    invalid_hex_4 = 123456      # Not a string input
    invalid_hex_5 = None        # Not a string input

    for invalid_input in [invalid_hex_1, invalid_hex_2, invalid_hex_3, invalid_hex_4, invalid_hex_5]:
        try:
            print(f"Attempting to convert '{invalid_input}': {hex_to_rgb(invalid_input)}")
        except ValueError as e:
            print(f"Error for '{invalid_input}': {e}")

    # Example 4: Error handling for RGB to HEX
    print("\nError handling examples (RGB to HEX):")
    invalid_rgb_1 = (256, 0, 0)     # Red component out of valid 0-255 range
    invalid_rgb_2 = (0, -1, 0)      # Green component out of valid 0-255 range
    invalid_rgb_3 = (0, 0, 255.5)   # Blue component is not an integer
    invalid_rgb_4 = ("255", 0, 0)   # Red component is a string, not an integer
    invalid_rgb_5 = (10, 20)        # Missing a component

    for invalid_input in [invalid_rgb_1, invalid_rgb_2, invalid_rgb_3, invalid_rgb_4, invalid_rgb_5]:
        try:
            # Use a dummy variable `r, g, b` for unpacked values if the input isn't a 3-tuple
            # The function signature will handle the number of arguments
            print(f"Attempting to convert {str(invalid_input):<15}: {rgb_to_hex(*invalid_input)}")
        except TypeError as e: # Catch TypeError if *invalid_input doesn't match function args
            print(f"Error for '{invalid_input}': Invalid number of arguments or type issue: {e}")
        except ValueError as e:
            print(f"Error for '{invalid_input}': {e}")

    print("\n-----------------------------------")
    print("Color Code Converter examples finished.")
