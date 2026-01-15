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
    candidates = ["wps_list.XLSX", "wps_list.xlsx", "wps_list.xlsx.xlsx"]
else:
    candidates = ["ter_list.xlsx", "ter_list.xlsx.xlsx", "ter_list.XLSX"]

for f in candidates:
    if os.path.exists(f):
        file_path = f
        break

try:
    if file_path:
        file_size = os.path.getsize(file_path)
        if file_size < 3000:
            st.error(f"🚨 오빠! '{file_path}' 파일 용량이 {file_size} Bytes밖에 안 돼요!")
            st.info("💡 이건 실제 엑셀이 아니라 '껍데기'일 확률이 높아요. 웹에서 직접 업로드해 보세요!")
            st.stop()

        # 엑셀 읽기
        xl = pd.ExcelFile(file_path, engine='openpyxl')
        
        if main_menu == "TER (트러블 리포트)":
            st.title("🛠️ TER 트러블 정밀 분석기")
            # [수정] 'TER'라는 이름의 시트가 있는지 확인하고 바로 로드!
            target_sheet = 'TER'
            if target_sheet in xl.sheet_names:
                df = pd.read_excel(xl, sheet_name=target_sheet)
                st.success(f"✅ '{file_path}'의 [{target_sheet}] 시트를 성공적으로 읽어왔어요! 🤙")
            else:
                # 만약 TER 시트가 없으면 첫 번째 시트를 대신 읽어요
                df = pd.read_excel(xl, sheet_name=0)
                st.warning(f"⚠️ '{target_sheet}' 시트가 없어서 첫 번째 시트({xl.sheet_names[0]})를 가져왔어요.")
        else:
            st.title("👨‍🏭 WPS 실무 전문가")
            df = pd.read_excel(xl)
            st.success(f"✅ WPS 데이터를 로드 완료했습니다! 😍")

        # 5. 질문 및 답변
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
        st.error(f"❌ 깃허브에 파일이 없어요 오빠! 😭")

except Exception as e:
    st.error(f"🚨 오빠, 여기서 문제가 생겼어요: {e}")
