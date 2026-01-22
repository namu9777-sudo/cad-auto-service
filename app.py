import streamlit as st
import random

# 여백 및 레이아웃 설정
st.set_page_config(page_title="로또 분석기", layout="centered")

# CSS: 가로 정렬 및 모바일 최적화
st.markdown("""
    <style>
    .main { padding: 0rem 1rem; }
    .stApp { background-color: white; }
    h1 { font-size: 1.4rem !important; margin-bottom: 0px; }
    .ball-container { display: flex; justify-content: space-between; margin: 10px 0; max-width: 320px; }
    .ball { 
        width: 35px; height: 35px; border-radius: 50%; 
        display: flex; align-items: center; justify-content: center; 
        color: white; font-weight: bold; font-size: 13px;
        box-shadow: inset -3px -3px 5px rgba(0,0,0,0.1);
    }
    .report { font-size: 0.75rem; color: #666; margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📐 스마트 로또 분석기")
st.caption("통계적 필터링 기반 번호 조합")

# 데이터 및 로직 (오타 수정됨)
hot_nums = [1, 14, 27, 34, 45, 11, 23, 5, 18, 39]
cold_nums = [2, 9, 16, 22, 31, 40, 3, 10, 25, 44]

def get_balanced_nums():
    while True:
        sample = random.sample(hot_nums, 2) + random.sample(cold_nums, 1) + random.sample(range(1, 46), 3)
        res = sorted(list(set(sample)))
        if len(res) != 6: continue
        odd_c = len([n for n in res if n % 2 != 0])
        total_s = sum(res)
        if odd_c in [2, 3, 4] and 100 <= total_s <= 175:
            return res, odd_c, total_s

# 입력부
game_count = st.select_slider("생성할 게임 수", options=[1, 3, 5], value=3)

if st.button("🚀 행운의 조합 설계 시작"):
    for i in range(game_count):
        nums, oc, ts = get_balanced_nums()
        
        # 번호 가로 배치 HTML 구조
        ball_html = '<div class="ball-container">'
        for n in nums:
            color = "#fbc400" if n <= 10 else "#69c8f2" if n <= 20 else "#ff7272" if n <= 30 else "#aaaaaa" if n <= 40 else "#b0d840"
            ball_html += f'<div class="ball" style="background-color:{color};">{n}</div>'
        ball_html += '</div>'
        
        st.markdown(ball_html, unsafe_allow_html=True)
        st.markdown(f'<p class="report">📊 분석결과: 홀짝 {oc}:{6-oc} / 번호합계 {ts}</p>', unsafe_allow_html=True)

    st.toast("추출이 완료되었습니다!")
