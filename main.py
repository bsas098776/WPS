import streamlit as st
import pandas as pd
import google.generativeai as genai
import os

# 1. 페이지 설정
st.set_page_config(page_title="윤성 실무 AI 전문가", page_icon="🛡️", layout="wide")

# 2. 릴레이 API 키 로드
keys = st.secrets.get("GEMINI_KEYS", [])

def ask_gemini(prompt, api_keys):
    for i, key in enumerate(api_keys):
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-2.0-flash') # 최신 모델로 업그레이드!
            response = model.generate_content(prompt)
            return response.text, i + 1
        except Exception as e:
            if "429" in str(e): continue
            else: return f"에러: {e}", None
    return "모든 API 키가 만료되었어요 오빠! 😭", None

# 3. 사이드바 업무 선택 (여기서 main_menu를 정의해요!)
st.sidebar.title("📂 윤성 데이터 센터")
main_menu = st.sidebar.radio("원하시는 업무를 고르세요", ["WPS (용접 규격)", "TER (트러블 리포트)"])

# 4. 데이터 로드 로직 (오빠의 깃허브 파일명 100% 반영)
try:
    if main_menu == "WPS (용접 규격)":
        file_path = "wps_list.XLSX"
        st.title("👨‍🏭 WPS 실무 전문가")
    else:
        file_path = "ter_list.xlsx"
        st.title("🛠️ TER 트러블 정밀 분석기")

    if os.path.exists(file_path):
        # [필살기] 파일을 바이너리(rb)로 직접 열어서 엔진에 전달!
        # 이렇게 하면 'not a zip file' 에러를 가장 확실히 막을 수 있어요 🤙
        with open(file_path, "rb") as f:
            if main_menu == "TER (트러블 리포트)":
                xl = pd.ExcelFile(f, engine='openpyxl')
                selected_sheet = st.sidebar.selectbox("📋 분석할 시트 선택", xl.sheet_names)
                df = pd.read_excel(xl, sheet_name=selected_sheet)
            else:
                df = pd.read_excel(f, engine='openpyxl')
            
        st.success(f"✅ 오빠! '{file_path}' 데이터를 완벽하게 읽어왔어요! 꺄하~ 😍")
        
        # 5. 질문 및 답변 분석
        full_context = df.to_csv(index=False)
        user_input = st.text_input(f"💬 {main_menu}에 대해 무엇이든 물어보세요!")

        if user_input:
            with st.spinner('전체 데이터를 정밀 분석 중... 🔍'):
                prompt = f"""너는 {main_menu} 분야의 최고 전문가야. 
                아래 제공된 [전체 데이터]를 꼼꼼히 읽고 오빠에게 친절하게 대답해줘.
                
                [전체 데이터]
                {full_context}
                
                [질문]
                {user_input}"""
                
                answer, key_num = ask_gemini(prompt, keys)
                if key_num:
                    st.info(f"🤖 {key_num}번 엔진 가동! 분석 완료했어요 오빠 🤙")
                    st.markdown(answer)
    else:
        st.error(f"❌ 깃허브에 '{file_path}' 파일이 없어요! 파일명을 확인해 주세요.")

except Exception as e:
    st.error(f"🚨 오빠, 여기서 문제가 생겼어요: {e}")
    st.info("💡 팁: 'not a zip file'이 계속 뜨면 깃허브에서 파일을 지웠다 다시 올려보는 게 가장 빨라요!")
