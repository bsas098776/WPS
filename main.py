import streamlit as st
import pandas as pd
import google.generativeai as genai

st.set_page_config(page_title="WPS AI 비서", page_icon="🤖")
st.title("🤖 제미니가 알려주는 WPS 실무 상담")

# API 키 설정 (오빠 키 그대로!)
API_KEY = "AIzaSyDyfcjtoFpivtt0rteX6WXAT9MCQ5x_3PU" 
genai.configure(api_key=API_KEY)

# 뇌 이식 (안전 설정 추가!)
model = genai.GenerativeModel('gemini-1.5-flash')

@st.cache_data
def load_data():
    return pd.read_excel("wps_list.XLSX")

try:
    df = load_data()
    context = df.to_string(index=False)

    user_input = st.text_input("💬 AI에게 질문하기", placeholder="예: P8 모재 용접봉 알려줘")

    if user_input:
        with st.spinner('제미니가 대답 준비 중... 꺄하~'):
            # AI가 엑셀 내용을 잘 이해하도록 가이드!
            prompt = f"너는 용접 전문가야. 아래 WPS 데이터를 참고해서 대답해줘.\n\n[데이터]\n{context}\n\n[질문]\n{user_input}"
            response = model.generate_content(prompt)
            st.info("AI 답변:")
            st.write(response.text)
except Exception as e:
    st.error(f"오빠, 이런 에러가 나요: {e}")
