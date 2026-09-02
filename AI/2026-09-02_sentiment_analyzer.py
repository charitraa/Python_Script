# pip install nltk
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

"""
This script provides a simple sentiment analysis tool using NLTK's VADER (Valence Aware Dictionary and sEntiment Reasoner)
lexicon and rule-based sentiment analysis model. It takes a piece of text and classifies its sentiment as
Positive, Negative, or Neutral, along with numerical scores.

VADER is a lexicon and rule-based sentiment analysis model that is specifically attuned to sentiments
expressed in social media, and works well on text from a variety of domains.
"""

def analyze_sentiment(text: str) -> dict:
    """
    Analyzes the sentiment of a given text using NLTK's VADER model.

    Args:
        text (str): The input string text to be analyzed.

    Returns:
        dict: A dictionary containing the sentiment classification ('Positive', 'Negative', 'Neutral')
              and the raw VADER polarity scores (neg, neu, pos, compound).
    """
    # Initialize the VADER sentiment intensity analyzer.
    # For simplicity and self-containment within the function, it's initialized here.
    # In a larger application, you might initialize this once and reuse the object.
    analyzer = SentimentIntensityAnalyzer()

    # Get the polarity scores for the text.
    # Scores include 'neg' (negative), 'neu' (neutral), 'pos' (positive), and 'compound'.
    # The 'compound' score is a normalized, weighted composite score which is the most popular
    # metric to use for overall sentiment analysis. It ranges from -1 (most extreme negative)
    # to +1 (most extreme positive).
    vs = analyzer.polarity_scores(text)

    # Determine the sentiment label based on the compound score.
    # Common thresholds are used:
    #   - compound score >= 0.05 for positive
    #   - compound score <= -0.05 for negative
    #   - otherwise (between -0.05 and 0.05) for neutral
    sentiment = ""
    if vs['compound'] >= 0.05:
        sentiment = "Positive"
    elif vs['compound'] <= -0.05:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    return {
        "sentiment": sentiment,
        "scores": vs
    }

if __name__ == "__main__":
    # Before using VADER, its lexicon (data) needs to be downloaded.
    # This block checks if the 'vader_lexicon' is already present and downloads it if not.
    # This prevents repeated downloads and ensures the script works on first run.
    try:
        nltk.data.find('sentiment/vader_lexicon.zip')
    except nltk.downloader.DownloadError:
        print("Downloading VADER lexicon for NLTK (first-time setup)...")
        nltk.download('vader_lexicon')
        print("VADER lexicon downloaded successfully.\n")
    else:
        print("VADER lexicon is already downloaded.\n")


    print("--- Sentiment Analyzer ---")
    print("Analyzing various text samples:\n")

    # Example texts to analyze
    texts = [
        "This movie was fantastic! I loved every moment of it.",
        "I absolutely hated the food, it was terrible and overpriced.",
        "The weather today is neither good nor bad, just cloudy.",
        "What a wonderful day to learn Python programming!",
        "The customer service was slow, but the product itself is decent.",
        "This is an incredibly sad story.",
        "I am not happy with the situation.",
        "This is not a bad movie.", # Example of negation handling
        "The concert was good, but the venue was awful.", # Example of mixed sentiment
        "Python is a powerful programming language."
    ]

    # Analyze each text and print the results
    for i, text in enumerate(texts):
        result = analyze_sentiment(text)
        print(f"Text {i+1}: \"{text}\"")
        print(f"  Sentiment: {result['sentiment']}")
        # Print scores formatted to two decimal places for readability
        print(f"  Scores (Neg, Neu, Pos, Compound): {result['scores']['neg']:.2f}, {result['scores']['neu']:.2f}, {result['scores']['pos']:.2f}, {result['scores']['compound']:.2f}\n")

    print("--- End of Analysis ---")
