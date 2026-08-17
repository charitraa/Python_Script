"""
This script provides a simple currency converter using fixed exchange rates.
It allows users to convert a specified amount from one currency to another
based on predefined rates relative to the US Dollar (USD).

Please note: The exchange rates in this script are hardcoded and
are not real-time. For up-to-date rates, an external API would be required.
This version is designed for educational purposes and to demonstrate basic
conversion logic and user interaction.
"""

import sys

# Hardcoded exchange rates relative to USD.
# This means: 1 unit of the key currency is worth X USD.
# For example, 1 EUR is worth 1.08 USD.
# These rates are illustrative and not real-time.
EXCHANGE_RATES_IN_USD = {
    'USD': 1.0,   # 1 US Dollar is 1.0 US Dollar
    'EUR': 1.08,  # 1 Euro is 1.08 US Dollars
    'GBP': 1.26,  # 1 British Pound is 1.26 US Dollars
    'JPY': 0.0067, # 1 Japanese Yen is 0.0067 US Dollars
    'CAD': 0.73,  # 1 Canadian Dollar is 0.73 US Dollars
    'AUD': 0.65,  # 1 Australian Dollar is 0.65 US Dollars
    'CHF': 1.10,  # 1 Swiss Franc is 1.10 US Dollars
    'CNY': 0.14,  # 1 Chinese Yuan is 0.14 US Dollars
    'INR': 0.012, # 1 Indian Rupee is 0.012 US Dollars
}

def convert_currency(amount: float, from_currency: str, to_currency: str) -> float | None:
    """
    Converts a given amount from one currency to another using predefined rates.

    Args:
        amount (float): The amount of money to convert.
        from_currency (str): The three-letter code of the currency to convert from (e.g., 'USD').
        to_currency (str): The three-letter code of the currency to convert to (e.g., 'EUR').

    Returns:
        float: The converted amount, or None if conversion is not possible
               due to invalid currency codes or invalid amount.
    """

    # Convert currency codes to uppercase to ensure case-insensitivity
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    # Validate if the amount is positive
    if amount <= 0:
        print("Error: Amount must be a positive number.")
        return None

    # Check if 'from_currency' is in our exchange rate dictionary
    if from_currency not in EXCHANGE_RATES_IN_USD:
        print(f"Error: Currency '{from_currency}' not supported.")
        return None

    # Check if 'to_currency' is in our exchange rate dictionary
    if to_currency not in EXCHANGE_RATES_IN_USD:
        print(f"Error: Currency '{to_currency}' not supported.")
        return None

    # Step 1: Convert the 'from_currency' amount to its equivalent in USD
    # We multiply by the rate because EXCHANGE_RATES_IN_USD stores how many USD 1 unit of that currency is worth.
    # E.g., 10 EUR * 1.08 USD/EUR = 10.8 USD
    amount_in_usd = amount * EXCHANGE_RATES_IN_USD[from_currency]

    # Step 2: Convert the USD amount to the 'to_currency'
    # We divide by the rate because we want to know how many units of 'to_currency'
    # we get for the USD amount. E.g., 10.8 USD / 1.08 USD/EUR = 10 EUR
    converted_amount = amount_in_usd / EXCHANGE_RATES_IN_USD[to_currency]

    return converted_amount

if __name__ == "__main__":
    print("Welcome to the Simple Currency Converter!")
    print("---------------------------------------")

    # Display available currencies
    print("Available currencies:")
    for currency_code in sorted(EXCHANGE_RATES_IN_USD.keys()):
        print(f"- {currency_code}")
    print("---------------------------------------")

    # Get input from the user
    try:
        amount_str = input("Enter the amount to convert: ")
        amount_to_convert = float(amount_str)
    except ValueError:
        print("Invalid amount. Please enter a numerical value.")
        sys.exit(1) # Exit the script if the amount is invalid

    from_curr = input("Enter the currency to convert FROM (e.g., USD): ").strip()
    to_curr = input("Enter the currency to convert TO (e.g., EUR): ").strip()

    print("\n--- Conversion Result ---")
    # Perform the conversion
    result = convert_currency(amount_to_convert, from_curr, to_curr)

    if result is not None:
        # Format the output to two decimal places for currency
        print(f"{amount_to_convert:.2f} {from_curr.upper()} is equal to {result:.2f} {to_curr.upper()}")
    else:
        print("Conversion failed. Please check your inputs.")

    print("---------------------------------------")
    print("Thank you for using the converter!")
