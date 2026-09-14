"""
This script implements a simple Caesar cipher for encrypting and decrypting text.

A Caesar cipher is one of the simplest and most widely known encryption techniques.
It's a type of substitution cipher in which each letter in the plaintext is replaced
by a letter some fixed number of positions down or up the alphabet. For example,
with a left shift of 3, D would be replaced by A, E would become B, and so on.
"""

def _caesar_shift_char(char, shift):
    """
    Helper function to shift a single alphabetic character by a given shift value.
    Non-alphabetic characters are returned unchanged.
    Handles both uppercase and lowercase letters.
    """
    if 'a' <= char <= 'z':
        # For lowercase letters, calculate the new position
        # ord(char) gets the ASCII value of the character.
        # Subtracting ord('a') makes 'a' become 0, 'b' become 1, etc.
        # Add the shift, then use modulo 26 to wrap around the alphabet (A-Z has 26 letters).
        # Adding ord('a') back converts the 0-25 range back to the lowercase ASCII range.
        return chr(((ord(char) - ord('a') + shift) % 26) + ord('a'))
    elif 'A' <= char <= 'Z':
        # Same logic for uppercase letters, using 'A' as the base.
        return chr(((ord(char) - ord('A') + shift) % 26) + ord('A'))
    else:
        # If the character is not an English alphabet letter, return it as is.
        return char

def caesar_encrypt(text, shift):
    """
    Encrypts the given text using the Caesar cipher.

    Args:
        text (str): The plaintext to be encrypted.
        shift (int): The number of positions to shift each letter.
                     A positive integer shifts letters forward (e.g., A becomes D with shift 3).
                     This function internally normalizes the shift to be between 0 and 25.

    Returns:
        str: The encrypted ciphertext.
    """
    encrypted_text = []
    # Normalize the shift value to be within 0-25.
    # This ensures that a shift of 27 is treated the same as a shift of 1, etc.
    normalized_shift = shift % 26
    for char in text:
        encrypted_text.append(_caesar_shift_char(char, normalized_shift))
    return "".join(encrypted_text)

def caesar_decrypt(text, shift):
    """
    Decrypts the given ciphertext using the Caesar cipher.

    Args:
        text (str): The ciphertext to be decrypted.
        shift (int): The original shift value used for encryption.
                     A positive integer will correctly reverse the encryption.

    Returns:
        str: The decrypted plaintext.
    """
    # Decryption is essentially encryption with a negative shift.
    # Python's modulo operator handles negative numbers correctly in this context.
    # For example, if shift is 3, then -3 % 26 results in 23.
    # A forward shift of 23 is equivalent to a backward shift of 3.
    return caesar_encrypt(text, -shift)

if __name__ == "__main__":
    # --- Working Example Usage ---

    print("--- Simple Caesar Cipher Demonstration ---")

    original_message = "Hello, World! This is a secret message for beginners."
    encryption_key = 3  # The common Caesar cipher shift value

    print(f"\nOriginal Message: '{original_message}'")
    print(f"Encryption Key (Shift): {encryption_key}")

    # Encrypt the message
    encrypted_message = caesar_encrypt(original_message, encryption_key)
    print(f"Encrypted Message: '{encrypted_message}'")

    # Decrypt the message
    decrypted_message = caesar_decrypt(encrypted_message, encryption_key)
    print(f"Decrypted Message: '{decrypted_message}'")

    # --- Another Example with a different key and mixed case ---
    print("\n--- Another Example ---")

    message_2 = "Python Programming is FUN and Easy!"
    key_2 = 10

    print(f"\nOriginal Message: '{message_2}'")
    print(f"Encryption Key (Shift): {key_2}")

    encrypted_message_2 = caesar_encrypt(message_2, key_2)
    print(f"Encrypted Message: '{encrypted_message_2}'")

    decrypted_message_2 = caesar_decrypt(encrypted_message_2, key_2)
    print(f"Decrypted Message: '{decrypted_message_2}'")

    # --- Example with a very large shift (should wrap around) ---
    print("\n--- Example with a Large Key (wrap around) ---")

    message_3 = "Wrap Around Test"
    key_3 = 29 # 29 % 26 is 3, so it should behave like a shift of 3

    print(f"\nOriginal Message: '{message_3}'")
    print(f"Encryption Key (Shift): {key_3} (effectively {key_3 % 26})")

    encrypted_message_3 = caesar_encrypt(message_3, key_3)
    print(f"Encrypted Message: '{encrypted_message_3}'")

    decrypted_message_3 = caesar_decrypt(encrypted_message_3, key_3)
    print(f"Decrypted Message: '{decrypted_message_3}'")
