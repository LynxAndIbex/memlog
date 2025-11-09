import streamlit as st
import json
import os
from datetime import datetime
import requests

# --------------------------
# Configuration
# --------------------------
MEMORIES_FILE = "memories.json"
HF_API_URL_TRANSCRIBE = "https://api.openrouter.ai/v1/completions"  # Gemma 3n 4B
HF_API_URL_CONVERSE = "https://api.openrouter.ai/v1/completions"    # Llama 3.2 3B Instruct
HF_API_KEY = st.secrets["HF_API_KEY"]  # Put your OpenRouter API key in Streamlit secrets

# --------------------------
# Helpers
# --------------------------
def transcribe_audio(audio_file_path):
    """Send audio file to transcription model (Gemma 3n 4B)"""
    with open(audio_file_path, "rb") as f:
        audio_bytes = f.read()

    payload = {
        "model": "google/gemma-3n-4b",
        "input": audio_bytes.hex(),  # Encode audio as hex for API
        "mode": "speech-to-text"
    }
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    response = requests.post(HF_API_URL_TRANSCRIBE, headers=headers, json=payload)
    result = response.json()
    return result.get("output_text", "")

def poeticize(text):
    """Transform transcript into a poetic memory"""
    lines = text.strip().split(". ")
    verses = []

    for line in lines:
        if not line.strip():
            continue
        line = line.strip().capitalize().rstrip(".")
        verses.append(f"As time unfolds, {line.lower()},\nNow framed in gold, a moment to ponder.")

    poem_body = "\n\n".join(verses[:4])  # limit to 4 stanzas
    return (
        "🌸 A Memory in Verse 🌸\n\n"
        + poem_body
        + "\n\n— remembered softly from a voice long past"
    )

def save_memory(memory_text, filename):
    new_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "filename": filename,
        "memory_text": memory_text
    }
    if os.path.exists(MEMORIES_FILE):
        with open(MEMORIES_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    data.append(new_entry)
    with open(MEMORIES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_memories():
    if os.path.exists(MEMORIES_FILE):
        with open(MEMORIES_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                formatted = ""
                for i, mem in enumerate(data, 1):
                    formatted += f"Memory {i} (from {mem['filename']} at {mem['timestamp']}):\n"
                    formatted += mem['memory_text'] + "\n\n"
                return formatted
            except json.JSONDecodeError:
                return "Error loading memories."
    else:
        return "No memories saved yet."

def delete_memory(index):
    if not os.path.exists(MEMORIES_FILE):
        return "No memories to delete."

    try:
        idx = int(index) - 1
    except ValueError:
        return "Please enter a valid number."

    with open(MEMORIES_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return "Error reading memories file."

    if idx < 0 or idx >= len(data):
        return "Index out of range."

    deleted = data.pop(idx)
    with open(MEMORIES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return f"Deleted memory {idx+1}: {deleted['filename']}"

# --------------------------
# Streamlit UI
# --------------------------
st.title("🧠 Alzheimer's Memory Logger - Echo")

st.markdown("""
Upload or record an audio memory to transcribe and convert it into a poetic memory.
""")

# Upload / record audio
audio_file = st.file_uploader("Upload Audio", type=["wav", "mp3", "m4a"])

if audio_file:
    # Save temp audio file
    temp_audio_path = f"temp_{audio_file.name}"
    with open(temp_audio_path, "wb") as f:
        f.write(audio_file.getbuffer())

    # Transcribe
    st.info("Transcribing audio...")
    transcript = transcribe_audio(temp_audio_path)
    st.text_area("Transcript", transcript, height=120)

    # Poeticize
    poetic_memory = poeticize(transcript)
    st.text_area("Poetic Memory", poetic_memory, height=200)

    # Save memory
    save_memory(poetic_memory, audio_file.name)
    st.success("Memory saved successfully!")

st.markdown("---")

# View memories
st.subheader("View Saved Memories")
if st.button("Load Memories"):
    st.text_area("All Memories", load_memories(), height=300)

# Delete a memory
st.subheader("Delete a Memory")
mem_to_delete = st.text_input("Memory Number to Delete")
if st.button("Delete Memory"):
    result = delete_memory(mem_to_delete)
    st.success(result)

# Download memories
st.subheader("Download All Memories")
if os.path.exists(MEMORIES_FILE):
    with open(MEMORIES_FILE, "rb") as f:
        st.download_button("Download memories.json", f, file_name="memories.json")
