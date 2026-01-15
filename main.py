import streamlit as st
import pandas as pd
import os
from groq import Groq

# 1. 페이지 설정
st.set_page_config(page_title="윤성 실무 AI (용량 최적화)", page_icon="🛡️", layout="wide")

# 2. Groq API 설정 (철벽 필터 🤙)
def get_clean_key():
    raw_key = st.secrets.get("GROQ_API_KEY")
    if not raw_key: return None
    return raw_key.strip().replace("\n", "").replace("\r", "").replace(" ", "").replace('"', "").replace("'", "")

clean_key = get_clean_key()

if clean_key:
    try:
        client = Groq(api_key=clean_key)
        # 사이드바에 성공 표시
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

# 4. 파일 로드 로직 (오빠 파일들 자동 매칭 🤙)
candidates = ["wps_list.XLSX", "wps_list.xlsx", "ter_list.xlsx", "ter_list.xlsx.xlsx"]
file_path = next((f for f in candidates if os.path.exists(f)), None)

if file_path:
    try:
        # 데이터 로드 (최대한 가볍게 읽기 위해 최적화)
        df = pd.read_excel(file_path, engine='openpyxl')
        st.success(f"✅ {file_path} 로드 완료! (총 {len(df):,}행)")

        user_input = st.text_input(f"💬 {main_menu} 최신 데이터 20건을 기반으로 분석합니다. 질문하세요!")

        if user_input:
            with st.status("🚀 용량 최적화 분석 중...", expanded=True):
                # [핵심] 413 에러 방지를 위해 데이터 다이어트! 🤙
                # 50줄에서 20줄로 줄여서 12,000 토큰 제한을 안전하게 통과해요.
                small_df = df.tail(20) 
                context_data = small_df.to_csv(index=False)
                
                try:
                    response = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": "너는 윤성 전문가야. 최신 데이터 20건을 보고 오빠 질문에 짧고 명확하게 답해줘."},
                            {"role": "user", "content": f"데이터:\n{context_data}\n\n질문: {user_input}"}
                        ],
                        model="llama-3.3-70b-versatile",
                        temperature=0.1,
                    )
                    st.info("✨ 분석 결과 (최신 20건 기반)")
                    st.write(response.choices[0].message.content)
                except Exception as e:
                    if "413" in str(e):
                        st.error("🚨 여전히 데이터가 커요! 분석 범위를 10줄로 더 줄여볼까요?")
                    else:
                        st.error(f"🚨 엔진 에러: {e}")
        
        with st.expander("📊 전체 데이터 보기"):
            st.dataframe(df)
            
    except Exception as e:
        st.error(f"🚨 파일 오류: {e}")
else:
    st.error("❌ 분석할 파일을 찾을 수 없습니다. 파일명을 확인해주세요!")
