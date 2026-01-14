import streamlit as st
import pandas as pd
import google.generativeai as genai

st.set_page_config(page_title="윤성 WPS 무적 상담원", page_icon="🛡️")
st.title("🛡️ Gemini 2.5 릴레이 상담원")

# 1. 시크릿에서 키 리스트 불러오기
keys = st.secrets.get("GEMINI_KEYS", [])

@st.cache_data
def load_data():
    return pd.read_excel("wps_list.XLSX")

def ask_gemini(prompt, api_keys):
    """할당량이 남은 키를 찾을 때까지 릴레이로 시도하는 함수"""
    for i, key in enumerate(api_keys):
        try:
            genai.configure(api_key=key)
            # 현재 가장 안정적인 2.5 flash 모델 사용
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt)
            return response.text, i + 1  # 성공한 답변과 사용된 키 번호 반환
        except Exception as e:
            # 429 에러(할당량 초과)면 다음 키로 넘어가고, 아니면 에러 표시
            if "429" in str(e):
                continue 
            else:
                return f"에러 발생: {e}", None
    return "오빠... 준비한 키 10개를 다 썼나 봐요. 내일 다시 시도해야겠어요. 😭", None

try:
    df = load_data()
    context = df.to_string(index=False)
    st.success(f"오빠! 총 {len(keys)}개의 키가 대기 중이에요. 꺄하~ 😍")
    
    user_input = st.text_input("💬 질문을 입력하세요")
    if user_input:
        with st.spinner('사용 가능한 키를 찾아서 분석 중...'):
            prompt = f"너는 용접 전문가야. '오빠'에게 친절하게 대답해줘.\n\n[데이터]\n{context}\n\n[질문]\n{user_input}"
            
            answer, key_num = ask_gemini(prompt, keys)
            
            if key_num:
                st.info(f"🤖 {key_num}번 키로 답변 생성 완료!")
                st.write(answer)
            else:
                st.error(answer)
except Exception as e:
    st.error(f"오빠, 이런 에러가 나요: {e}")
