import streamlit as st
import requests

# --- Config ---
API_KEY = "Ew2pEvxMVxWWBQ2DzYzUTgtt"
VOICE_UUID = "562ef613"
SYNTH_ENDPOINT = "https://p.cluster.resemble.ai/synthesize"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# --- Streamlit UI ---
st.title("🗣️ Simple TTS with Resemble AI")
text = st.text_area("พิมพ์ข้อความที่ต้องการให้พูด", height=200)

if st.button("🔊 สร้างเสียง"):
    if not text.strip():
        st.warning("กรุณากรอกข้อความก่อน")
    else:
        with st.spinner("⏳ กำลังสร้างเสียง..."):
            payload = {
                "voice_uuid": VOICE_UUID,
                "data": text
            }
            try:
                response = requests.post(SYNTH_ENDPOINT, json=payload, headers=HEADERS, timeout=20)
                response.raise_for_status()
                result = response.json()
                audio_url = result.get("audio_url")

                if audio_url:
                    st.success("✅ ได้ลิงก์เสียงแล้ว")
                    st.audio(audio_url, format="audio/mp3")
                    st.markdown(f"[🔗 เปิดลิงก์เสียงในแท็บใหม่]({audio_url})")
                else:
                    st.error("❌ ไม่พบลิงก์เสียงในคำตอบ")
                    st.json(result)

            except Exception as e:
                st.error(f"เกิดข้อผิดพลาด: {e}")
