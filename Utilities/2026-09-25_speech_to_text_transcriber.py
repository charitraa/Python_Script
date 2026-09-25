"""
This script provides a simple Speech-to-Text transcriber using Google's Web Speech API.
It takes an audio file (preferably .wav format) as input and outputs the transcribed text.

It's designed to be beginner-friendly, requiring only a well-known third-party library
(SpeechRecognition) and explaining how to provide an audio file for transcription.
"""

# pip install SpeechRecognition

import speech_recognition as sr
import os
import wave
import struct

def transcribe_audio_file(audio_file_path):
    """
    Transcribes speech from an audio file using Google's Web Speech API.

    Args:
        audio_file_path (str): The path to the audio file (e.g., .wav, .aiff, .flac).
                               For best compatibility and performance, a .wav file is recommended.

    Returns:
        str: The transcribed text, or an informative error message if transcription fails.
    """
    recognizer = sr.Recognizer()

    # Ensure the file exists
    if not os.path.exists(audio_file_path):
        return f"Error: Audio file not found at '{audio_file_path}'"

    # Use the audio file as the audio source for the recognizer
    try:
        with sr.AudioFile(audio_file_path) as source:
            print(f"Reading audio from '{audio_file_path}'...")
            # Adjust for ambient noise to improve accuracy (optional but recommended)
            # recognizer.adjust_for_ambient_noise(source) 
            audio_data = recognizer.record(source)  # Read the entire audio file

        print("Transcribing audio... (This may take a moment as it contacts Google's servers)")
        # Use Google Web Speech API to recognize the speech
        # The 'language' parameter can be set for different languages, e.g., 'es-ES' for Spanish
        text = recognizer.recognize_google(audio_data, language="en-US")
        return text

    except sr.UnknownValueError:
        # This error occurs if the API cannot understand the audio (e.g., no speech, too much noise)
        return "Speech Recognition could not understand audio (no clear speech detected)."
    except sr.RequestError as e:
        # This error occurs if there's an issue contacting the Google Web Speech API
        return f"Could not request results from Google Web Speech API service; check your internet connection and API status: {e}"
    except Exception as e:
        # Catch any other unexpected errors during file processing or recognition
        return f"An unexpected error occurred: {e}"


if __name__ == "__main__":
    # --- Example Usage ---

    # IMPORTANT: For a meaningful transcription, you will need a .wav audio file
    # containing spoken words. The SpeechRecognition library works best with WAV files.
    #
    # If you don't have a WAV file, you can easily create one:
    # 1. Use your phone's voice recorder app and save/share as WAV.
    # 2. Use an online voice recorder (e.g., Vocaroo.com, Online-Voice-Recorder.com)
    #    and download the recording as a WAV file.
    # 3. Use an audio editing software like Audacity to record and export as WAV.
    #
    # Ensure the audio is clear and speech is prominent for best results.

    # For demonstration, this script will attempt to create a *dummy* silent WAV file
    # if no such file exists. This dummy file will not contain speech, so transcription
    # will correctly result in "Speech Recognition could not understand audio."
    # This allows the script to run out-of-the-box, but you MUST replace it with
    # a real audio file for actual speech transcription.

    dummy_audio_file_name = "dummy_silence.wav"
    if not os.path.exists(dummy_audio_file_name):
        print(f"Creating a dummy silent WAV file at '{dummy_audio_file_name}' for demonstration.")
        print("Please replace this with a real audio file containing speech for actual transcription.")
        try:
            # Create a silent WAV file (2 seconds of silence)
            sample_rate = 16000  # samples per second
            duration = 2         # seconds
            channels = 1         # mono
            sample_width = 2     # 2 bytes per sample (16-bit audio)
            
            # Open the WAV file in write mode
            with wave.open(dummy_audio_file_name, 'wb') as wf:
                wf.setnchannels(channels)
                wf.setsampwidth(sample_width)
                wf.setframerate(sample_rate)
                
                # Write silent frames (zero values)
                num_frames = sample_rate * duration * channels
                # For 16-bit audio, a silent sample is 0. struct.pack('h', 0) packs a short int (2 bytes)
                silent_frame = struct.pack('h', 0) 
                wf.writeframes(silent_frame * num_frames)
                
            print(f"Dummy file '{dummy_audio_file_name}' created.")
            print("Remember to replace this with an actual audio file containing speech!")
        except Exception as e:
            print(f"Could not create dummy WAV file: {e}")
            print("Please ensure you have write permissions or create a WAV file manually.")
            dummy_audio_file_name = None # Indicate that dummy file creation failed

    if dummy_audio_file_name and os.path.exists(dummy_audio_file_name):
        print(f"\n--- Attempting to transcribe '{dummy_audio_file_name}' ---")
        print("Expected result for dummy file: 'Speech Recognition could not understand audio.'")
        transcribed_text = transcribe_audio_file(dummy_audio_file_name)
        
        print("\n--- Transcription Result (for dummy file) ---")
        print(f"Transcribed Text: {transcribed_text}")
        print("\nTo get actual speech transcription, please provide a real audio file with spoken words.")
        
        # Clean up the dummy file after demonstration
        try:
            os.remove(dummy_audio_file_name)
            print(f"\nCleaned up dummy file: {dummy_audio_file_name}")
        except OSError as e:
            print(f"Error removing dummy file '{dummy_audio_file_name}': {e}")
    else:
        print("\n--- Cannot run transcription example as no valid audio file is available. ---")
        print("Please create or provide a .wav file and update the 'audio_file_path' variable.")

    # You can uncomment and modify the following lines to transcribe your own audio file:
    # my_real_audio_file = "path/to/your/actual_speech.wav"
    # if os.path.exists(my_real_audio_file):
    #     print(f"\n--- Attempting to transcribe real file: {my_real_audio_file} ---")
    #     transcribed_real_text = transcribe_audio_file(my_real_audio_file)
    #     print("\n--- Transcription Result (for real file) ---")
    #     print(f"Transcribed Text: {transcribed_real_text}")
    # else:
    #     print(f"\nNote: Real audio file '{my_real_audio_file}' not found. Skipping real file transcription.")
