"""
This script implements a simple rule-based chatbot.

The chatbot processes user input by checking if specific keywords or phrases are present
in the input. If a keyword is found, it responds with a predefined message.
If no keywords match, it provides a generic default response.

It's designed to be beginner-friendly, demonstrating basic string matching and
a continuous conversational loop.
"""

class SimpleChatbot:
    """
    A basic rule-based chatbot that responds to user input based on predefined patterns.
    """
    def __init__(self):
        """
        Initializes the chatbot with a set of rules and a default response.
        Each rule is a tuple: (keyword_to_match, response_string).
        The order of rules matters; the first matching rule will be used.
        Keywords are checked in a case-insensitive manner against the user's input.
        """
        self.rules = [
            ("hello", "Hi there! How can I help you today?"),
            ("hi", "Hello! Nice to chat with you."),
            ("how are you", "I'm a bot, so I don't have feelings, but thanks for asking!"),
            ("your name", "I am a simple rule-based chatbot."),
            ("weather", "I cannot check the weather, but I hope it's lovely wherever you are!"),
            ("help", "I can answer questions based on simple keywords. Try asking about my name or how I am."),
            ("python", "Python is a great programming language!"),
            ("creator", "I was created using Python for demonstration purposes."),
            ("goodbye", "Goodbye! Have a great day!"),
            ("bye", "See you later!"),
            ("thank you", "You're welcome!"),
            ("thanks", "My pleasure!")
        ]
        self.default_response = "I'm not sure how to respond to that. Can you rephrase or ask something else?"

    def get_response(self, user_input):
        """
        Generates a response based on the user's input.

        The method converts the user input to lowercase and then iterates through
        the predefined rules. It returns the response of the first rule whose
        keyword is found within the user's input. If no keyword matches,
        it returns the default response.

        Args:
            user_input (str): The text input from the user.

        Returns:
            str: The chatbot's response.
        """
        user_input_lower = user_input.lower() # Convert input to lowercase for case-insensitive matching

        # Iterate through the rules to find a match
        for keyword, response in self.rules:
            if keyword in user_input_lower:
                return response
        
        # If no rule matches after checking all of them, return the default response
        return self.default_response

if __name__ == "__main__":
    # Create an instance of the chatbot
    chatbot = SimpleChatbot()

    print("Hello! I'm a simple rule-based chatbot.")
    print("You can type 'quit', 'exit', or 'bye' to end our conversation at any time.")

    while True:
        # Prompt the user for input
        user_input = input("You: ")

        # Check if the user wants to exit the conversation
        if user_input.lower() in ["quit", "exit", "bye"]:
            print("Chatbot: Goodbye! Thanks for chatting.")
            break
        
        # Get the chatbot's response based on the user's input
        response = chatbot.get_response(user_input)
        
        # Print the chatbot's response
        print(f"Chatbot: {response}")
