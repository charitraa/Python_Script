import re
from collections import Counter

def summarize_text(text, num_sentences=None, ratio=0.3):
    """
    Generates a summary of the input text using a simple frequency-based method.

    This function tokenizes the text into sentences, calculates the frequency
    of words, scores each sentence based on the frequency of its words, and
    then returns the top-scoring sentences as the summary.

    Args:
        text (str): The input text to be summarized.
        num_sentences (int, optional): The desired number of sentences in the summary.
                                       If provided, 'ratio' is ignored. Defaults to None.
        ratio (float, optional): The desired ratio of summary sentences to total sentences
                                 in the original text (e.g., 0.3 for 30%).
                                 Ignored if 'num_sentences' is provided. Defaults to 0.3.

    Returns:
        str: The summarized text.
    """

    if not text or not isinstance(text, str):
        return "" # Return empty string for invalid input

    # Define a set of common English stop words to filter out less important words.
    # This list can be expanded for better accuracy but kept small for simplicity
    # and to avoid external dependencies.
    stop_words = {
        "a", "an", "and", "are", "as", "is", "at", "be", "but", "by", "for",
        "in", "if", "into", "it", "not", "of", "on", "or", "such", "that",
        "the", "their", "then", "there", "these", "they", "this", "to", "was",
        "will", "with", "he", "she", "it", "we", "you", "them", "which", "when",
        "where", "who", "whom", "how", "has", "had", "do", "does", "did", "have",
        "from", "him", "her", "its", "our", "us", "my", "your", "mine", "yours"
    }

    # 1. Sentence Tokenization
    # Split the text into sentences using common sentence-ending punctuation.
    # We use re.split to handle multiple delimiters and keep the delimiters for joining later.
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', text)
    # Filter out any empty strings that might result from splitting.
    sentences = [s.strip() for s in sentences if s.strip()]

    if not sentences:
        return "" # No sentences found

    # 2. Word Tokenization and Cleaning
    # Create a list of all meaningful words in the text, converting to lowercase
    # and removing punctuation.
    words = []
    for sentence in sentences:
        # Use regex to find all alphabetic sequences, convert to lowercase
        # and filter out stop words.
        clean_words = re.findall(r'\b[a-z]+\b', sentence.lower())
        words.extend([word for word in clean_words if word not in stop_words])

    # 3. Calculate Word Frequencies
    # Use collections.Counter to easily count the occurrences of each word.
    word_frequencies = Counter(words)

    # If all words are stop words or no words remain after cleaning,
    # we can't score sentences meaningfully.
    if not word_frequencies:
        # Fallback: if no meaningful words, return a truncated version or first sentence
        return sentences[0] if sentences else ""

    # Normalize frequencies: divide each word's frequency by the frequency of the most common word.
    # This helps in preventing very long documents from skewing scores too much.
    max_frequency = max(word_frequencies.values())
    for word in word_frequencies:
        word_frequencies[word] /= max_frequency

    # 4. Score Sentences
    # Assign a score to each sentence based on the sum of normalized frequencies of its words.
    sentence_scores = {}
    for i, sentence in enumerate(sentences):
        # Again, clean words from the current sentence for scoring.
        clean_words = re.findall(r'\b[a-z]+\b', sentence.lower())
        current_sentence_score = 0
        for word in clean_words:
            if word in word_frequencies:
                current_sentence_score += word_frequencies[word]
        sentence_scores[i] = current_sentence_score

    # 5. Select Top Sentences for Summary
    # Determine the number of sentences for the summary.
    if num_sentences is not None:
        summary_size = min(num_sentences, len(sentences))
    else:
        summary_size = max(1, int(len(sentences) * ratio)) # Ensure at least one sentence if ratio is very small

    # Sort sentences by their scores in descending order.
    # We store (index, score) pairs and sort by score.
    ranked_sentences = sorted(sentence_scores.items(), key=lambda item: item[1], reverse=True)

    # Select the top 'summary_size' sentence indices.
    top_sentence_indices = [index for index, _ in ranked_sentences[:summary_size]]

    # Reconstruct the summary in the original order of sentences for better readability.
    # This prevents the summary from jumping around chronologically.
    summary_sentences = [sentences[i] for i in sorted(top_sentence_indices)]

    # Join the selected sentences to form the final summary.
    summary = " ".join(summary_sentences)

    return summary

