import streamlit as st
import requests
import base64
from io import BytesIO

# --- ตั้งค่า API ---
API_KEY = "Ew2pEvxMVxWWBQ2DzYzUTgtt"
VOICE_UUID = "562ef613"
SYNTH_ENDPOINT = "https://p.cluster.resemble.ai/synthesize"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# --- UI ---
st.title("🗣️ แปลงข้อความเป็นเสียง (ภาษาไทย) ด้วย Resemble AI")

text = st.text_area("📄 พิมพ์ข้อความที่ต้องการให้ระบบพูด", height=200)

use_ssml = st.checkbox("📑 ใช้ SSML (เหมาะกับภาษาไทย 100%)", value=True)

if st.button("🔊 สร้างเสียง"):
    if not text.strip():
        st.warning("⚠️ กรุณากรอกข้อความก่อน")
    else:
        with st.spinner("⏳ กำลังสร้างเสียง..."):

            # สร้างข้อความที่จะส่ง
            final_text = (
                f"<speak><lang xml:lang='th-TH'>{text}</lang></speak>"
                if use_ssml else text
            )

            payload = {
                "voice_uuid": VOICE_UUID,
                "data": final_text
            }

            try:
                response = requests.post(SYNTH_ENDPOINT, json=payload, headers=HEADERS, timeout=30)
                response.raise_for_status()
                result = response.json()

                if result.get("audio_content"):
                    audio_base64 = result["audio_content"]
                    audio_bytes = base64.b64decode(audio_base64)
                    audio_buffer = BytesIO(audio_bytes)

                    st.success("✅ สร้างเสียงเรียบร้อยแล้ว!")
                    st.audio(audio_buffer, format="audio/wav")
                    st.download_button("⬇️ ดาวน์โหลดเสียง", data=audio_buffer, file_name="เสียงพูด.wav", mime="audio/wav")
                else:
                    st.error("❌ ไม่พบเสียงในคำตอบที่ได้จาก Resemble AI")
                    st.json(result)

            except Exception as e:
                st.error(f"เกิดข้อผิดพลาด: {e}")
