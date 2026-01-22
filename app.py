import streamlit as st
import random
import time

st.set_page_config(page_title="번호 고정! 로또 추출기", page_icon="💰")

st.title("💰 건축가님 대박 기원 로또 추첨기")
st.write("번호가 사라지지 않게 고정해두었습니다. 천천히 확인하세요!")

# 사이드바 설정
with st.sidebar:
    st.header("🍀 설정")
    num_games = st.slider("생성할 게임 수", 1, 10, 5)

# 번호 추출 로직
if st.button("🎰 행운의 번호 추출하기"):
    st.divider()
    
    for i in range(num_games):
        # 1~45 중 6개 무작위 추출 및 정렬
        nums = sorted(random.sample(range(1, 46), 6))
        
        # 각 게임별로 컨테이너를 만들어 번호를 박제합니다.
        st.subheader(f"📍 {i+1}번째 행운의 조합")
        cols = st.columns(6)
        
        for idx, n in enumerate(nums):
            # 번호별 색상
            if n <= 10: color = "orange"
            elif n <= 20: color = "blue"
            elif n <= 30: color = "red"
            elif n <= 40: color = "gray"
            else: color = "green"
            
            # success 박스를 써서 눈에 잘 띄고 사라지지 않게 만듭니다.
            cols[idx].markdown(f"### :{color}[{n}]")
        
        st.write("") # 게임 간 간격
        time.sleep(0.1) # 짧은 효과음 대신 시각적 딜레이

    st.balloons()
    st.success("🎉 모든 번호 추출 완료! 이 번호로 1등 가시죠!")
