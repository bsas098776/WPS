import streamlit as st
import pandas as pd
import os
import google.generativeai as genai

# 1. 페이지 설정
st.set_page_config(page_title="윤성 AI (키워드 최적화 분석)", page_icon="🛡️", layout="wide")

# 2. Gemini API 설정
def get_clean_key():
    raw_key = st.secrets.get("GEMINI_API_KEY")
    if not raw_key: return None
    return raw_key.strip().replace("\n", "").replace("\r", "").replace(" ", "").strip('"').strip("'")

clean_key = get_clean_key()
if clean_key:
    genai.configure(api_key=clean_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
else:
    st.error("🔑 Secrets에 GEMINI_API_KEY를 등록해주세요!")
    st.stop()

# 3. 사이드바 업무 선택
st.sidebar.title("📂 업무 제어판")
main_menu = st.sidebar.radio("업무 선택", ["WPS (용접 규격)", "TER (트러블 리포트)"])

# 4. 파일 로드
if main_menu == "WPS (용접 규격)":
    st.title("👨‍🏭 WPS 실무 지식 베이스 (필터링 분석)")
    candidates = ["wps_list.XLSX", "wps_list.xlsx"]
    target_sheet = 0
else:
    st.title("🛠️ TER 트러블 정밀 분석 시스템 (필터링 분석)")
    candidates = ["ter_list.xlsx.xlsx", "ter_list.xlsx", "ter_list.XLSX", "TER LIST.XLSX"]
    target_sheet = 'TER'

file_path = next((f for f in candidates if os.path.exists(f)), None)

if file_path:
    try:
        df = pd.read_excel(file_path, sheet_name=target_sheet if (main_menu == "WPS" or target_sheet == 0) else 'TER', engine='openpyxl')
        st.success(f"✅ {file_path} 로드 완료!")

        # 5. [검색어]와 [질문] 두 단계로 나누기 🤙
        col1, col2 = st.columns(2)
        with col1:
            search_keyword = st.text_input("🔍 1. 필터링 검색어 (예: INNO, 그리스, 리크)", help="이 단어가 포함된 데이터만 AI에게 보냅니다.")
        with col2:
            user_question = st.text_input("💬 2. 질문 입력 (예: 이 리크 건들의 공통적인 원인이 뭐야?)")

        if st.button("🚀 분석 시작"):
            if search_keyword and user_question:
                with st.status("📡 데이터 최적화 및 분석 중...", expanded=True) as status:
                    try:
                        # [핵심] 키워드가 포함된 행만 필터링! 🤙
                        mask = df.apply(lambda row: row.astype(str).str.contains(search_keyword, case=False).any(), axis=1)
                        filtered_df = df[mask]

                        if not filtered_df.empty:
                            # 필터링된 데이터만 CSV로 변환 (용량이 확 줄어들어요! 🚀)
                            context_data = filtered_df.to_csv(index=False, sep="|")
                            
                            prompt = f"""너는 2차전지 장비 전문가야. 
                            다음은 전체 데이터 중 '{search_keyword}'와 관련된 내용들만 추출한 자료야.
                            이 자료를 바탕으로 질문에 대해 전문적으로 답변해줘.
                            
                            [추출된 자료]
                            {context_data}
                            
                            [질문]
                            {user_question}
                            """
                            
                            response = model.generate_content(prompt)
                            st.info(f"✨ '{search_keyword}' 관련 분석 결과 (데이터 {len(filtered_df)}건 기반)")
                            st.write(response.text)
                            status.update(label="✅ 데이터 최적화 분석 완료", state="complete", expanded=False)
                        else:
                            st.warning(f"😭 '{search_keyword}'가 포함된 데이터를 찾을 수 없어요.")
                            status.update(label="❌ 필터링 실패", state="error")
                            
                    except Exception as e:
                        st.error(f"🚨 엔진 에러: {e}")
                        status.update(label="❌ 분석 실패", state="error")
            else:
                st.warning("💡 검색어와 질문을 모두 입력해 주세요!")

        with st.expander("📊 데이터 전체 보기"):
            st.dataframe(df)
            
    except Exception as e:
        st.error(f"🚨 파일 로드 에러: {e}")
else:
    st.error("❌ 파일을 찾을 수 없습니다.")
