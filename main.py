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
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt)
            return response.text, i + 1
        except Exception as e:
            if "429" in str(e): continue
            else: return f"에러: {e}", None
    return "준비된 모든 키가 만료되었습니다. 😭", None

# 3. 사이드바 업무 선택
st.sidebar.title("📂 업무 모드 선택")
main_menu = st.sidebar.radio("원하시는 업무를 고르세요", ["WPS (용접 규격)", "TER (트러블 리포트)"])

# 4. 파일 로드 로직 (오빠가 알려준 파일명 그대로!)
try:
    if main_menu == "WPS (용접 규격)":
        # WPS 파일명은 보통 wps_list.XLSX 인 경우가 많으니 확인 부탁드려요!
        file_path = "wps_list.XLSX" 
        st.title("👨‍🏭 WPS 실무 전문가")
        
        if os.path.exists(file_path):
            df = pd.read_excel(file_path, engine='openpyxl')
            st.success("✅ WPS 전수 조사 준비 완료! 꺄하~ 😍")
        else:
            st.warning(f"⚠️ '{file_path}' 파일을 깃허브에서 찾을 수 없어요. 파일명을 확인해 주세요!")
            st.stop()

    else:
        # 오빠가 보내준 TER 파일명 정확히 입력!
        file_path = "1. TER(전체) LIST (250107).xlsx"
        st.title("🛠️ TER 트러블 정밀 분석기")
        
        if os.path.exists(file_path):
            # 시트가 워낙 많으니 선택 기능을 넣었어요.
            xl = pd.ExcelFile(file_path, engine='openpyxl')
            selected_sheet = st.sidebar.selectbox("📋 분석할 시트 선택", xl.sheet_names)
            
            # 전체 행을 읽어옵니다!
            df = pd.read_excel(file_path, sheet_name=selected_sheet, engine='openpyxl')
            st.success(f"✅ '{selected_sheet}' 시트 전체 분석 준비 완료! 🤙✨")
        else:
            st.error(f"❌ 깃허브에 '{file_path}' 파일이 없어요! 파일명을 확인해 주세요.")
            st.stop()

    # 5. 질문 및 전체 데이터 분석
    # AI가 읽기 편하게 CSV 형식으로 변환
    full_context = df.to_csv(index=False)
    user_input = st.text_input(f"💬 {main_menu} 관련 무엇이든 물어보세요! (전체 데이터 기반)")

    if user_input:
        with st.spinner('전체 데이터를 정밀 분석 중이에요... 🔍'):
            prompt = f"""너는 {main_menu} 분야의 최고 전문가야. 
            아래 제공된 [전체 데이터]를 꼼꼼히 읽고 오빠에게 친절하게 대답해줘.
            
            [전체 데이터]
            {full_context}
            
            [오빠의 질문]
            {user_input}"""
            
            answer, key_num = ask_gemini(prompt, keys)
            if key_num:
                st.info(f"🤖 {key_num}번 엔진으로 분석을 완료했어요!")
                st.markdown(answer)

except Exception as e:
    st.error(f"🚨 오빠, 예기치 못한 에러가 났어요: {e}")
