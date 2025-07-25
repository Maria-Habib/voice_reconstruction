import streamlit as st
import requests
import os
import json


ngrok_api_key = "2xEPEjvSvamX0iItl5WixghrbiT_2KDJEaPiDXv8eJtVc1Wsd"
API_URL = "http://localhost:8000"


#from pyngrok import ngrok

#public_url = ngrok.connect(port = '80')

AUDIOS_PATH = "/mount/src/voice_reconstruction/uclass_v1"
DATA_FILE = "precomputed_ASR_TTS_uclass1.json"

st.set_page_config(layout="wide")


st.title("Voice Disorder Annotation")

# Input fields for annotator ID and mother tongue
col1, col2 = st.columns(2)
with col1:
    annotator = st.text_input("Enter your annotator ID or Name", key="annotator_id")
with col2:
    mother_tongue = st.text_input("Enter your mother tongue language", key="mother_tongue")

# Check if both fields are filled
if not annotator and not mother_tongue:
    st.warning("Please enter your annotator ID and mother tongue to continue.")
    st.stop()
elif not annotator:
    st.warning("Please enter your annotator ID to continue.")
    st.stop()
elif not mother_tongue:
    st.warning("Please enter your mother tongue language to continue.")
    st.stop()

# The rest of the interface only shows if both fields are filled
# Load precomputed results (transcriptions and TTS audio)
with open(DATA_FILE, "r") as f:
    precomputed_data = json.load(f)

audio_files = sorted(precomputed_data.keys())

# Pagination variables
batch_size = 10  # Number of files to display per page
max_idx = len(audio_files) - 1  # Maximum index for pagination

start_idx = st.number_input("Page", min_value=0, max_value=max_idx, step=batch_size)
batch = audio_files[start_idx:start_idx + batch_size]

# Store all labels in session state
if "labels" not in st.session_state:
    st.session_state.labels = {}

# UI for displaying and annotating audio files
for audio_file in batch:
    st.markdown("---")
    st.write(f"### {audio_file}")

    audio_path = os.path.join(AUDIOS_PATH, audio_file)
    tts_path = precomputed_data[audio_file]["tts_audio"]
    transcription = precomputed_data[audio_file]["transcription"]

    # Display audio sample, transcription, and TTS audio
    st.write(f"Disordered Voice:")

    from pathlib import Path

    audio_path = Path("/mount/src/voice_reconstruction/uclass_v1/tts_F_0050_10y9m_1.wav")
    
    # Check if file exists
    if not audio_path.exists():
        st.error(f"❌ File does not exist: {audio_path}")
        st.stop()
    
    # Check file size
    if audio_path.stat().st_size == 0:
        st.error(f"❌ File is empty: {audio_path}")
        st.stop()
    
    # Try reading manually
    try:
        with open(audio_path, "rb") as f:
            audio_bytes = f.read()
        st.success(f"✅ File exists and is readable: {audio_path}")
    except Exception as e:
        st.error(f"❌ File cannot be read: {e}")
        st.stop()
    
    # If it worked, play audio
    st.audio(audio_bytes)

    
    st.audio(audio_path)
    st.text_area("Transcription", transcription, height=100, key=f"transcription_display_{audio_file}")
    st.write(f"Reconstructed Voice:")
    st.audio(tts_path)

    # Collect label from the user
    label = st.radio(
        "Are the speakers the same?",
        ("same", "different"),
        key=f"label_{audio_file}"
    )

    # Store the label in session state along with mother tongue
    st.session_state.labels[audio_file] = {
        "label": label,
        "mother_tongue": mother_tongue,
        "annotator": annotator
    }

# Button to submit all labels
if st.button("Submit Labels"):
    for audio_file, label_data in st.session_state.labels.items():
        try:
            # Save the label and additional info using POST request to the API
            response = requests.post(f"{API_URL}/save_label", json={
                "audio_name": audio_file,
                "user_label": label_data["label"],
                "annotator": label_data["annotator"],
                "mother_tongue": label_data["mother_tongue"]
            })

            if response.status_code == 200:
                st.toast(f"✅ Label for {audio_file} saved!", icon="💾")
            else:
                st.error(f"❌ Failed to save label for {audio_file}")
        except Exception as e:
            st.error(f"❌ Error saving label for {audio_file}: {e}")
