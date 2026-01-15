import streamlit as st
import pandas as pd
import google.generativeai as genai
import os

# 1. 페이지 설정
st.set_page_config(page_title="윤성 실무 AI 전문가", page_icon="🛡️", layout="wide")

# 2. Gemini API 키 설정
keys = st.secrets.get("GEMINI_KEYS", [])

def ask_gemini(prompt, api_keys):
    """엔진별 상세 에러 내용을 수집하여 원인을 파악합니다."""
    error_details = []
    for i, key in enumerate(api_keys):
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content(prompt)
            return response.text, i + 1
        except Exception as e:
            # 구체적인 에러 메시지를 수집합니다.
            error_details.append(f"{i+1}번 키: {str(e)}")
            continue
    
    # 모든 키 실패 시 상세 원인 출력
    full_error_msg = "\n".join(error_details)
    return f"모든 API 키가 응답하지 않습니다. 상세 이유:\n{full_error_msg}", None

# 3. 사이드바 및 파일 로드 (매니저님 기존 설정 유지)
st.sidebar.title("📂 데이터 센터")
main_menu = st.sidebar.radio("업무 모드를 선택하세요", ["WPS (용접 규격)", "TER (트러블 리포트)"])

if main_menu == "WPS (용접 규격)":
    candidates = ["wps_list.XLSX", "wps_list.xlsx", "wps_list.xlsx.xlsx"]
else:
    candidates = ["ter_list.xlsx.xlsx", "ter_list.xlsx", "ter_list.XLSX", "TER LIST.XLSX"]

file_path = next((f for f in candidates if os.path.exists(f)), None)

try:
    if file_path:
        file_size = os.path.getsize(file_path)
        if file_size < 5120: # 5KB 기준
            st.error(f"🚨 알림: '{file_path}' 파일 용량이 너무 작습니다 ({file_size} Bytes).")
            st.stop()

        xl = pd.ExcelFile(file_path, engine='openpyxl')
        df = pd.read_excel(xl, sheet_name='TER' if main_menu == "TER (트러블 리포트)" and 'TER' in xl.sheet_names else 0)
        st.success(f"✅ {main_menu} 데이터 로드 완료! (파일명: {file_path})")

        # 5. 질문 처리
        user_input = st.text_input(f"💬 {main_menu} 데이터에 대해 질문해 주세요.")

        if user_input:
            with st.status("🚀 분석 엔진 가동 중...", expanded=True) as status:
                full_context = df.to_csv(index=False) 
                prompt = f"너는 윤성 전문가야. 아래 데이터를 보고 질문에 답해줘.\n\n[데이터]\n{full_context}\n\n[질문]\n{user_input}"
                
                answer, key_num = ask_gemini(prompt, keys)
                
                if key_num:
                    status.update(label=f"✅ {key_num}번 엔진 분석 완료!", state="complete", expanded=False)
                    st.info(answer)
                else:
                    status.update(label="❌ 분석 실패", state="error")
                    st.error(answer) # 여기서 상세 에러 원인이 출력됩니다!
    else:
        st.error("❌ 파일을 찾을 수 없습니다.")
except Exception as e:
    st.error(f"🚨 시스템 오류: {e}")
