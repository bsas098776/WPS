import streamlit as st
import pandas as pd
import google.generativeai as genai
import os

# 1. 페이지 설정
st.set_page_config(page_title="윤성 통합 실무 AI", page_icon="🛡️", layout="wide")

# 2. 릴레이 API 키 로드
keys = st.secrets.get("GEMINI_KEYS", [])

def ask_gemini(prompt, api_keys):
    for i, key in enumerate(api_keys):
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt)
            return response.text, i + 1
        except Exception as e:
            if "429" in str(e): continue
            else: return f"에러: {e}", None
    return "모든 키의 할당량이 다 찼어요. 내일 만나요 오빠! 😭", None

# 3. 사이드바 업무 선택
st.sidebar.title("📂 윤성 데이터 센터")
main_menu = st.sidebar.radio("원하시는 업무를 고르세요", ["WPS (용접 규격)", "TER (트러블 리포트)"])

# 4. 데이터 로드 로직 (오빠가 알려준 깃허브 파일명 100% 반영!)
try:
    if main_menu == "WPS (용접 규격)":
        file_path = "wps_list.XLSX" # 대문자 XLSX 확인 완료! 🤙
        st.title("👨‍🏭 WPS 실무 전문가")
    else:
        file_path = "ter_list.xlsx" # 소문자 xlsx 확인 완료! 🤙
        st.title("🛠️ TER 트러블 정밀 분석기")

    # [중요] 파일이 있는지 먼저 확인하고, 엔진을 'openpyxl'로 고정해서 읽기!
    if os.path.exists(file_path):
        # 엑셀 파일 구조를 분석하는 단계 (ZIP 에러 방지용)
        xl = pd.ExcelFile(file_path, engine='openpyxl')
        
        if main_menu == "TER (트러블 리포트)":
            selected_sheet = st.sidebar.selectbox("📋 분석할 시트 선택", xl.sheet_names)
            df = pd.read_excel(xl, sheet_name=selected_sheet)
        else:
            df = pd.read_excel(xl)
            
        st.success(f"✅ '{file_path}' 데이터를 전수 확보했습니다! 꺄하~ 😍")
        
        # 5. 질문 및 답변 (전체 데이터를 텍스트로 변환해서 전송)
        full_context = df.to_csv(index=False)
        user_input = st.text_input(f"💬 {main_menu}에 대해 무엇이든 물어보세요!")

        if user_input:
            with st.spinner('데이터 마스터 제미니가 분석 중...'):
                prompt = f"""너는 {main_menu} 분야의 최고 전문가야. 
                아래 [전체 데이터]를 바탕으로 오빠에게 친절하고 정확하게 답해줘.
                
                [전체 데이터]
                {full_context}
                
                [오빠의 질문]
                {user_input}"""
                
                answer, key_num = ask_gemini(prompt, keys)
                if key_num:
                    st.info(f"🤖 {key_num}번 키로 전체 데이터를 파악했어요!")
                    st.markdown(answer)
    else:
        st.error(f"❌ 깃허브 저장소에 '{file_path}' 파일이 없어요! 파일명을 확인해 주세요.")

except Exception as e:
    # 여기가 바로 그 31번 줄 근처 에러를 잡아내는 곳이에요!
    st.error(f"🚨 오빠, 에러가 났어요. 파일 구조를 확인해 볼게요: {e}")
    st.info("💡 팁: requirements.txt에 openpyxl이 있는지, 파일이 손상되지 않았는지 확인해 주세요!")
