"""
This script implements a simple recommendation engine using item-item collaborative filtering.
It recommends items to a user based on the similarity between items the user has already rated
and other items in the dataset. The similarity between items is calculated using Pearson
correlation coefficient based on how different users have rated those items.

The core idea is: "If you liked item A, and item A is very similar to item B, then you might like item B."

Data Structure:
The script expects a dictionary where keys are user names and values are another dictionary
containing item names as keys and their ratings as values.
Example:
    preferences = {
        'Alice': {'Movie1': 5, 'Movie2': 3, 'Movie3': 4},
        'Bob': {'Movie1': 4, 'Movie2': 2, 'Movie4': 5},
        # ...
    }
"""

import math

def _get_common_raters(item1, item2, preferences):
    """
    Helper function to find users who have rated both item1 and item2.
    Returns a list of tuples: [(rating_item1_by_user1, rating_item2_by_user1), ...]
    """
    common_ratings = []
    for user_prefs in preferences.values():
        if item1 in user_prefs and item2 in user_prefs:
            common_ratings.append((user_prefs[item1], user_prefs[item2]))
    return common_ratings

def calculate_similarity(item1, item2, preferences):
    """
    Calculates the Pearson correlation coefficient between two items based on
    user ratings. This measures how similar items are based on common users' preferences.

    Pearson correlation is robust to differences in individual user rating scales
    (e.g., one user might always rate high, another always rates low).

    Args:
        item1 (str): The name of the first item.
        item2 (str): The name of the second item.
        preferences (dict): A dictionary of user preferences.
                            Format: {'user_name': {'item_name': rating, ...}, ...}

    Returns:
        float: The Pearson correlation coefficient (between -1 and 1).
               Returns 0.0 if there are no common raters or if one of the items
               has a constant rating across common users (no variance).
    """
    common_ratings = _get_common_raters(item1, item2, preferences)

    if len(common_ratings) < 2:
        # Not enough common users to calculate a meaningful correlation.
        return 0.0

    # Extract ratings for item1 and item2 from common users
    ratings_item1 = [r[0] for r in common_ratings]
    ratings_item2 = [r[1] for r in common_ratings]

    n = len(ratings_item1)

    # Calculate sums
    sum_item1 = sum(ratings_item1)
    sum_item2 = sum(ratings_item2)

    # Calculate sum of squares
    sum_sq_item1 = sum([x**2 for x in ratings_item1])
    sum_sq_item2 = sum([y**2 for y in ratings_item2])

    # Calculate sum of products
    sum_prod_items = sum([ratings_item1[i] * ratings_item2[i] for i in range(n)])

    # Calculate Pearson numerator
    # Formula: SUM( (Xi - mean_X) * (Yi - mean_Y) )
    # Simplified: SUM(XiYi) - (SUM(Xi) * SUM(Yi) / N)
    numerator = sum_prod_items - (sum_item1 * sum_item2 / n)

    # Calculate Pearson denominator
    # Formula: SQRT( SUM((Xi - mean_X)^2) * SUM((Yi - mean_Y)^2) )
    # Simplified: SQRT( (SUM(Xi^2) - SUM(Xi)^2 / N) * (SUM(Yi^2) - SUM(Yi)^2 / N) )
    denominator_item1 = math.sqrt(sum_sq_item1 - (sum_item1**2 / n))
    denominator_item2 = math.sqrt(sum_sq_item2 - (sum_item2**2 / n))

    denominator = denominator_item1 * denominator_item2

    if denominator == 0:
        # Avoid division by zero. This happens if all ratings for an item are identical
        # among the common users (e.g., all common users rated item1 as '5').
        # In this case, there's no variance, and correlation is undefined, so we return 0.
        return 0.0
    
    return numerator / denominator


