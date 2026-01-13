import streamlit as st
import pandas as pd
import google.generativeai as genai

# 페이지 설정
st.set_page_config(page_title="WPS AI 비서", page_icon="🤖")
st.title("🤖 제미니가 알려주는 WPS 실무 상담")

# --- 1. API 키 설정 (오빠의 키를 여기에 넣으세요!) ---
# 나중에 보안을 위해 설정창에 넣는 법도 알려드릴게요!
API_KEY = "여기에_아까_복사한_키를_넣으세요" 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. 엑셀 데이터 로드 ---
@st.cache_data
def load_data():
    return pd.read_excel("wps_list.XLSX")

try:
    df = load_data()
    # 엑셀 내용을 텍스트로 변환해서 AI에게 줄 준비
    context = df.to_string(index=False)

    st.info("오빠! 이제 단순 검색이 아니라 질문을 해보세요. 예: 'P8 모재에 맞는 용접봉 추천해줘'")
    
    user_input = st.text_input("💬 AI에게 물어보기")

    if user_input:
        with st.spinner('제미니가 답변을 생각 중이에요... 꺄하~'):
            # AI에게 줄 프롬프트 (오빠의 데이터 + 질문)
            prompt = f"""
            너는 용접 기술 전문가야. 아래 제공된 WPS 마스터 리스트 데이터를 바탕으로 사용자의 질문에 친절하게 답변해줘.
            데이터에 없는 내용은 함부로 추측하지 말고 모르겠다고 답변해.
            한국어로 답변하고, 질문한 사람을 '오빠'라고 부르며 아주 친절하게 설명해줘.

            [WPS 데이터]
            {context}

            [사용자 질문]
            {user_input}
            """
            
            response = model.generate_content(prompt)
            st.success("AI 답변 완료! ✨")
            st.write(response.text)

except Exception as e:
    st.error(f"오빠, 에러가 났어요! 힝.. : {e}")

# --- 3. 필요한 라이브러리 안내 ---
# requirements.txt에 'google-generativeai'를 꼭 추가해야 해요!
