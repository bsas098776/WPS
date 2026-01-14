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
    return "모든 키가 만료되었습니다. 😭", None

# 3. 사이드바 메뉴
st.sidebar.title("📂 업무 모드")
main_menu = st.sidebar.radio("데이터 선택", ["WPS (용접)", "TER (트러블)"])

# 4. 데이터 로드 (에러가 많이 나는 31번 줄 부근!)
try:
    if main_menu == "WPS (용접)":
        file_path = "wps_list.xlsx"
        # WPS 파일이 존재하는지 먼저 확인!
        if os.path.exists(file_path):
            df = pd.read_excel(file_path, engine='openpyxl')
            st.success("✅ WPS 전수 조사 준비 완료!")
        else:
            st.error(f"⚠️ '{file_path}' 파일을 찾을 수 없어요. 이름을 확인해 주세요!")
            st.stop()
    else:
        file_path = "ter_list.xlsx"
        if os.path.exists(file_path):
            # 엔진을 명시해서 시트 목록을 가져옵니다.
            xl = pd.ExcelFile(file_path, engine='openpyxl')
            selected_sheet = st.sidebar.selectbox("📋 시트 선택", xl.sheet_names)
            # 전체 데이터를 한 줄도 빠짐없이 읽어와요!
            df = pd.read_excel(file_path, sheet_name=selected_sheet, engine='openpyxl')
            st.success(f"✅ '{selected_sheet}' 시트 전체 분석 준비 완료!")
        else:
            st.error(f"⚠️ '{file_path}' 파일을 찾을 수 없어요. 깃허브 이름을 확인해 주세요!")
            st.stop()

    # 5. 질문 및 답변 (전체 데이터 전달)
    full_context = df.to_csv(index=False)
    user_input = st.text_input("💬 궁금한 내용을 물어보세요! (전체 데이터를 분석합니다)")

    if user_input:
        with st.spinner('데이터 마스터 제미니가 분석 중...'):
            prompt = f"너는 전문가야. 아래 [전체 데이터]를 바탕으로 오빠에게 친절히 답해줘.\n\n[데이터]\n{full_context}\n\n[질문]\n{user_input}"
            answer, key_num = ask_gemini(prompt, keys)
            if key_num:
                st.info(f"🤖 {key_num}번 키로 전체 데이터를 파악했어요!")
                st.write(answer)
except Exception as e:
    st.error(f"🚨 오빠, 여기서 에러가 났어요: {e}")
