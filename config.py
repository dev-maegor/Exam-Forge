import os
import streamlit as st
from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    try:
        API_KEY = st.secrets["GEMINI_API_KEY"]
    except Exception:
        API_KEY = None

MODEL_NAME = "gemini-3.5-flash-lite"
client = genai.Client(api_key=API_KEY) if API_KEY else None