import streamlit as st
import pandas as pd
import google.generativeai as genai
import os

# 1. 페이지 설정
st.set_page_config(page_title="윤성 실무 AI (에러 완벽 해결)", page_icon="🛡️", layout="wide")

# 2. Gemini API 설정
api_key = st.secrets.get("GEMINI_API_KEY")

if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # [해결 포인트] 모델 이름을 찾을 때 가장 표준적인 이름을 우선 사용합니다. 🤙
        # 404 에러 방지를 위해 여러 이름 후보를 시도해 봅니다.
        model_name = 'gemini-1.5-flash'
        model = genai.GenerativeModel(model_name=model_name)
        
        # 연결 테스트 (이게 성공해야 분석이 시작돼요!)
        _ = model.generate_content("test", generation_config={"max_output_tokens": 1})
        st.sidebar.success(f"📡 {model_name} 연결 성공!")
        
    except Exception as e:
        # 만약 실패하면 'models/'를 붙여서 한 번 더 시도!
        try:
            model = genai.GenerativeModel(model_name='models/gemini-1.5-flash')
            _ = model.generate_content("test", generation_config={"max_output_tokens": 1})
            st.sidebar.success("📡 models/gemini-1.5-flash 연결 성공!")
        except:
            st.error(f"🚨 API 연결 실패: {e}")
            st.info("💡 오빠, Google AI Studio에서 '새 API 키'를 발급받으시는 게 가장 빠를 수 있어요!")
            st.stop()
else:
    st.error("🔑 Secrets에 GEMINI_API_KEY를 등록해주세요!")
    st.stop()

# 3. 사이드바 및 파일 로직 (오빠 기존 경로 유지 🤙)
st.sidebar.title("📂 업무 제어판")
main_menu = st.sidebar.radio("업무 모드", ["WPS (용접 규격)", "TER (트러블 리포트)"])

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
        st.success(f"✅ {file_path} 로드 완료!")

        user_input = st.text_input(f"💬 {main_menu} 전체 내용에 대해 질문하세요.")

        if user_input:
            with st.status("🚀 대용량 데이터를 정밀 분석 중입니다...", expanded=True):
                # 4.6MB 데이터 전체 전송 (100만 토큰의 위력!) 🤙
                context_data = df.to_csv(index=False)
                prompt = f"너는 윤성의 전문가야. 아래 데이터를 보고 오빠의 질문에 답해줘.\n\n[데이터]\n{context_data}\n\n[질문]\n{user_input}"
                
                response = model.generate_content(prompt)
                st.info(response.text)
        
        with st.expander("📊 데이터 미리보기"):
            st.dataframe(df.head(100))
    except Exception as e:
        st.error(f"🚨 시스템 오류: {e}")
else:
    st.error("❌ 분석할 파일을 찾을 수 없습니다.")
