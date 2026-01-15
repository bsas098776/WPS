import streamlit as st
import pandas as pd
import os
from groq import Groq

# 1. 페이지 설정 및 디자인
st.set_page_config(page_title="윤성 실무 AI 전문가", page_icon="🛡️", layout="wide")

# 2. Groq API 설정 (Secrets 확인)
api_key = st.secrets.get("GROQ_API_KEY")
if api_key:
    client = Groq(api_key=api_key)
else:
    st.error("🔑 Streamlit Secrets에 GROQ_API_KEY를 등록해주세요!")
    st.stop()

# 3. AI 분석 함수 (무료 티어 할당량 최적화)
def ask_ai(prompt, model_id="llama-3.3-70b-versatile"):
    try:
        completion = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": "너는 윤성의 2차전지 장비 전문가야. 제공된 데이터를 기반으로 매니저 오빠의 질문에 친절하고 정확하게 답해줘."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        return completion.choices[0].message.content
    except Exception as e:
        if "rate_limit" in str(e).lower():
            return "🚨 [할당량 초과] 너무 많은 데이터를 한 번에 보냈거나 질문이 잦았습니다. 잠시 후 다시 시도해주세요."
        return f"🚨 에러 발생: {e}"

# 4. 사이드바 - 업무 모드 및 모델 선택
st.sidebar.title("📂 업무 제어판")
main_menu = st.sidebar.radio("업무 모드를 선택하세요", ["WPS (용접 규격)", "TER (트러블 리포트)"])

st.sidebar.markdown("---")
selected_model = st.sidebar.selectbox(
    "AI 엔진 선택",
    ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"],
    index=0
)

# 5. 파일 로드 로직 (WPS/TER 경로 분기)
if main_menu == "WPS (용접 규격)":
    st.title("👨‍🏭 WPS 실무 지식 베이스")
    candidates = ["wps_list.XLSX", "wps_list.xlsx", "wps_list.xlsx.xlsx"]
    target_sheet = 0 # WPS는 보통 첫 번째 시트
else:
    st.title("🛠️ TER 트러블 정밀 분석 시스템")
    candidates = ["ter_list.xlsx.xlsx", "ter_list.xlsx", "ter_list.XLSX", "TER LIST.XLSX"]
    target_sheet = 'TER' # TER은 특정 시트 이름 지정

file_path = next((f for f in candidates if os.path.exists(f)), None)

try:
    if file_path:
        xl = pd.ExcelFile(file_path, engine='openpyxl')
        
        # 시트 존재 여부 확인 후 로드
        if isinstance(target_sheet, str) and target_sheet not in xl.sheet_names:
            df = pd.read_excel(xl, sheet_name=0)
        else:
            df = pd.read_excel(xl, sheet_name=target_sheet)
            
        st.success(f"✅ {file_path} 로드 완료!")

        # 6. 질문 및 답변 인터페이스
        user_input = st.text_input(f"💬 {main_menu}에 대해 궁금한 점을 물어보세요.")

        if user_input:
            with st.status("🚀 Groq 엔진 분석 중...", expanded=True) as status:
                # [데이터 최적화 전략]
                # 1. WPS는 용량이 작으므로 전체 전송
                # 2. TER은 용량이 크므로 핵심 열만 추출 + 최신 400줄 제한
                if main_menu == "TER (트러블 리포트)":
                    # 컬럼이 너무 많으면 토큰을 많이 먹으므로 주요 컬럼만 슬라이싱 (앞의 10개 컬럼)
                    refined_df = df.iloc[-400:, :10] 
                    context_data = refined_df.to_csv(index=False)
                    st.caption("ℹ️ 대용량 파일이므로 최신 400개 항목을 집중 분석합니다.")
                else:
                    context_data = df.to_csv(index=False)

                prompt = f"아래 [데이터]를 바탕으로 질문에 답해줘.\n\n[데이터]\n{context_data}\n\n[질문]\n{user_input}"
                
                answer = ask_ai(prompt, selected_model)
                status.update(label="✅ 분석 완료!", state="complete", expanded=False)
                st.info(answer)
                
        # 데이터 미리보기 (선택 사항)
        with st.expander("📊 로드된 데이터 미리보기"):
            st.dataframe(df.head(50))
            
    else:
        st.error(f"❌ '{main_menu}' 관련 파일을 찾을 수 없습니다. (파일명 확인 필요)")

except Exception as e:
    st.error(f"🚨 시스템 오류: {e}")
