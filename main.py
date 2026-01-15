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
            # [속도 향상] 모델을 1.5-flash로 설정하면 대용량 데이터 분석이 더 빨라요!
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            return response.text, i + 1
        except Exception as e:
            if "429" in str(e): continue
            else: return f"에러: {e}", None
    return "준비된 모든 키가 만료되었습니다. 😭", None

# 3. 사이드바 및 파일 로드 로직 (기존과 동일하되 시트 고정!)
st.sidebar.title("📂 윤성 데이터 센터")
main_menu = st.sidebar.radio("원하시는 업무를 고르세요", ["WPS (용접 규격)", "TER (트러블 리포트)"])

candidates = ["ter_list.xlsx", "ter_list.xlsx.xlsx", "ter_list.XLSX", "wps_list.XLSX", "wps_list.xlsx"]
file_path = next((f for f in candidates if os.path.exists(f)), None)

try:
    if file_path:
        xl = pd.ExcelFile(file_path, engine='openpyxl')
        
        if main_menu == "TER (트러블 리포트)":
            st.title("🛠️ TER 트러블 정밀 분석기")
            df = pd.read_excel(xl, sheet_name='TER' if 'TER' in xl.sheet_names else 0)
        else:
            st.title("👨‍🏭 WPS 실무 전문가")
            df = pd.read_excel(xl)

        st.success(f"✅ '{file_path}' 데이터를 성공적으로 로드했어요! 🤙")

        # 5. 질문 및 답변 (에러 추적 기능 강화)
        user_input = st.text_input(f"💬 {main_menu}에 대해 질문해 주세요! (예: 이노믹서 리크 건 찾아줘)")

        if user_input:
            # [중요] 사용자가 엔터를 치면 바로 실행됨을 시각적으로 보여줌!
            with st.status("🚀 제미니가 데이터를 분석하고 있어요...", expanded=True) as status:
                st.write("1. 엑셀 데이터를 텍스트로 변환 중...")
                # 데이터가 너무 크면 앞부분 1000줄만 먼저 보내도록 최적화
                full_context = df.iloc[:1000].to_csv(index=False) 
                
                st.write("2. 제미니 엔진 가동 중...")
                prompt = f"너는 윤성 전문가야. 아래 데이터를 보고 대답해줘.\n\n[데이터]\n{full_context}\n\n[질문]\n{user_input}"
                
                answer, key_num = ask_gemini(prompt, keys)
                
                if key_num:
                    status.update(label=f"✅ {key_num}번 엔진으로 분석 완료!", state="complete", expanded=False)
                    st.markdown("### 🤖 분석 결과")
                    st.write(answer)
                else:
                    status.update(label="❌ 분석 실패", state="error")
                    st.error(answer)
    else:
        st.error("❌ 파일을 찾을 수 없어요!")

except Exception as e:
    st.error(f"🚨 시스템 오류: {e}")
