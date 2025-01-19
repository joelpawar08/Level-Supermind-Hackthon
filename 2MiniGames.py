import streamlit as st
import time
import pyaudio
import speech_recognition as sr
from googletrans import Translator
from fuzzywuzzy import fuzz
import asyncio
from groq import Groq
import os

# Set up the API key in environment variables
os.environ['GROQ_API_KEY'] = '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'  # Replace with your actual Groq API key

# Initialize Groq client
client = Groq(api_key=os.getenv('GROQ_API_KEY'))

# Translator setup
translator = Translator()

# Language dictionary for basic phrases
LANGUAGES = {
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Italian": "it",
}

# Initialize the Speech Recognition recognizer
recognizer = sr.Recognizer()

# Function to recognize speech
def recognize_speech_from_microphone():
    """Capture speech from the microphone and return the recognized text."""
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)  # Adjust for ambient noise
        st.info("Please say the phrase you hear.")
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
        try:
            # Recognizing speech using Google Web Speech API
            recognized_text = recognizer.recognize_google(audio)
            return recognized_text
        except sr.UnknownValueError:
            return "Sorry, I could not understand what you said. Please try again."
        except sr.RequestError:
            return "Could not request results, check your network connection."

# Function to translate phrase asynchronously
async def async_translate_phrase(phrase, target_language):
    return await translator.translate(phrase, dest=target_language)

# Wrapper function to run the async translation
def translate_phrase(phrase, target_language):
    return asyncio.run(async_translate_phrase(phrase, target_language))

# Function to compare user speech with correct phrase
def check_accuracy(user_input, correct_phrase):
    score = fuzz.ratio(user_input.lower(), correct_phrase.lower())
    return score

# Function to generate a language learning experience
def language_learning_game():
    # List of phrases to learn
    phrases = [
        "How are you?", 
        "Good morning", 
        "What is your name?", 
        "Where are you from?", 
        "I love programming"
    ]
    
    # Initialize the index to track the current question
    if 'question_index' not in st.session_state:
        st.session_state.question_index = 0

    # Choose a language to learn
    language_choice = st.selectbox("Choose the language you want to learn", list(LANGUAGES.keys()))

    # Get the current phrase and target language
    phrase = phrases[st.session_state.question_index]
    target_language = LANGUAGES[language_choice]
    
    # Translate the phrase into the chosen language
    translated_phrase = translate_phrase(phrase, target_language)
    
    st.write(f"Phrase in {language_choice}: {translated_phrase.text}")
    
    # Speak the phrase in the target language (simulation)
    st.write(f"Chatbot says: '{translated_phrase.text}' (Try saying this phrase)")

    # Button for user to speak now
    if st.button("Speak Now"):
        user_input = recognize_speech_from_microphone()
        st.write(f"You said: {user_input}")
        
        # Check the accuracy of the user's response
        accuracy = check_accuracy(user_input, translated_phrase.text)
        st.write(f"Your accuracy: {accuracy}%")
        
        if accuracy >= 75:
            st.success("Great job! Let's move on to the next question.")
            
            # Increment the question index to move to the next phrase
            if st.session_state.question_index < len(phrases) - 1:
                st.session_state.question_index += 1
            else:
                st.write("You've completed all the questions!")
                # Reset to allow the game to start again
                st.session_state.question_index = 0
        else:
            st.warning("Your accuracy is less than 75%. Try again!")

# Run the language learning game
if __name__ == "__main__":
    st.title("Language Learning Chatbot")
    language_learning_game()
