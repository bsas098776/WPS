import streamlit as st
import pandas as pd
import os
from openai import OpenAI # GitHub Models는 OpenAI 형식을 써요! 🤙

# 1. 페이지 설정
st.set_page_config(page_title="윤성 실무 AI (GitHub 모델 버전)", page_icon="🛡️", layout="wide")

# 2. GitHub Models 설정
# Secrets에 GITHUB_TOKEN 이라는 이름으로 PAT를 등록해주세요!
github_token = st.secrets.get("GITHUB_TOKEN")

if github_token:
    client = OpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=github_token,
    )
else:
    st.error("🔑 Secrets에 GITHUB_TOKEN을 등록해주세요!")
    st.stop()

# 3. 사이드바 및 파일 로직
st.sidebar.title("📂 업무 제어판")
main_menu = st.sidebar.radio("업무 모드", ["WPS (용접 규격)", "TER (트러블 리포트)"])

# 파일 경로 (오빠 기존 설정 그대로! 🤙)
if main_menu == "WPS (용접 규격)":
    candidates = ["wps_list.XLSX", "wps_list.xlsx"]
    target_sheet = 0
else:
    candidates = ["ter_list.xlsx.xlsx", "ter_list.xlsx", "ter_list.XLSX"]
    target_sheet = 'TER'

file_path = next((f for f in candidates if os.path.exists(f)), None)

if file_path:
    try:
        xl = pd.ExcelFile(file_path, engine='openpyxl')
        df = pd.read_excel(xl, sheet_name=target_sheet if (isinstance(target_sheet, int) or target_sheet in xl.sheet_names) else 0)
        st.success(f"✅ {file_path} 로드 성공!")

        user_input = st.text_input(f"💬 {main_menu} 전체 내용에 대해 질문하세요.")

        if user_input:
            with st.status("🚀 GitHub Llama-3.1-70B 엔진 가동 중...", expanded=True):
                # GitHub Llama 모델은 컨텍스트가 128k로 넉넉해요!
                # 4.6MB 중 핵심 데이터 1,000줄 정도는 넉넉히 들어갑니다 🤙
                context_data = df.tail(1000).to_csv(index=False)
                
                response = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "너는 윤성의 전문가야. 데이터를 보고 오빠의 질문에 답해줘."},
                        {"role": "user", "content": f"데이터:\n{context_data}\n\n질문: {user_input}"}
                    ],
                    model="meta-llama-3.1-70b", # GitHub에서 제공하는 강력한 모델!
                    temperature=0.2,
                )
                st.info(response.choices[0].message.content)
        
        with st.expander("📊 데이터 미리보기"):
            st.dataframe(df.head(100))
    except Exception as e:
        st.error(f"🚨 에러 발생: {e}")
else:
    st.error("❌ 분석할 파일을 찾을 수 없습니다.")
