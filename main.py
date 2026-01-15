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
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content(prompt)
            return response.text, i + 1
        except Exception as e:
            if "429" in str(e): continue
            else: return f"에러: {e}", None
    return "준비된 모든 키가 만료되었습니다. 😭", None

# 3. 사이드바 업무 선택
st.sidebar.title("📂 윤성 데이터 센터")
main_menu = st.sidebar.radio("원하시는 업무를 고르세요", ["WPS (용접 규격)", "TER (트러블 리포트)"])

# 4. 철벽 방어 파일 로드 시스템 🤙
file_path = None
if main_menu == "WPS (용접 규격)":
    # WPS 후보군
    candidates = ["wps_list.XLSX", "wps_list.xlsx", "wps_list.xlsx.xlsx"]
else:
    # TER 후보군 (오빠를 괴롭히던 이름들 다 넣어놨어요!)
    candidates = ["ter_list.xlsx", "ter_list.xlsx.xlsx", "ter_list.XLSX"]

# 파일 찾기 시작!
for f in candidates:
    if os.path.exists(f):
        file_path = f
        break

try:
    if file_path:
        # 파일 용량 체크 (2KB 껍데기 방지!)
        file_size = os.path.getsize(file_path)
        if file_size < 3000: # 3KB 미만이면 경고!
            st.error(f"🚨 오빠! '{file_path}' 파일 용량이 {file_size} Bytes밖에 안 돼요!")
            st.info("💡 이건 실제 엑셀이 아니라 '껍데기'일 확률이 높아요. 웹에서 직접 업로드해 보세요!")
            st.stop()

        # 엑셀 읽기 (엔진 고정!)
        xl = pd.ExcelFile(file_path, engine='openpyxl')
        
        if main_menu == "TER (트러블 리포트)":
            st.title("🛠️ TER 트러블 정밀 분석기")
            selected_sheet = st.sidebar.selectbox("📋 분석할 시트 선택", xl.sheet_names)
            df = pd.read_excel(xl, sheet_name=selected_sheet)
        else:
            st.title("👨‍🏭 WPS 실무 전문가")
            df = pd.read_excel(xl)

        st.success(f"✅ '{file_path}' ({selected_sheet if main_menu == 'TER (트러블 리포트)' else '기본'}) 로드 완료! 🤙✨")

        # 5. 질문 및 답변 (전체 데이터 기반)
        full_context = df.to_csv(index=False)
        user_input = st.text_input(f"💬 {main_menu}에 대해 무엇이든 물어보세요!")

        if user_input:
            with st.spinner('전체 데이터를 꼼꼼히 분석 중이에요... 🔍'):
                prompt = f"""너는 {main_menu} 분야의 최고 전문가야. 
                아래 제공된 [전체 데이터]를 바탕으로 오빠에게 친절하고 정확하게 답해줘.
                
                [전체 데이터]
                {full_context}
                
                [질문]
                {user_input}"""
                
                answer, key_num = ask_gemini(prompt, keys)
                if key_num:
                    st.info(f"🤖 {key_num}번 엔진 가동 완료!")
                    st.markdown(answer)
    else:
        st.error(f"❌ 깃허브에 파일이 없어요 오빠! 후보군({candidates})을 다 뒤져봤는데 못 찾았어요. 😭")

except Exception as e:
    st.error(f"🚨 오빠, 여기서 문제가 생겼어요: {e}")
