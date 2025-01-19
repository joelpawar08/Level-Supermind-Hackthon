import streamlit as st
import requests
import json

# LangFlow configuration
BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "468406f1-1b12-48c1-965c-4bbdb89cfd0e"
APPLICATION_TOKEN = "AstraCS:nDQuMsiWAUbQrHJRRpDuymKo:8b99c460d307d14e5eeea166e6d03bf71680a962dd0246c5c6b9d14a2ab70ab0"
ENDPOINT = "Joel"
DEFAULT_TWEAKS = {
    "Agent-9uBIc": {},
    "ChatInput-oVz94": {},
    "ChatOutput-o51qf": {},
    "URL-JswEG": {},
    "CalculatorTool-Gltai": {},
    "WikipediaAPI-cEAmX": {}
}

def run_flow(message, endpoint, tweaks=None):
    """
    Executes a request to the LangFlow API and retrieves the response.
    """
    api_url = f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/{endpoint}"
    payload = {
        "input_value": message,
        "output_type": "chat",
        "input_type": "chat",
    }
    if tweaks:
        payload["tweaks"] = tweaks

    headers = {
        "Authorization": f"Bearer {APPLICATION_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an error for HTTP status codes 4xx/5xx
        response_data = response.json()
        
        # Parse response data
        outputs = response_data.get("outputs", [])
        if outputs:
            message_results = outputs[0].get("outputs", [])[0].get("results", {})
            text = message_results.get("message", {}).get("text", "No text found.")
            return text
        return "No outputs available in the response."

    except requests.exceptions.HTTPError as http_err:
        try:
            error_data = response.json()
            return f"HTTP Error {response.status_code}: {error_data.get('detail', response.text)}"
        except json.JSONDecodeError:
            return f"HTTP Error {response.status_code}: {http_err}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

# Streamlit app
st.title("LangFlow Streamlit Application")
st.write("Interact with your LangFlow flow using this app.")

# User input
user_message = st.text_input("Enter your message:")
use_tweaks = st.checkbox("Enable Tweaks", value=True)

if st.button("Run Flow"):
    if user_message:
        tweaks = DEFAULT_TWEAKS if use_tweaks else None
        with st.spinner("Running flow..."):
            try:
                result = run_flow(user_message, ENDPOINT, tweaks)
                st.success("Flow executed successfully!")
                st.text_area("Output", result, height=300)
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a message before running the flow.")