import streamlit as st
import requests
import json
from typing import Optional
import warnings

# LangFlow configuration
BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "468406f1-1b12-48c1-965c-4bbdb89cfd0e"
FLOW_ID = "99073cd3-78e4-43d9-8a5c-51e2c2876aea"
APPLICATION_TOKEN = "AstraCS:RseZZAxUZZxZDkCfgHUguAig:4df0c2eef710f1e180cab04823635391ff389f8a7b36a1bb288affcf2c390342"
ENDPOINT = "Joel"  # The endpoint name of the flow

# Default tweaks
TWEAKS = {
    "Agent-9uBIc": {},
    "ChatInput-oVz94": {},
    "ChatOutput-o51qf": {},
    "URL-JswEG": {},
    "CalculatorTool-Gltai": {},
    "WikipediaAPI-cEAmX": {}
}

def run_flow(message: str,
             endpoint: str,
             output_type: str = "chat",
             input_type: str = "chat",
             tweaks: Optional[dict] = None,
             application_token: Optional[str] = None) -> dict:
    """
    Run a flow with a given message and optional tweaks.
    """
    api_url = f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/{endpoint}"

    payload = {
        "input_value": message,
        "output_type": output_type,
        "input_type": input_type,
    }
    
    headers = None
    if tweaks:
        payload["tweaks"] = tweaks
    if application_token:
        headers = {"Authorization": "Bearer " + application_token, "Content-Type": "application/json"}

    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()

# Streamlit UI
st.title("LangFlow Streamlit Application")
st.write("Interact with LangFlow flow using this application.")

# User input fields
user_message = st.text_area("Enter your message:", "")
endpoint = st.text_input("Endpoint (default: Joel):", ENDPOINT)
tweaks_input = st.text_area("Tweaks (JSON format):", json.dumps(TWEAKS, indent=2))
application_token = st.text_input("Application Token:", APPLICATION_TOKEN)
output_type = st.selectbox("Select Output Type:", ["chat", "text", "json"])
input_type = st.selectbox("Select Input Type:", ["chat", "text"])

# File upload option (optional)
upload_file = st.file_uploader("Upload a file (optional):", type=["txt", "json", "csv"])

if st.button("Run Flow"):
    try:
        # Parse the tweaks JSON input
        tweaks = json.loads(tweaks_input)
    except json.JSONDecodeError:
        st.error("Invalid JSON format for tweaks.")
        tweaks = None

    if user_message:
        with st.spinner("Running the flow..."):
            # Call the flow and display the result
            response = run_flow(
                message=user_message,
                endpoint=endpoint,
                output_type=output_type,
                input_type=input_type,
                tweaks=tweaks,
                application_token=application_token
            )

            st.success("Flow executed successfully!")
            st.json(response, expanded=True)

            # If a file is uploaded, show file content
            if upload_file:
                st.write("Uploaded file content:")
                file_content = upload_file.getvalue().decode("utf-8")
                st.text(file_content)
    else:
        st.warning("Please enter a message to run the flow.")
