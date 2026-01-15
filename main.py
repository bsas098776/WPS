import streamlit as st
import pandas as pd
import os
from groq import Groq

# 1. 페이지 설정
st.set_page_config(page_title="윤성 실무 AI (Groq 안정화)", page_icon="🛡️", layout="wide")

# 2. Groq API 설정 (철벽 방어 모드 🤙)
# 시크릿에서 가져온 키의 줄바꿈, 공백을 싹 지워서 401 에러를 원천 차단해요!
raw_key = st.secrets.get("GROQ_API_KEY")

if raw_key:
    # 401 에러 방지를 위해 키를 아주 깨끗하게 다듬어줍니다
    clean_key = raw_key.strip().replace("\n", "").replace("\r", "").replace(" ", "").strip('"').strip("'")
    try:
        client = Groq(api_key=clean_key)
    except Exception as e:
        st.error(f"🚨 Groq 초기화 실패: {e}")
        st.stop()
else:
    st.error("🔑 Secrets에 GROQ_API_KEY를 한 줄로 예쁘게 등록해주세요!")
    st.stop()

# 3. 사이드바 - 업무 모드 선택
st.sidebar.title("📂 업무 제어판")
main_menu = st.sidebar.radio("업무 모드를 선택하세요", ["WPS (용접 규격)", "TER (트러블 리포트)"])

# 4. 파일 로드 (오빠의 4.6MB 파일들 자동 탐색 🤙)
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
        # 엑셀 로드
        xl = pd.ExcelFile(file_path, engine='openpyxl')
        # 시트가 있는지 확인 후 로드
        if isinstance(target_sheet, str) and target_sheet not in xl.sheet_names:
            df = pd.read_excel(xl, sheet_name=0)
        else:
            df = pd.read_excel(xl, sheet_name=target_sheet)
            
        st.success(f"✅ {file_path} 로드 완료! (총 {len(df):,}행)")

        # 5. 질문 및 답변 인터페이스
        user_input = st.text_input(f"💬 {main_menu} 최신 데이터에 대해 질문하세요.")

        if user_input:
            with st.status("🚀 Groq Llama-3.3 엔진이 분석 중...", expanded=True):
                # [중요] 413 토큰 에러 방지를 위해 최신 50줄만 분석합니다! 🤙
                # 4.6MB 전체는 나중에 유료 모델로 시도하고, 일단은 에러 없는 분석이 우선!
                context_df = df.tail(50) 
                context_data = context_df.to_csv(index=False)
                
                try:
                    response = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": "너는 윤성의 2차전지 장비 전문가야. 제공된 최신 50건의 데이터를 보고 오빠의 질문에 친절하게 답해줘."},
                            {"role": "user", "content": f"[최신 데이터]\n{context_data}\n\n[질문]\n{user_input}"}
                        ],
                        model="llama-3.3-70b-versatile",
                        temperature=0.2,
                    )
                    st.info("✨ 분석 결과 (최신 50건 기반)")
                    st.write(response.choices[0].message.content)
                except Exception as e:
                    st.error(f"🚨 Groq 엔진 에러: {e}")
        
        with st.expander("📊 데이터 미리보기 (전체 데이터 확인용)"):
            st.dataframe(df) # 브라우저 상에서는 전체 다 볼 수 있어요!
            
    except Exception as e:
        st.error(f"🚨 파일 읽기 오류: {e}")
else:
    st.error(f"❌ '{main_menu}' 파일을 찾을 수 없습니다. 파일명을 확인해 주세요!")
