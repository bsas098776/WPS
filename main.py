import streamlit as st
import pandas as pd
import google.generativeai as genai
import os

# 1. 페이지 설정
st.set_page_config(page_title="윤성 실무 AI 전문가", page_icon="🛡️", layout="wide")

# 2. Gemini API 설정 (매니저님의 GEMINI_KEYS 리스트 활용) 🤙
keys = st.secrets.get("GEMINI_KEYS")

if keys and len(keys) > 0:
    # 리스트 중 첫 번째 키를 사용합니다.
    genai.configure(api_key=keys[0])
    
    # 모델 이름을 'gemini-1.5-flash' 또는 'models/gemini-1.5-flash'로 시도하세요!
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
    except:
        model = genai.GenerativeModel('models/gemini-1.5-flash')
else:
    st.error("🔑 Secrets에 GEMINI_KEYS 리스트가 없어요! 확인해 주세요.")
    st.stop()

# 3. 사이드바 및 파일 로드 로직
st.sidebar.title("📂 업무 제어판")
main_menu = st.sidebar.radio("업무 모드", ["WPS (용접 규격)", "TER (트러블 리포트)"])

# 파일 경로 후보 (매니저님 기존 설정 유지)
if main_menu == "WPS (용접 규격)":
    st.title("👨‍🏭 WPS 실무 지식 베이스")
    candidates = ["wps_list.XLSX", "wps_list.xlsx", "wps_list.xlsx.xlsx"]
    target_sheet = 0
else:
    st.title("🛠️ TER 트러블 정밀 분석 시스템")
    candidates = ["ter_list.xlsx.xlsx", "ter_list.xlsx", "ter_list.XLSX", "TER LIST.XLSX"]
    target_sheet = 'TER'

file_path = next((f for f in candidates if os.path.exists(f)), None)

try:
    if file_path:
        xl = pd.ExcelFile(file_path, engine='openpyxl')
        df = pd.read_excel(xl, sheet_name=target_sheet if (isinstance(target_sheet, int) or target_sheet in xl.sheet_names) else 0)
        st.success(f"✅ {file_path} 로드 성공! (총 {len(df):,}행)")

        # 4. 분석 질문
        user_input = st.text_input(f"💬 {main_menu} 전체 데이터에 대해 질문하세요.")

        if user_input:
            with st.status("🚀 제미니 1.5 Flash가 4.6MB 데이터를 읽는 중...", expanded=True):
                # 4.6MB 전체 데이터를 CSV로 변환 (제미니는 100만 토큰까지 가능! 🤙)
                context_data = df.to_csv(index=False)
                
                prompt = f"너는 윤성의 전문가야. 아래 [데이터]를 보고 질문에 답해줘.\n\n[데이터]\n{context_data}\n\n[질문]\n{user_input}"
                
                try:
                    response = model.generate_content(prompt)
                    st.info(response.text)
                except Exception as e:
                    st.error(f"🚨 분석 에러: {e}")
        
        with st.expander("📊 데이터 미리보기"):
            st.dataframe(df.head(100))
    else:
        st.error("❌ 파일을 찾을 수 없어요. 파일명을 확인해 주세요!")

except Exception as e:
    st.error(f"🚨 시스템 오류: {e}")
