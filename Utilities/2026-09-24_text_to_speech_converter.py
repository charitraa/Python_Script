# To run this script, you will need to install the gTTS library.
# You can install it using pip:
# pip install gTTS

"""
This script provides a simple Text-to-Speech (TTS) converter.
It takes a text string and converts it into spoken audio, saving the output
as an MP3 file. It leverages Google's Text-to-Speech service via the gTTS library.

Features:
- Converts text to speech in various languages.
- Saves the generated speech as an MP3 audio file.
- Beginner-friendly with clear instructions and example usage.
"""

from gtts import gTTS
import os # Used to get the absolute path for user information

def text_to_speech(text, output_filename="output.mp3", lang='en', slow=False):
    """
    Converts a given text string into speech and saves it as an MP3 audio file.

    This function utilizes the gTTS (Google Text-to-Speech) library, which
    requires an active internet connection to generate the audio.

    Args:
        text (str): The text string to be converted to speech.
        output_filename (str, optional): The name of the output MP3 file.
                                         Defaults to "output.mp3".
                                         The file will be saved in the same
                                         directory from which the script is run.
        lang (str, optional): The language of the text. Common options include
                              'en' for English, 'es' for Spanish, 'fr' for French,
                              etc. Defaults to 'en'.
        slow (bool, optional): If True, the speech will be slower. Defaults to False.
    """
    try:
        # Create a gTTS object.
        # The 'text' parameter is the string to convert.
        # The 'lang' parameter specifies the language.
        # The 'slow' parameter controls the speech speed.
        tts = gTTS(text=text, lang=lang, slow=slow)

        # Save the generated audio to an MP3 file.
        # The .save() method writes the audio data to the specified filename.
        tts.save(output_filename)
        print(f"Successfully converted text to speech and saved to '{output_filename}'")
    except Exception as e:
        # Catch potential errors, such as no internet connection, invalid language, etc.
        print(f"An error occurred during text-to-speech conversion: {e}")
        print("Please ensure you have an active internet connection.")
        print("Also, double-check the 'lang' parameter for validity (e.g., 'en', 'es', 'fr').")

if __name__ == "__main__":
    # --- Working Example Usage ---

    print("--- Text-to-Speech Converter Script ---")
    print("This script will convert your text into an audio file.")

    # 1. Define the text you want to convert to speech.
    sample_text = (
        "Hello there! This is a simple test of the text-to-speech converter script. "
        "It uses Google's technology to turn written words into spoken audio. "
        "You can easily change the text and language below."
    )

    # 2. Define the name for the output audio file.
    # This file will be saved in the same directory where this script is located.
    output_audio_file = "my_first_spoken_message.mp3"

    # 3. Define the language for the speech.
    # 'en' is for English. You can try 'es' for Spanish, 'fr' for French, etc.
    # Make sure the text matches the chosen language for best results.
    speech_language = 'en' # Change this to 'es' for Spanish or 'fr' for French and update sample_text!

    # 4. Call the text_to_speech function to perform the conversion.
    text_to_speech(sample_text, output_audio_file, speech_language, slow=False)

    print("\n--- Playback Information ---")
    # Get the absolute path to the saved file for clarity.
    absolute_file_path = os.path.abspath(output_audio_file)
    print(f"Your audio file has been saved to: {absolute_file_path}")
    print("You can now play 'my_first_spoken_message.mp3' using any media player "
          "(e.g., VLC, Windows Media Player, QuickTime, or even a web browser).")
    print("Enjoy listening to your spoken message!")

    # --- Optional: Uncomment the following lines for another example in Spanish ---
    # print("\n--- Testing another language (Spanish example) ---")
    # spanish_text = "¡Hola! Este es un mensaje de prueba en español. Espero que te guste."
    # spanish_output_file = "spanish_spoken_message.mp3"
    # text_to_speech(spanish_text, spanish_output_file, lang='es', slow=True) # Slower speech for variety
    # absolute_spanish_path = os.path.abspath(spanish_output_file)
    # print(f"Spanish audio saved to: {absolute_spanish_path}")
    # print("Remember to use a media player to listen to 'spanish_spoken_message.mp3'.")
