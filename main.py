import streamlit as st
import pandas as pd
import google.generativeai as genai

# 페이지 설정
st.set_page_config(page_title="WPS AI 비서", page_icon="🤖")
st.title("🤖 제미니 2.0 실무 상담원")

# 1. API 키 설정 (오빠의 cckc 키 그대로 사용!)
API_KEY = "AIzaSyB7SrAlQzRi80ginfPkNAd8DkICFddZr18" 
genai.configure(api_key=API_KEY)

# 2. 모델 설정 (오빠가 발견한 최신형 2.0 Flash로 변경!)
# 'gemini-2.0-flash-exp'는 현재 가장 빠르고 똑똑한 버전이에요!
model = genai.GenerativeModel('gemini-2.0-flash-exp')

@st.cache_data
def load_data():
    return pd.read_excel("wps_list.XLSX")

try:
    df = load_data()
    # AI가 읽기 편하게 엑셀 데이터를 텍스트로 변환
    context = df.to_string(index=False)

    st.success("오빠! 최신형 Gemini 2.0 엔진이 가동 중이에요! 꺄하~ 😍")
    
    user_input = st.text_input("💬 질문을 입력하세요", placeholder="예: P8 모재에 적합한 용접봉은?")

    if user_input:
        with st.spinner('제미니 2.0이 엑셀을 분석하고 있어요...'):
            prompt = f"""
            너는 용접 전문가야. 제공된 WPS 리스트를 바탕으로 답변해줘.
            사용자를 '오빠'라고 부르고 아주 친절하게 설명해줘.
            
            [데이터]
            {context}
            
            [질문]
            {user_input}
            """
            response = model.generate_content(prompt)
            st.info("🤖 AI의 전문 답변:")
            st.write(response.text)

except Exception as e:
    st.error(f"오빠, 에러가 났어요! 힝.. : {e}")
