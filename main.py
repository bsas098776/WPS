import streamlit as st
import pandas as pd
import google.generativeai as genai

# 페이지 설정
st.set_page_config(page_title="윤성 WPS AI 비서", page_icon="🍌")
st.title("🍌 Gemini 2.5 Flash-Lite 상담원")

# 1. 오빠의 API 키 설정
API_KEY = "AIzaSyDomjRAFhabTQ8w7pfnJZr6FkcmApicckc" 
genai.configure(api_key=API_KEY)

# 2. 모델 설정 (최신 2.5 Flash-Lite!)
# 이 모델은 100만 토큰까지 지원해서 아주 든든해요!
model = genai.GenerativeModel('gemini-2.5-flash-lite')

@st.cache_data
def load_data():
    return pd.read_excel("wps_list.XLSX")

try:
    df = load_data()
    context = df.to_string(index=False)

    st.success("WPS에 대한 문의사항 물어보세요.")
    
    user_input = st.text_input("💬 질문을 입력하세요", placeholder="예: P8 모재에 적합한 용접봉은?")

    if user_input:
        with st.spinner('Gemini 2.5가 대용량 데이터를 분석 중...'):
            prompt = f"""
            너는 용접 기술 전문가야. 아래 WPS 데이터를 참고해서 답변해줘.
            사용자를 아주 친절하고 대하고, 전문적으로 설명해줘.
            
            [WPS 데이터]
            {context}
            
            [질문]
            {user_input}
            """
            
            response = model.generate_content(prompt)
            st.info("🤖 Gemini 2.5의 답변:")
            st.write(response.text)

except Exception as e:
    st.error(f"이런 에러가 나요: {e}")
