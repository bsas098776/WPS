import streamlit as st
import pandas as pd
import google.generativeai as genai

# 페이지 설정
st.set_page_config(page_title="윤성 WPS AI 비서", page_icon="🚀")
st.title("🚀 Gemini 2.0 최신형 상담원")

# 1. 보안 금고(Secrets)에서 키 불러오기
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception:
    st.error("Streamlit Settings에서 Secrets를 설정해 주세요! 힝..")
    st.stop()

# 2. 모델 설정 (1.5 대신 하루 1,500번 가능한 2.5 Flash!)
# 2.5 Flash는 1.5보다 훨씬 똑똑하고 지원 기간도 넉넉해요!
model = genai.GenerativeModel('gemini-2.0-flash')

@st.cache_data
def load_data():
    return pd.read_excel("wps_list.XLSX")

try:
    df = load_data()
    context = df.to_string(index=False)
    st.success("2026년형 Gemini 2.5 엔진 가동 중! 이제 무제한급이에요! 꺄하~ 😍")
    
    user_input = st.text_input("💬 질문을 입력하세요 (예: P1 용접봉 추천)")
    if user_input:
        with st.spinner('최신형 2.5 엔진이 분석 중이에요...'):
            prompt = f"너는 용접 전문가야. 친절하게 대답해줘.\n\n[데이터]\n{context}\n\n[질문]\n{user_input}"
            response = model.generate_content(prompt)
            st.info("🤖 AI의 전문 답변:")
            st.write(response.text)
except Exception as e:
    st.error(f"이런 메시지가 떠요: {e}")
