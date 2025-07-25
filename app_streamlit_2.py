import streamlit as st
import os
import json
from io import BytesIO

# Streamlit setup
st.set_page_config(layout="wide")
st.title("Voice Disorder Annotation")

AUDIOS_PATH = "/mount/src/voice_reconstruction/uclass_v1"
DATA_FILE = "precomputed_uclass_1.json"
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
batch_size = 20
total_files = len(audio_files)
total_pages = (total_files + batch_size - 1) // batch_size  # ceiling div

# Initialize current page index in session state if not present
if "page_idx" not in st.session_state:
    st.session_state.page_idx = 0

# Functions to move pages
def next_page():
    if st.session_state.page_idx < total_pages - 1:
        st.session_state.page_idx += 1

def prev_page():
    if st.session_state.page_idx > 0:
        st.session_state.page_idx -= 1

# Calculate current batch based on session page_idx
start_idx = st.session_state.page_idx * batch_size
batch = audio_files[start_idx:start_idx + batch_size]

# Session state for labels
if "labels" not in st.session_state:
    st.session_state.labels = {}

# Display batch items
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

st.markdown("---")

# Pagination controls at the bottom
col_prev, col_page, col_next = st.columns([1, 2, 1])

with col_prev:
    if st.button("⬅️ Previous"):
        prev_page()
with col_page:
    st.markdown(f"### Page {st.session_state.page_idx + 1} / {total_pages}")
with col_next:
    if st.button("Next ➡️"):
        next_page()

# Save labels locally (optional)
# if st.button("Submit Labels"):
#     try:
#         with open(LABELS_OUTPUT_FILE, "w") as f:
#             json.dump(st.session_state.labels, f, indent=2)
#         st.success("✅ All labels saved successfully!")
#     except Exception as e:
#         st.error(f"❌ Failed to save labels: {e}")

json_data = json.dumps(st.session_state.labels, indent=2)
st.download_button("Download Labels", json_data, file_name="saved_labels.json", mime="application/json")




