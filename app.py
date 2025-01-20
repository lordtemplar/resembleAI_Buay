import streamlit as st
import requests
from io import BytesIO
from pydub import AudioSegment

# API Key for Resemble AI
API_KEY = "Ew2pEvxMVxWWBQ2DzYzUTgtt"
BASE_URL = "https://app.resemble.ai/v1"

# Adjust audio speed
def adjust_audio_speed(audio_content, speed=1.0):
    """Adjust audio playback speed."""
    audio = AudioSegment.from_file(BytesIO(audio_content), format="mp3")
    new_audio = audio._spawn(audio.raw_data, overrides={"frame_rate": int(audio.frame_rate * speed)})
    return new_audio.set_frame_rate(audio.frame_rate)

# Streamlit app
def main():
    st.title("Text-to-Speech with Resemble AI")

    # Large text input
    text = st.text_area("Enter your text below:", height=200)

    # Input for Project UUID and Voice UUID
    project_uuid = st.text_input("Project UUID", "Enter your project UUID")
    voice_uuid = st.text_input("Voice UUID", "Enter your voice UUID")

    # Speed adjustment slider
    speed = st.slider("Playback Speed", min_value=0.5, max_value=2.0, value=1.0, step=0.1)

    if st.button("Generate and Play Voice"):
        if not text or not project_uuid or not voice_uuid:
            st.error("Please fill in all fields.")
        else:
            # Generate voice using Resemble AI API
            audio_url = generate_voice(project_uuid, voice_uuid, text)
            if audio_url:
                st.success("Voice generated successfully!")

                # Fetch audio and adjust speed
                audio_content = requests.get(audio_url).content
                adjusted_audio = BytesIO()
                adjust_audio_speed(audio_content, speed).export(adjusted_audio, format="mp3")
                adjusted_audio.seek(0)

                # Play adjusted audio
                st.audio(adjusted_audio, format="audio/mp3")

                # Provide download option
                st.download_button(
                    label="Download Adjusted Audio",
                    data=adjusted_audio,
                    file_name="adjusted_voice.mp3",
                    mime="audio/mp3"
                )
            else:
                st.error("Failed to generate voice. Check your input and try again.")


def generate_voice(project_uuid, voice_uuid, text):
    """Generate audio from text using Resemble AI"""
    url = f"{BASE_URL}/projects/{project_uuid}/clips"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "data": {
            "text": text,
            "voice": voice_uuid,
            "project_uuid": project_uuid
        }
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        response_data = response.json()
        return response_data.get("url")
    else:
        st.error(f"Error: {response.status_code} - {response.text}")
        return None

if __name__ == "__main__":
    main()
