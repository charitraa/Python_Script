"""
This script generates strong, random passwords based on user-defined criteria.
It allows the user to specify the desired password length and which types of characters
(uppercase letters, lowercase letters, digits, and symbols) to include.
The script ensures that at least one character from each selected type is included
(if the password length allows) to meet user expectations for a diverse password.
"""

import random
import string

def generate_password(length, include_uppercase, include_lowercase, include_digits, include_symbols):
    """
    Generates a random password based on specified criteria.

    Args:
        length (int): The desired length of the password.
        include_uppercase (bool): True to include uppercase letters (A-Z).
        include_lowercase (bool): True to include lowercase letters (a-z).
        include_digits (bool): True to include digits (0-9).
        include_symbols (bool): True to include symbols (e.g., !@#$%^&*).

    Returns:
        str: The generated password.

    Raises:
        ValueError: If no character types are selected or if the length is too short
                    to include all requested character types.
    """
    # Define character sets using the string module for convenience
    lowercase_chars = string.ascii_lowercase
    uppercase_chars = string.ascii_uppercase
    digit_chars = string.digits
    symbol_chars = string.punctuation

    # Initialize a list to hold all allowed characters for the password pool
    all_allowed_chars = []
    # Initialize a list to hold characters that *must* be included to guarantee type diversity
    must_have_chars = []

    # Conditionally add character types to the pool and select one guaranteed character
    if include_lowercase:
        all_allowed_chars.extend(lowercase_chars)
        must_have_chars.append(random.choice(lowercase_chars))
    if include_uppercase:
        all_allowed_chars.extend(uppercase_chars)
        must_have_chars.append(random.choice(uppercase_chars))
    if include_digits:
        all_allowed_chars.extend(digit_chars)
        must_have_chars.append(random.choice(digit_chars))
    if include_symbols:
        all_allowed_chars.extend(symbol_chars)
        must_have_chars.append(random.choice(symbol_chars))

    # --- Validation Checks ---
    if not all_allowed_chars:
        raise ValueError("No character types selected. Please choose at least one type.")

    if length < len(must_have_chars):
        raise ValueError(
            f"Password length ({length}) is too short to include all required character types "
            f"({len(must_have_chars)}). Please increase the length or reduce character types."
        )
    # --- End Validation Checks ---

    # Start building the password list with the guaranteed characters
    password_list = must_have_chars[:]

    # Fill the rest of the password length with random characters from the combined pool
    # The number of characters remaining to pick is length - len(must_have_chars)
    for _ in range(length - len(must_have_chars)):
        password_list.append(random.choice(all_allowed_chars))

    # Shuffle the list to randomize the position of the guaranteed characters,
    # making the password less predictable.
    random.shuffle(password_list)

    # Join the list of characters to form the final password string
    return "".join(password_list)


if __name__ == "__main__":
    print("--- Welcome to the Password Generator ---")

    while True:
        try:
            # Get password length from user
            password_length = int(input("Enter desired password length (e.g., 12): "))
            if password_length <= 0:
                print("Password length must be a positive number. Please try again.")
                continue
            break # Exit loop if input is valid
        except ValueError:
            print("Invalid input. Please enter a number for the length.")

    # Get character type preferences from user
    # Convert 'y'/'Y' to True, anything else to False
    include_lowercase = input("Include lowercase letters (a-z)? (y/n): ").lower() == 'y'
    include_uppercase = input("Include uppercase letters (A-Z)? (y/n): ").lower() == 'y'
    include_digits = input("Include digits (0-9)? (y/n): ").lower() == 'y'
    include_symbols = input("Include symbols (!@#$%^&* etc.)? (y/n): ").lower() == 'y'

    try:
        # Generate the password using the user's choices
        generated_password = generate_password(
            password_length,
            include_uppercase,
            include_lowercase,
            include_digits,
            include_symbols
        )
        print("\n--- Generated Password ---")
        print(generated_password)
        print("--------------------------")
    except ValueError as e:
        # Catch any errors from the generate_password function
        print(f"\nError: {e}")
        print("Please restart the script and make valid selections.")
