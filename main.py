import streamlit as st
import pandas as pd
import os
from groq import Groq

# 1. 페이지 설정
st.set_page_config(page_title="윤성 실무 AI (데이터 압축 최적화)", page_icon="🛡️", layout="wide")

# 2. Groq API 설정
api_key = st.secrets.get("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None

def ask_ai(prompt, model_id):
    try:
        completion = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": "너는 윤성의 전문가야. 제공된 데이터를 꼼꼼히 분석해서 답해줘."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"🚨 에러: {e}"

# 3. 사이드바 제어판
st.sidebar.title("📂 제어판")
selected_model = "llama-3.3-70b-versatile" # 가장 똑똑한 모델 고정 🤙

# 4. 파일 로드 및 최적화 분석
candidates = ["ter_list.xlsx.xlsx", "ter_list.xlsx", "wps_list.XLSX"]
file_path = next((f for f in candidates if os.path.exists(f)), None)

if file_path and client:
    xl = pd.ExcelFile(file_path, engine='openpyxl')
    df = pd.read_excel(xl, sheet_name='TER' if 'TER' in xl.sheet_names else 0)
    st.success(f"✅ {file_path} 로드 완료!")

    user_input = st.text_input("💬 분석 질문을 입력하세요 (예: 이노믹서 관련 모든 이슈 요약해줘)")

    if user_input:
        with st.status("🚀 핵심 데이터 추출 및 정밀 분석 중..."):
            # [압축 전략] 불필요한 열은 빼고 핵심 열만 추출해서 토큰을 아낍니다! 🤙
            # 매니저님의 파일 컬럼명에 맞춰 '현상', '조치' 등 주요 컬럼만 선택하세요.
            # 예: available_cols = ['부위', '현상', '원인', '조치']
            # 여기서는 우선 전체 중 텍스트가 많은 상위 컬럼 위주로 샘플링합니다.
            
            refined_df = df.iloc[:, [1, 2, 3, 4, 5]] # 주요 컬럼 5개만 선택 (예시)
            
            # 토큰 한도 내에서 최대한 많은 행(약 600~800행)을 보냅니다.
            context_data = refined_df.tail(700).to_csv(index=False)
            
            prompt = f"아래 데이터는 최근 발생한 트러블 리포트야. 질문에 답해줘.\n\n[데이터]\n{context_data}\n\n[질문]\n{user_input}"
            
            answer = ask_ai(prompt, selected_model)
            st.info(answer)
