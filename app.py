import streamlit as st
import requests
from io import BytesIO
from pydub import AudioSegment

# API Key for Resemble AI
API_KEY = "Ew2pEvxMVxWWBQ2DzYzUTgtt"
BASE_URL = "https://f.cluster.resemble.ai/synthesize"

# Adjust audio speed
def adjust_audio_speed(audio_content, speed=1.0):
    """Adjust audio playback speed."""
    st.debug("Adjusting audio speed...")
    audio = AudioSegment.from_file(BytesIO(audio_content), format="mp3")
    new_audio = audio._spawn(audio.raw_data, overrides={"frame_rate": int(audio.frame_rate * speed)})
    return new_audio.set_frame_rate(audio.frame_rate)

# Streamlit app
def main():
    st.title("Text-to-Speech with Resemble AI")

    # Large text input
    text = st.text_area("Enter your text below:", height=200)

    # Speed adjustment slider
    speed = st.slider("Playback Speed", min_value=0.5, max_value=2.0, value=1.0, step=0.1)

    if st.button("Generate and Play Voice"):
        if not text:
            st.error("Please fill in the text field.")
        else:
            st.debug("Initiating voice generation process...")
            audio_urls = generate_voice(text)
            if audio_urls:
                st.success("Voice generated successfully!")

                for index, audio_url in enumerate(audio_urls):
                    st.debug(f"Fetching audio content from: {audio_url}")
                    audio_content = requests.get(audio_url).content

                    st.debug("Adjusting playback speed for the audio...")
                    adjusted_audio = BytesIO()
                    adjust_audio_speed(audio_content, speed).export(adjusted_audio, format="mp3")
                    adjusted_audio.seek(0)

                    # Play adjusted audio
                    st.audio(adjusted_audio, format="audio/mp3")

                    # Provide download option
                    st.download_button(
                        label=f"Download Adjusted Audio {index + 1}",
                        data=adjusted_audio,
                        file_name=f"adjusted_voice_{index + 1}.mp3",
                        mime="audio/mp3"
                    )
            else:
                st.error("Failed to generate voice. Check your input and try again.")


def generate_voice(text):
    """Generate audio from text using Resemble AI"""
    st.debug("Preparing API request...")
    url = BASE_URL
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Split text into manageable chunks
    max_chunk_size = 500  # Adjust based on Resemble AI's limits
    chunks = [text[i:i + max_chunk_size] for i in range(0, len(text), max_chunk_size)]
    st.debug(f"Split text into {len(chunks)} chunks.")

    audio_urls = []
    for i, chunk in enumerate(chunks):
        st.debug(f"Processing chunk {i + 1}/{len(chunks)}...")
        payload = {
            "voice_uuid": "562ef613",
            "data": chunk
        }
        
        st.debug(f"Sending API request for chunk {i + 1}...")
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            st.debug(f"Received successful response for chunk {i + 1}.")
            response_data = response.json()
            audio_urls.append(response_data.get("audio_url"))
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
            return None

    st.debug("All chunks processed successfully.")
    return audio_urls

if __name__ == "__main__":
    main()
