import streamlit as st
import requests
from io import BytesIO
from pydub import AudioSegment

# ===== CONFIG =====
API_KEY = "Ew2pEvxMVxWWBQ2DzYzUTgtt"
BASE_URL = "https://f.cluster.resemble.ai/synthesize"
VOICE_UUID = "562ef613"  # ปรับตาม voice จริงของคุณ

# ===== HELPER =====
def adjust_audio_speed(audio_content, speed=1.0):
    try:
        audio = AudioSegment.from_file(BytesIO(audio_content), format="mp3")
        new_audio = audio._spawn(audio.raw_data, overrides={
            "frame_rate": int(audio.frame_rate * speed)
        }).set_frame_rate(audio.frame_rate)
        return new_audio
    except Exception as e:
        st.error(f"Error adjusting audio speed: {e}")
        return AudioSegment.silent(duration=1000)  # fallback

def generate_voice(text):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    max_chunk_size = 500
    chunks = [text[i:i + max_chunk_size] for i in range(0, len(text), max_chunk_size)]
    audio_urls = []

    for i, chunk in enumerate(chunks):
        with st.spinner(f"🔊 Generating voice for chunk {i + 1}/{len(chunks)}..."):
            payload = {
                "voice_uuid": VOICE_UUID,
                "data": chunk
            }

            try:
                response = requests.post(BASE_URL, json=payload, headers=headers, timeout=20)
                response.raise_for_status()
                audio_url = response.json().get("audio_url")

                if not audio_url or not audio_url.startswith("http"):
                    st.error(f"Invalid audio URL for chunk {i + 1}")
                    continue

                audio_urls.append(audio_url)

            except requests.exceptions.RequestException as e:
                st.error(f"Chunk {i + 1} failed: {e}")
                return None

    return audio_urls

# ===== MAIN STREAMLIT APP =====
def main():
    st.title("🗣️ Text-to-Speech with Resemble AI")

    text = st.text_area("📄 Enter text to convert to speech:", height=200)
    speed = st.slider("🎚️ Playback Speed", min_value=0.5, max_value=2.0, value=1.0, step=0.1)

    if st.button("▶️ Generate and Play"):
        if not text.strip():
            st.warning("Please enter some text.")
            return

        st.info("Sending text to Resemble AI...")
        audio_urls = generate_voice(text)

        if audio_urls:
            st.success("✅ Voice generation completed.")

            for index, url in enumerate(audio_urls):
                try:
                    st.write(f"Fetching audio from: {url}")
                    audio_response = requests.get(url, timeout=15)

                    if audio_response.status_code != 200:
                        st.error(f"Error fetching audio chunk {index + 1}")
                        continue

                    adjusted_audio = BytesIO()
                    adjust_audio_speed(audio_response.content, speed).export(adjusted_audio, format="mp3")
                    adjusted_audio.seek(0)

                    st.audio(adjusted_audio, format="audio/mp3")

                    st.download_button(
                        label=f"⬇️ Download Audio {index + 1}",
                        data=adjusted_audio,
                        file_name=f"voice_{index + 1}.mp3",
                        mime="audio/mp3"
                    )
                except Exception as e:
                    st.error(f"Failed to play chunk {index + 1}: {e}")
        else:
            st.error("❌ Voice generation failed. Please try again.")

if __name__ == "__main__":
    main()
