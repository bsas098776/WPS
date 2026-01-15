import streamlit as st
import pandas as pd
import google.generativeai as genai
import os

# 1. 페이지 설정
st.set_page_config(page_title="윤성 실무 AI 전문가", page_icon="🛡️", layout="wide")

# 2. Gemini API 키 설정
keys = st.secrets.get("GEMINI_KEYS", [])

def ask_gemini(prompt, api_keys):
    """Gemini 2.0 Flash 엔진을 호출하여 분석 결과를 반환합니다."""
    for i, key in enumerate(api_keys):
        try:
            genai.configure(api_key=key)
            # 가장 최신 모델인 Gemini 2.0 Flash 적용
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content(prompt)
            return response.text, i + 1
        except Exception as e:
            try:
                model = genai.GenerativeModel('gemini-2.0-flash-exp')
                response = model.generate_content(prompt)
                return response.text, i + 1
            except:
                if "429" in str(e): continue
                else: return f"에러 발생: {e}", None
    return "API 키가 만료되었습니다. 관리자에게 문의하세요.", None

# 3. 사이드바 메뉴
st.sidebar.title("📂 데이터 센터")
main_menu = st.sidebar.radio("업무 모드를 선택하세요", ["WPS (용접 규격)", "TER (트러블 리포트)"])

# 4. 파일 로드 로직
if main_menu == "WPS (용접 규격)":
    candidates = ["wps_list.XLSX", "wps_list.xlsx", "wps_list.xlsx.xlsx"]
else:
    candidates = ["ter_list.xlsx.xlsx", "ter_list.xlsx", "ter_list.XLSX", "TER LIST.XLSX"]

file_path = next((f for f in candidates if os.path.exists(f)), None)

try:
    if file_path:
        # [수정] 매니저님 요청에 따라 최소 용량 기준을 5KB로 설정
        # 5,120 Bytes(5KB) 미만일 때만 업로드 오류로 간주합니다.
        file_size = os.path.getsize(file_path)
        if file_size < 5120: 
            st.error(f"🚨 알림: '{file_path}' 파일 용량이 너무 작습니다 ({file_size} Bytes).")
            st.info("💡 5KB 미만의 파일은 정상적인 엑셀 데이터가 아닐 가능성이 높습니다. GitHub 업로드 상태를 확인해 주세요.")
            st.stop()

        # 엑셀 로드
        xl = pd.ExcelFile(file_path, engine='openpyxl')
        
        if main_menu == "TER (트러블 리포트)":
            st.title("🛠️ TER 트러블 정밀 분석 시스템")
            target_sheet = 'TER'
            df = pd.read_excel(xl, sheet_name=target_sheet if target_sheet in xl.sheet_names else 0)
            st.success(f"✅ TER 데이터 로드 완료! (파일명: {file_path})")
        else:
            st.title("👨‍🏭 WPS 실무 지식 베이스")
            df = pd.read_excel(xl)
            st.success(f"✅ WPS 데이터 로드 완료! (파일명: {file_path})")

        # 5. 질문 및 답변 인터페이스
        user_input = st.text_input(f"💬 {main_menu} 데이터에 대해 질문해 주세요.")

        if user_input:
            with st.status("🚀 Gemini 2.0 엔진이 분석 중입니다...", expanded=True) as status:
                st.write("1. 데이터 컨텍스트 변환 중...")
                full_context = df.to_csv(index=False) 
                
                st.write("2. AI 모델 기반 전문 추론 중...")
                prompt = f"""너는 윤성의 전문가야. 아래 제공된 [데이터 세트]를 참고해서 사용자의 질문에 답변해줘.
                
                [데이터 세트]
                {full_context}
                
                [사용자 질문]
                {user_input}"""
                
                answer, key_num = ask_gemini(prompt, keys)
                
                if key_num:
                    status.update(label=f"✅ 분석 완료! ({key_num}번 엔진 가동)", state="complete", expanded=False)
                    st.markdown("### 🤖 분석 결과")
                    st.info(answer)
                else:
                    status.update(label="❌ 분석 실패", state="error")
                    st.error(answer)
    else:
        st.error(f"❌ 파일을 찾을 수 없습니다. (대상 후보: {candidates})")

except Exception as e:
    st.error(f"🚨 시스템 오류가 발생했습니다: {e}")
