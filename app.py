import streamlit as st
import whisper
import os
import tempfile

# Load model (we'll use base or tiny to keep things fast)
model = whisper.load_model("base")

st.title("Whisper Voice Transcriber")

uploaded_file = st.file_uploader("Upload an audio file", type=["mp3", "wav", "m4a"])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
        temp_audio.write(uploaded_file.read())
        temp_audio_path = temp_audio.name

    st.info("Transcribing...")
    result = model.transcribe(temp_audio_path)
    st.success("Transcription complete!")

    st.subheader("Transcript:")
    st.write(result["text"])

    os.remove(temp_audio_path)
