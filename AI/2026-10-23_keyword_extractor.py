"""
This script provides a simple keyword extraction utility.

It identifies important words or phrases in a given text based on their frequency
after removing common words (stop words) and punctuation. It's designed to be
beginner-friendly, using only Python's standard library.

The process involves:
1. Converting text to lowercase.
2. Removing punctuation.
3. Splitting the text into individual words (tokens).
4. Filtering out common English stop words (e.g., 'the', 'is', 'a').
5. Counting the frequency of the remaining words.
6. Returning the most frequent words as keywords.
"""

import collections
import string

# A basic set of English stop words.
# These are common words that often carry little semantic meaning
# and are typically removed during text processing to focus on more
# significant terms.
# For more comprehensive lists, consider using libraries like NLTK or SpaCy.
STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "if", "as", "at", "by", "for", "from",
    "in", "on", "to", "with", "about", "above", "below", "between", "down",
    "up", "out", "off", "over", "under", "again", "further", "then", "once",
    "here", "there", "when", "where", "why", "how", "all", "any", "both",
    "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not",
    "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will",
    "just", "don", "should", "now", "d", "ll", "m", "o", "re", "ve", "y", "ain",
    "aren", "couldn", "didn", "doesn", "hadn", "hasn", "haven", "isn", "ma",
    "mightn", "mustn", "needn", "shan", "shouldn", "wasn", "weren", "won", "wouldn",
    "i", "he", "she", "it", "we", "you", "they", "me", "him", "her", "us", "them",
    "my", "your", "his", "its", "our", "their", "this", "that", "these", "those",
    "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
    "do", "does", "did", "having", "doing", "get", "go", "say", "see", "make",
    "come", "take", "give", "look", "know", "think", "find", "tell", "ask", "work",
    "use", "want", "show", "try", "call", "feel", "put", "mean", "leave", "begin",
    "much", "many", "even", "little", "long", "short", "big", "small",
    "new", "old", "good", "bad", "great", "poor", "high", "low", "first", "last",
    "next", "previous", "every", "always", "never", "often", "seldom", "sometimes",
    "usually", "rarely", "almost", "nearly", "quite", "really", "around", "behind",
    "besides", "beyond", "during", "except", "inside", "near", "outside", "past",
    "through", "until", "upon", "while", "though", "unless", "whatever", "who",
    "whom", "whose", "which", "what", "wherever", "whenever", "whereby", "whereas",
    "whilst", "yet", "since", "until", "else", "etc", "would", "could", "may",
    "might", "must", "can", "shall", "will", "go", "went", "gone", "going", "gets"
}


def extract_keywords(text: str, num_keywords: int = 5) -> list[str]:
    """
    Extracts keywords from a given text based on word frequency.

    The function performs the following steps:
    1. Converts the entire text to lowercase.
    2. Removes all punctuation by replacing each punctuation character with a space.
       This helps to separate words correctly (e.g., "word.next" becomes "word next").
    3. Splits the cleaned text into individual words (tokens).
    4. Filters out common English stop words defined in the STOP_WORDS set.
    5. Counts the frequency of the remaining non-stop words.
    6. Returns the `num_keywords` most frequent words.

    Args:
        text (str): The input text from which to extract keywords.
        num_keywords (int): The maximum number of keywords to return.
                            Defaults to 5. If there are fewer unique
                            non-stop words than `num_keywords`, all
                            available words will be returned.

    Returns:
        list[str]: A list of extracted keywords, sorted by frequency in
                   descending order. If multiple words have the same frequency,
                   their relative order might depend on their first appearance
                   in the text or internal Counter mechanics.
    """
    # Convert text to lowercase to ensure consistency and avoid treating
    # "Python" and "python" as different words.
    text = text.lower()

    # Create a translation table to remove punctuation.
    # str.maketrans creates a mapping from one set of characters to another.
    # Here, we map every character in string.punctuation to a space.
    # This prevents words like "hello!" from becoming "hello" which would merge
    # with "world" if we simply removed punctuation without replacement,
    # resulting in "helloworld". Replacing with spaces ensures "hello world".
    translator = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
    text = text.translate(translator)

    # Split the text into individual words.
    # text.split() splits by any whitespace and handles multiple spaces gracefully
    # by treating them as a single delimiter.
    # We then filter out any empty strings that might result (e.g., from "word  word").
    words = [word for word in text.split() if word]

    # Filter out stop words.
    # We create a new list containing only those words that are not present
    # in our predefined STOP_WORDS set.
    filtered_words = [word for word in words if word not in STOP_WORDS]

    # Count word frequencies using collections.Counter.
    # Counter is a convenient dictionary subclass designed for counting hashable objects.
    word_counts = collections.Counter(filtered_words)

    # Get the most common words.
    # `most_common(n)` returns a list of the n most common elements and their counts
    # as (element, count) tuples, from the most common to the least.
    # We only need the words themselves, so we extract the first element of each tuple.
    keywords = [word for word, count in word_counts.most_common(num_keywords)]

    return keywords


