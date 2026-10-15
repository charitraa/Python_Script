"""
This script provides a simple command-line recipe finder.
It contains a predefined list of recipes and allows users to search for recipes
they can make based on the ingredients they have available.
Users can input a comma-separated list of ingredients, and the script will
list matching recipes. Users can then select a recipe to view its full details,
including ingredients and instructions.
"""

# Define a list of sample recipes. In a real-world application, these might be
# loaded from a database or a file.
ALL_RECIPES = [
    {
        "name": "Scrambled Eggs",
        "ingredients": ["eggs", "milk", "butter", "salt", "pepper"],
        "instructions": (
            "1. Crack eggs into a bowl, add milk, salt, and pepper. Whisk well.\n"
            "2. Melt butter in a non-stick pan over medium heat.\n"
            "3. Pour egg mixture into the pan. Stir gently with a spatula as eggs cook.\n"
            "4. Cook until eggs are set but still moist. Serve immediately."
        )
    },
    {
        "name": "Peanut Butter & Jelly Sandwich",
        "ingredients": ["bread", "peanut butter", "jelly"],
        "instructions": (
            "1. Take two slices of bread.\n"
            "2. Spread peanut butter on one slice and jelly on the other.\n"
            "3. Combine the two slices, jelly-side and peanut butter-side facing each other.\n"
            "4. Cut diagonally if desired and serve."
        )
    },
    {
        "name": "Simple Garden Salad",
        "ingredients": ["lettuce", "tomato", "cucumber", "olive oil", "vinegar", "salt", "pepper"],
        "instructions": (
            "1. Wash and chop lettuce, tomato, and cucumber.\n"
            "2. Combine vegetables in a large bowl.\n"
            "3. Drizzle with olive oil and vinegar.\n"
            "4. Season with salt and pepper to taste. Toss gently and serve."
        )
    },
    {
        "name": "Quick Pasta with Tomato Sauce",
        "ingredients": ["pasta", "canned tomatoes", "onion", "garlic", "olive oil", "salt", "pepper"],
        "instructions": (
            "1. Cook pasta according to package directions.\n"
            "2. While pasta cooks, heat olive oil in a pan. Add chopped onion and garlic, sauté until soft.\n"
            "3. Add canned tomatoes, salt, and pepper. Simmer for 10-15 minutes.\n"
            "4. Drain pasta, add to the sauce, toss well and serve."
        )
    }
]

def display_recipe(recipe):
    """
    Prints the details of a given recipe dictionary to the console.

    Args:
        recipe (dict): A dictionary containing 'name', 'ingredients', and 'instructions'.
    """
    print(f"\n--- {recipe['name'].upper()} ---")
    print("\nIngredients:")
    for ingredient in recipe['ingredients']:
        print(f"- {ingredient.capitalize()}") # Capitalize for better display
    print("\nInstructions:")
    print(recipe['instructions'])
    print("-" * (len(recipe['name']) + 8)) # A separator line for readability

def find_recipes_by_ingredients(available_ingredients, all_recipes_list):
    """
    Finds recipes that can be made with the given available ingredients.
    A recipe is considered 'makeable' if all of its required ingredients
    are present in the available_ingredients list.

    Args:
        available_ingredients (list): A list of ingredients the user has.
        all_recipes_list (list): A list of all available recipe dictionaries.

    Returns:
        list: A list of recipe dictionaries that can be made.
    """
    # Convert available ingredients to a set for efficient lookup
    # and convert to lowercase for case-insensitive matching.
    available_ingredients_set = {ing.lower().strip() for ing in available_ingredients}
    
    matching_recipes = []
    for recipe in all_recipes_list:
        # Convert recipe ingredients to a set and lowercase for comparison.
        recipe_ingredients_set = {ing.lower().strip() for ing in recipe['ingredients']}
        
        # Check if all ingredients required by the recipe are in the available ingredients.
        # .issubset() checks if every element in recipe_ingredients_set is also in available_ingredients_set.
        if recipe_ingredients_set.issubset(available_ingredients_set):
            matching_recipes.append(recipe)
            
    return matching_recipes

def main():
    """
    The main function to run the Recipe Finder application.
    Handles user interaction, searching, and displaying recipes.
    """
    print("Welcome to the Recipe Finder!")
    print("-----------------------------\n")

    while True:
        user_input = input(
            "Enter the ingredients you have (comma-separated), or type 'exit' to quit: "
        )
        
        if user_input.lower().strip() == 'exit':
            print("Thank you for using the Recipe Finder. Goodbye!")
            break
            
        # Split the input string by commas, remove leading/trailing whitespace,
        # and filter out any empty strings that might result from multiple commas.
        available_ingredients = [
            ing.strip() for ing in user_input.split(',') if ing.strip()
        ]

        if not available_ingredients:
            print("No ingredients entered. Please try again.")
            continue

        # Find recipes that match the available ingredients
        found_recipes = find_recipes_by_ingredients(available_ingredients, ALL_RECIPES)

        if found_recipes:
            print("\nHere are the recipes you can make:")
            for i, recipe in enumerate(found_recipes):
                print(f"{i + 1}. {recipe['name']}")
            
            # Loop to allow user to view multiple recipes or search again
            while True:
                try:
                    choice = input(
                        "\nEnter the number of the recipe to view details, "
                        "or 's' to search again, or 'exit' to quit: "
                    )
                    
                    if choice.lower() == 'exit':
                        print("Thank you for using the Recipe Finder. Goodbye!")
                        return # Exit the main function
                    
                    if choice.lower() == 's':
                        break # Break out of inner loop, go to outer loop to ask for ingredients again
                        
                    recipe_index = int(choice) - 1 # Convert user's 1-based index to 0-based
                    if 0 <= recipe_index < len(found_recipes):
                        display_recipe(found_recipes[recipe_index])
                        # After displaying, give option to view another or search again
                        another_choice = input(
                            "\nView another recipe (y/n)? Or 's' to search again: "
                        ).lower().strip()
                        if another_choice == 'n':
                            print("Thank you for using the Recipe Finder. Goodbye!")
                            return # Exit the main function
                        elif another_choice == 's':
                            break # Break inner loop, go to outer loop for new ingredients
                        # If 'y' or invalid, continue inner loop to ask for recipe choice again
                    else:
                        print("Invalid recipe number. Please try again.")
                except ValueError:
                    print("Invalid input. Please enter a number, 's', or 'exit'.")
        else:
            print(
                "\nNo recipes found with ALL of your ingredients. "
                "Try adding more ingredients or searching for something else."
            )
            # Give an option to search again or exit if no recipes were found
            retry_choice = input(
                "Would you like to search again (y/n)? "
            ).lower().strip()
            if retry_choice != 'y':
                print("Thank you for using the Recipe Finder. Goodbye!")
                break # Break out of outer loop to exit


if __name__ == "__main__":
    main()
