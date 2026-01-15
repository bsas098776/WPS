import streamlit as st
import pandas as pd
import os
from groq import Groq

# 1. 페이지 설정 및 키 설정 (기존과 동일)
st.set_page_config(page_title="윤성 AI (키워드 검색형)", page_icon="🛡️", layout="wide")

def get_clean_key():
    raw_key = st.secrets.get("GROQ_API_KEY")
    return raw_key.strip().replace("\n", "").replace("\r", "").replace(" ", "").strip('"').strip("'") if raw_key else None

clean_key = get_clean_key()
client = Groq(api_key=clean_key) if clean_key else None

# 2. 사이드바 업무 선택
st.sidebar.title("📂 업무 제어판")
main_menu = st.sidebar.radio("업무 선택", ["WPS (용접 규격)", "TER (트러블 리포트)"])

# 3. 파일 로드 로직
if main_menu == "WPS (용접 규격)":
    candidates = ["wps_list.XLSX", "wps_list.xlsx"]
    target_sheet = 0
else:
    candidates = ["ter_list.xlsx.xlsx", "ter_list.xlsx", "ter_list.XLSX", "TER LIST.XLSX"]
    target_sheet = 'TER'

file_path = next((f for f in candidates if os.path.exists(f)), None)

if file_path:
    df = pd.read_excel(file_path, sheet_name=target_sheet if (main_menu == "WPS" or target_sheet == 0) else 'TER')
    st.success(f"✅ {file_path} 로드 완료!")

    # 4. [업그레이드] 검색어 입력 및 질문 🤙
    search_keyword = st.text_input("🔍 찾고 싶은 키워드를 입력하세요 (예: INNO, 그리스, 리크)")
    user_question = st.text_input("💬 질문을 입력하세요")

    if st.button("🚀 정밀 분석 시작"):
        if search_keyword and user_question:
            with st.status("📡 데이터 검색 및 AI 분석 중..."):
                # [필살기] 전체 데이터에서 키워드가 포함된 행만 필터링! 🤙
                # 모든 열을 문자열로 바꾼 뒤 키워드가 있는지 확인해요.
                mask = df.apply(lambda row: row.astype(str).str.contains(search_keyword, case=False).any(), axis=1)
                filtered_df = df[mask]

                if not filtered_df.empty:
                    # 검색된 내용이 너무 많으면 상위 30개만!
                    context_data = filtered_df.head(30).to_csv(index=False)
                    
                    response = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": "너는 윤성 전문가야. 검색된 데이터를 바탕으로 답해줘."},
                            {"role": "user", "content": f"검색결과:\n{context_data}\n\n질문: {user_question}"}
                        ],
                        model="llama-3.3-70b-versatile",
                    )
                    st.info(f"✨ '{search_keyword}' 검색 결과 기반 분석")
                    st.write(response.choices[0].message.content)
                else:
                    st.warning(f"😭 데이터 전체에서 '{search_keyword}'를 찾을 수 없어요.")
        else:
            st.error("💡 키워드와 질문을 모두 입력해 주세요!")

    with st.expander("📊 데이터 미리보기"):
        st.dataframe(df)
