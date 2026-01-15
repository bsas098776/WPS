import streamlit as st
import pandas as pd
import os
from groq import Groq

# 1. 페이지 설정
st.set_page_config(page_title="윤성 실무 AI (파일 매칭 완벽버전)", page_icon="🛡️", layout="wide")

# 2. Groq API 설정 (철벽 필터 🤙)
def get_clean_key():
    raw_key = st.secrets.get("GROQ_API_KEY")
    if not raw_key: return None
    return raw_key.strip().replace("\n", "").replace("\r", "").replace(" ", "").replace('"', "").replace("'", "")

clean_key = get_clean_key()

if clean_key:
    try:
        client = Groq(api_key=clean_key)
        st.sidebar.success("📡 Groq 엔진 연결 상태: 양호")
    except Exception as e:
        st.error(f"🚨 연결 실패: {e}")
        st.stop()
else:
    st.error("🔑 Secrets에 GROQ_API_KEY를 등록해주세요!")
    st.stop()

# 3. 사이드바 - 업무 모드
st.sidebar.title("📂 업무 제어판")
main_menu = st.sidebar.radio("업무 선택", ["WPS (용접 규격)", "TER (트러블 리포트)"])

# 4. [파일 매칭 로직 수정] 선택한 메뉴에 맞는 파일만 찾도록 설정! 🤙
if main_menu == "WPS (용접 규격)":
    st.title("👨‍🏭 WPS 실무 지식 베이스")
    # WPS 관련 파일명 후보들만!
    candidates = ["wps_list.XLSX", "wps_list.xlsx", "wps_list.xlsx.xlsx"]
    target_sheet = 0
else:
    st.title("🛠️ TER 트러블 정밀 분석 시스템")
    # TER 관련 파일명 후보들만!
    candidates = ["ter_list.xlsx.xlsx", "ter_list.xlsx", "ter_list.XLSX", "TER LIST.XLSX"]
    target_sheet = 'TER'

# 현재 선택된 메뉴에 해당하는 파일만 찾습니다!
file_path = next((f for f in candidates if os.path.exists(f)), None)

if file_path:
    try:
        xl = pd.ExcelFile(file_path, engine='openpyxl')
        
        # 시트 이름 확인 후 로드
        if isinstance(target_sheet, str) and target_sheet not in xl.sheet_names:
            df = pd.read_excel(xl, sheet_name=0) # 시트 없으면 첫번째 로드
        else:
            df = pd.read_excel(xl, sheet_name=target_sheet)
            
        st.success(f"✅ {file_path} 로드 완료! (총 {len(df):,}행)")

        # 5. 질문 및 답변 인터페이스
        user_input = st.text_input(f"💬 {main_menu} 최신 데이터 20건을 기반으로 분석합니다. 질문하세요!")

        if user_input:
            with st.status("🚀 데이터 정밀 분석 중...", expanded=True):
                # 최신 20줄만 추출해서 분석 (413 에러 방지 🤙)
                small_df = df.tail(20) 
                context_data = small_df.to_csv(index=False)
                
                response = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "너는 윤성 전문가야. 제공된 데이터를 보고 답해줘."},
                        {"role": "user", "content": f"데이터:\n{context_data}\n\n질문: {user_input}"}
                    ],
                    model="llama-3.3-70b-versatile",
                    temperature=0.1,
                )
                st.info("✨ 분석 결과 (최신 20건 기반)")
                st.write(response.choices[0].message.content)
        
        with st.expander("📊 전체 데이터 보기"):
            st.dataframe(df)
            
    except Exception as e:
        st.error(f"🚨 파일 처리 오류: {e}")
else:
    st.error(f"❌ '{main_menu}' 관련 파일을 찾을 수 없습니다. 파일명이 {candidates} 중 하나인지 확인해주세요!")
