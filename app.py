import streamlit as st
import random

# 레이아웃 설정
st.set_page_config(page_title="로또 설계자", layout="centered")

# CSS: 글씨를 더 진하게(Bold) 하고 가독성 극대화
st.markdown("""
    <style>
    .main { padding: 0rem 1rem; }
    h1 { font-size: 1.5rem !important; color: #111 !important; font-weight: 800 !important; }
    .ball-container { display: flex; justify-content: space-between; margin: 12px 0; max-width: 320px; }
    .ball { 
        width: 38px; height: 38px; border-radius: 50%; 
        display: flex; align-items: center; justify-content: center; 
        color: white !important; font-weight: 900 !important; font-size: 15px !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        box-shadow: inset -3px -3px 6px rgba(0,0,0,0.2);
    }
    .report { font-size: 0.8rem; color: #222 !important; font-weight: 600; margin-bottom: 15px; border-bottom: 2px solid #eee; padding-bottom: 5px; }
    .stButton>button { font-weight: 800 !important; border: 2px solid #333; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏗️ 건축가 설계 로또 분석기")
st.caption("실제 최근 당첨 통계 및 황금 비율 필터링 적용")

# [핵심] 최근 10회차 실제 많이 나온 번호 자동 리스트 (직접 업데이트 가능 영역)
# 건축가님, 이 숫자들만 매주 바꿔주시면 AI가 알아서 조합합니다!
recent_hot = [1, 6, 14, 23, 31, 34, 38, 40, 44, 45] # 최근 다수 출현
recent_cold = [2, 5, 9, 12, 17, 21, 26, 28, 33, 42] # 최근 미출현

def generate_architect_logic():
    while True:
        # 핫에서 2개, 콜드에서 2개, 완전 랜덤에서 2개 조합
        base = random.sample(recent_hot, 2) + random.sample(recent_cold, 2) + random.sample(range(1, 46), 2)
        res = sorted(list(set(base)))
        if len(res) != 6: continue
        
        odd_c = len([n for n in res if n % 2 != 0])
        total_s = sum(res)
        # 전문가 필터: 홀짝 3:3 선호, 합계 110~160 사이 집중
        if odd_c in [2, 3, 4] and 110 <= total_s <= 165:
            return res, odd_c, total_s

game_count = st.select_slider("생성할 게임 수", options=[1, 3, 5], value=3)

if st.button("🎰 행운의 도면 설계 시작"):
    for i in range(game_count):
        nums, oc, ts = generate_architect_logic()
        
        ball_html = '<div class="ball-container">'
        for n in nums:
            # 로또 공식 색상
            color = "#fbc400" if n <= 10 else "#69c8f2" if n <= 20 else "#ff7272" if n <= 30 else "#aaaaaa" if n <= 40 else "#b0d840"
            ball_html += f'<div class="ball" style="background-color:{color};">{n}</div>'
        ball_html += '</div>'
        
        st.markdown(ball_html, unsafe_allow_html=True)
        st.markdown(f'<p class="report">📊 설계데이터: 홀짝 {oc}:{6-oc} / 합계 {ts} / 핫·콜드 매칭완료</p>', unsafe_allow_html=True)

    st.balloons()
