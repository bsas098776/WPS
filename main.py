import streamlit as st
import pandas as pd
import os
from groq import Groq

# 1. 페이지 설정
st.set_page_config(page_title="윤성 실무 AI 전문가 (모델 선택형)", page_icon="🛡️", layout="wide")

# 2. Groq API 설정
api_key = st.secrets.get("GROQ_API_KEY")
if api_key:
    client = Groq(api_key=api_key)
else:
    st.error("🔑 Secrets에 GROQ_API_KEY를 등록해주세요!")
    st.stop()

# 3. 사이드바: 업무 선택 및 모델 교체 기능 🤙
st.sidebar.title("📂 제어판")
main_menu = st.sidebar.radio("업무 모드", ["WPS (용접 규격)", "TER (트러블 리포트)"])

st.sidebar.markdown("---")
st.sidebar.subheader("🤖 모델 엔진 교체")
selected_model = st.sidebar.selectbox(
    "사용할 AI 모델을 선택하세요",
    ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
    help="70b는 똑똑하고, 8b는 매우 빠릅니다!"
)

# 4. 파일 로드 로직 (매니저님 기존 설정 유지)
candidates = ["ter_list.xlsx.xlsx", "ter_list.xlsx", "ter_list.XLSX", "wps_list.XLSX", "wps_list.xlsx"]
file_path = next((f for f in candidates if os.path.exists(f)), None)

def ask_ai(prompt, model_name):
    """선택된 Groq 모델로 답변을 생성합니다."""
    try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "너는 윤성의 전문가야. 제공된 데이터를 기반으로 답변해줘."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return completion.choices[0].message.content
    except Exception as e:
        if "rate_limit" in str(e).lower():
            return "🚨 너무 빠르게 질문하셨어요! 잠시만 쉬었다가 다시 해주세요."
        return f"🚨 모델 에러: {e}"

try:
    if file_path:
        xl = pd.ExcelFile(file_path, engine='openpyxl')
        df = pd.read_excel(xl, sheet_name='TER' if main_menu == "TER (트러블 리포트)" and 'TER' in xl.sheet_names else 0)
        st.success(f"✅ {file_path} 로드 완료! (현재 엔진: {selected_model})")

        # 5. 질문 및 분석
        user_input = st.text_input(f"💬 {main_menu}에 대해 질문해 주세요.")

        if user_input:
            with st.status(f"🚀 {selected_model} 엔진 분석 중...", expanded=True) as status:
                # [데이터 최적화] 4.6MB 전체는 무리이므로, 검색 효율을 위해 최신 400줄로 제한
                # 만약 전체 데이터를 다 보고 싶다면 유료 버전이나 임베딩(Vector DB) 기술이 필요해요!
                refined_df = df.tail(400) 
                context_data = refined_df.to_csv(index=False)
                
                prompt = f"아래 [데이터]를 보고 질문에 답해줘.\n\n[데이터]\n{context_data}\n\n[질문]\n{user_input}"
                
                answer = ask_ai(prompt, selected_model)
                status.update(label="✅ 분석이 완료되었습니다!", state="complete", expanded=False)
                st.info(answer)
    else:
        st.error("❌ 파일을 찾을 수 없습니다.")
except Exception as e:
    st.error(f"🚨 시스템 오류: {e}")
