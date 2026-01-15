import streamlit as st
import pandas as pd
import google.generativeai as genai
import os

# 1. 페이지 설정
st.set_page_config(page_title="윤성 실무 AI (전체 데이터 분석)", page_icon="🛡️", layout="wide")

# 2. Gemini API 설정 및 모델 자동 탐색 🤙
api_key = st.secrets.get("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
    
    # 404 에러 방지를 위해 여러 이름 후보를 순차적으로 시도합니다!
    model_names = [
        'gemini-1.5-flash',
        'models/gemini-1.5-flash',
        'gemini-1.5-flash-latest'
    ]
    
    model = None
    connected_name = ""
    
    for name in model_names:
        try:
            temp_model = genai.GenerativeModel(name)
            # 실제로 작동하는지 가벼운 테스트
            _ = temp_model.generate_content("ping", generation_config={"max_output_tokens": 1})
            model = temp_model
            connected_name = name
            break
        except:
            continue
            
    if model:
        st.sidebar.success(f"📡 연결 성공: {connected_name}")
    else:
        st.error("🚨 제미니 1.5 Flash 모델을 찾을 수 없습니다. API 키를 새로 발급받아주세요!")
        st.stop()
else:
    st.error("🔑 Secrets에 GEMINI_API_KEY를 등록해주세요!")
    st.stop()

# 3. 사이드바 - 업무 모드 선택
st.sidebar.title("📂 업무 제어판")
main_menu = st.sidebar.radio("업무 모드를 선택하세요", ["WPS (용접 규격)", "TER (트러블 리포트)"])

# 4. 파일 로드 (매니저님 기존 파일명 후보들 🤙)
if main_menu == "WPS (용접 규격)":
    st.title("👨‍🏭 WPS 실무 지식 베이스")
    candidates = ["wps_list.XLSX", "wps_list.xlsx", "wps_list.xlsx.xlsx"]
    target_sheet = 0
else:
    st.title("🛠️ TER 트러블 정밀 분석 시스템")
    candidates = ["ter_list.xlsx.xlsx", "ter_list.xlsx", "ter_list.XLSX", "TER LIST.XLSX"]
    target_sheet = 'TER'

file_path = next((f for f in candidates if os.path.exists(f)), None)

try:
    if file_path:
        xl = pd.ExcelFile(file_path, engine='openpyxl')
        
        # 시트 이름 확인 후 로드
        if isinstance(target_sheet, str) and target_sheet not in xl.sheet_names:
            df = pd.read_excel(xl, sheet_name=0)
        else:
            df = pd.read_excel(xl, sheet_name=target_sheet)
            
        st.success(f"✅ {file_path} 로드 완료! (총 {len(df):,}행)")

        # 5. 질문 및 답변 인터페이스
        user_input = st.text_input(f"💬 {main_menu} 전체 데이터에 대해 질문해 주세요.")

        if user_input:
            with st.status("🚀 100만 토큰 엔진이 4.6MB 데이터를 정밀 분석 중...", expanded=True) as status:
                # [전체 데이터 전송 전략] 🤙
                # 제미니 1.5 Flash는 100만 토큰까지 가능하므로, 데이터를 통째로 CSV로 변환합니다.
                context_data = df.to_csv(index=False)
                
                prompt = f"""너는 윤성의 2차전지 장비 전문가야. 
                아래 제공된 [전체 데이터]를 꼼꼼히 읽고, 오빠의 질문에 전문적이고 친절하게 답해줘.
                
                [전체 데이터]
                {context_data}
                
                [질문]
                {user_input}"""
                
                try:
                    response = model.generate_content(prompt)
                    status.update(label="✅ 분석 완료!", state="complete", expanded=False)
                    st.info(response.text)
                except Exception as e:
                    if "429" in str(e):
                        st.error("🚨 너무 빨리 질문하셨어요! 1분만 쉬었다가 다시 해주세요. 🤙")
                    else:
                        st.error(f"🚨 분석 중 에러가 발생했어요: {e}")
                
        # 데이터 미리보기
        with st.expander("📊 데이터 미리보기 (상위 100개)"):
            st.dataframe(df.head(100))
            
    else:
        st.error(f"❌ '{main_menu}' 파일을 찾을 수 없습니다. 경로를 확인해 주세요!")

except Exception as e:
    st.error(f"🚨 시스템 오류: {e}")
