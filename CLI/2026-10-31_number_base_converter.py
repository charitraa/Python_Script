"""
number_base_converter.py

A beginner-friendly Python script to convert numbers between different bases.
It supports converting numbers from base 2 (binary) up to base 36.
(Digits 0-9 and A-Z are used for bases higher than 10).

Usage:
Call the `convert_base` function with the number as a string, its source base,
and the desired target base.
Example: convert_base("FF", 16, 2)  # Converts hexadecimal "FF" to binary.
"""

# Define the set of characters used for different bases (0-9, A-Z)
# This allows conversion up to base 36.
# For example, in base 16 (hexadecimal), 'A' represents 10, 'B' represents 11, etc.
# In base 36, 'Z' represents 35.
DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def convert_base(number_str, source_base, target_base):
    """
    Converts a number from a given source base to a target base.

    Args:
        number_str (str): The number to convert, represented as a string.
                          E.g., "1011" for binary, "FF" for hexadecimal.
        source_base (int): The base of the input number (e.g., 2 for binary,
                           10 for decimal, 16 for hexadecimal).
                           Must be between 2 and 36, inclusive.
        target_base (int): The desired base for the output number.
                           Must be between 2 and 36, inclusive.

    Returns:
        str: The number converted to the target base, as a string.
             Returns an error message string if conversion fails due to invalid input.
    """
    # 1. Validate the source and target bases
    if not (2 <= source_base <= 36):
        return f"Error: Source base {source_base} is out of range. Must be between 2 and 36."
    if not (2 <= target_base <= 36):
        return f"Error: Target base {target_base} is out of range. Must be between 2 and 36."

    # 2. Convert the input number from its source base to a decimal (base 10) integer.
    # Python's built-in int() function can directly handle this conversion for bases 2-36.
    try:
        decimal_value = int(number_str, source_base)
    except ValueError:
        # This error occurs if number_str contains digits invalid for the source_base
        # (e.g., '2' in binary, 'G' in hexadecimal).
        return (f"Error: '{number_str}' is not a valid number in base {source_base}. "
                "Ensure digits are appropriate for the base (e.g., 0-1 for binary, 0-9A-F for hex).")
    except TypeError:
        # This error occurs if number_str is not actually a string.
        return f"Error: Input number must be a string. Got type {type(number_str).__name__}."

    # 3. Handle the special case where the decimal value is 0.
    # Zero in any base is simply "0".
    if decimal_value == 0:
        return "0"

    # 4. If the target base is 10, we can return the decimal_value directly as a string.
    if target_base == 10:
        return str(decimal_value)

    # 5. Convert the decimal integer to the target base.
    # This involves repeated division by the target base and collecting remainders.
    result = ""
    current_decimal = decimal_value

    while current_decimal > 0:
        remainder = current_decimal % target_base
        # Prepend the digit corresponding to the remainder to build the result string.
        # We use the DIGITS string to get the correct character (e.g., 'A' for 10, 'B' for 11).
        result = DIGITS[remainder] + result
        current_decimal //= target_base  # Perform integer division

    return result

if __name__ == "__main__":
    print("--- Number Base Converter Examples ---")
    print("\n--- Valid Conversions ---")

    # Example 1: Binary "1011" (base 2) to Decimal (base 10)
    # Expected: 1*2^3 + 0*2^2 + 1*2^1 + 1*2^0 = 8 + 0 + 2 + 1 = 11
    binary_num = "1011"
    source = 2
    target = 10
    print(f"Converting '{binary_num}' (base {source}) to base {target}: "
          f"{convert_base(binary_num, source, target)}")

    # Example 2: Decimal "255" (base 10) to Hexadecimal (base 16)
    # Expected: FF
    decimal_num = "255"
    source = 10
    target = 16
    print(f"Converting '{decimal_num}' (base {source}) to base {target}: "
          f"{convert_base(decimal_num, source, target)}")

    # Example 3: Hexadecimal "FF" (base 16) to Binary (base 2)
    # Expected: 11111111
    hex_num = "FF"
    source = 16
    target = 2
    print(f"Converting '{hex_num}' (base {source}) to base {target}: "
          f"{convert_base(hex_num, source, target)}")

    # Example 4: Octal "73" (base 8) to Base 4
    # First, 73 (base 8) = 7*8^1 + 3*8^0 = 56 + 3 = 59 (base 10)
    # Then, 59 (base 10) to base 4:
    # 59 / 4 = 14 R 3
    # 14 / 4 = 3 R 2
    # 3 / 4 = 0 R 3
    # Reading remainders up: 323
    octal_num = "73"
    source = 8
    target = 4
    print(f"Converting '{octal_num}' (base {source}) to base {target}: "
          f"{convert_base(octal_num, source, target)}")

    # Example 5: Base 36 "Z" (base 36) to Decimal (base 10)
    # Expected: 35 (as 'Z' is the 36th character, index 35 in DIGITS)
    base36_num = "Z"
    source = 36
    target = 10
    print(f"Converting '{base36_num}' (base {source}) to base {target}: "
          f"{convert_base(base36_num, source, target)}")

    # Example 6: Base 36 "1A" (base 36) to Decimal (base 10)
    # Expected: 1*36^1 + 10*36^0 = 36 + 10 = 46
    base36_num_long = "1A"
    source = 36
    target = 10
    print(f"Converting '{base36_num_long}' (base {source}) to base {target}: "
          f"{convert_base(base36_num_long, source, target)}")

    # Example 7: Decimal 0 to Binary
    print(f"Converting '0' (base 10) to base 2: "
          f"{convert_base('0', 10, 2)}") # Expected: 0

    print("\n--- Error Handling Examples ---")

    # Error 1: Invalid source base (less than 2)
    print(f"Invalid source base (1): {convert_base('10', 1, 10)}")

    # Error 2: Invalid target base (greater than 36)
    print(f"Invalid target base (50): {convert_base('10', 10, 50)}")

    # Error 3: Invalid digit for source base (e.g., '2' in a binary number)
    print(f"Invalid digit for binary: {convert_base('102', 2, 10)}")

    # Error 4: Invalid digit for hexadecimal (e.g., 'G' in a hexadecimal number)
    print(f"Invalid digit for hex: {convert_base('FG', 16, 10)}")

    # Error 5: Input number is not a string
    print(f"Input number not a string: {convert_base(123, 10, 16)}")

    # Error 6: Empty string input (int() will handle this)
    print(f"Empty string input: {convert_base('', 10, 16)}")<ctrl63>
