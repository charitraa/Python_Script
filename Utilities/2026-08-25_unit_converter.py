"""
This script provides a simple command-line unit converter.

It supports conversions for three main categories:
1.  **Length**: meters (m), kilometers (km), miles (mi), feet (ft), inches (in), centimeters (cm)
2.  **Mass**: kilograms (kg), grams (g), pounds (lb), ounces (oz)
3.  **Temperature**: Celsius (c), Fahrenheit (f), Kelvin (k)

The user is prompted to enter a numerical value, its original unit, and the desired target unit.
The script then calculates and displays the converted value.
It includes basic error checking to handle invalid numerical input, unknown units, or attempts
to convert between units of different categories (e.g., length to mass).
"""

# --- Unit Definitions and Conversion Factors ---

# Conversion factors for length units to a base unit (meter).
# Example: 1 km = 1000 m, so the factor for 'km' is 1000.0.
LENGTH_UNITS = {
    "m": 1.0,         # meters (base unit for length conversions)
    "km": 1000.0,     # kilometers
    "mi": 1609.344,   # miles
    "ft": 0.3048,     # feet
    "in": 0.0254,     # inches
    "cm": 0.01,       # centimeters
}

# Conversion factors for mass units to a base unit (kilogram).
# Example: 1 g = 0.001 kg, so the factor for 'g' is 0.001.
MASS_UNITS = {
    "kg": 1.0,        # kilograms (base unit for mass conversions)
    "g": 0.001,       # grams
    "lb": 0.453592,   # pounds
    "oz": 0.0283495,  # ounces
}

# Temperature units are handled differently due to their non-linear conversions (involving offsets).
# We use string identifiers here, and specific functions for their conversion logic.
TEMPERATURE_UNITS = {
    "c": "celsius",
    "f": "fahrenheit",
    "k": "kelvin",
}

# A dynamic dictionary to map unit names to their respective categories.
# This helps in identifying what type of conversion needs to be performed
# and ensures units are in the same category for a valid conversion.
UNIT_CATEGORIES = {}
for unit_name in LENGTH_UNITS.keys():
    UNIT_CATEGORIES[unit_name] = "length"
for unit_name in MASS_UNITS.keys():
    UNIT_CATEGORIES[unit_name] = "mass"
for unit_name in TEMPERATURE_UNITS.keys():
    UNIT_CATEGORIES[unit_name] = "temperature"


# --- Conversion Helper Functions (Internal Use) ---

def _convert_length(value: float, from_unit: str, to_unit: str) -> float:
    """
    Converts a value between different length units.
    It works by first converting the value from its original unit to the base unit (meters),
    and then from meters to the target unit.
    """
    # Convert the original value to the base unit (meters)
    value_in_meters = value * LENGTH_UNITS[from_unit]
    # Convert from meters to the target unit
    converted_value = value_in_meters / LENGTH_UNITS[to_unit]
    return converted_value

def _convert_mass(value: float, from_unit: str, to_unit: str) -> float:
    """
    Converts a value between different mass units.
    Similar to length, it converts the value from its original unit to the base unit (kilograms),
    and then from kilograms to the target unit.
    """
    # Convert the original value to the base unit (kilograms)
    value_in_kg = value * MASS_UNITS[from_unit]
    # Convert from kilograms to the target unit
    converted_value = value_in_kg / MASS_UNITS[to_unit]
    return converted_value

def _convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
    """
    Converts a value between different temperature units.
    This function uses Celsius as an intermediate base for all conversions to simplify logic.
    """
    # Step 1: Convert the original value to Celsius
    value_in_celsius: float
    if from_unit == "f":
        # Fahrenheit to Celsius: (F - 32) * 5/9
        value_in_celsius = (value - 32) * 5 / 9
    elif from_unit == "k":
        # Kelvin to Celsius: K - 273.15
        value_in_celsius = value - 273.15
    elif from_unit == "c":
        # Value is already in Celsius
        value_in_celsius = value
    else:
        # This case should ideally be caught by the main converter function,
        # but included as a safeguard.
        raise ValueError(f"Unsupported temperature 'from' unit: {from_unit}")

    # Step 2: Convert from Celsius to the target unit
    converted_value: float
    if to_unit == "f":
        # Celsius to Fahrenheit: C * 9/5 + 32
        converted_value = value_in_celsius * 9 / 5 + 32
    elif to_unit == "k":
        # Celsius to Kelvin: C + 273.15
        converted_value = value_in_celsius + 273.15
    elif to_unit == "c":
        # Target is Celsius, no further conversion needed
        converted_value = value_in_celsius
    else:
        # Safeguard for unsupported target units
        raise ValueError(f"Unsupported temperature 'to' unit: {to_unit}")

    return converted_value


