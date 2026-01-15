import streamlit as st
import pandas as pd
import os
from openai import OpenAI 

# 1. 페이지 설정
st.set_page_config(page_title="윤성 실무 AI (Kimi 128k 엔진)", page_icon="🐼", layout="wide")

# 2. Kimi API 설정 (Streamlit Secrets에서 KIMI_API_KEY를 가져옵니다)
kimi_key = st.secrets.get("KIMI_API_KEY")

if kimi_key:
    client = OpenAI(
        base_url="https://api.moonshot.cn/v1", # Kimi API의 표준 주소예요!
        api_key=kimi_key,
    )
else:
    st.error("🔑 Secrets에 KIMI_API_KEY를 등록해주세요! (sk-... 형태)")
    st.stop()

# 3. 사이드바 업무 선택
st.sidebar.title("📂 업무 제어판")
main_menu = st.sidebar.radio("업무 모드 선택", ["WPS (용접 규격)", "TER (트러블 리포트)"])

# 4. 파일 로드 (오빠의 파일 후보들 🤙)
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
        # 지정된 시트가 없으면 첫 번째 시트를 로드합니다 🤙
        sheet_name = target_sheet if (isinstance(target_sheet, int) or target_sheet in xl.sheet_names) else 0
        df = pd.read_excel(xl, sheet_name=sheet_name)
        st.success(f"✅ {file_path} 로드 성공! (총 {len(df):,}행)")

        # 5. 질문 및 답변
        user_input = st.text_input(f"💬 Kimi 128k 엔진이 대기 중입니다. 무엇이든 물어보세요!")

        if user_input:
            with st.status("🚀 Kimi가 4.6MB 데이터를 정밀 분석 중입니다...", expanded=True):
                # [Kimi의 필살기] 데이터 전체를 CSV로 변환해서 한 번에 보냅니다! 🤙
                # 128k 토큰은 엑셀 수만 줄도 한 번에 읽을 수 있는 크기예요.
                context_data = df.to_csv(index=False)
                
                try:
                    response = client.chat.completions.create(
                        model="moonshot-v1-128k", # 대용량 분석용 끝판왕 모델!
                        messages=[
                            {"role": "system", "content": "너는 윤성의 2차전지 장비 전문가야. 제공된 전체 데이터를 바탕으로 오빠의 질문에 친절하고 정확하게 답해줘."},
                            {"role": "user", "content": f"[전체 데이터]\n{context_data}\n\n[질문]\n{user_input}"}
                        ],
                        temperature=0.3, # 답변의 일관성을 위해 낮게 설정!
                    )
                    st.info("✨ Kimi의 분석 결과")
                    st.write(response.choices[0].message.content)
                except Exception as e:
                    st.error(f"🚨 Kimi 엔진 호출 에러: {e}")
        
        with st.expander("📊 전체 데이터 미리보기"):
            st.dataframe(df.head(100))
            
    except Exception as e:
        st.error(f"🚨 파일 로드 중 오류 발생: {e}")
else:
    st.error(f"❌ '{main_menu}' 파일을 찾을 수 없습니다. 파일명을 다시 확인해 주세요!")
