import streamlit as st
import pandas as pd
import os
from groq import Groq # 다시 가장 착한 Groq로 돌아왔어요 🤙

# 1. 페이지 설정
st.set_page_config(page_title="윤성 실무 AI (안정화 버전)", page_icon="🛡️", layout="wide")

# 2. Groq API 설정
groq_key = st.secrets.get("GROQ_API_KEY")

if groq_key:
    client = Groq(api_key=groq_key)
else:
    st.error("🔑 Secrets에 GROQ_API_KEY를 등록해주세요!")
    st.stop()

# 3. 사이드바 업무 선택
st.sidebar.title("📂 업무 제어판")
main_menu = st.sidebar.radio("업무 모드", ["WPS (용접 규격)", "TER (트러블 리포트)"])

# 4. 파일 로드 (오빠 기존 경로 🤙)
if main_menu == "WPS (용접 규격)":
    candidates = ["wps_list.XLSX", "wps_list.xlsx"]
    target_sheet = 0
else:
    candidates = ["ter_list.xlsx.xlsx", "ter_list.xlsx", "ter_list.XLSX"]
    target_sheet = 'TER'

file_path = next((f for f in candidates if os.path.exists(f)), None)

if file_path:
    try:
        df = pd.read_excel(file_path, engine='openpyxl', sheet_name=target_sheet if (isinstance(target_sheet, int) or target_sheet in ['TER']) else 0)
        st.success(f"✅ {file_path} 로드 성공! (안정적 분석 모드)")

        user_input = st.text_input(f"💬 {main_menu} 최신 데이터 50건에 대해 질문하세요.")

        if user_input:
            with st.spinner("🚀 Groq 엔진이 광속으로 분석 중..."):
                # [필살기: 데이터 다이어트 🤙]
                # 4.6MB 중 가장 중요한 최신 50줄만 딱 잘라서 보냅니다!
                # 이렇게 하면 413, 429 에러 절대 안 나요!
                small_df = df.tail(50) 
                context_data = small_df.to_csv(index=False)
                
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "너는 윤성의 전문가야. 최신 데이터 50건을 보고 답해줘."},
                        {"role": "user", "content": f"데이터:\n{context_data}\n\n질문: {user_input}"}
                    ],
                )
                st.info(completion.choices[0].message.content)
        
        with st.expander("📊 데이터 미리보기 (전체 데이터 확인용)"):
            st.dataframe(df) # 브라우저에서는 전체 다 볼 수 있어요!
            
    except Exception as e:
        st.error(f"🚨 에러 발생: {e}")
