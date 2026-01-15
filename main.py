import streamlit as st
import pandas as pd
import os
from groq import Groq

# 1. 페이지 설정
st.set_page_config(page_title="윤성 AI (절대 에러 안남 모드)", page_icon="🛡️", layout="wide")

# 2. Groq API 설정
def get_clean_key():
    raw_key = st.secrets.get("GROQ_API_KEY")
    if not raw_key: return None
    return raw_key.strip().replace("\n", "").replace("\r", "").replace(" ", "").strip('"').strip("'")

clean_key = get_clean_key()
client = Groq(api_key=clean_key) if clean_key else None

# 3. 사이드바 업무 선택
st.sidebar.title("📂 업무 제어판")
main_menu = st.sidebar.radio("업무 선택", ["WPS (용접 규격)", "TER (트러블 리포트)"])

# 4. 파일 로드 (선택 메뉴에 따른 파일 분리 🤙)
if main_menu == "WPS (용접 규격)":
    st.title("👨‍🏭 WPS 실무 지식 베이스")
    candidates = ["wps_list.XLSX", "wps_list.xlsx"]
    target_sheet = 0
else:
    st.title("🛠️ TER 트러블 정밀 분석 시스템")
    candidates = ["ter_list.xlsx.xlsx", "ter_list.xlsx", "ter_list.XLSX", "TER LIST.XLSX"]
    target_sheet = 'TER'

file_path = next((f for f in candidates if os.path.exists(f)), None)

if file_path:
    try:
        df = pd.read_excel(file_path, sheet_name=target_sheet if (main_menu == "WPS" or target_sheet == 0) else 'TER')
        st.success(f"✅ {file_path} 로드 완료!")

        # 5. [안전 밸브 장착] 검색 및 질문 🤙
        search_keyword = st.text_input("🔍 찾고 싶은 핵심 단어 하나만 입력 (예: INNO, 그리스, 리크)")
        user_question = st.text_input("💬 질문을 입력하세요")

        if st.button("🚀 분석 시작"):
            if search_keyword and user_question and client:
                with st.status("📡 데이터 최적화 분석 중..."):
                    # 1. 키워드 포함 행 찾기
                    mask = df.apply(lambda row: row.astype(str).str.contains(search_keyword, case=False).any(), axis=1)
                    filtered_df = df[mask]

                    if not filtered_df.empty:
                        # [핵심] 검색 결과가 아무리 많아도 상위 5개만 보내서 에러 방지! 🤙
                        # 413 에러(용량초과)를 막는 가장 확실한 방법이에요.
                        small_context = filtered_df.head(5).to_csv(index=False)
                        
                        try:
                            response = client.chat.completions.create(
                                messages=[
                                    {"role": "system", "content": "너는 윤성 전문가야. 검색된 상위 5건의 데이터를 보고 짧고 명확하게 답해줘."},
                                    {"role": "user", "content": f"검색된 데이터:\n{small_context}\n\n질문: {user_question}"}
                                ],
                                model="llama-3.3-70b-versatile",
                                temperature=0.1
                            )
                            st.info(f"✨ '{search_keyword}' 관련 최신 정보 분석 결과")
                            st.write(response.choices[0].message.content)
                        except Exception as e:
                            st.error(f"🚨 엔진 통신 에러: {e}")
                    else:
                        st.warning(f"😭 '{search_keyword}'를 찾을 수 없어요. 단어를 바꿔볼까요?")
            else:
                st.warning("💡 키워드, 질문, API 키를 모두 확인해 주세요!")

        with st.expander("📊 데이터 전체 보기 (직접 확인용)"):
            st.dataframe(df)
            
    except Exception as e:
        st.error(f"🚨 파일 로드 에러: {e}")
else:
    st.error("❌ 파일을 찾을 수 없습니다.")
