import streamlit as st
import pandas as pd
import google.generativeai as genai
import os

# ... (상단 설정 및 ask_gemini 함수는 동일) ...

try:
    if main_menu == "WPS (용접 규격)":
        file_path = "wps_list.XLSX"
    else:
        file_path = "ter_list.xlsx"

    if os.path.exists(file_path):
        # [해결책] 바이너리 모드로 파일을 직접 열어서 넘겨줍니다! 🤙
        with open(file_path, "rb") as f:
            if main_menu == "TER (트러블 리포트)":
                # ExcelFile을 사용해 시트를 먼저 파악해요
                xl = pd.ExcelFile(f, engine='openpyxl')
                selected_sheet = st.sidebar.selectbox("📋 시트 선택", xl.sheet_names)
                df = pd.read_excel(xl, sheet_name=selected_sheet)
            else:
                df = pd.read_excel(f, engine='openpyxl')
            
        st.success(f"✅ 오빠! '{file_path}'를 완벽하게 읽어냈어요! 😍")
        
        # 데이터 분석 로직 (CSV 변환 후 AI 전달)
        full_context = df.to_csv(index=False)
        # ... (이후 질문/답변 로직) ...
    else:
        st.error("❌ 파일을 찾을 수 없어요. 깃허브 업로드 상태를 봐주세요!")

except Exception as e:
    st.error(f"🚨 오빠, 엔진이 또 투정을 부려요: {e}")
    st.info("💡 만약 'not a zip file'이 계속 뜨면, 깃허브에서 파일을 지웠다가 다시 업로드해 보세요!")
