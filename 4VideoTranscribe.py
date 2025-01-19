import streamlit as st
import os
import re
import time
from pydub import AudioSegment
from pydub.utils import make_chunks
from moviepy import VideoFileClip
from groq import Groq
from googletrans import Translator
from nltk.util import ngrams
from nltk.translate.bleu_score import sentence_bleu
from rouge_score import rouge_scorer
from collections import Counter
import asyncio  # Import asyncio for async handling

# Set up the API key in environment variables
os.environ['GROQ_API_KEY'] = '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'  # Replace with your actual Groq API key

# Initialize the Groq client and Google Translator
client = Groq(api_key=os.getenv('GROQ_API_KEY'))
translator = Translator()

# List of supported languages
LANGUAGES = {
    "Hindi": "hi",
    "Marathi": "mr",
    "Gujarati": "gu",
    "Tamil": "ta",
    "Kannada": "kn",
    "Telugu": "te",
    "Bengali": "bn",
    "Malayalam": "ml",
    "Punjabi": "pa",
    "Odia": "or"
}

# Function to extract audio from video
def extract_audio_from_video(video_path, output_audio_path):
    """Extract audio from a video file and save it as a WAV file."""
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(output_audio_path)
    clip.close()

# Function to split audio into smaller chunks
def split_audio_into_chunks(audio_path, chunk_length_ms):
    audio = AudioSegment.from_file(audio_path)
    chunks = make_chunks(audio, chunk_length_ms)

    chunk_paths = []
    for i, chunk in enumerate(chunks):
        chunk_path = f"{audio_path}chunk{i}.wav"
        chunk.export(chunk_path, format="wav")
        chunk_paths.append(chunk_path)

    return chunk_paths

# Function to transcribe audio using Groq API
def transcribe_audio_with_groq(file_path):
    """Send audio file to Groq API for transcription."""
    with open(file_path, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(file_path, file.read()),
            model="whisper-large-v3-turbo",
            response_format="json",
            temperature=0.0
        )
    return transcription.text

# Function to transcribe a large audio file in chunks
def transcribe_large_audio(audio_path):
    chunk_length_ms = 60000  # 60 seconds per chunk
    chunk_paths = split_audio_into_chunks(audio_path, chunk_length_ms)

    full_transcription = []
    for chunk_path in chunk_paths:
        transcription_text = transcribe_audio_with_groq(chunk_path)
        full_transcription.append(transcription_text)
        os.remove(chunk_path)  # Clean up chunk file after processing

    return " ".join(full_transcription)

# N-Gram Validation
def validate_with_ngrams(text, n=3):
    """Generate n-grams and count their occurrences to validate transcription consistency."""
    tokens = text.split()
    ngram_counts = Counter(ngrams(tokens, n))
    return ngram_counts.most_common(10)

# Function to translate text
async def translate_text(text, target_language_code):
    """Translate text into the selected target language."""
    translation = await translator.translate(text, dest=target_language_code)  # Make sure this is awaited
    return translation.text

# Streamlit UI
st.title("Video Transcription and Translation with Execution Times")
st.write("Upload a video, transcribe its audio, and translate the text into different languages.")

# File upload
uploaded_file = st.file_uploader("Upload Video File", type=["mp4", "mov", "avi", "mkv"])
if uploaded_file:
    video_path = f"uploaded_video_{time.time()}.mp4"
    with open(video_path, "wb") as f:
        f.write(uploaded_file.read())

    # Extract audio from video
    audio_path = video_path.replace(".mp4", ".wav")
    extract_audio_from_video(video_path, audio_path)

    # Transcribe audio
    st.info("Transcribing audio... This may take some time.")
    transcription_start_time = time.time()
    transcription_text = transcribe_large_audio(audio_path)
    transcription_execution_time = time.time() - transcription_start_time

    if transcription_text:
        st.success("Transcription Complete!")
        st.write(f"Transcribed Text: {transcription_text}")
        st.write(f"Transcription Execution Time: {transcription_execution_time:.2f} seconds")

        # Language selection for translation
        selected_language = st.selectbox("Select Language for Translation:", list(LANGUAGES.keys()))

        if selected_language:
            translation_start_time = time.time()

            # Perform translation using asyncio
            translated_text = asyncio.run(translate_text(transcription_text, LANGUAGES[selected_language]))

            translation_execution_time = time.time() - translation_start_time

            st.write(f"### Translated Text ({selected_language}):")
            st.write(translated_text)
            st.write(f"Translation Execution Time: {translation_execution_time:.2f} seconds")

    # Clean up files
    os.remove(video_path)
    os.remove(audio_path)