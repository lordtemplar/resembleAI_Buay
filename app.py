import streamlit as st
import requests
import base64
from io import BytesIO

# --- Config ---
API_KEY = "Ew2pEvxMVxWWBQ2DzYzUTgtt"
VOICE_UUID = "562ef613"
SYNTH_ENDPOINT = "https://p.cluster.resemble.ai/synthesize"

HEADERS = {
    "Authorization": f"Bearer " + API_KEY,
    "Content-Type": "application/json"
}

st.title("🗣️ Simple TTS with Resemble (Base64 Audio)")

text = st.text_area("พิมพ์ข้อความ:", height=200)

if st.button("🔊 สร้างเสียง"):
    if not text.strip():
        st.warning("⚠️ กรุณากรอกข้อความ")
    else:
        with st.spinner("🔄 กำลังสร้างเสียง..."):
            payload = {
                "voice_uuid": VOICE_UUID,
                "data": text
            }
            try:
                response = requests.post(SYNTH_ENDPOINT, json=payload, headers=HEADERS, timeout=20)
                response.raise_for_status()
                result = response.json()

                if result.get("audio_content"):
                    # 🔓 ถอดรหัส base64 → WAV
                    audio_base64 = result["audio_content"]
                    audio_bytes = base64.b64decode(audio_base64)
                    audio_buffer = BytesIO(audio_bytes)

                    st.success("✅ เสียงสร้างเรียบร้อย")
                    st.audio(audio_buffer, format="audio/wav")
                    st.download_button("⬇️ ดาวน์โหลดเสียง", data=audio_buffer, file_name="voice.wav", mime="audio/wav")
                else:
                    st.error("❌ ไม่พบข้อมูลเสียงในผลลัพธ์")
                    st.json(result)

            except Exception as e:
                st.error(f"❌ เกิดข้อผิดพลาด: {e}")
