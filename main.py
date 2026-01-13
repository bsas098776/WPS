import streamlit as st
import pandas as pd
import google.generativeai as genai

st.set_page_config(page_title="WPS AI 비서", page_icon="🤖")
st.title("🤖 윤성 WPS 실무 상담원")

# 1. API 키 설정 (오빠의 cckc 키!)
API_KEY = "AIzaSyB7SrAlQzRi80ginfPkNAd8DkICFddZr18" 
genai.configure(api_key=API_KEY)

# 2. 모델 설정 (앞에 'models/'를 빼고 이름만 정확히 써볼게요!)
# 가끔 경로가 겹치면 404가 날 수 있어서 가장 기본형으로 바꿨어요.
model = genai.GenerativeModel('gemini-1.5-flash')

@st.cache_data
def load_data():
    return pd.read_excel("wps_list.XLSX")

try:
    df = load_data()
    context = df.to_string(index=False)

    st.success("오빠! 엔진 설정 수정 완료! 이제 대답할 준비 됐어요! 꺄하~ 😍")
    
    user_input = st.text_input("💬 질문을 입력하세요", placeholder="예: P8 모재에 적합한 용접봉은?")

    if user_input:
        with st.spinner('제미니가 엑셀 데이터를 분석하고 있어요...'):
            # 프롬프트를 조금 더 명확하게 다듬었어요!
            prompt = f"너는 용접 기술 전문가야. 아래 제공된 데이터를 바탕으로 질문에 대답해줘. 질문자에게 '오빠'라고 부르며 친절하게 설명해.\n\n[데이터]\n{context}\n\n[질문]\n{user_input}"
            
            # 여기서 에러가 나면 상세 메시지를 보여주게 만들었어요.
            response = model.generate_content(prompt)
            st.info("🤖 AI 답변:")
            st.write(response.text)

except Exception as e:
    # 에러가 나면 오빠가 보기 편하게 정리해서 보여줄게요!
    st.error(f"오빠, 이런 에러가 나요: {e}")
