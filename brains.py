import os
import google.generativeai as genai
from dotenv import load_dotenv
import streamlit as st

# Load environment variables (works locally and in cloud)
load_dotenv()

# Try to get key from OS (Local) or Streamlit Secrets (Cloud)
API_KEY = os.getenv("GEMINI_API_KEY") or st.secrets["GEMINI_API_KEY"]

# Configure Gemini
genai.configure(api_key=API_KEY)

# We use the Pro model for maximum reasoning capability
MODEL_NAME = "gemini-1.5-pro"

def talk_to_brain(system_prompt, user_prompt):
    """
    Sends a request to Google Gemini and returns the content.
    """
    if not API_KEY:
        return "Error: GEMINI_API_KEY not found."

    try:
        # Create the model with the system instruction
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            system_instruction=system_prompt
        )

        # Generate content
        response = model.generate_content(user_prompt)
        
        # Return text
        return response.text.strip()

    except Exception as e:
        print(f"Error communicating with Gemini: {e}")
        return None