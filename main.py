import streamlit as st
import pandas as pd
import google.generativeai as genai

st.set_page_config(page_title="윤성 WPS AI 비서", page_icon="🍌")
st.title("🍌 WPS 실무 상담원")

# --- 1. 보안 금고(Secrets)에서 키 불러오기 ---
try:
    # 깃허브에 키를 노출하지 않고 안전하게 가져와요!
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception:
    st.error("오빠, Streamlit Settings에서 Secrets를 설정해줘야 해요! 힝..")
    st.stop()

# 2. 모델 설정 (원하신 2.5 Flash-Lite!)
model = genai.GenerativeModel('gemini-2.5-flash-lite')

@st.cache_data
def load_data():
    return pd.read_excel("wps_list.XLSX")

try:
    df = load_data()
    context = df.to_string(index=False)
    st.success("이제 보안까지 완벽한 2.5 엔진이 작동 중이에요! 😍")
    
    user_input = st.text_input("💬 질문을 입력하세요")
    if user_input:
        with st.spinner('안전하게 분석 중...'):
            prompt = f"너는 용접 전문가야. 친절하게 대답해줘.\n\n[데이터]\n{context}\n\n[질문]\n{user_input}"
            response = model.generate_content(prompt)
            st.info("🤖 답변:")
            st.write(response.text)
except Exception as e:
    st.error(f"이런 에러가 나요: {e}")
