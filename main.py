import streamlit as st
import pandas as pd
import os
import google.generativeai as genai
import re

# 1. 페이지 설정
st.set_page_config(page_title="윤성 AI (정밀 검색 모드)", page_icon="🛡️", layout="wide")

# 2. Gemini API 설정
def get_clean_key():
    raw_key = st.secrets.get("GEMINI_API_KEY")
    if not raw_key: return None
    return raw_key.strip().replace("\n", "").replace("\r", "").replace(" ", "").strip('"').strip("'")

clean_key = get_clean_key()
if clean_key:
    genai.configure(api_key=clean_key)
    model = genai.GenerativeModel('gemini-2.0-flash') 
else:
    st.error("🔑 Secrets에 GEMINI_API_KEY를 등록해주세요!")
    st.stop()

# 3. 사이드바 업무 선택
st.sidebar.title("📂 업무 제어판")
main_menu = st.sidebar.radio("업무 선택", ["WPS (용접 규격)", "TER (트러블 리포트)"])

# --- [ 💖 이미지 업로드 방식 비서 추가 부분 🤙✨ ] ---
with st.sidebar:
    # 위치를 더 아래로 안정감 있게 내렸어요!
    st.container(height=350, border=False) 
    
    # 오빠! 깃허브에 올린 'assistant.png' 파일을 직접 불러와요. 
    # 외부 링크가 아니라서 이제 절대 안 깨질 거예요! 꺄하~ 😍
    if os.path.exists("assistant.png"):
        st.image("assistant.png", width=220)
    else:
        # 파일이 없을 때를 대비한 귀여운 아이콘
        st.write("👩‍💼 (이미지를 업로드 해주세요!)")
    
    # 사각형 문구 (오빠 취향에 맞춰 더 화사하게!)
    st.markdown("""
        <div style="
            background-color: #ffffff; 
            padding: 10px; 
            border-radius: 15px; 
            text-align: center;
            border: 2px solid #ffdeeb;
            box-shadow: 0px 4px 12px rgba(255, 192, 203, 0.4);
            margin-top: -10px;
        ">
            <span style="color: #ff4b91; font-weight: bold; font-size: 15px;">
                ✨ 업무 어시스턴트 ✨
            </span>
        </div>
    """, unsafe_allow_html=True)
# ---------------------------------------------------

# [이하 4번부터의 데이터 처리 로직은 오빠의 기존 코드와 동일해요!]
if main_menu == "WPS (용접 규격)":
    st.title("👨‍🏭 WPS 실무 지식 베이스")
    candidates = ["wps_list.XLSX", "wps_list.xlsx"]
    target_sheet = 0
else:
    st.title("🛠️ TER 트러블 정밀 분석 시스템")
    candidates = ["ter_list.xlsx.xlsx", "ter_list.xlsx", "ter_list.XLSX", "TER LIST.XLSX"]
    target_sheet = 'TER'

file_path = next((f for f in candidates if os.path.exists(f)), None)

if file_path:
    try:
        df = pd.read_excel(file_path, sheet_name=target_sheet if (main_menu == "WPS" or target_sheet == 0) else 'TER', engine='openpyxl')
        st.success(f"✅ {file_path} 로드 완료! (총 {len(df)}행)")
        # ... (이하 생략)
    except Exception as e:
        st.error(f"🚨 파일 로드 에러: {e}")
