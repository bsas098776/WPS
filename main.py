import streamlit as st
import pandas as pd
import google.generativeai as genai

# 1. 페이지 설정
st.set_page_config(page_title="윤성 WPS AI 비서", page_icon="⚡")
st.title("⚡ Gemini 2.0 실무 상담원")

# 2. 오빠의 API 키 설정
API_KEY = "AIzaSyB7SrAlQzRi80ginfPkNAd8DkICFddZr18" 
genai.configure(api_key=API_KEY)

# 3. 모델 설정 (안정적인 정식 버전으로 변경!)
# -exp를 제거한 'gemini-2.0-flash'가 가장 빠르고 안정적이에요.
model = genai.GenerativeModel('gemini-2.0-flash')

@st.cache_data
def load_data():
    # 엑셀 파일 이름이 wps_list.XLSX인지 꼭 확인해주세요!
    return pd.read_excel("wps_list.XLSX")

try:
    df = load_data()
    # AI가 참고할 수 있게 엑셀 데이터를 텍스트로 변환
    context = df.to_string(index=False)

    st.success("오빠! 엔진 최적화 완료! 이제 질문해 보세요. 꺄하~ 😍")
    
    user_input = st.text_input("💬 궁금한 용접 조건을 물어보세요", placeholder="예: P1 모재에 맞는 용접봉 추천해 줘")

    if user_input:
        with st.spinner('제미니가 데이터를 정밀 분석 중이에요...'):
            # AI에게 역할과 데이터를 주는 프롬프트
            prompt = f"""
            너는 용접 기술 전문가야. 아래 WPS 리스트 데이터를 바탕으로 사용자의 질문에 답변해줘.
            사용자를 '오빠'라고 부르며 아주 친절하고 전문적으로 설명해줘.
            데이터에 기반해서 답변하고, 필요한 경우 실무적인 팁도 알려줘.

            [WPS 데이터]
            {context}

            [사용자 질문]
            {user_input}
            """
            
            # 답변 생성 및 에러 처리
            response = model.generate_content(prompt)
            st.info("🤖 AI의 전문 답변:")
            st.write(response.text)

except Exception as e:
    # 429(사용량 초과) 에러 발생 시 안내
    if "429" in str(e):
        st.error("오빠, 구글 AI가 지금 질문을 너무 많이 받아서 지쳤나 봐요! 1분만 쉬었다가 다시 물어봐 줄래요? 힝.. 😭")
    else:
        st.error(f"오빠, 이런 에러가 나요: {e}")
