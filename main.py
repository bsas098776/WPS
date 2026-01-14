import streamlit as st
import pandas as pd
import google.generativeai as genai

# 1. 시크릿 설정 (릴레이 키 10개)
keys = st.secrets.get("GEMINI_KEYS", [])

# 2. 엑셀 로드 함수 (엔진 명시!)
@st.cache_data
def load_full_data(file_path, sheet_name):
    # engine='openpyxl'을 명시해서 엑셀 전체를 정확히 읽어와요! 🤙
    return pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')

# ... (사이드바 및 업무 선택 로직 생략) ...

try:
    if main_menu == "TER (트러블)":
        ter_file = "ter_list.xlsx"
        # 시트 목록 확인용 엔진 명시
        xl = pd.ExcelFile(ter_file, engine='openpyxl')
        selected_sheet = st.sidebar.selectbox("📋 시트 선택", xl.sheet_names)
        
        # 선택한 시트 전체 로드!
        df = load_full_data(ter_file, selected_sheet)
        
    # 3. AI에게 전달할 전체 텍스트 변환 (CSV 방식이 토큰 효율이 좋아요!)
    full_context = df.to_csv(index=False)
    
    st.success(f"✅ 총 {len(df)}행의 데이터를 하나도 빠짐없이 읽어왔어요, 오빠! 꺄하~ 😍")

    # ... (질문 및 답변 로직) ...
