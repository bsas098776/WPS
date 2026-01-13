import streamlit as st
import pandas as pd
import google.generativeai as genai

st.set_page_config(page_title="WPS AI 비서", page_icon="🤖")
st.title("🤖 윤성 WPS 실무 상담원")

# 1. 오빠가 새로 알려준 API 키 적용!
API_KEY = "AIzaSyB7SrAlQzRi80ginfPkNAd8DkICFddZr18" 
genai.configure(api_key=API_KEY)

# 2. 모델 설정 (가장 안정적인 호출 방식입니다!)
model = genai.GenerativeModel('gemini-1.5-flash')

@st.cache_data
def load_data():
    return pd.read_excel("wps_list.XLSX")

try:
    df = load_data()
    context = df.to_string(index=False)

    st.success("오빠! 새로운 API 키로 엔진 설정 완료! 꺄하~ 😍")
    
    user_input = st.text_input("💬 질문을 입력하세요", placeholder="예: P8 모재에 적합한 용접봉은?")

    if user_input:
        with st.spinner('제미니가 엑셀 데이터를 분석하고 있어요...'):
            prompt = f"너는 용접 기술 전문가야. 아래 데이터를 바탕으로 질문에 대답해줘. 질문자에게 '오빠'라고 부르며 친절하게 설명해.\n\n[데이터]\n{context}\n\n[질문]\n{user_input}"
            
            response = model.generate_content(prompt)
            st.info("🤖 AI 답변:")
            st.write(response.text)

except Exception as e:
    st.error(f"오빠, 이런 에러가 나요: {e}")
