import streamlit as st
import os
import json
from io import BytesIO

# Streamlit setup
st.set_page_config(layout="wide")
st.title("Voice Disorder Annotation")

AUDIOS_PATH = "/mount/src/voice_reconstruction/uclass_v1"
DATA_FILE = "precomputed_ASR_TTS_uclass1.json"
LABELS_OUTPUT_FILE = "saved_labels.json"

# Load audio safely
def load_audio_bytes(path):
    try:
        with open(path, "rb") as f:
            return BytesIO(f.read())
    except Exception as e:
        st.error(f"Error loading audio: {path}\n{e}")
        return None

# Input fields for annotator ID and mother tongue
col1, col2 = st.columns(2)
with col1:
    annotator = st.text_input("Enter your annotator ID or Name", key="annotator_id")
with col2:
    mother_tongue = st.text_input("Enter your mother tongue language", key="mother_tongue")

if not annotator or not mother_tongue:
    st.warning("Please enter both your annotator ID and mother tongue to continue.")
    st.stop()

# Load precomputed results
with open(DATA_FILE, "r") as f:
    precomputed_data = json.load(f)

audio_files = sorted(precomputed_data.keys())

# Pagination setup
batch_size = 10
max_idx = len(audio_files) - 1
start_idx = st.number_input("Page", min_value=0, max_value=max_idx, step=batch_size)
batch = audio_files[start_idx:start_idx + batch_size]

# Session state for labels
if "labels" not in st.session_state:
    st.session_state.labels = {}

# UI for annotation
for audio_file in batch:
    st.markdown("---")
    st.write(f"### {audio_file}")

    audio_path = os.path.join(AUDIOS_PATH, audio_file)
    tts_path = os.path.join(AUDIOS_PATH, precomputed_data[audio_file]["tts_audio"])
    transcription = precomputed_data[audio_file]["transcription"]

    st.write("Disordered Voice:")
    dis_audio = load_audio_bytes(audio_path)
    if dis_audio:
        st.audio(dis_audio)

    st.text_area("Transcription", transcription, height=100, key=f"transcription_display_{audio_file}")

    st.write("Reconstructed Voice:")
    tts_audio = load_audio_bytes(tts_path)
    if tts_audio:
        st.audio(tts_audio)

    label = st.radio(
        "Are the speakers the same?",
        ("same", "different"),
        key=f"label_{audio_file}"
    )

    st.session_state.labels[audio_file] = {
        "label": label,
        "mother_tongue": mother_tongue,
        "annotator": annotator
    }

# Save labels locally
if st.button("Submit Labels"):
    try:
        with open(LABELS_OUTPUT_FILE, "w") as f:
            json.dump(st.session_state.labels, f, indent=2)
        st.success("✅ All labels saved successfully!")
    except Exception as e:
        st.error(f"❌ Failed to save labels: {e}")

st.download_button("Download Labels", json_data, file_name="saved_labels.json", mime="application/json")

# import streamlit as st
# import requests
# import os
# import json
# from io import BytesIO

# ngrok_api_key = "2xEPEjvSvamX0iItl5WixghrbiT_2KDJEaPiDXv8eJtVc1Wsd"
# API_URL = "http://localhost:8000"


# #from pyngrok import ngrok

# #public_url = ngrok.connect(port = '80')

# AUDIOS_PATH = "/mount/src/voice_reconstruction/uclass_v1"
# DATA_FILE = "precomputed_ASR_TTS_uclass1.json"

# st.set_page_config(layout="wide")


# st.title("Voice Disorder Annotation")


# def load_audio_bytes(path):
#     try:
#         with open(path, "rb") as f:
#             return BytesIO(f.read())
#     except Exception as e:
#         st.error(f"Error loading audio: {path}\n{e}")
#         return None
        

