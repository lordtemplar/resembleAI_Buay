import streamlit as st
from resemble import Resemble
import requests
from io import BytesIO
from pydub import AudioSegment

# === Setup ===
API_KEY = "Ew2pEvxMVxWWBQ2DzYzUTgtt"
Resemble.api_key(API_KEY)

# === Audio Speed Adjustment ===
def adjust_audio_speed(audio_content, speed=1.0):
    try:
        audio = AudioSegment.from_file(BytesIO(audio_content), format="mp3")
        new_audio = audio._spawn(audio.raw_data, overrides={
            "frame_rate": int(audio.frame_rate * speed)
        }).set_frame_rate(audio.frame_rate)
        return new_audio
    except Exception as e:
        st.error(f"Error adjusting audio speed: {e}")
        return AudioSegment.silent(duration=1000)

# === Voice + Project Setup ===
def get_default_project_and_voice():
    project_uuid = Resemble.v2.projects.all(1, 10)['items'][0]['uuid']
    voice_uuid = Resemble.v2.voices.all(1, 10)['items'][0]['uuid']
    return project_uuid, voice_uuid

# === Generate Voice ===
def generate_voice(text, project_uuid, voice_uuid):
    try:
        response = Resemble.v2.clips.create_sync(
            project_uuid,
            voice_uuid,
            text
        )
        audio_url = response.get('audio_src')
        if not audio_url:
            st.error("No audio URL returned.")
            return None
        return audio_url
    except Exception as e:
        st.error(f"Error generating voice: {e}")
        return None

# === Streamlit App ===
def main():
    st.title("🎙️ Resemble AI TTS via Official SDK")

    text = st.text_area("💬 Enter your text:", height=200)
    speed = st.slider("⏩ Playback Speed", min_value=0.5, max_value=2.0, value=1.0, step=0.1)

    if st.button("🗣️ Generate Voice"):
        if not text.strip():
            st.warning("Please enter some text.")
            return

        with st.spinner("🔄 Getting project and voice info..."):
            project_uuid, voice_uuid = get_default_project_and_voice()

        with st.spinner("🧠 Generating voice..."):
            audio_url = generate_voice(text, project_uuid, voice_uuid)

        if audio_url:
            st.success("✅ Voice generated successfully.")
            st.write("🎧 Fetching audio from:")
            st.code(audio_url)

            audio_response = requests.get(audio_url)
            adjusted_audio = BytesIO()
            adjust_audio_speed(audio_response.content, speed).export(adjusted_audio, format="mp3")
            adjusted_audio.seek(0)

            st.audio(adjusted_audio, format="audio/mp3")
            st.download_button("⬇️ Download", adjusted_audio, file_name="resemble_voice.mp3", mime="audio/mp3")
        else:
            st.error("❌ Failed to generate voice.")

if __name__ == "__main__":
    main()
