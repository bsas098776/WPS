import streamlit as st
import pandas as pd
import google.generativeai as genai

st.set_page_config(page_title="WPS AI 비서", page_icon="🤖")
st.title("🤖 윤성 WPS 실무 상담원")

# 1. API 키 설정 (오빠의 cckc 키!)
API_KEY = "AIzaSyB7SrAlQzRi80ginfPkNAd8DkICFddZr18" 
genai.configure(api_key=API_KEY)

# 2. 모델 설정 (무료 할당량이 가장 넉넉한 1.5 Flash로 안정화!)
model = genai.GenerativeModel('models/gemini-1.5-flash')

@st.cache_data
def load_data():
    # 엑셀 파일 이름 대소문자 주의!
    return pd.read_excel("wps_list.XLSX")

try:
    df = load_data()
    context = df.to_string(index=False)

    st.success("오빠! 이제 안정적인 엔진으로 교체 완료했어요! 꺄하~ 😍")
    
    user_input = st.text_input("💬 질문을 입력하세요", placeholder="예: P8 모재에 적합한 용접봉은?")

    if user_input:
        with st.spinner('제미니가 엑셀 데이터를 분석하고 있어요...'):
            # AI에게 역할 부여!
            prompt = f"너는 용접 전문가야. 아래 WPS 데이터를 참고해서 '오빠'에게 친절하게 대답해줘.\n\n[데이터]\n{context}\n\n[질문]\n{user_input}"
            response = model.generate_content(prompt)
            st.info("🤖 AI 답변:")
            st.write(response.text)

except Exception as e:
    # 429 에러가 또 나면 사용자에게 친절하게 안내!
    if "429" in str(e):
        st.error("오빠, 구글 AI가 지금 너무 바쁜가 봐요! 1분만 있다가 다시 물어봐 줄래요? 힝.. 😭")
    else:
        st.error(f"오빠, 이런 에러가 나요: {e}")