# # Input fields for annotator ID and mother tongue
# col1, col2 = st.columns(2)
# with col1:
#     annotator = st.text_input("Enter your annotator ID or Name", key="annotator_id")
# with col2:
#     mother_tongue = st.text_input("Enter your mother tongue language", key="mother_tongue")

# # Check if both fields are filled
# if not annotator and not mother_tongue:
#     st.warning("Please enter your annotator ID and mother tongue to continue.")
#     st.stop()
# elif not annotator:
#     st.warning("Please enter your annotator ID to continue.")
#     st.stop()
# elif not mother_tongue:
#     st.warning("Please enter your mother tongue language to continue.")
#     st.stop()

# # The rest of the interface only shows if both fields are filled
# # Load precomputed results (transcriptions and TTS audio)
# with open(DATA_FILE, "r") as f:
#     precomputed_data = json.load(f)

# audio_files = sorted(precomputed_data.keys())

# # Pagination variables
# batch_size = 10  # Number of files to display per page
# max_idx = len(audio_files) - 1  # Maximum index for pagination

# start_idx = st.number_input("Page", min_value=0, max_value=max_idx, step=batch_size)
# batch = audio_files[start_idx:start_idx + batch_size]

# # Store all labels in session state
# if "labels" not in st.session_state:
#     st.session_state.labels = {}

# # UI for displaying and annotating audio files
# for audio_file in batch:
#     st.markdown("---")
#     st.write(f"### {audio_file}")
    
#     BASE_AUDIO_DIR = "/mount/src/voice_reconstruction/uclass_v1"
#     audio_path = os.path.join(BASE_AUDIO_DIR, audio_file)

#     # tts_path = precomputed_data[audio_file]["tts_audio"]
 
#     tts_path = os.path.join(AUDIOS_PATH, precomputed_data[audio_file]["tts_audio"])

#     transcription = precomputed_data[audio_file]["transcription"]

#     # Display audio sample, transcription, and TTS audio
#     st.write(f"Disordered Voice:")
#     # st.audio(audio_path)
#     # st.write("Disordered Voice:")
    
#     dis_audio = load_audio_bytes(audio_path)
#     if dis_audio:
#         st.audio(dis_audio)
    
#     st.text_area("Transcription", transcription, height=100, key=f"transcription_display_{audio_file}")

#     st.write("Reconstructed Voice:")
#     tts_audio = load_audio_bytes(tts_path)
#     if tts_audio:
#         st.audio(tts_audio)
    
#     # st.write(f"Reconstructed Voice:")
#     # st.audio(tts_path)

#     # Collect label from the user
#     label = st.radio(
#         "Are the speakers the same?",
#         ("same", "different"),
#         key=f"label_{audio_file}"
#     )

#     # Store the label in session state along with mother tongue
#     st.session_state.labels[audio_file] = {
#         "label": label,
#         "mother_tongue": mother_tongue,
#         "annotator": annotator
#     }


# if st.button("Submit Labels"):
#     try:
#         with open(LABELS_OUTPUT_FILE, "w") as f:
#             json.dump(st.session_state.labels, f, indent=2)
#         st.success("✅ All labels saved successfully!")
#     except Exception as e:
#         st.error(f"❌ Failed to save labels: {e}")


# # Button to submit all labels
# if st.button("Submit Labels"):
#     for audio_file, label_data in st.session_state.labels.items():
#         try:
#             # Save the label and additional info using POST request to the API
#             response = requests.post(f"{API_URL}/save_label", json={
#                 "audio_name": audio_file,
#                 "user_label": label_data["label"],
#                 "annotator": label_data["annotator"],
#                 "mother_tongue": label_data["mother_tongue"]
#             })

#             if response.status_code == 200:
#                 st.toast(f"✅ Label for {audio_file} saved!", icon="💾")
#             else:
#                 st.error(f"❌ Failed to save label for {audio_file}")
#         except Exception as e:
#             st.error(f"❌ Error saving label for {audio_file}: {e}")
