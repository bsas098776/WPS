import streamlit as st
import pandas as pd
import os
from groq import Groq

# 1. 페이지 설정
st.set_page_config(page_title="윤성 실무 AI 전문가 (Groq 엔진)", page_icon="🛡️", layout="wide")

# 2. Groq API 설정
api_key = st.secrets.get("GROQ_API_KEY")
if api_key:
    client = Groq(api_key=api_key)
else:
    st.error("🔑 Secrets에 GROQ_API_KEY를 등록해주세요!")
    st.stop()

def ask_ai(prompt):
    """Groq 엔진을 사용하여 초고속으로 답변을 생성합니다."""
    try:
        # Llama 3.3 70B 모델은 제미니 1.5/2.0만큼 똑똑해요! 🤙
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "너는 윤성의 2차전지 장비 전문가야. 제공된 데이터를 기반으로 친절하게 답변해."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3 # 분석을 위해 답변의 일관성을 높였어요.
        )
        return completion.choices[0].message.content
    except Exception as e:
        if "rate_limit_exceeded" in str(e).lower():
            return "🚨 Groq 할당량도 잠시 초과되었습니다. 잠시 후 시도하세요!"
        return f"에러 발생: {e}"

# 3. 사이드바 메뉴 (기존과 동일 🤙)
st.sidebar.title("📂 데이터 센터")
main_menu = st.sidebar.radio("업무 모드를 선택하세요", ["WPS (용접 규격)", "TER (트러블 리포트)"])

# 4. 파일 로드 (매니저님 기존 로직 완벽 유지)
if main_menu == "WPS (용접 규격)":
    candidates = ["wps_list.XLSX", "wps_list.xlsx", "wps_list.xlsx.xlsx"]
else:
    candidates = ["ter_list.xlsx.xlsx", "ter_list.xlsx", "ter_list.XLSX", "TER LIST.XLSX"]

file_path = next((f for f in candidates if os.path.exists(f)), None)

try:
    if file_path:
        file_size = os.path.getsize(file_path)
        if file_size < 5120: # 5KB 기준
            st.error(f"🚨 알림: '{file_path}' 파일 용량이 비정상적으로 작습니다.")
            st.stop()

        xl = pd.ExcelFile(file_path, engine='openpyxl')
        
        # TER 시트 자동 고정 기능 🤙
        if main_menu == "TER (트러블 리포트)":
            st.title("🛠️ TER 트러블 정밀 분석 시스템 (Groq)")
            target_sheet = 'TER'
            df = pd.read_excel(xl, sheet_name=target_sheet if target_sheet in xl.sheet_names else 0)
        else:
            st.title("👨‍🏭 WPS 실무 지식 베이스 (Groq)")
            df = pd.read_excel(xl)

        st.success(f"✅ {file_path} 로드 완료! (엔진: Groq)")

        # 5. 질문 및 답변 인터페이스
        user_input = st.text_input(f"💬 {main_menu}에 대해 질문해 주세요.")

        if user_input:
            with st.status("🚀 Groq LPU 엔진이 초고속 분석 중...", expanded=True) as status:
                # 엑셀 데이터를 CSV로 변환 (너무 크면 AI가 힘들어하니 상위 500줄 권장)
                full_context = df.head(500).to_csv(index=False) 
                
                prompt = f"아래 [데이터]를 바탕으로 질문에 답해줘.\n\n[데이터]\n{full_context}\n\n[질문]\n{user_input}"
                
                answer = ask_ai(prompt)
                status.update(label="✅ 분석 완료!", state="complete", expanded=False)
                st.info(answer)
    else:
        st.error("❌ 파일을 찾을 수 없습니다.")

except Exception as e:
    st.error(f"🚨 오류 발생: {e}")
