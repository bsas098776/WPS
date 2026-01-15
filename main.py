import streamlit as st
import pandas as pd
import google.generativeai as genai
import os

# 1. 페이지 설정
st.set_page_config(page_title="윤성 실무 AI 전문가", page_icon="🛡️", layout="wide")

# 2. Gemini API 설정 (시크릿 이름: GEMINI_API_KEY)
api_key = st.secrets.get("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
    # 모델 이름 인식을 더 확실하게 하기 위해 예외 처리를 넣었어요! 🤙
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
    except:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
else:
    st.error("🔑 Secrets에 GEMINI_API_KEY를 등록해주세요!")
    st.stop()

# 3. 사이드바 - 업무 모드 선택
st.sidebar.title("📂 업무 제어판")
main_menu = st.sidebar.radio("업무 모드를 선택하세요", ["WPS (용접 규격)", "TER (트러블 리포트)"])

# 4. 파일 로드 (매니저님 기존 경로)
if main_menu == "WPS (용접 규격)":
    st.title("👨‍🏭 WPS 실무 지식 베이스")
    candidates = ["wps_list.XLSX", "wps_list.xlsx"]
    target_sheet = 0
else:
    st.title("🛠️ TER 트러블 정밀 분석 시스템")
    candidates = ["ter_list.xlsx.xlsx", "ter_list.xlsx", "ter_list.XLSX"]
    target_sheet = 'TER'

file_path = next((f for f in candidates if os.path.exists(f)), None)

try:
    if file_path:
        xl = pd.ExcelFile(file_path, engine='openpyxl')
        df = pd.read_excel(xl, sheet_name=target_sheet if (isinstance(target_sheet, int) or target_sheet in xl.sheet_names) else 0)
        st.success(f"✅ {file_path} 로드 성공! (총 {len(df):,}행)")

        # 5. 질문 및 답변
        user_input = st.text_input(f"💬 {main_menu} 전체 내용에 대해 질문하세요.")

        if user_input:
            with st.status("🚀 제미니 1.5 Flash가 데이터를 정밀 분석 중...", expanded=True):
                # 4.6MB 전체 데이터 전송 (100만 토큰 위력! 🤙)
                context_data = df.to_csv(index=False)
                prompt = f"너는 윤성의 전문가야. 아래 [데이터]를 보고 질문에 답해줘.\n\n[데이터]\n{context_data}\n\n[질문]\n{user_input}"
                
                try:
                    response = model.generate_content(prompt)
                    st.info(response.text)
                except Exception as e:
                    if "404" in str(e):
                        st.error("🚨 모델을 찾을 수 없어요. 모델 이름을 다시 확인해 볼게요!")
                    elif "429" in str(e):
                        st.error("🚨 너무 빨리 질문하셨어요! 1분만 쉬었다가 다시 해주세요. 🤙")
                    else:
                        st.error(f"🚨 분석 중 에러 발생: {e}")
        
        with st.expander("📊 데이터 미리보기"):
            st.dataframe(df.head(100))
    else:
        st.error("❌ 파일을 찾을 수 없습니다.")
except Exception as e:
    st.error(f"🚨 시스템 오류: {e}")
