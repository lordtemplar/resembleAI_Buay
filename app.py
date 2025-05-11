import streamlit as st
from resemble import Resemble
import requests
from io import BytesIO
from pydub import AudioSegment

# === CONFIG ===
API_KEY = "Ew2pEvxMVxWWBQ2DzYzUTgtt"
Resemble.api_key(API_KEY)

# === HELPER ===
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

def get_default_project_and_voice():
    try:
        project_list = Resemble.v2.projects.all(1, 10)
        voice_list = Resemble.v2.voices.all(1, 10)

        if not project_list['items'] or not voice_list['items']:
            st.error("❌ Could not find any project or voice. Please check your Resemble dashboard.")
            return None, None

        project_uuid = project_list['items'][0]['uuid']
        voice_uuid = voice_list['items'][0]['uuid']

        st.info(f"🎯 Project UUID: {project_uuid}")
        st.info(f"🎤 Voice UUID: {voice_uuid}")

        return project_uuid, voice_uuid

    except Exception as e:
        st.error(f"Failed to retrieve project/voice UUID: {e}")
        return None, None

def generate_voice(text, project_uuid, voice_uuid):
    try:
        response = Resemble.v2.clips.create_sync(
            project_uuid,
            voice_uuid,
            text
        )

        # Debug output
        st.subheader("🧾 Raw Response from API")
        st.json(response)

        audio_url = response.get("audio_src")

        if not audio_url or not audio_url.startswith("http"):
            st.error("❌ No valid audio URL returned.")
            return None
        return audio_url

    except Exception as e:
        st.error(f"❌ Error generating voice: {e}")
        return None

# === MAIN APP ===
def main():
    st.title("🗣️ Resemble AI TTS via SDK")

    text = st.text_area("💬 Enter text:", height=200)
    speed = st.slider("⏩ Playback Speed", min_value=0.5, max_value=2.0, value=1.0, step=0.1)

    if st.button("🎤 Generate Voice"):
        if not text.strip():
            st.warning("⚠️ Text field is empty.")
            return

        with st.spinner("Fetching project and voice UUID..."):
            project_uuid, voice_uuid = get_default_project_and_voice()

        if not project_uuid or not voice_uuid:
            return

        with st.spinner("Generating audio via Resemble AI..."):
            audio_url = generate_voice(text, project_uuid, voice_uuid)

        if audio_url:
            st.success("✅ Voice generated successfully.")
            st.audio(audio_url, format="audio/mp3")

            audio_response = requests.get(audio_url)
            adjusted_audio = BytesIO()
            adjust_audio_speed(audio_response.content, speed).export(adjusted_audio, format="mp3")
            adjusted_audio.seek(0)

            st.audio(adjusted_audio, format="audio/mp3")
            st.download_button("⬇️ Download Adjusted Audio", adjusted_audio, file_name="voice.mp3", mime="audio/mp3")
        else:
            st.error("❌ Could not generate audio.")

if __name__ == "__main__":
    main()
