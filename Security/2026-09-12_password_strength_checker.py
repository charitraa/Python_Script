"""
This script provides a simple password strength checker.

It evaluates a given password based on several criteria:
- Length (minimum 8 characters, with bonuses for 12+ and 16+ characters)
- Inclusion of lowercase letters
- Inclusion of uppercase letters
- Inclusion of digits
- Inclusion of special characters
- A bonus for mixing multiple character types

Based on these criteria, it assigns a score and classifies the password
as Very Weak, Weak, Moderate, Strong, or Very Strong,
and provides detailed feedback on how to improve its strength.
"""

import re

def check_password_strength(password: str) -> tuple[str, list[str]]:
    """
    Checks the strength of a given password based on various criteria.

    Args:
        password (str): The password string to be evaluated.

    Returns:
        tuple[str, list[str]]: A tuple containing:
            - A string indicating the strength level (e.g., "Weak", "Strong").
            - A list of strings providing detailed feedback.
    """
    score = 0
    feedback = []

    # --- Criteria 1: Length ---
    # A base score is given for meeting the minimum recommended length of 8 characters.
    # Additional points are awarded for longer passwords, encouraging more robust choices.
    if len(password) >= 8:
        score += 1
        feedback.append("✓ Password is at least 8 characters long.")
        if len(password) >= 12:
            score += 1 # Bonus point for passwords 12 characters or longer.
            feedback.append("✓ Password is at least 12 characters long (excellent!).")
        if len(password) >= 16:
            score += 1 # Bonus point for passwords 16 characters or longer.
            feedback.append("✓ Password is at least 16 characters long (outstanding!).")
    else:
        feedback.append("✗ Password is too short (aim for at least 8 characters).")

    # --- Criteria 2: Character Types ---
    # Each check (lowercase, uppercase, digit, special character) adds a point
    # if the password contains that type of character. Regular expressions (re module)
    # are used to efficiently search for these character types.
    has_lowercase = bool(re.search(r"[a-z]", password))
    has_uppercase = bool(re.search(r"[A-Z]", password))
    has_digit = bool(re.search(r"\d", password))
    # Regex for common special characters.
    # The `\` before `[` `]` etc. is to escape them so they are treated as literal characters
    # within the character set `[]`. This pattern covers a wide range of common special symbols.
    has_special = bool(re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?`~]", password))

    if has_lowercase:
        score += 1
        feedback.append("✓ Includes lowercase letters.")
    else:
        feedback.append("✗ Add lowercase letters.")

    if has_uppercase:
        score += 1
        feedback.append("✓ Includes uppercase letters.")
    else:
        feedback.append("✗ Add uppercase letters.")

    if has_digit:
        score += 1
        feedback.append("✓ Includes digits.")
    else:
        feedback.append("✗ Add digits.")

    if has_special:
        score += 1
        feedback.append("✓ Includes special characters.")
    else:
        feedback.append("✗ Add special characters.")

    # --- Criteria 3: Variety Bonus ---
    # A bonus point is awarded if the password uses a good mix (3 or more) of character types.
    # This encourages more complex passwords that are harder to guess.
    character_types = sum([has_lowercase, has_uppercase, has_digit, has_special])
    if character_types >= 3:
        score += 1
        feedback.append("✓ Uses a good mix of character types.")
    else:
        feedback.append("✗ Try to mix more character types for better strength.")

    # --- Determine Strength Level ---
    # The total score determines the final strength rating.
    # The maximum possible score with the current criteria is 8 points:
    # 3 (for length >= 16) + 4 (for all 4 character types) + 1 (for variety bonus) = 8
    if score <= 2:
        strength = "Very Weak"
    elif score <= 4:
        strength = "Weak"
    elif score <= 6:
        strength = "Moderate"
    elif score <= 7:
        strength = "Strong"
    else: # score == 8 (or higher, though 8 is max with current logic)
        strength = "Very Strong"

    return strength, feedback

if __name__ == "__main__":
    print("--- Password Strength Checker ---")
    print("Enter a password to check its strength. Type 'q' to quit.")

    while True:
        user_password = input("\nEnter password: ")
        
        if user_password.lower() == 'q':
            break

        if not user_password:
            print("Please enter a password.")
            continue

        strength, feedback_messages = check_password_strength(user_password)

        print(f"\nPassword entered: '{user_password}'")
        print(f"Overall Strength: {strength}")
        print("\nDetailed Feedback:")
        for msg in feedback_messages:
            print(f"  {msg}")
        print("-" * 40) # Separator for readability

    print("Exiting Password Strength Checker. Goodbye!")
