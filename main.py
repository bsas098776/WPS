import streamlit as st
import pandas as pd
import google.generativeai as genai
import os

# 1. 페이지 설정
st.set_page_config(page_title="윤성 실무 AI (제미니 전체분석)", page_icon="🛡️", layout="wide")

# 2. Gemini API 설정 🤙 (오빠 시크릿의 GEMINI_API_KEY를 사용합니다)
api_key = st.secrets.get("GEMINI_API_KEY")

if api_key:
    try:
        genai.configure(api_key=api_key)
        # 404 에러 방지를 위해 가장 확실한 이름표를 붙여줍니다!
        # 만약 이게 안되면 'models/gemini-1.5-flash'로 자동 전환합니다.
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            # 연결 테스트
            _ = model.generate_content("test", generation_config={"max_output_tokens": 1})
        except:
            model = genai.GenerativeModel('models/gemini-1.5-flash')
        
        st.sidebar.success("📡 구글 제미니 1.5 Flash 엔진 연결 성공!")
    except Exception as e:
        st.error(f"🚨 API 연결 실패: {e}")
        st.stop()
else:
    st.error("🔑 Secrets에 GEMINI_API_KEY가 등록되지 않았어요!")
    st.stop()

# 3. 사이드바 업무 선택
st.sidebar.title("📂 업무 제어판")
main_menu = st.sidebar.radio("업무 모드", ["WPS (용접 규격)", "TER (트러블 리포트)"])

# 4. 파일 로드 (오빠의 4.6MB 엑셀 파일들) 🤙
if main_menu == "WPS (용접 규격)":
    st.title("👨‍🏭 WPS 실무 지식 베이스")
    candidates = ["wps_list.XLSX", "wps_list.xlsx", "wps_list.xlsx.xlsx"]
    target_sheet = 0
else:
    st.title("🛠️ TER 트러블 정밀 분석 시스템")
    candidates = ["ter_list.xlsx.xlsx", "ter_list.xlsx", "ter_list.XLSX"]
    target_sheet = 'TER'

file_path = next((f for f in candidates if os.path.exists(f)), None)

if file_path:
    try:
        xl = pd.ExcelFile(file_path, engine='openpyxl')
        df = pd.read_excel(xl, sheet_name=target_sheet if (isinstance(target_sheet, int) or target_sheet in xl.sheet_names) else 0)
        st.success(f"✅ {file_path} 로드 성공! (총 {len(df):,}행)")

        # 5. 질문 및 답변
        user_input = st.text_input(f"💬 {main_menu} 전체 데이터에 대해 질문하세요.")

        if user_input:
            with st.status("🚀 100만 토큰 엔진이 전체 데이터를 읽는 중...", expanded=True):
                # 제미니 1.5 Flash는 4.6MB 전체를 삼킬 수 있어요! 🤙
                context_data = df.to_csv(index=False)
                prompt = f"너는 윤성의 전문가야. 아래 데이터를 보고 오빠의 질문에 답해줘.\n\n[데이터]\n{context_data}\n\n[질문]\n{user_input}"
                
                response = model.generate_content(prompt)
                st.info(response.text)
        
        with st.expander("📊 데이터 미리보기"):
            st.dataframe(df.head(100))
    except Exception as e:
        st.error(f"🚨 시스템 오류: {e}")
else:
    st.error("❌ 분석할 파일을 찾을 수 없습니다. (wps_list.xlsx 또는 ter_list.xlsx)")
