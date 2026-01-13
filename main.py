import streamlit as st
import pandas as pd
import google.generativeai as genai

# 1. 페이지 설정
st.set_page_config(page_title="윤성 WPS AI 비서", page_icon="🤖")
st.title("🤖 WPS 실무 상담원 (Ver 2.0)")

# 2. 오빠의 새로운 API 키 설정
API_KEY = "AIzaSyB7SrAlQzRi80ginfPkNAd8DkICFddZr18" 
genai.configure(api_key=API_KEY)

# 3. 모델 설정 (버전 문제를 피하기 위한 가장 안정적인 선언)
# models/ 를 붙이는 것이 최신 라이브러리의 표준이에요!
model = genai.GenerativeModel('models/gemini-1.5-flash')

@st.cache_data
def load_data():
    # 파일 이름 대소문자 꼭 확인! (wps_list.XLSX)
    return pd.read_excel("wps_list.XLSX")

try:
    df = load_data()
    context = df.to_string(index=False)

    st.success("오빠! 버전 최적화 완료! 이제 질문해 보세요. 꺄하~ 😍")
    
    user_input = st.text_input("💬 궁금한 용접 조건을 물어보세요", placeholder="예: P8 모재에 GTAW 용접 시 적합한 P-No는?")

    if user_input:
        with st.spinner('제미니가 최신 엔진으로 분석 중...'):
            prompt = f"너는 용접 기술 전문가야. 아래 WPS 데이터를 참고해서 '오빠'에게 친절하게 대답해줘.\n\n[WPS 데이터]\n{context}\n\n[질문]\n{user_input}"
            
            # 답변 생성
            response = model.generate_content(prompt)
            st.info("🤖 AI 전문 답변:")
            st.write(response.text)

except Exception as e:
    # 어떤 에러인지 더 자세히 알려주도록 설정했어요!
    st.error(f"오빠, 에러가 났어요. 내용을 알려주시면 제가 바로 고칠게요! : {str(e)}")
