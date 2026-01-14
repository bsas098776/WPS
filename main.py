import streamlit as st
import pandas as pd
import google.generativeai as genai
import os

# 1. 페이지 설정
st.set_page_config(page_title="윤성 통합 실무 AI", page_icon="🛡️", layout="wide")

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
main_menu = st.sidebar.radio("원하시는 데이터를 고르세요", ["WPS (용접 규격)", "TER (트러블 리포트)"])

# 4. 데이터 로드 로직 (오빠가 알려준 깃허브 파일명 100% 반영!)
try:
    if main_menu == "WPS (용접 규격)":
        # 오빠가 알려준 대문자 확장자 그대로! 🤙
        file_path = "wps_list.XLSX" 
        st.title("👨‍🏭 WPS 실무 전문가")
        
        if os.path.exists(file_path):
            # 31번 줄 에러 방지를 위해 엔진 명시
            df = pd.read_excel(file_path, engine='openpyxl')
            st.success(f"✅ '{file_path}' 전수 조사 준비 완료! 꺄하~ 😍")
        else:
            st.error(f"❌ 깃허브에 '{file_path}' 파일이 없어요! 대소문자를 확인해 주세요.")
            st.stop()

    else:
        # 오빠가 알려준 소문자 파일명 그대로! 🤙
        file_path = "ter_list.xlsx"
        st.title("🛠️ TER 트러블 정밀 분석기")
        
        if os.path.exists(file_path):
            # 시트 목록을 먼저 가져오기
            xl = pd.ExcelFile(file_path, engine='openpyxl')
            selected_sheet = st.sidebar.selectbox("📋 분석할 시트 선택", xl.sheet_names)
            
            # 선택한 시트 전체 데이터를 읽어옵니다!
            df = pd.read_excel(file_path, sheet_name=selected_sheet, engine='openpyxl')
            st.success(f"✅ '{selected_sheet}' 시트 분석 준비 완료! 🤙✨")
        else:
            st.error(f"❌ 깃허브에 '{file_path}' 파일이 없어요! 확인 부탁드려요 오빠 😭")
            st.stop()

    # 5. 질문 및 답변 (데이터 전량 전송)
    full_context = df.to_csv(index=False)
    user_input = st.text_input(f"💬 {main_menu}에 대해 무엇이든 물어보세요!")

    if user_input:
        with st.spinner('데이터를 정밀 스캔 중이에요... 🔍'):
            prompt = f"""너는 {main_menu} 분야의 최고 전문가야. 
            아래 [전체 데이터]를 바탕으로 오빠에게 친절하고 정확하게 답해줘.
            
            [전체 데이터]
            {full_context}
            
            [질문]
            {user_input}"""
            
            answer, key_num = ask_gemini(prompt, keys)
            if key_num:
                st.info(f"🤖 {key_num}번 엔진으로 분석 완료!")
                st.markdown(answer)

except Exception as e:
    st.error(f"🚨 오빠, 여기서 문제가 생겼어요: {e}")
