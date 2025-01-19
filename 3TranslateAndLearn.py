import os
import asyncio
from googletrans import Translator
import streamlit as st

# Initialize the Translator
translator = Translator()

# Asynchronous translation function
async def async_translate_phrase(phrase, target_language):
    return await translator.translate(phrase, dest=target_language)

# Function to handle translation synchronously
def translate_phrase(phrase, target_language):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)  # Set the new event loop
    return loop.run_until_complete(async_translate_phrase(phrase, target_language))

# Main game logic
def language_learning_game():
    st.title("Language Learning Game")
    
    phrase = st.text_input("Enter a phrase to translate:")
    target_language = st.selectbox("Select target language", ['es', 'fr', 'de', 'it', 'pt'])  # Example languages
    
    if phrase:
        translated_phrase = translate_phrase(phrase, target_language)
        st.write(f"Translated Phrase: {translated_phrase.text}")

# Run the game in Streamlit
if __name__ == "__main__":
    language_learning_game()
