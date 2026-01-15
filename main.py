import streamlit as st
import pandas as pd
import os
import google.generativeai as genai

# ... (페이지 설정 및 API 설정은 동일하게 유지 🤙) ...

if file_path:
    try:
        df = pd.read_excel(file_path, sheet_name=target_sheet if (main_menu == "WPS" or target_sheet == 0) else 'TER')
        st.success(f"✅ {file_path} 로드 완료!")

        user_question = st.text_input("💬 질문을 입력하세요")

        if st.button("🚀 분석 시작"):
            if user_question:
                with st.status("📡 데이터 최적화 분석 중...", expanded=True) as status:
                    try:
                        # [핵심 1] 분석에 불필요한 공백이나 중복 행을 제거해서 토큰 아끼기 🤙
                        # 텍스트가 너무 긴 컬럼이나 무의미한 컬럼이 있다면 여기서 drop(['컬럼명'], axis=1) 하셔도 돼요!
                        cleaned_df = df.dropna(how='all').drop_duplicates()
                        
                        # [핵심 2] CSV 대신 좀 더 압축된 형태인 JSON이나 탭 구분자로 보내기
                        # CSV의 콤마(,) 조차도 토큰을 잡아먹거든요! 꺄하~ 😍
                        context_data = cleaned_df.to_csv(index=False, sep="|") # 구분자를 | 로 바꿔서 압축!
                        
                        prompt = f"""너는 2차전지 장비 전문가야. 제공된 데이터를 분석해서 답해줘.
                        데이터:
                        {context_data}
                        
                        질문: {user_question}
                        """
                        
                        # [핵심 3] 제미니에게 전송!
                        response = model.generate_content(prompt)
                        
                        st.info("✨ 분석 결과")
                        st.write(response.text)
                        
                        status.update(label="✅ 데이터 최적화 분석 완료", state="complete", expanded=False)
                        
                    except Exception as e:
                        if "429" in str(e):
                            st.error("🚨 제미니가 지금 너무 바빠요(한도 초과)! 1분만 쉬었다가 다시 눌러주세요. 😭")
                        else:
                            st.error(f"🚨 에러 발생: {e}")
                        status.update(label="❌ 분석 실패", state="error")
# ... (나머지 동일 🤙) ...
