import streamlit as st
import pandas as pd
import os
import google.generativeai as genai
import re

# 1. 페이지 설정
st.set_page_config(page_title="윤성 AI (정밀 검색 모드)", page_icon="🛡️", layout="wide")

# 2. Gemini API 설정 (생략 없음)
def get_clean_key():
    raw_key = st.secrets.get("GEMINI_API_KEY")
    if not raw_key: return None
    return raw_key.strip().replace("\n", "").replace("\r", "").replace(" ", "").strip('"').strip("'")

clean_key = get_clean_key()
if clean_key:
    genai.configure(api_key=clean_key)
    model = genai.GenerativeModel('gemini-2.0-flash') 
else:
    st.error("🔑 Secrets에 GEMINI_API_KEY를 등록해주세요!")
    st.stop()

# 3. 사이드바 업무 선택
st.sidebar.title("📂 업무 제어판")
main_menu = st.sidebar.radio("업무 선택", ["WPS (용접 규격)", "TER (트러블 리포트)"])

# --- [ 💖 화사한 피부톤의 미인 비서 추가 부분 🤙✨ ] ---
with st.sidebar:
    # 1. 위치를 더 아래로 내리기 위해 빈 공간 컨테이너 높이를 키웠어요!
    st.container(height=280, border=False) 
    
    # 2. 오빠가 원하신 화사한 피부톤 + 인사/설명 모션의 움직이는 이미지!
    # (실제 프로젝트 시에는 오빠가 가진 GIF 파일을 깃허브에 올리고 그 경로를 쓰시면 더 좋아요!)
    assistant_gif = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJ6bmZ4bmZ4bmZ4bmZ4bmZ4bmZ4bmZ4bmZ4bmZ4bmZ4bmZ4JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1z/3o7TKMGpxx66SdG43C/giphy.gif" # 화사한 느낌의 예시 GIF
    
    # 이미지를 중앙 정렬해서 보여줄게요
    st.image("https://i.imgur.com/vH9XvIe.png", width=220) # 윈터/장원영 급 화사한 피부톤의 커스텀 이미지 예시
    
    # 3. 이미지 바로 아래 '업무 어시스턴트' 사각형 문구
    st.markdown("""
        <div style="
            background-color: #ffffff; 
            padding: 10px; 
            border-radius: 15px; 
            text-align: center;
            border: 2px solid #ffccdd;
            box-shadow: 0px 4px 10px rgba(255, 182, 193, 0.3);
            margin-top: -5px;
        ">
            <span style="color: #ff4b91; font-weight: bold; font-size: 15px;">
                ✨ 업무 어시스턴트 ✨
            </span>
        </div>
    """, unsafe_allow_html=True)
# ---------------------------------------------------

# 4. 파일 경로 설정
if main_menu == "WPS (용접 규격)":
    st.title("👨‍🏭 WPS 실무 지식 베이스")
    candidates = ["wps_list.XLSX", "wps_list.xlsx"]
    target_sheet = 0
else:
    st.title("🛠️ TER 트러블 정밀 분석 시스템")
    candidates = ["ter_list.xlsx.xlsx", "ter_list.xlsx", "ter_list.XLSX", "TER LIST.XLSX"]
    target_sheet = 'TER'

file_path = next((f for f in candidates if os.path.exists(f)), None)

# [이후 메인 로직 유지]
if file_path:
    try:
        df = pd.read_excel(file_path, sheet_name=target_sheet if (main_menu == "WPS" or target_sheet == 0) else 'TER', engine='openpyxl')
        st.success(f"✅ {file_path} 로드 완료! (총 {len(df)}행)")

        st.markdown("### 🔍 정밀 데이터 필터링")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            req_word = st.text_input("1️⃣ 필수 포함 (AND)", placeholder="예: SK")
        with col2:
            opt_word1 = st.text_input("2️⃣ 선택 1 (OR)", placeholder="예: 그리스, GREASE")
        with col3:
            opt_word2 = st.text_input("3️⃣ 선택 2 (OR)", placeholder="예: 리크, LEAK")

        user_question = st.text_input("💬 분석 질문 입력", placeholder="예: 해당 건들의 공통적인 원인이 뭐야?")

        combined_text = df.apply(lambda row: row.astype(str).str.cat(sep=' ').upper(), axis=1)
        mask = pd.Series([True] * len(df))

        if req_word:
            mask &= combined_text.str.contains(req_word.upper().strip())
        
        if opt_word1:
            keywords1 = [k.strip().upper() for k in re.split(',|/|OR', opt_word1.upper()) if k.strip()]
            if keywords1:
                mask &= combined_text.apply(lambda x: any(k in x for k in keywords1))

        if opt_word2:
            keywords2 = [k.strip().upper() for k in re.split(',|/|OR', opt_word2.upper()) if k.strip()]
            if keywords2:
                mask &= combined_text.apply(lambda x: any(k in x for k in keywords2))

        filtered_df = df[mask]

        if st.button("🚀 정밀 분석 시작"):
            if not filtered_df.empty and user_question:
                with st.status("📡 데이터 정밀 분석 중...", expanded=True) as status:
                    try:
                        context_data = filtered_df.to_csv(index=False, sep="|")
                        prompt = f"""너는 2차전지 전문가야. 제공된 필터링된 데이터로 질문에 답해줘.
                        관련 사례가 여러 개면 모두 요약해줘야 해.
                        데이터: {context_data}
                        질문: {user_question}
                        """
                        response = model.generate_content(prompt)
                        st.info("✨ 분석 결과")
                        st.write(response.text)
                        status.update(label="✅ 데이터 정밀 분석 완료", state="complete", expanded=False)
                    except Exception as e:
                        st.error(f"🚨 엔진 에러: {e}")
                        status.update(label="❌ 분석 실패", state="error")
            else:
                st.warning("💡 검색 결과가 없거나 질문이 비어있어요!")

        with st.expander(f"📊 검색 결과 보기 ({len(filtered_df)}건)"):
            if not filtered_df.empty:
                st.dataframe(filtered_df)
            else:
                st.write("검색 조건을 입력하시면 필터링된 결과가 여기에 표시됩니다. 🤙")
            
    except Exception as e:
        st.error(f"🚨 파일 로드 에러: {e}")
else:
    st.error("❌ 분석할 파일을 찾을 수 없습니다. 깃허브에 파일이 있는지 확인해 주세요!")
