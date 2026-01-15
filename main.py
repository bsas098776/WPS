import streamlit as st
import pandas as pd
from groq import Groq
import os

# 1. Groq API 설정 (철벽 방어 모드 🤙)
raw_key = st.secrets.get("GROQ_API_KEY")

if raw_key:
    # 앞뒤에 있을지 모를 공백과 줄바꿈을 싹 지워버립니다!
    clean_key = raw_key.strip().replace("\n", "").replace("\r", "").replace(" ", "")
    try:
        client = Groq(api_key=clean_key)
    except Exception as e:
        st.error(f"🚨 Groq 클라이언트 초기화 실패: {e}")
        st.stop()
else:
    st.error("🔑 Secrets에 GROQ_API_KEY를 등록해주세요!")
    st.stop()

# 2. 파일 로드 및 질문 로직 (안정화 버전)
st.title("🛡️ 윤성 실무 AI (Groq 광속 분석)")

# 파일 자동 탐색 (오빠 기존 설정 그대로 🤙)
candidates = ["wps_list.XLSX", "wps_list.xlsx", "ter_list.xlsx", "ter_list.xlsx.xlsx"]
file_path = next((f for f in candidates if os.path.exists(f)), None)

if file_path:
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        st.success(f"✅ {file_path} 로드 성공!")

        user_input = st.text_input("💬 질문을 입력하세요 (최신 50줄 분석)")
        if user_input:
            # 8,000 토큰 한도를 피하기 위해 최신 50줄만 분석 🤙
            context = df.tail(50).to_csv(index=False)
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "너는 윤성의 2차전지 장비 전문가야."},
                    {"role": "user", "content": f"데이터:\n{context}\n\n질문: {user_input}"}
                ]
            )
            st.info(response.choices[0].message.content)
    except Exception as e:
        st.error(f"🚨 오류 발생: {e}")