def get_recommendations(user, preferences, num_recommendations=5):
    """
    Generates item recommendations for a given user.

    The recommendations are based on items the user has already rated.
    It identifies items similar to those rated by the user (especially highly-rated ones)
    and suggests items the user hasn't seen yet. The score for a recommended item
    is a weighted sum of similarities, where weights are the user's ratings for similar items.

    Args:
        user (str): The name of the user for whom to generate recommendations.
        preferences (dict): A dictionary of all user preferences (ratings).
        num_recommendations (int): The maximum number of recommendations to return.

    Returns:
        list: A sorted list of tuples (item_name, predicted_score) for recommended items.
              The list is sorted in descending order of predicted score.
              Returns an empty list if the user is not found or has no rated items.
    """
    if user not in preferences or not preferences[user]:
        print(f"Warning: User '{user}' not found or has no rated items.")
        return []

    user_ratings = preferences[user]
    
    # Collect all unique items from the entire dataset
    all_items = set()
    for user_prefs in preferences.values():
        all_items.update(user_prefs.keys())

    # Dictionary to store potential recommendations and their scores
    recommendation_scores = {}

    # Iterate over items the target user has already rated
    for rated_item, user_rating_for_item in user_ratings.items():
        # Iterate over all other items in the dataset
        for candidate_item in all_items:
            # We are interested in items the user hasn't rated yet
            if candidate_item not in user_ratings:
                # Calculate similarity between the rated item and the candidate item
                similarity = calculate_similarity(rated_item, candidate_item, preferences)

                # Only consider positively correlated items for recommendations.
                # A negative similarity means items are inversely related, not helpful here.
                if similarity > 0:
                    # Add to the recommendation score for the candidate item.
                    # The score is weighted by the user's rating for the similar item.
                    # This means if a user liked 'Movie A' (rating 5) and 'Movie A' is
                    # highly similar to 'Movie B', 'Movie B' gets a higher score
                    # than if 'Movie A' was only moderately liked (rating 3).
                    recommendation_scores.setdefault(candidate_item, 0.0)
                    recommendation_scores[candidate_item] += similarity * user_rating_for_item

    # Sort the recommendations by score in descending order
    sorted_recommendations = sorted(
        recommendation_scores.items(), key=lambda item: item[1], reverse=True
    )

    return sorted_recommendations[:num_recommendations]


if __name__ == "__main__":
    # --- Example Usage ---

    # Define a sample dataset of user preferences (ratings for items)
    # Ratings are on a scale of 1-5, where 5 is best.
    sample_preferences = {
        'Alice':   {'Laptop': 5, 'Smartphone': 4, 'Headphones': 3, 'Monitor': 4, 'Keyboard': 2},
        'Bob':     {'Laptop': 4, 'Headphones': 5, 'Mouse': 4, 'Webcam': 3, 'Monitor': 3},
        'Charlie': {'Smartphone': 5, 'Headphones': 4, 'Webcam': 5, 'Mouse': 5, 'Gaming Chair': 4},
        'David':   {'Laptop': 3, 'Monitor': 5, 'Keyboard': 4, 'Mouse': 3, 'Gaming Chair': 5},
        'Eve':     {'Smartphone': 4, 'Laptop': 3, 'Headphones': 4, 'Webcam': 4, 'Gaming Chair': 3},
    }

    print("--- Sample User Preferences ---")
    for user, items in sample_preferences.items():
        print(f"{user}: {items}")
    print("\n" + "="*40 + "\n")

    # Generate recommendations for Alice
    user_to_recommend_alice = 'Alice'
    print(f"Generating recommendations for '{user_to_recommend_alice}':")
    alice_recommendations = get_recommendations(user_to_recommend_alice, sample_preferences)

    if alice_recommendations:
        for item, score in alice_recommendations:
            print(f"- {item} (Predicted Score: {score:.2f})")
    else:
        print(f"No recommendations found for {user_to_recommend_alice}.")

    print("\n" + "="*40 + "\n")

    # Generate recommendations for Charlie
    user_to_recommend_charlie = 'Charlie'
    print(f"Generating recommendations for '{user_to_recommend_charlie}':")
    charlie_recommendations = get_recommendations(user_to_recommend_charlie, sample_preferences)

    if charlie_recommendations:
        for item, score in charlie_recommendations:
            print(f"- {item} (Predicted Score: {score:.2f})")
    else:
        print(f"No recommendations found for {user_to_recommend_charlie}.")

    print("\n" + "="*40 + "\n")

    # Generate recommendations for a user not in the dataset
    user_to_recommend_frank = 'Frank'
    print(f"Generating recommendations for '{user_to_recommend_frank}' (not in dataset):")
    frank_recommendations = get_recommendations(user_to_recommend_frank, sample_preferences)
    if not frank_recommendations:
        print(f"As expected, no recommendations found for {user_to_recommend_frank}.")

    print("\n" + "="*40 + "\n")

    # Example with a user who has rated only one item (might get fewer or no recommendations
    # due to lack of diverse input for similarity calculations).
    # Adding a new user who only rated one item.
    sample_preferences['Grace'] = {'Desktop PC': 5}
    user_to_recommend_grace = 'Grace'
    print(f"Generating recommendations for '{user_to_recommend_grace}' (rated one item):")
    grace_recommendations = get_recommendations(user_to_recommend_grace, sample_preferences)
    if grace_recommendations:
        for item, score in grace_recommendations:
            print(f"- {item} (Predicted Score: {score:.2f})")
    else:
        print(f"No strong recommendations found for {user_to_recommend_grace} based on limited input data.")
    print("\n" + "="*40 + "\n")
