"""
This script provides a simple, beginner-friendly "Random Password Vault".
It allows users to:
1. Generate strong, random passwords with customizable length and character types.
2. Store service credentials (service name, username, password) in a local JSON file.
3. Retrieve stored credentials by service name.
4. List all services for which credentials are stored.

IMPORTANT SECURITY NOTICE:
This script stores passwords in a plain-text JSON file. This is NOT secure
for real-world sensitive data. It is intended for educational purposes only
to demonstrate basic password management concepts and random password generation.
For a truly secure password vault, encryption (e.g., using a master password
and a robust cryptographic library) would be absolutely necessary.
DO NOT use this script to store actual sensitive passwords.
"""

import json
import os
import random
import string

# Define the file where passwords will be stored.
# IMPORTANT: For a real-world secure vault, this file should be encrypted!
# This script is for educational purposes to demonstrate password management concepts.
PASSWORD_FILE = "passwords.json"

def load_passwords():
    """
    Loads passwords from the JSON file.
    If the file does not exist or is empty, returns an empty dictionary.
    Handles potential JSON decoding errors for corrupted files.
    """
    if not os.path.exists(PASSWORD_FILE) or os.path.getsize(PASSWORD_FILE) == 0:
        return {}
    try:
        with open(PASSWORD_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        # Handle cases where the JSON file is malformed (e.g., manually edited incorrectly)
        print(f"Warning: {PASSWORD_FILE} is corrupted. Starting with an empty vault.")
        return {}
    except IOError as e:
        # Handle general I/O errors, like permission issues
        print(f"Error loading passwords: {e}")
        return {}

def save_passwords(passwords):
    """
    Saves the current dictionary of passwords to the JSON file.
    Uses indent=4 for pretty-printing the JSON, making it human-readable.
    """
    try:
        with open(PASSWORD_FILE, 'w') as f:
            json.dump(passwords, f, indent=4) # Use indent for pretty printing the JSON
    except IOError as e:
        # Handle general I/O errors when writing
        print(f"Error saving passwords: {e}")

def generate_password(length=12, use_uppercase=True, use_lowercase=True, use_digits=True, use_symbols=True):
    """
    Generates a strong, random password based on specified criteria.

    Args:
        length (int): The desired length of the password.
        use_uppercase (bool): If True, include uppercase letters (A-Z).
        use_lowercase (bool): If True, include lowercase letters (a-z).
        use_digits (bool): If True, include digits (0-9).
        use_symbols (bool): If True, include common symbols (!@#$%^&*()_+-=[]{};:'",.<>/?|`~).

    Returns:
        str: The generated password, or an empty string if no character types are selected.
             If the requested length is too short to include at least one character
             from each selected type, the length is adjusted to the minimum required.
    """
    char_pools = []       # List of character sets (e.g., [string.ascii_uppercase, string.digits])
    must_include = []     # List to hold one guaranteed character from each selected pool

    if use_uppercase:
        char_pools.append(string.ascii_uppercase)
        must_include.append(random.choice(string.ascii_uppercase))
    if use_lowercase:
        char_pools.append(string.ascii_lowercase)
        must_include.append(random.choice(string.ascii_lowercase))
    if use_digits:
        char_pools.append(string.digits)
        must_include.append(random.choice(string.digits))
    if use_symbols:
        char_pools.append(string.punctuation)
        must_include.append(random.choice(string.punctuation))

    if not char_pools:
        print("Error: No character types selected for password generation. Cannot generate a password.")
        return ""

    # Adjust length if it's too short to include at least one character from each selected type
    if length < len(must_include):
        print(f"Warning: Requested password length ({length}) is too short to include at least one character "
              f"from each selected type ({len(must_include)} required). Increasing length to {len(must_include)}.")
        length = len(must_include)

    # Combine all selected character pools into a single string for general random selection
    all_characters = "".join(char_pools)
    
    # Start the password with the mandatory characters
    password_list = must_include[:]
    
    # Fill the remaining length with random characters from the combined pool
    for _ in range(length - len(password_list)):
        password_list.append(random.choice(all_characters))
    
    # Shuffle the entire list to ensure the mandatory characters are not always at the beginning
    random.shuffle(password_list)
    return "".join(password_list)

def add_entry(passwords):
    """
    Prompts the user to add a new password entry or update an existing one.
    Allows the user to either generate a new strong password or enter one manually.
    """
    service = input("Enter service name (e.g., Google, Facebook): ").strip()
    if not service:
        print("Service name cannot be empty. Aborting.")
        return

    username = input("Enter username/email for the service: ").strip()
    if not username:
        print("Username cannot be empty. Aborting.")
        return

    # Inform the user if they are updating an existing entry
    if service in passwords:
        print(f"Service '{service}' already exists. Its entry will be updated.")
    
    password = ""
    while True:
        choice = input("Generate a strong password (G) or enter manually (M)? [G/M]: ").strip().upper()
        if choice == 'G':
            try:
                # Prompt for password generation options
                length_str = input("Enter desired password length (default 12): ")
                length = int(length_str) if length_str else 12
                if length <= 0:
                    print("Password length must be a positive number.")
                    continue

                use_upper = input("Include uppercase letters (A-Z)? [y/n] (default y): ").strip().lower() != 'n'
                use_lower = input("Include lowercase letters (a-z)? [y/n] (default y): ").strip().lower() != 'n'
                use_digits = input("Include digits (0-9)? [y/n] (default y): ").strip().lower() != 'n'
                use_symbols = input("Include symbols (!@#$ etc.)? [y/n] (default y): ").strip().lower() != 'n'

                gen_password = generate_password(length, use_upper, use_lower, use_digits, use_symbols)
                if gen_password:
                    print(f"Generated Password: {gen_password}")
                    password = gen_password
                    break # Exit the while loop after successful generation
                else:
                    print("Password generation failed. Please try different options.")
            except ValueError:
                print("Invalid input for length. Please enter a number.")
            except Exception as e:
                print(f"An unexpected error occurred during password generation: {e}")

        elif choice == 'M':
            password = input("Enter password manually: ")
            if not password:
                print("Password cannot be empty. Please enter a password or choose to generate one.")
            else:
                break # Exit the while loop after manual entry
        else:
            print("Invalid choice. Please enter 'G' to generate or 'M' to enter manually.")

    # Store the new/updated entry
    passwords[service] = {"username": username, "password": password}
    save_passwords(passwords)
    print(f"Entry for '{service}' saved successfully.")

def get_entry(passwords):
    """
    Retrieves and displays a password entry for a specified service.
    """
    service = input("Enter service name to retrieve: ").strip()
    if not service:
        print("Service name cannot be empty. Aborting.")
        return

    entry = passwords.get(service)
    if entry:
        print(f"\n--- Entry for {service} ---")
        print(f"  Username: {entry['username']}")
        print(f"  Password: {entry['password']}") # Displaying password in plain text. See security warning.
        print("--------------------------")
    else:
        print(f"No entry found for service '{service}'.")

def list_entries(passwords):
    """
    Lists all stored service names in the vault.
    Sorts the service names alphabetically for easy viewing.
    """
    if not passwords:
        print("The vault is empty.")
        return

    print("\n--- Stored Services ---")
    for service in sorted(passwords.keys()):
        print(f"- {service}")
    print("-----------------------")

def main_menu():
    """
    Displays the main interactive menu for the password vault.
    Loads existing passwords and handles user choices.
    """
    passwords = load_passwords() # Load passwords at the start of the session

    while True:
        print("\n--- Password Vault Menu ---")
        print("1. Add/Update Password Entry")
        print("2. Retrieve Password Entry")
        print("3. List All Services")
        print("4. Generate a Random Password (without saving)")
        print("5. Exit")
        print("---------------------------")

        choice = input("Enter your choice: ").strip()

        if choice == '1':
            add_entry(passwords)
        elif choice == '2':
            get_entry(passwords)
        elif choice == '3':
            list_entries(passwords)
        elif choice == '4':
            # Option to just generate a password without saving it
            try:
                length_str = input("Enter desired password length (default 12): ")
                length = int(length_str) if length_str else 12
                if length <= 0:
                    print("Password length must be a positive number.")
                    continue
                
                use_upper = input("Include uppercase letters (A-Z)? [y/n] (default y): ").strip().lower() != 'n'
                use_lower = input("Include lowercase letters (a-z)? [y/n] (default y): ").strip().lower() != 'n'
                use_digits = input("Include digits (0-9)? [y/n] (default y): ").strip().lower() != 'n'
                use_symbols = input("Include symbols (!@#$ etc.)? [y/n] (default y): ").strip().lower() != 'n'

                gen_password = generate_password(length, use_upper, use_lower, use_digits, use_symbols)
                if gen_password:
                    print(f"Your generated password: {gen_password}")
            except ValueError:
                print("Invalid input for length. Please enter a number.")
            except Exception as e:
                print(f"An unexpected error occurred during password generation: {e}")
        elif choice == '5':
            print("Exiting Password Vault. Goodbye!")
            break # Exit the main loop
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")

# This block ensures that `main_menu()` is called only when the script is executed directly.
if __name__ == "__main__":
    main_menu()
