import streamlit as st
import pandas as pd
import google.generativeai as genai
import os

# 1. 페이지 설정 (브라우저 탭 제목 및 아이콘)
st.set_page_config(page_title="윤성 실무 AI 전문가", page_icon="🛡️", layout="wide")

# 2. Gemini API 키 설정 (Streamlit Secrets 활용)
keys = st.secrets.get("GEMINI_KEYS", [])

def ask_gemini(prompt, api_keys):
    """제미니 엔진을 호출하여 답변을 생성합니다."""
    for i, key in enumerate(api_keys):
        try:
            genai.configure(api_key=key)
            # 가장 빠르고 지능적인 Gemini 2.0 Flash 모델 적용
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content(prompt)
            return response.text, i + 1
        except Exception as e:
            # 예외 상황 발생 시 다음 키로 전환 시도
            try:
                model = genai.GenerativeModel('gemini-2.0-flash-exp')
                response = model.generate_content(prompt)
                return response.text, i + 1
            except:
                if "429" in str(e): continue
                else: return f"에러 발생: {e}", None
    return "현재 사용 가능한 API 키가 모두 만료되었습니다. 관리자에게 문의하세요. 😭", None

# 3. 사이드바 메뉴 구성
st.sidebar.title("📂 데이터 센터")
main_menu = st.sidebar.radio("업무 모드를 선택하세요", ["WPS (용접 규격)", "TER (트러블 리포트)"])

# 4. 파일 로드 및 파일명 최적화
if main_menu == "WPS (용접 규격)":
    candidates = ["wps_list.XLSX", "wps_list.xlsx", "wps_list.xlsx.xlsx"]
else:
    candidates = ["ter_list.xlsx.xlsx", "ter_list.xlsx", "ter_list.XLSX", "TER LIST.XLSX"]

# 후보군 중 실제 존재하는 파일을 탐색합니다.
file_path = next((f for f in candidates if os.path.exists(f)), None)

try:
    if file_path:
        # 파일 무결성 체크 (용량이 너무 작으면 껍데기 파일로 간주)
        file_size = os.path.getsize(file_path)
        if file_size < 10000: # 10KB 미만 방어
            st.error(f"🚨 알림: '{file_path}' 파일 용량이 비정상적으로 작습니다 ({file_size} Bytes).")
            st.info("💡 GitHub 업로드 과정에서 파일이 누락되었을 수 있습니다. 웹에서 원본 파일을 다시 업로드해 주세요.")
            st.stop()

        # 엑셀 데이터 읽기
        xl = pd.ExcelFile(file_path, engine='openpyxl')
        
        if main_menu == "TER (트러블 리포트)":
            st.title("🛠️ TER 트러블 정밀 분석 시스템")
            # [자동화] 'TER' 시트가 존재하면 자동으로 선택합니다.
            target_sheet = 'TER'
            if target_sheet in xl.sheet_names:
                df = pd.read_excel(xl, sheet_name=target_sheet)
                st.success(f"✅ '{file_path}'의 [{target_sheet}] 시트를 성공적으로 로드했습니다! 🤙")
            else:
                df = pd.read_excel(xl, sheet_name=0)
                st.warning(f"⚠️ '{target_sheet}' 시트를 찾을 수 없어 첫 번째 시트를 로드했습니다.")
        else:
            st.title("👨‍🏭 WPS 실무 지식 베이스")
            df = pd.read_excel(xl)
            st.success(f"✅ WPS 데이터 로드 완료! 분석 준비가 되었습니다. 😍")

        # 5. 질문 및 답변 인터페이스
        user_input = st.text_input(f"💬 {main_menu} 데이터에 대해 궁금한 점을 입력해 주세요.")

        if user_input:
            with st.status("🚀 Gemini 2.0 엔진이 데이터를 정밀 분석 중입니다...", expanded=True) as status:
                st.write("1. 엑셀 데이터를 지능형 컨텍스트로 변환 중...")
                full_context = df.to_csv(index=False) 
                
                st.write("2. 최신 AI 모델에 데이터 주입 및 추론 중...")
                prompt = f"""너는 2차전지 장비 전문 기업 '윤성'의 숙련된 전문가야.
                아래 제공된 [데이터 세트]를 기반으로 사용자의 질문에 전문적이고 친절하게 답변해줘.
                
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
        st.error(f"❌ 파일을 찾을 수 없습니다. 경로와 파일명을 확인해 주세요. (후보: {candidates})")

except Exception as e:
    st.error(f"🚨 시스템 오류가 발생했습니다: {e}")
