import streamlit as st
import random

# 화면 여백을 최소화하여 블로그 삽입에 최적화
st.set_page_config(page_title="로또 설계자", layout="centered")

# CSS를 사용하여 글씨 크기와 상단 여백 조절
st.markdown("""
    <style>
    .main { padding-top: 0rem; }
    h1 { font-size: 1.8rem !important; color: #2E4053; }
    h3 { font-size: 1.2rem !important; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3rem; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("📐 스마트 로또 설계기")
st.caption("통계적 필터링(홀짝/합계)이 적용된 건축가 전용 조합")

# 필터링 로직 (건축가님의 핫앤콜드 반영)
hot_nums = [1, 14, 27, 34, 45, 11, 23, 5, 18, 39]
cold_nums = [2, 9, 16, 22, 31, 40, 3, 10, 25, 44]

def get_balanced_nums():
    while True:
        sample = random.sample(hot_nums, 2) + random.sample(cold_numbers, 1) + random.sample(range(1, 46), 3)
        res = sorted(list(set(sample)))
        if len(res) != 6: continue
        
        odd_c = len([n for n in res if n % 2 != 0])
        total_s = sum(res)
        # 통계적 우세 지역: 홀짝 2:4~4:2, 합계 100~175
        if odd_c in [2, 3, 4] and 100 <= total_s <= 175:
            return res, odd_c, total_s

# 슬라이더 대신 깔끔한 선택박스 사용
game_count = st.select_slider("생성할 게임 수", options=[1, 3, 5], value=3)

if st.button("🚀 행운의 조합 설계 시작"):
    st.divider()
    for i in range(game_count):
        nums, oc, ts = get_balanced_nums()
        
        # 번호들을 한 줄에 깔끔하게 표시
        cols = st.columns(6)
        for idx, n in enumerate(nums):
            color = "#FFD700" if n <= 10 else "#1E90FF" if n <= 20 else "#FF4500" if n <= 30 else "#808080" if n <= 40 else "#32CD32"
            cols[idx].markdown(f"""
                <div style="background-color:{color}; color:white; border-radius:50%; 
                width:35px; height:35px; display:flex; align-items:center; justify-content:center; 
                font-weight:bold; font-size:14px; margin:auto;">{n}</div>
                """, unsafe_allow_html=True)
        st.caption(f"분석: 홀짝 {oc}:{6-oc} / 합계 {ts}")
        st.write("") 

    st.toast("행운의 번호가 설계되었습니다!")
