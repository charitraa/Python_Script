# pip install pyotp

import pyotp
import time
import sys # For sys.stdout.write and sys.flush

"""
This script generates Time-based One-Time Passwords (TOTP), commonly used for Two-Factor Authentication (2FA).
It takes a base32-encoded secret key (provided by services like Google, GitHub, etc., during 2FA setup)
and generates a new 6-digit code every 30 seconds, displaying the remaining time for the current code.

IMPORTANT SECURITY NOTE:
This script is for demonstration and personal use. Never hardcode your secret keys directly into the script.
Always treat your 2FA secret keys as highly sensitive information. If you share this script, remove any real
secret keys from the example usage.
For robust security, consider using dedicated 2FA applications on your mobile device.
"""

def generate_and_display_totp_codes(secret_key: str):
    """
    Generates and continuously displays TOTP codes for the given secret key.
    The code updates every 30 seconds, showing the remaining time until the next code.

    Args:
        secret_key (str): The base32-encoded secret key provided by the service
                          when setting up Two-Factor Authentication.
    """
    try:
        # Create a TOTP object from the secret key.
        # pyotp handles base32 decoding internally.
        totp = pyotp.TOTP(secret_key)
    except Exception as e:
        print(f"Error: Could not initialize TOTP with the provided secret key. "
              f"Please ensure it's a valid base32-encoded string (e.g., JBSWY3DPEHPK3PXP). Details: {e}")
        return

    print(f"\nGenerating 2FA codes for secret key: {secret_key[:4]}...{secret_key[-4:]}")
    print("Press Ctrl+C to quit.\n")

    try:
        # Loop indefinitely to keep generating and displaying codes
        while True:
            # Get the current 6-digit TOTP code.
            current_code = totp.now()

            # Calculate remaining time for the current code.
            # totp.interval is typically 30 seconds for most TOTP implementations.
            # time.time() gives the current epoch seconds.
            # The modulo operation gives seconds elapsed within the current 30-second interval.
            # Subtracting this from the interval gives the number of seconds remaining.
            remaining_seconds = totp.interval - (int(time.time()) % totp.interval)

            # Print the code and remaining time.
            # Using sys.stdout.write and sys.stdout.flush allows us to overwrite the current line
            # in the terminal, creating a dynamic countdown effect.
            # The carriage return '\r' moves the cursor to the beginning of the line.
            sys.stdout.write(f"\rCurrent Code: {current_code} | Expires in: {remaining_seconds:02d} seconds")
            sys.stdout.flush()

            # Wait for 1 second before refreshing the display.
            # This makes the countdown smooth.
            time.sleep(1)

            # If remaining_seconds is 1 (meaning there's 0 seconds left after the time.sleep(1)
            # and the code is about to expire), print a new line to make the update cleaner.
            if remaining_seconds == 1:
                time.sleep(1) # Wait for the last second to tick over
                print() # Move to the next line for the new code
                # The next loop iteration will then calculate and display the new code.

    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully, exiting the loop.
        print("\nExiting code generator. Goodbye!")
    except Exception as e:
        # Catch any other unexpected errors.
        print(f"\nAn unexpected error occurred: {e}")


if __name__ == "__main__":
    # --- EXAMPLE USAGE ---

    print("--- Two-Factor Authentication (2FA) Code Generator ---")
    print("This script helps you generate Time-based One-Time Passwords (TOTP) from a secret key.")
    print("You will need the base32-encoded secret key provided by the service (e.g., Google, GitHub, etc.)")
    print("when you initially set up 2FA for an account. This key looks like a long string of uppercase letters and numbers.")
    print("It's usually displayed as a QR code, or as a text string that you can copy.")

    # A common dummy secret key used for testing TOTP (generates codes for the text 'Hello!').
    # REPLACE THIS WITH YOUR ACTUAL BASE32 SECRET KEY FOR YOUR ACCOUNTS!
    # DO NOT SHARE YOUR REAL SECRET KEY WITH ANYONE.
    dummy_secret = "JBSWY3DPEHPK3PXP"
    print(f"\nExample dummy secret key: '{dummy_secret}' (generates codes based on 'Hello!').")
    print("For your actual accounts, you'll use a unique secret key provided during setup.")
    print("If you don't have a secret key for a service, you cannot generate codes for it.")

    # Prompt the user to enter their secret key.
    user_secret = input("\nEnter your base32 secret key (or press Enter to use the dummy key): ").strip()

    if not user_secret:
        # If the user presses Enter without typing anything, use the dummy key.
        user_secret = dummy_secret
        print(f"Using dummy secret key: {dummy_secret}")
    else:
        # Normalize the secret key: remove spaces and convert to uppercase, as some services
        # might display the key with spaces or in mixed case. Base32 keys are typically uppercase.
        user_secret = user_secret.replace(" ", "").upper()
        # Print a snippet of the key for confirmation, but avoid printing the whole key for security.
        print(f"Using provided secret key: {user_secret[:4]}...{user_secret[-4:]}")

    # Call the function to start generating and displaying codes.
    generate_and_display_totp_codes(user_secret)
