import streamlit as st
import random
import time

st.set_page_config(page_title="행운의 로또 생성기", page_icon="🍀")

st.title("🍀 건축가님을 위한 행운의 번호")
st.write("도면 설계로 쌓인 피로를 날려버릴 행운의 번호를 추출합니다!")

# 사이드바 설정
with st.sidebar:
    st.header("⚙️ 생성 옵션")
    count = st.slider("생성할 게임 수", 1, 10, 5)
    st.info("버튼을 누르면 AI가 행운의 조합을 분석합니다.")

if st.button("🚀 행운의 번호 추출하기"):
    for i in range(count):
        with st.spinner(f"{i+1}번째 게임 분석 중..."):
            time.sleep(0.3) # 시각적인 재미를 위한 효과
            # 1~45 사이의 숫자 중 6개를 중복 없이 추출
            lotto = random.sample(range(1, 46), 6)
            lotto.sort() # 번호 정렬
            
            # 예쁘게 출력
            cols = st.columns(6)
            for idx, num in enumerate(lotto):
                cols[idx].success(f"**{num}**")
    
    st.balloons() # 축하 효과!
    st.divider()
    st.subheader("🎉 이번 주 주인공은 건축가님입니다!")
