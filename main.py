import streamlit as st
import pandas as pd
import google.generativeai as genai

st.set_page_config(page_title="윤성 WPS AI 비서", page_icon="⚡")
st.title("⚡ Gemini 실무 상담원 (무제한급)")

# --- 1. 보안 금고(Secrets)에서 키 불러오기 ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception:
    st.error("오빠, Streamlit Settings에서 Secrets를 확인해 주세요! 힝..")
    st.stop()

# 2. 모델 설정 (하루 1,500회 요청 가능한 1.5 Flash!)
# 아까 2.5보다 훨씬 넉넉하게 쓰실 수 있어요! 
model = genai.GenerativeModel('gemini-1.5-flash')

@st.cache_data
def load_data():
    return pd.read_excel("wps_list.XLSX")

try:
    df = load_data()
    context = df.to_string(index=False)
    st.success("이제 하루 1,500번 질문해도 끄떡없는 엔진이에요! 꺄하~ 😍")
    
    user_input = st.text_input("💬 질문을 입력하세요 (예: P8 용접봉 알려줘)")
    if user_input:
        with st.spinner('제미니가 성실하게 답변 준비 중...'):
            prompt = f"너는 용접 전문가야. 친절하게 대답해줘.\n\n[데이터]\n{context}\n\n[질문]\n{user_input}"
            response = model.generate_content(prompt)
            st.info("🤖 AI의 전문 답변:")
            st.write(response.text)
except Exception as e:
    st.error(f"에러가 났어요: {e}")