if __name__ == "__main__":
    # --- Example Usage ---

    print("--- Keyword Extractor Example ---")
    print("This script extracts keywords based on word frequency.")
    print("----------------------------------")

    # Example 1: A simple sentence
    text1 = "Python is a popular programming language. It is great for data science."
    print(f"Original Text 1:\n'{text1}'")
    keywords1 = extract_keywords(text1, num_keywords=3)
    print(f"Extracted Keywords (Top 3): {keywords1}")
    print("----------------------------------")

    # Example 2: A longer paragraph about technology and innovation
    text2 = """
    Artificial intelligence (AI) is rapidly transforming various industries.
    Machine learning, a subset of AI, enables systems to learn from data
    and improve performance over time without explicit programming.
    Deep learning, a further specialization, uses neural networks with
    many layers to model complex patterns in large datasets.
    Understanding these concepts is crucial for anyone interested in
    the future of technology and innovation.
    """
    print(f"Original Text 2:\n'{text2}'")
    keywords2 = extract_keywords(text2, num_keywords=5)
    print(f"Extracted Keywords (Top 5): {keywords2}")
    print("----------------------------------")

    # Example 3: Text with numbers and special characters
    text3 = "The company reported Q4 earnings of $1.5 billion, up 15% from last year! This marks a new record."
    print(f"Original Text 3:\n'{text3}'")
    keywords3 = extract_keywords(text3, num_keywords=4)
    print(f"Extracted Keywords (Top 4): {keywords3}")
    print("----------------------------------")

    # Example 4: Requesting more keywords than available unique significant words
    text4 = "Apple designs, manufactures and markets smartphones, personal computers, tablets, wearables and accessories worldwide."
    print(f"Original Text 4:\n'{text4}'")
    keywords4 = extract_keywords(text4, num_keywords=10) # Requesting 10, but might get fewer if less unique significant words exist
    print(f"Extracted Keywords (Top 10): {keywords4}")
    print("----------------------------------")

    # Example 5: Empty text input
    text5 = ""
    print(f"Original Text 5:\n'{text5}'")
    keywords5 = extract_keywords(text5)
    print(f"Extracted Keywords (Top 5): {keywords5}")
    print("----------------------------------")

    # Example 6: Text consisting mostly of stop words
    text6 = "The quick brown fox jumps over the lazy dog."
    print(f"Original Text 6:\n'{text6}'")
    keywords6 = extract_keywords(text6, num_keywords=3)
    print(f"Extracted Keywords (Top 3): {keywords6}")
    print("----------------------------------")

    # Example 7: Customer review text
    text7 = """
    This product is absolutely amazing! The battery life is incredible,
    and the camera takes stunning photos. I highly recommend it to everyone.
    The user interface is intuitive and easy to navigate. A truly great purchase.
    """
    print(f"Original Text 7:\n'{text7}'")
    keywords7 = extract_keywords(text7, num_keywords=4)
    print(f"Extracted Keywords (Top 4): {keywords7}")
    print("----------------------------------")
