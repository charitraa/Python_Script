import json
import os

"""
A simple command-line Contact Book Manager.

Allows users to add, view, search, update, and delete contacts.
Contacts are stored in a JSON file for persistence, making them
available even after the program closes.

Features:
- Add new contacts with name, phone, and email.
- View all existing contacts.
- Search for contacts by name, phone, or email.
- Update details of an existing contact.
- Delete contacts.
- Data persistence using a JSON file.
"""

# Define the filename for storing contacts.
FILENAME = 'contacts.json'

def load_contacts(filename):
    """
    Loads contacts from the specified JSON file.

    Args:
        filename (str): The path to the JSON file.

    Returns:
        list: A list of contact dictionaries, or an empty list if the
              file doesn't exist or is invalid.
    """
    # Check if the file exists. If not, it means no contacts have been saved yet.
    if not os.path.exists(filename):
        return []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            # Load the JSON data from the file.
            return json.load(f)
    except json.JSONDecodeError:
        # If the file exists but contains invalid JSON, print an error
        # and return an empty list to prevent program crash.
        print(f"Error: Could not decode JSON from {filename}. Starting with empty contact list.")
        return []
    except Exception as e:
        # Catch any other potential errors during file loading.
        print(f"An unexpected error occurred while loading contacts: {e}")
        return []

