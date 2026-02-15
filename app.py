import streamlit as st
import random
import time
import pandas as pd

# 1. 상위 20위 패턴 데이터 (AI 학습 데이터셋 역할)
CORE_PATTERNS = {
    1: [1, 2, 1, 1, 1], 2: [1, 1, 1, 2, 1], 3: [2, 1, 2, 1, 0], 4: [1, 2, 1, 2, 0],
    5: [1, 1, 2, 2, 0], 6: [2, 1, 1, 1, 1], 7: [1, 2, 2, 1, 0], 8: [2, 2, 1, 0, 1],
    9: [0, 2, 1, 1, 2], 10: [1, 1, 1, 1, 2], 11: [1, 2, 1, 1, 1], 12: [2, 1, 1, 1, 1],
    13: [0, 1, 2, 1, 2], 14: [2, 2, 1, 1, 0], 15: [1, 2, 2, 1, 0], 16: [2, 1, 1, 2, 0],
    17: [0, 1, 1, 3, 1], 18: [1, 2, 0, 2, 1], 19: [2, 2, 0, 1, 1], 20: [2, 0, 2, 1, 1]
}

recent_hot = [1, 2, 6, 9, 10, 17, 20, 22, 24, 27, 30, 35, 36, 37, 38, 39, 42, 45]
recent_cold = [11, 13, 14, 15, 19, 34, 43]

st.set_page_config(page_title="로또 설계자 AI PRO", layout="centered")

# CSS: AI 느낌을 주는 다크/블루 톤 디자인 적용
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #eee; border-radius: 5px; padding: 10px; }
    .ai-badge { background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%); color: white; padding: 2px 8px; border-radius: 10px; font-size: 0.65rem; font-weight: bold; margin-bottom: 5px; display: inline-block; }
    .ball-container { display: flex; justify-content: space-around; margin: 10px 0; padding: 10px; background: white; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .ball { width: 35px; height: 35px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white !important; font-weight: bold; font-size: 14px; box-shadow: inset -2px -2px 4px rgba(0,0,0,0.3); }
    .report { font-size: 0.75rem; color: #555; padding: 5px; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# AI 점수 계산 함수 (핵심!)
def calculate_ai_score(rk, oc, ts, s_min, s_max):
    score = 100
    score -= (rk - 1) * 2  # 패턴 순위가 낮을수록 감점
    if oc == 3: score += 5  # 홀짝 3:3 황금비율 가산점
    
    # 합계가 중심점에 가까울수록 가산점
    center_s = (s_min + s_max) / 2
    dist = abs(ts - center_s)
    score -= (dist / 10)
    
    return round(min(score, 99.8), 1) # 최대 99.8점

def generate_lotto(max_rank, h_num, c_num, s_min, s_max):
    all_nums = set(range(1, 46))
    others = list(all_nums - set(recent_hot) - set(recent_cold))
    
    for _ in range(2000):
        try:
            pool = random.sample(recent_hot, h_num) + random.sample(recent_cold, c_num) + random.sample(others, 6-(h_num+c_num))
            res = sorted(list(set(pool)))
            if len(res) != 6: continue
            
            odd_count = len([n for n in res if n % 2 != 0])
            if odd_count not in [2, 3, 4]: continue
            
            total_s = sum(res)
            if not (s_min <= total_s <= s_max): continue
            
            pattern = [0, 0, 0, 0, 0]
            for n in res:
                if n <= 9: pattern[0]+=1
                elif n <= 19: pattern[1]+=1
                elif n <= 29: pattern[2]+=1
                elif n <= 39: pattern[3]+=1
                else: pattern[4]+=1
            
            for rk in range(1, max_rank + 1):
                if CORE_PATTERNS[rk] == pattern:
                    score = calculate_ai_score(rk, odd_count, total_s, s_min, s_max)
                    return res, total_s, rk, odd_count, score
        except: continue
    return None, None, None, None, None

menu = st.tabs(["🤖 AI 번호 생성", "📜 과거 기록", "📸 QR 확인"])

with menu[0]:
    st.markdown("### 🏗️ 로또 설계 AI 분석기")
    with st.expander("⚙️ AI 정밀 필터 설정", expanded=True):
        rank_limit = st.slider("분석 패턴 범위 (1~20위)", 1, 20, 10)
        game_count = st.select_slider("생성 게임 수", options=[1, 2, 3, 4, 5], value=3)
        col1, col2 = st.columns(2)
        with col1: h_cnt = st.number_input("HOT 번호", 0, 6, 3)
        with col2: c_cnt = st.number_input("COLD 번호", 0, 6, 1)
        sum_range = st.slider("합계 범위 조절", 60, 230, (100, 170))

    if st.button("🎰 AI 복합 설계 시작", use_container_width=True):
        progress_text = st.empty()
        bar = st.progress(0)
        for pct in range(100):
            time.sleep(0.02) # 연출용 딜레이
            bar.progress(pct + 1)
            progress_text.text(f"AI 모델 데이터 학습 중... {pct+1}%")
        progress_text.empty()
        bar.empty()

        for _ in range(game_count):
            nums, ts, rk, oc, sc = generate_lotto(rank_limit, h_cnt, c_cnt, sum_range[0], sum_range[1])
            if nums:
                st.markdown(f'<div class="ai-badge">AI 추천 신뢰도 {sc}%</div>', unsafe_allow_html=True)
                ball_html = '<div class="ball-container">'
                for n in nums:
                    color = "#fbc400" if n <= 9 else "#69c8f2" if n <= 19 else "#ff7272" if n <= 29 else "#aaaaaa" if n <= 39 else "#b0d840"
                    ball_html += f'<div class="ball" style="background-color:{color};">{n}</div>'
                st.markdown(ball_html + '</div>', unsafe_allow_html=True)
                st.markdown(f'<p class="report"><b>역대 {rk}위 패턴</b> | 홀짝 {oc}:{6-oc} | 합계 {ts}</p>', unsafe_allow_html=True)
        st.balloons()

with menu[1]:
    st.subheader("📅 과거 당첨 기록")
    try:
        df = pd.read_csv("lotto_history.csv")
        st.dataframe(df.head(20000), use_container_width=True)
    except:
        st.info("lotto_history.csv 파일을 업로드해주세요.")

with menu[2]:
    st.subheader("📸 QR 당첨 확인")
    st.link_button("동행복권 QR 스캔 페이지 열기", "https://m.dhlottery.co.kr/qr.do?method=qrOrder", use_container_width=True)
