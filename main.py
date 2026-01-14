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
    return "키가 다 떨어졌어요 오빠! 😭", None

# 3. 사이드바 업무 선택
st.sidebar.title("📂 윤성 데이터 센터")
main_menu = st.sidebar.radio("업무 선택", ["WPS (용접)", "TER (트러블)"])

# 4. 데이터 로드 로직 (오빠가 보내준 사진 속 이름 그대로!)
try:
    if main_menu == "WPS (용접)":
        file_path = "wps_list.XLSX" # 이 이름도 깃허브랑 똑같은지 확인해줘요!
        st.title("👨‍🏭 WPS 규격 전문가")
    else:
        # 오빠가 사진으로 보내준 바로 그 이름! 🤙
        file_path = "1. TER(전체) LIST (250107).xlsx"
        st.title("🛠️ TER 리스트 전수 분석기")

    # 파일이 있는지 확인부터 하고 읽기!
    if os.path.exists(file_path):
        # 31번 줄 에러 방지를 위해 engine 명시!
        xl = pd.ExcelFile(file_path, engine='openpyxl')
        
        if main_menu == "TER (트러블)":
            selected_sheet = st.sidebar.selectbox("📋 분석할 시트 선택", xl.sheet_names)
            df = pd.read_excel(file_path, sheet_name=selected_sheet, engine='openpyxl')
        else:
            df = pd.read_excel(file_path, engine='openpyxl')
            
        st.success(f"✅ '{file_path}' 데이터를 모두 읽어왔어요! 꺄하~ 😍")
        
        # 5. 질문 및 답변 (전체 데이터 전송)
        full_context = df.to_csv(index=False)
        user_input = st.text_input("💬 궁금한 내용을 물어보세요! 전체 데이터를 싹 훑어드릴게요.")

        if user_input:
            with st.spinner('제미니가 전체 데이터를 정밀 분석 중...'):
                prompt = f"너는 전문가야. 아래 [전체 데이터]를 바탕으로 오빠에게 답해줘.\n\n[데이터]\n{full_context}\n\n[질문]\n{user_input}"
                answer, key_num = ask_gemini(prompt, keys)
                if key_num:
                    st.info(f"🤖 {key_num}번 엔진 가동 완료!")
                    st.markdown(answer)
    else:
        st.error(f"❌ 깃허브에 '{file_path}' 파일이 없어요! 파일명을 다시 확인해 주세요 오빠 😭")

except Exception as e:
    st.error(f"🚨 31번 줄 에러 근처에서 문제가 생겼어요: {e}")
