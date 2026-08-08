"""
A simple command-line calculator script.

This script takes three command-line arguments: two numbers and an operator
between them. It performs the specified arithmetic operation and prints the result.

Usage:
    python calculator.py <number1> <operator> <number2>

Examples:
    python calculator.py 10 + 5       # Adds 10 and 5
    python calculator.py 7.5 * 2      # Multiplies 7.5 by 2
    python calculator.py 20 / 4       # Divides 20 by 4
    python calculator.py 10 - 3       # Subtracts 3 from 10
"""

import sys

def main():
    """
    Parses command-line arguments, performs a calculation, and prints the result.
    Handles argument validation, type conversion, and error conditions.
    """
    # Check if the correct number of arguments is provided.
    # sys.argv includes the script name itself as the first element.
    # So, we expect 4 arguments in total: [script_name, number1, operator, number2].
    if len(sys.argv) != 4:
        print("Usage: python calculator.py <number1> <operator> <number2>")
        print("Example: python calculator.py 10 + 5")
        sys.exit(1) # Exit with an error code to indicate failure

    # Extract arguments from sys.argv
    # sys.argv[0] is the script name itself
    num1_str = sys.argv[1]    # The first number as a string
    operator = sys.argv[2]    # The operator as a string
    num2_str = sys.argv[3]    # The second number as a string

    try:
        # Attempt to convert the number strings to float.
        # Floats allow for decimal numbers (e.g., 7.5).
        num1 = float(num1_str)
        num2 = float(num2_str)
    except ValueError:
        # If conversion fails, it means one or both inputs were not valid numbers.
        print(f"Error: Both '{num1_str}' and '{num2_str}' must be valid numbers.")
        sys.exit(1) # Exit with an error code

    result = None # Initialize result to None, will be set after calculation

    # Perform the arithmetic operation based on the operator string.
    if operator == '+':
        result = num1 + num2
    elif operator == '-':
        result = num1 - num2
    elif operator == '*':
        result = num1 * num2
    elif operator == '/':
        # Check for division by zero before performing the operation.
        if num2 == 0:
            print("Error: Cannot divide by zero.")
            sys.exit(1) # Exit with an error code for this specific error
        result = num1 / num2
    else:
        # If the operator is not recognized, print an error and exit.
        print(f"Error: Invalid operator '{operator}'. Supported operators are +, -, *, /")
        sys.exit(1) # Exit with an error code

    # Print the result.
    # We check if the result is an integer (e.g., 10.0 instead of 10).
    # If it is, we print it as an integer for cleaner output.
    if result == int(result):
        print(int(result))
    else:
        print(result)

# This block ensures that the 'main()' function is called only when the script
# is executed directly (e.g., `python calculator.py ...`), not when it's
# imported as a module into another Python script.
if __name__ == "__main__":
    main()
