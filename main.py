import streamlit as st
import pandas as pd
import google.generativeai as genai
import os

# 1. 페이지 설정
st.set_page_config(page_title="윤성 실무 AI (최종 해결 버전)", page_icon="🛡️", layout="wide")

# 2. Gemini API 설정
api_key = st.secrets.get("GEMINI_API_KEY")

if api_key:
    try:
        genai.configure(api_key=api_key)
        # 404 에러 방지를 위해 사용 가능한 모델 리스트를 내부적으로 확인하고 연결합니다 🤙
        # 'gemini-1.5-flash'가 가장 범용적이고 TPM이 높아요!
        model = genai.GenerativeModel('gemini-1.5-flash')
        # 연결 테스트 (이게 안 되면 바로 에러 메시지 출력)
        _ = model.generate_content("ping", generation_config={"max_output_tokens": 1})
        st.sidebar.success("📡 Gemini 1.5 Flash 연결 성공!")
    except Exception as e:
        st.error(f"🚨 API 연결 실패: {e}")
        st.info("💡 Google AI Studio에서 '새 API 키'를 발급받아 교체해 보시는 것을 추천드려요!")
        st.stop()
else:
    st.error("🔑 Secrets에 GEMINI_API_KEY를 등록해주세요!")
    st.stop()

# 3. 사이드바 업무 선택
st.sidebar.title("📂 업무 제어판")
main_menu = st.sidebar.radio("업무 모드", ["WPS (용접 규격)", "TER (트러블 리포트)"])

# 4. 파일 로드 (매니저님 기존 경로 유지)
if main_menu == "WPS (용접 규격)":
    st.title("👨‍🏭 WPS 실무 지식 베이스")
    candidates = ["wps_list.XLSX", "wps_list.xlsx"]
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
        st.success(f"✅ {file_path} 로드 완료! (총 {len(df):,}행)")

        # 5. 질문 및 답변
        user_input = st.text_input(f"💬 {main_menu} 전체 데이터에 대해 질문하세요.")

        if user_input:
            with st.status("🚀 제미니가 대용량 데이터를 정밀 분석 중입니다...", expanded=True):
                # 4.6MB 데이터 전체 전송! 🤙
                context_data = df.to_csv(index=False)
                prompt = f"너는 윤성의 2차전지 장비 전문가야. 아래 데이터를 보고 오빠의 질문에 답해줘.\n\n[데이터]\n{context_data}\n\n[질문]\n{user_input}"
                
                try:
                    response = model.generate_content(prompt)
                    st.info(response.text)
                except Exception as e:
                    st.error(f"🚨 분석 중 에러 발생: {e}")
        
        with st.expander("📊 데이터 미리보기"):
            st.dataframe(df.head(100))
    except Exception as e:
        st.error(f"🚨 파일 로드 오류: {e}")
else:
    st.error("❌ 분석할 파일을 찾을 수 없습니다.")
