import streamlit as st
import pandas as pd
import google.generativeai as genai

# 페이지 설정
st.set_page_config(page_title="윤성 WPS AI 비서", page_icon="⚡")
st.title("⚡ Gemini 2.0 실무 상담원")

# 1. 오빠의 새로운 API 키 설정
API_KEY = "AIzaSyB7SrAlQzRi80ginfPkNAd8DkICFddZr18" 
genai.configure(api_key=API_KEY)

# 2. 모델 설정 (오빠가 원하시는 2.0 Flash 최신 버전!)
# 'gemini-2.0-flash-exp'는 현재 가장 똑똑하고 빠른 엔진이에요.
model = genai.GenerativeModel('gemini-2.0-flash-exp')

@st.cache_data
def load_data():
    return pd.read_excel("wps_list.XLSX")

try:
    df = load_data()
    context = df.to_string(index=False)

    st.success("오빠! 최신형 2.0 엔진으로 업그레이드 완료! 꺄하~ 😍")
    
    user_input = st.text_input("💬 질문을 입력하세요", placeholder="예: P8 모재에 적합한 용접봉은?")

    if user_input:
        with st.spinner('Gemini 2.0이 엑셀 데이터를 정밀 분석 중...'):
            # AI에게 더 똑똑하게 대답하라고 가이드를 줬어요!
            prompt = f"""
            너는 용접 기술 전문가야. 아래 WPS 데이터를 참고해서 답변해줘.
            사용자를 '오빠'라고 부르고 아주 친절하고 전문적으로 설명해줘.
            데이터에 근거해서 답변하되, 실무적인 조언도 곁들여줘.
            
            [WPS 데이터]
            {context}
            
            [질문]
            {user_input}
            """
            
            response = model.generate_content(prompt)
            st.info("🤖 Gemini 2.0의 전문 답변:")
            st.write(response.text)

except Exception as e:
    # 에러가 나면 오빠가 보기 편하게 출력!
    if "429" in str(e):
        st.error("오빠, 2.0 엔진이 지금 인기가 너무 많아서 잠시 쉬고 있나 봐요! 1분만 있다가 다시 눌러주세요! 힝.. 😭")
    else:
        st.error(f"오빠, 이런 에러가 나요: {e}")