# --- Main Conversion Function ---

def convert_units(value: float, from_unit: str, to_unit: str) -> float:
    """
    Main function to convert a numerical value from one unit to another.

    Args:
        value (float): The numerical value to be converted.
        from_unit (str): The abbreviation of the original unit (e.g., "m", "kg", "f").
        to_unit (str): The abbreviation of the desired target unit (e.g., "km", "g", "c").

    Returns:
        float: The converted value.

    Raises:
        ValueError: If the units are unknown, if they belong to different categories
                    (e.g., trying to convert length to mass), or if an unexpected
                    conversion error occurs.
    """
    # Normalize unit inputs to lowercase for consistent matching, and remove leading/trailing spaces.
    from_unit = from_unit.strip().lower()
    to_unit = to_unit.strip().lower()

    # Determine the category of the source unit using the UNIT_CATEGORIES mapping.
    from_category = UNIT_CATEGORIES.get(from_unit)
    if not from_category:
        # If the source unit is not found, raise an error with a helpful message.
        raise ValueError(f"Unknown source unit: '{from_unit}'. "
                         f"Please use one of: {', '.join(UNIT_CATEGORIES.keys())}")

    # Determine the category of the target unit.
    to_category = UNIT_CATEGORIES.get(to_unit)
    if not to_category:
        # If the target unit is not found, raise an error.
        raise ValueError(f"Unknown target unit: '{to_unit}'. "
                         f"Please use one of: {', '.join(UNIT_CATEGORIES.keys())}")

    # Ensure both units belong to the same category for a valid conversion.
    # It's illogical to convert, for example, length to mass.
    if from_category != to_category:
        raise ValueError(f"Cannot convert from {from_category} ('{from_unit}') "
                         f"to {to_category} ('{to_unit}'). Units must be in the same category.")

    # Perform the conversion based on the identified category by calling the appropriate helper function.
    if from_category == "length":
        return _convert_length(value, from_unit, to_unit)
    elif from_category == "mass":
        return _convert_mass(value, from_unit, to_unit)
    elif from_category == "temperature":
        return _convert_temperature(value, from_unit, to_unit)
    else:
        # This case should theoretically not be reached if UNIT_CATEGORIES is correctly defined
        # and covers all helper functions. It acts as a final safeguard.
        raise ValueError(f"Unsupported conversion category: {from_category}")


# --- Example Usage (Main execution block) ---

if __name__ == "__main__":
    print("Welcome to the Python Unit Converter!")
    print("--------------------------------------------------")
    print("Available units and their abbreviations:")
    print(f"  Length: {', '.join(LENGTH_UNITS.keys())}")
    print(f"  Mass: {', '.join(MASS_UNITS.keys())}")
    print(f"  Temperature: {', '.join(TEMPERATURE_UNITS.keys())}")
    print("--------------------------------------------------")

    # The main loop allows the user to perform multiple conversions without restarting the script.
    while True:
        try:
            # Get the numerical value from the user.
            value_str = input("Enter the value to convert (or type 'quit' to exit): ").strip()
            if value_str.lower() == 'quit':
                break # Exit the loop if the user types 'quit'

            # Attempt to convert the input string to a floating-point number.
            value = float(value_str)

            # Get the original unit from the user.
            from_unit = input("Enter the original unit (e.g., m, kg, f): ").strip().lower()
            # Get the target unit from the user.
            to_unit = input("Enter the target unit (e.g., km, g, c): ").strip().lower()

            # Perform the conversion using the main converter function.
            converted_value = convert_units(value, from_unit, to_unit)

            # Display the result, rounded to four decimal places for readability.
            print(f"\n{value} {from_unit} is {converted_value:.4f} {to_unit}\n")

        except ValueError as e:
            # Catch and display errors related to invalid numerical input, unknown units,
            # or category mismatches, which are raised by `float()` or `convert_units()`.
            print(f"\nError: {e}\n")
        except Exception as e:
            # Catch any other unexpected errors that might occur.
            print(f"\nAn unexpected error occurred: {e}\n")

        print("--------------------------------------------------") # Separator for next conversion or before exit

    print("Thank you for using the Unit Converter. Goodbye!")
