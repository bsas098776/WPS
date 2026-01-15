import streamlit as st
import pandas as pd
import google.generativeai as genai
import os

# 1. 페이지 설정
st.set_page_config(page_title="윤성 실무 AI 전문가 (안정화 버전)", page_icon="🛡️", layout="wide")

# 2. Gemini API 설정
api_key = st.secrets.get("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
    
    # [핵심 수정] 404 에러를 피하기 위해 가동 가능한 모델을 순차적으로 탐색합니다! 🤙
    available_models = ['gemini-1.5-flash', 'gemini-1.0-pro', 'gemini-pro']
    model = None
    
    for model_name in available_models:
        try:
            model = genai.GenerativeModel(model_name)
            # 테스트 호출로 모델이 정말 있는지 확인
            test_res = model.generate_content("test", generation_config={"max_output_tokens": 1})
            st.sidebar.success(f"📡 연결 성공: {model_name}")
            break
        except:
            continue
            
    if model is None:
        st.error("🚨 사용 가능한 제미니 모델을 찾을 수 없습니다. API 키 권한을 확인해 주세요.")
        st.stop()
else:
    st.error("🔑 Secrets에 GEMINI_API_KEY를 등록해주세요!")
    st.stop()

# 3. 사이드바 업무 선택
st.sidebar.title("📂 업무 제어판")
main_menu = st.sidebar.radio("업무 모드", ["WPS (용접 규격)", "TER (트러블 리포트)"])

# 4. 파일 로드
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
        st.success(f"✅ {file_path} 로드 완료! (총 {len(df):,}행)")

        # 5. 질문 및 답변
        user_input = st.text_input(f"💬 {main_menu}에 대해 질문하세요.")

        if user_input:
            with st.status("🚀 데이터를 분석 중입니다...", expanded=True):
                # [안전 장치] 1.0 Pro 모델일 경우를 대비해 데이터를 200줄로 적절히 조절합니다. 🤙
                # 4.6MB 전체가 안 되면 여기서부터 조금씩 줄여가며 최적점을 찾을 거예요!
                refined_df = df.tail(200) 
                context_data = refined_df.to_csv(index=False)
                
                prompt = f"너는 윤성의 전문가야. 아래 데이터를 보고 오빠의 질문에 답해줘.\n\n[데이터]\n{context_data}\n\n[질문]\n{user_input}"
                
                try:
                    response = model.generate_content(prompt)
                    st.info(response.text)
                except Exception as e:
                    st.error(f"🚨 분석 에러: {e}")
        
        with st.expander("📊 데이터 미리보기"):
            st.dataframe(df.head(100))
    else:
        st.error("❌ 분석할 엑셀 파일을 찾을 수 없습니다.")
except Exception as e:
    st.error(f"🚨 시스템 오류: {e}")
