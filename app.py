import streamlit as st
import requests
import base64
from io import BytesIO

# --- ตั้งค่าการเชื่อมต่อ ---
API_KEY = "Ew2pEvxMVxWWBQ2DzYzUTgtt"
VOICE_UUID = "562ef613"
SYNTH_ENDPOINT = "https://p.cluster.resemble.ai/synthesize"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# --- ส่วนติดต่อผู้ใช้ ---
st.title("🗣️ แปลงข้อความเป็นเสียงภาษาไทย ด้วย Resemble AI")

text = st.text_area("📄 พิมพ์ข้อความที่ต้องการให้พูด", height=200)

if st.button("🔊 สร้างเสียงพูด"):
    if not text.strip():
        st.warning("⚠️ กรุณากรอกข้อความก่อน")
    else:
        with st.spinner("⏳ กำลังดำเนินการ..."):
            payload = {
                "voice_uuid": VOICE_UUID,
                "data": text
            }
            try:
                response = requests.post(SYNTH_ENDPOINT, json=payload, headers=HEADERS, timeout=20)
                response.raise_for_status()
                result = response.json()

                if result.get("audio_content"):
                    # แปลง base64 เป็นไฟล์เสียง
                    audio_base64 = result["audio_content"]
                    audio_bytes = base64.b64decode(audio_base64)
                    audio_buffer = BytesIO(audio_bytes)

                    st.success("✅ สร้างเสียงสำเร็จเรียบร้อย")
                    st.audio(audio_buffer, format="audio/wav")
                    st.download_button("⬇️ ดาวน์โหลดเสียง", data=audio_buffer, file_name="เสียงพูด.wav", mime="audio/wav")
                else:
                    st.error("❌ ไม่พบข้อมูลเสียง กรุณาลองใหม่อีกครั้ง")
                    st.json(result)

            except Exception as e:
                st.error(f"❌ เกิดข้อผิดพลาดในการเชื่อมต่อ: {e}")
