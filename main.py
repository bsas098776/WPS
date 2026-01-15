import streamlit as st
import pandas as pd
import os
import google.generativeai as genai

# 1. 페이지 설정
st.set_page_config(page_title="윤성 AI (멀티 검색 모드)", page_icon="🛡️", layout="wide")

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
    st.error("🔑 Secrets 확인 필요!")
    st.stop()

# 3. 사이드바 및 파일 로드 (생략 없이 오빠를 위해 전체 제공! 🤙)
st.sidebar.title("📂 업무 제어판")
main_menu = st.sidebar.radio("업무 선택", ["WPS (용접 규격)", "TER (트러블 리포트)"])

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
        df = pd.read_excel(file_path, sheet_name=target_sheet if (main_menu == "WPS" or target_sheet == 0) else 'TER', engine='openpyxl')
        st.success(f"✅ {file_path} 로드 완료!")

        # 4. 멀티 검색 인터페이스 🤙
        st.markdown("💡 **검색 팁**: `그리스 AND 리크` (모두 포함), `INNO OR MIXER` (하나라도 포함)")
        col1, col2 = st.columns([2, 3])
        with col1:
            search_query = st.text_input("🔍 멀티 검색어 입력", placeholder="예: 그리스 AND 리크")
        with col2:
            user_question = st.text_input("💬 질문 입력", placeholder="예: 위 사례들의 공통 조치 사항은?")

        # 5. [핵심] 멀티 검색 필터링 로직 🧠
        filtered_df = pd.DataFrame()
        if search_query:
            query = search_query.upper()
            # 전체를 문자열로 합쳐서 검색 준비
            combined_series = df.apply(lambda row: row.astype(str).str.cat(sep=' ').upper(), axis=1)
            
            if " AND " in query:
                keywords = [k.strip() for k in query.split(" AND ")]
                mask = combined_series.apply(lambda x: all(k in x for k in keywords))
            elif " OR " in query:
                keywords = [k.strip() for k in query.split(" OR ")]
                mask = combined_series.apply(lambda x: any(k in x for k in keywords))
            else:
                mask = combined_series.str.contains(query, case=False)
            
            filtered_df = df[mask]

        if st.button("🚀 분석 시작"):
            if not filtered_df.empty and user_question:
                with st.status("📡 데이터 정밀 분석 중...", expanded=True) as status:
                    try:
                        context_data = filtered_df.to_csv(index=False, sep="|")
                        prompt = f"너는 2차전지 전문가야. 다음 데이터로 질문에 답해줘.\n\n데이터:\n{context_data}\n\n질문: {user_question}"
                        response = model.generate_content(prompt)
                        st.info("✨ 분석 결과")
                        st.write(response.text)
                        status.update(label="✅ 데이터 최적화 분석 완료", state="complete", expanded=False)
                    except Exception as e:
                        st.error(f"🚨 엔진 에러: {e}")
            else:
                st.warning("💡 검색 결과가 없거나 질문이 비어있어요!")

        # 6. 필터링된 행만 딱 보여주기! 🤙✨
        with st.expander(f"📊 검색 결과 ({len(filtered_df)}건)"):
            if not filtered_df.empty:
                st.dataframe(filtered_df)
            else:
                st.write("검색 결과가 여기에 표시됩니다. 🤙")
            
    except Exception as e:
        st.error(f"🚨 로드 에러: {e}")
else:
    st.error("❌ 파일을 찾을 수 없습니다.")