def save_contacts(filename, contacts):
    """
    Saves the current list of contacts to the specified JSON file.

    Args:
        filename (str): The path to the JSON file.
        contacts (list): The list of contact dictionaries to save.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            # Use json.dump to write the contacts list to the file.
            # indent=4 makes the JSON file human-readable.
            json.dump(contacts, f, indent=4)
    except Exception as e:
        # Catch any errors during file saving.
        print(f"Error: Could not save contacts to {filename}: {e}")

def display_contact(contact, index=None):
    """
    Helper function to print a single contact's details in a formatted way.

    Args:
        contact (dict): The contact dictionary.
        index (int, optional): The index of the contact in a list,
                               used for numbering. Defaults to None.
    """
    # Add a number prefix if an index is provided.
    prefix = f"{index + 1}. " if index is not None else ""
    print(f"{prefix}Name: {contact['name']}")
    print(f"   Phone: {contact['phone']}")
    # Use .get() for optional fields like 'email' to provide a default 'N/A'
    # if the key is missing or its value is None.
    print(f"   Email: {contact.get('email', 'N/A') if contact.get('email') else 'N/A'}")
    print("-" * 20)

def find_contacts_by_name(contacts, name_query):
    """
    Finds contacts whose names (case-insensitive) contain the name_query.

    Args:
        contacts (list): The list of all contact dictionaries.
        name_query (str): The string to search for within contact names.

    Returns:
        list: A list of tuples, where each tuple contains (original_index, contact_dict).
              This allows us to modify the original list correctly.
    """
    found = []
    name_query_lower = name_query.lower()
    for i, contact in enumerate(contacts):
        if name_query_lower in contact['name'].lower():
            found.append((i, contact))
    return found

def add_contact(contacts):
    """
    Prompts the user for contact details and adds a new contact to the list.

    Args:
        contacts (list): The list of contact dictionaries to modify.
    """
    print("\n--- Add New Contact ---")
    while True:
        name = input("Enter contact name: ").strip()
        if name: # Ensure name is not empty
            break
        else:
            print("Name cannot be empty. Please try again.")

    # Optional: Warn if a contact with the same name already exists.
    # The program allows duplicate names as different people can have the same name.
    if any(c['name'].lower() == name.lower() for c in contacts):
        print(f"Warning: A contact named '{name}' already exists.")

    while True:
        phone = input("Enter phone number: ").strip()
        if phone: # Ensure phone number is not empty
            break
        else:
            print("Phone number cannot be empty. Please try again.")

    email = input("Enter email address (optional): ").strip()

    new_contact = {
        'name': name,
        'phone': phone,
        'email': email if email else None # Store None if email field is left empty
    }
    contacts.append(new_contact)
    print(f"Contact '{name}' added successfully!")
    save_contacts(FILENAME, contacts) # Save changes immediately

def view_contacts(contacts):
    """
    Displays all contacts in the list.

    Args:
        contacts (list): The list of contact dictionaries.
    """
    print("\n--- All Contacts ---")
    if not contacts:
        print("No contacts available. Add some first!")
        return

    # Iterate through contacts and display each one with its index.
    for i, contact in enumerate(contacts):
        display_contact(contact, i)

def search_contact(contacts):
    """
    Prompts the user for a search term and displays matching contacts.
    Searches across name, phone, and email fields (case-insensitive).

    Args:
        contacts (list): The list of contact dictionaries.
    """
    print("\n--- Search Contact ---")
    if not contacts:
        print("No contacts to search. Add some first!")
        return

    search_term = input("Enter search term (name, phone, or email): ").strip().lower()
    if not search_term:
        print("Search term cannot be empty.")
        return

    found_matches = []
    for contact in contacts:
        # Check if the search term is in name, phone, or email (case-insensitive)
        # Handle cases where 'email' might be None.
        if (search_term in contact['name'].lower() or
            search_term in contact['phone'].lower() or
            (contact['email'] and search_term in contact['email'].lower())):
            found_matches.append(contact)

    if not found_matches:
        print(f"No contacts found matching '{search_term}'.")
    else:
        print(f"\n--- Found {len(found_matches)} Contact(s) ---")
        for i, contact in enumerate(found_matches):
            display_contact(contact, i)

def update_contact(contacts):
    """
    Allows the user to update an existing contact's details.
    If multiple contacts match the name, the user can choose which one to update.

    Args:
        contacts (list): The list of contact dictionaries to modify.
    """
    print("\n--- Update Contact ---")
    if not contacts:
        print("No contacts to update. Add some first!")
        return

    name_query = input("Enter the name of the contact to update: ").strip()
    if not name_query:
        print("Name query cannot be empty.")
        return

    found = find_contacts_by_name(contacts, name_query)

    if not found:
        print(f"No contacts found with name matching '{name_query}'.")
        return

    contact_to_update_index = -1
    selected_contact_data = None

    if len(found) == 1:
        # If only one contact is found, select it automatically.
        contact_to_update_index, selected_contact_data = found[0]
        print(f"Found one contact: {selected_contact_data['name']}")
    else:
        # If multiple contacts are found, prompt the user to choose.
        print("\nMultiple contacts found. Please choose one to update:")
        for i, (original_idx, contact) in enumerate(found):
            print(f"  {i+1}. {contact['name']} (Phone: {contact['phone']})")

        while True:
            try:
                choice = int(input("Enter the number of the contact to update: "))
                if 1 <= choice <= len(found):
                    contact_to_update_index, selected_contact_data = found[choice - 1]
                    break
                else:
                    print("Invalid choice. Please enter a number from the list.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    print(f"\nUpdating contact: {selected_contact_data['name']}")

    # Prompt for new details, using current values as defaults.
    # If the user enters nothing, the current value is retained.
    new_name = input(f"Enter new name (current: {selected_contact_data['name']}): ").strip()
    if not new_name:
        new_name = selected_contact_data['name']

    new_phone = input(f"Enter new phone number (current: {selected_contact_data['phone']}): ").strip()
    if not new_phone:
        new_phone = selected_contact_data['phone']

    # Handle current email which might be None or an empty string.
    current_email = selected_contact_data.get('email', '') or ''
    new_email = input(f"Enter new email address (current: {current_email}): ").strip()
    
    # If user enters nothing, keep current email. If they enter 'None' or empty string
    # and there was no previous email, set to None.
    if not new_email:
        new_email = current_email if current_email else None
    else:
        new_email = new_email # Use the new non-empty input

    # Update the contact in the main list using its original index.
    contacts[contact_to_update_index]['name'] = new_name
    contacts[contact_to_update_index]['phone'] = new_phone
    contacts[contact_to_update_index]['email'] = new_email

    print(f"Contact '{selected_contact_data['name']}' updated successfully!")
    save_contacts(FILENAME, contacts) # Save changes immediately

def delete_contact(contacts):
    """
    Allows the user to delete an existing contact.
    If multiple contacts match the name, the user can choose which one to delete.

    Args:
        contacts (list): The list of contact dictionaries to modify.
    """
    print("\n--- Delete Contact ---")
    if not contacts:
        print("No contacts to delete. Add some first!")
        return

    name_query = input("Enter the name of the contact to delete: ").strip()
    if not name_query:
        print("Name query cannot be empty.")
        return

    found = find_contacts_by_name(contacts, name_query)

    if not found:
        print(f"No contacts found with name matching '{name_query}'.")
        return

    contact_to_delete_index = -1
    selected_contact_data = None

    if len(found) == 1:
        # If only one contact is found, select it automatically.
        contact_to_delete_index, selected_contact_data = found[0]
        print(f"Found one contact: {selected_contact_data['name']}")
    else:
        # If multiple contacts are found, prompt the user to choose.
        print("\nMultiple contacts found. Please choose one to delete:")
        for i, (original_idx, contact) in enumerate(found):
            print(f"  {i+1}. {contact['name']} (Phone: {contact['phone']})")

        while True:
            try:
                choice = int(input("Enter the number of the contact to delete: "))
                if 1 <= choice <= len(found):
                    contact_to_delete_index, selected_contact_data = found[choice - 1]
                    break
                else:
                    print("Invalid choice. Please enter a number from the list.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    confirm = input(f"Are you sure you want to delete '{selected_contact_data['name']}'? (yes/no): ").strip().lower()
    if confirm == 'yes':
        # Remove the contact from the list using its original index.
        # This is safe because 'found' stores the original index before any pops.
        contacts.pop(contact_to_delete_index)
        print(f"Contact '{selected_contact_data['name']}' deleted successfully!")
        save_contacts(FILENAME, contacts) # Save changes immediately
    else:
        print("Deletion cancelled.")

def display_menu():
    """Prints the main menu options to the console."""
    print("\n--- Contact Book Menu ---")
    print("1. Add New Contact")
    print("2. View All Contacts")
    print("3. Search Contact")
    print("4. Update Contact")
    print("5. Delete Contact")
    print("6. Exit")
    print("-------------------------")

def main():
    """
    Main function to run the Contact Book Manager application.
    Loads contacts at startup, presents a menu, and handles user choices.
    """
    # Load existing contacts when the application starts.
    contacts = load_contacts(FILENAME)

    while True:
        display_menu()
        choice = input("Enter your choice (1-6): ").strip()

        if choice == '1':
            add_contact(contacts)
        elif choice == '2':
            view_contacts(contacts)
        elif choice == '3':
            search_contact(contacts)
        elif choice == '4':
            update_contact(contacts)
        elif choice == '5':
            delete_contact(contacts)
        elif choice == '6':
            print("Exiting Contact Book Manager. Goodbye!")
            break # Exit the loop and end the program
        else:
            print("Invalid choice. Please enter a number between 1 and 6.")

# This ensures that main() is called only when the script is executed directly.
if __name__ == "__main__":
    main()