if __name__ == "__main__":
    # Example usage of the text summarizer.

    print("--- Example 1: Default summary ratio (30%) ---")
    long_text_example = """
    Artificial intelligence (AI) is rapidly transforming various industries across the globe.
    From healthcare to finance, AI applications are streamlining processes and enhancing decision-making.
    Machine learning, a crucial subset of AI, enables systems to learn from data without explicit programming,
    making them capable of predictive analytics and pattern recognition. Deep learning, an even more specialized
    field, uses neural networks with many layers to achieve state-of-the-art results in areas like image recognition
    and natural language processing. The ethical implications of AI are also a significant topic of discussion,
    with concerns about bias, privacy, job displacement, and the potential for misuse. Despite these challenges,
    AI continues to advance at an astonishing pace, promising a future of unprecedented innovation and efficiency
    in almost every facet of human life. Researchers are actively working on developing more robust and
    responsible AI systems to mitigate risks.
    """
    summary1 = summarize_text(long_text_example)
    print("Original Text (first 150 chars):\n", long_text_example[:150], "...\n")
    print("Summarized Text (Default Ratio):\n", summary1)
    print("-" * 50)

    print("--- Example 2: Specify number of sentences (2 sentences) ---")
    another_text = """
    Climate change is a long-term shift in global or regional climate patterns.
    Often referring specifically to the rise in global temperatures from the mid-20th century to present,
    it is primarily caused by human activities, especially the burning of fossil fuels, which increases
    heat-trapping greenhouse gas levels in Earth's atmosphere. This phenomenon leads to various impacts
    such as rising sea levels, more extreme weather events like floods and droughts, and disruptions to ecosystems.
    Scientists globally agree that urgent action is needed to reduce greenhouse gas emissions and adapt to
    the changes that are already inevitable. Renewable energy sources like solar and wind power are key solutions.
    """
    summary2 = summarize_text(another_text, num_sentences=2)
    print("Original Text (first 150 chars):\n", another_text[:150], "...\n")
    print("Summarized Text (2 Sentences):\n", summary2)
    print("-" * 50)

    print("--- Example 3: Specify a different ratio (50%) ---")
    text_for_ratio = """
    The Internet of Things (IoT) describes the network of physical objects—"things"—that are embedded with
    sensors, software, and other technologies for the purpose of connecting and exchanging data with other
    devices and systems over the internet. These devices range from ordinary household objects to sophisticated
    industrial tools. The IoT has evolved from the convergence of wireless technologies, micro-electromechanical
    systems (MEMS), and the internet. It helps in creating smart environments across various domains like smart homes,
    smart cities, and smart health. Privacy and security concerns are paramount as more devices get connected,
    requiring robust protocols and user awareness.
    """
    summary3 = summarize_text(text_for_ratio, ratio=0.5)
    print("Original Text (first 150 chars):\n", text_for_ratio[:150], "...\n")
    print("Summarized Text (50% Ratio):\n", summary3)
    print("-" * 50)

    print("--- Example 4: Empty Text Input ---")
    empty_text_summary = summarize_text("")
    print("Summary for empty text:", f"'{empty_text_summary}'")
    print("-" * 50)

    print("--- Example 5: Short Text Input ---")
    short_text = "This is a very short text. It has only two sentences. Will it work?"
    short_summary = summarize_text(short_text, num_sentences=1)
    print("Original Text:", short_text)
    print("Summarized Text (1 sentence):", short_summary)
    print("-" * 50)
