import streamlit as st
import pandas as pd
import os
from openai import OpenAI 

# 1. 페이지 설정
st.set_page_config(page_title="윤성 실무 AI (GitHub 모델 안정화)", page_icon="🛡️", layout="wide")

# 2. GitHub Models 설정
github_token = st.secrets.get("GITHUB_TOKEN")

if github_token:
    client = OpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=github_token,
    )
else:
    st.error("🔑 Secrets에 GITHUB_TOKEN을 등록해주세요!")
    st.stop()

# 3. 사이드바 업무 선택
st.sidebar.title("📂 업무 제어판")
main_menu = st.sidebar.radio("업무 모드를 선택하세요", ["WPS (용접 규격)", "TER (트러블 리포트)"])

# 4. 파일 로드 (오빠 기존 경로 완벽 유지 🤙)
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
        st.success(f"✅ {file_path} 로드 완료! (총 {len(df):,}행)")

        # 5. 질문 및 답변 인터페이스
        user_input = st.text_input(f"💬 {main_menu} 데이터에 대해 질문하세요.")

        if user_input:
            with st.status("🚀 GitHub AI 엔진 분석 중...", expanded=True):
                # 데이터 1,000줄 전송 🤙
                context_data = df.tail(1000).to_csv(index=False)
                
                # [해결 포인트] 모델 이름을 순차적으로 시도합니다!
                model_candidates = ["Meta-Llama-3.1-70B-Instruct", "gpt-4o", "Llama-3.3-70B-Instruct"]
                success = False
                
                for target_model in model_candidates:
                    try:
                        response = client.chat.completions.create(
                            messages=[
                                {"role": "system", "content": "너는 윤성의 2차전지 장비 전문가야. 제공된 데이터를 바탕으로 친절하게 답해줘."},
                                {"role": "user", "content": f"[데이터]\n{context_data}\n\n[질문]\n{user_input}"}
                            ],
                            model=target_model,
                            temperature=0.2,
                        )
                        st.info(f"✨ 분석 모델: {target_model}")
                        st.write(response.choices[0].message.content)
                        success = True
                        break # 성공하면 루프 탈출!
                    except Exception as e:
                        if "unknown_model" in str(e).lower():
                            continue # 다음 모델로 시도
                        else:
                            st.error(f"🚨 오류 발생 ({target_model}): {e}")
                            break
                
                if not success:
                    st.error("🚨 GitHub에서 사용할 수 있는 모델을 찾지 못했어요. 토큰 권한이나 모델명을 다시 확인해야 해요.")
        
        with st.expander("📊 데이터 미리보기"):
            st.dataframe(df.head(100))
            
    except Exception as e:
        st.error(f"🚨 파일 읽기 오류: {e}")
else:
    st.error("❌ 파일을 찾을 수 없습니다. 파일명을 확인해 주세요!")
