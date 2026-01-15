import streamlit as st
import pandas as pd
import os
import google.generativeai as genai
import re

# ... (기본 설정 및 API 부분은 동일 🤙) ...

if file_path:
    try:
        df = pd.read_excel(file_path, sheet_name=target_sheet if (main_menu == "WPS" or target_sheet == 0) else 'TER', engine='openpyxl')
        st.success(f"✅ {file_path} 로드 완료!")

        # 4. 정밀 검색 인터페이스 🤙✨
        st.markdown("### 🔍 정밀 데이터 필터링")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            req_word = st.text_input("1️⃣ 필수 포함 (AND)", placeholder="예: SK")
        with col2:
            opt_word1 = st.text_input("2️⃣ 선택 1 (OR)", placeholder="예: 그리스, GREASE")
        with col3:
            opt_word2 = st.text_input("3️⃣ 선택 2 (OR)", placeholder="예: 리크, LEAK")

        user_question = st.text_input("💬 분석 질문 입력", placeholder="예: 해당 건들의 최종 조치 사항 요약해줘")

        # 5. [강력한] 정밀 필터링 로직 🧠
        filtered_df = df.copy()
        
        # 전체 텍스트 합치기 (검색용)
        combined_text = df.apply(lambda row: row.astype(str).str.cat(sep=' ').upper(), axis=1)

        mask = pd.Series([True] * len(df))

        # 1) 필수 단어 체크
        if req_word:
            mask &= combined_text.str.contains(req_word.upper().strip())
        
        # 2) 선택 1 체크 (콤마나 슬래시로 구분해서 입력 가능 🤙)
        if opt_word1:
            keywords1 = [k.strip().upper() for k in re.split(',|/|OR', opt_word1.upper()) if k.strip()]
            mask &= combined_text.apply(lambda x: any(k in x for k in keywords1))

        # 3) 선택 2 체크
        if opt_word2:
            keywords2 = [k.strip().upper() for k in re.split(',|/|OR', opt_word2.upper()) if k.strip()]
            mask &= combined_text.apply(lambda x: any(k in x for k in keywords2))

        filtered_df = df[mask]

        if st.button("🚀 정밀 분석 시작"):
            if not filtered_df.empty and user_question:
                with st.status("📡 데이터 정밀 분석 중...", expanded=True) as status:
                    try:
                        context_data = filtered_df.to_csv(index=False, sep="|")
                        prompt = f"너는 2차전지 전문가야. 다음 필터링된 데이터로 답해줘.\n\n데이터:\n{context_data}\n\n질문: {user_question}"
                        response = model.generate_content(prompt)
                        st.info("✨ 분석 결과")
                        st.write(response.text)
                        status.update(label="✅ 데이터 정밀 분석 완료", state="complete", expanded=False)
                    except Exception as e:
                        st.error(f"🚨 엔진 에러: {e}")
            else:
                st.warning("💡 검색 결과가 없거나 질문이 비어있어요!")

        # 6. 결과만 딱 보여주기!
        with st.expander(f"📊 필터링된 결과 보기 ({len(filtered_df)}건)"):
            st.dataframe(filtered_df)
            
    except Exception as e:
        st.error(f"🚨 로드 에러: {e}")
# ... (이하 동일 🤙)
