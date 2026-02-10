import streamlit as st
import random
import pandas as pd

# 1. 상위 20위 패턴 데이터
CORE_PATTERNS = {
    1: [1, 2, 1, 1, 1], 2: [1, 1, 1, 2, 1], 3: [2, 1, 2, 1, 0], 4: [1, 2, 1, 2, 0],
    5: [1, 1, 2, 2, 0], 6: [2, 1, 1, 1, 1], 7: [1, 2, 2, 1, 0], 8: [2, 2, 1, 0, 1],
    9: [0, 2, 1, 1, 2], 10: [1, 1, 1, 1, 2], 11: [1, 2, 1, 1, 1], 12: [2, 1, 1, 1, 1],
    13: [0, 1, 2, 1, 2], 14: [2, 2, 1, 1, 0], 15: [1, 2, 2, 1, 0], 16: [2, 1, 1, 2, 0],
    17: [0, 1, 1, 3, 1], 18: [1, 2, 0, 2, 1], 19: [2, 2, 0, 1, 1], 20: [2, 0, 2, 1, 1]
}

recent_hot = [1, 2, 6, 9, 10, 17, 20, 22, 24, 27, 30, 35, 36, 37, 38, 39, 42, 45]
recent_cold = [11, 13, 14, 15, 19, 34, 43]

st.set_page_config(page_title="로또 디자이너 PRO", layout="centered")

st.markdown("""
    <style>
    .main { padding: 0.5rem; }
    h1 { font-size: 1.3rem !important; color: #111 !important; text-align: center; }
    .ball-container { display: flex; justify-content: space-around; margin: 10px 0; }
    .ball { 
        width: 35px; height: 35px; border-radius: 50%; 
        display: flex; align-items: center; justify-content: center; 
        color: white !important; font-weight: bold; font-size: 14px;
        box-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    .report { font-size: 0.75rem; color: #444; border-bottom: 1px solid #eee; padding-bottom: 8px; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

menu = st.tabs(["🎰 번호 생성", "📅 당첨 기록", "🔍 QR 확인"])

# --- 함수 정의 (가장 바깥쪽으로 뺌) ---
def generate_lotto(max_rank, h_num, c_num, s_min, s_max):
    all_nums = set(range(1, 46))
    others = list(all_nums - set(recent_hot) - set(recent_cold))
    
    attempts = 0
    while attempts < 2000:
        attempts += 1
        # pool 생성 시 개수 부족 방지
        try:
            pool = random.sample(recent_hot, h_num) + \
                   random.sample(recent_cold, c_num) + \
                   random.sample(others, 6 - (h_num + c_num))
        except ValueError: continue
            
        res = sorted(list(set(pool)))
        if len(res) != 6: continue
        
        odd_count = len([n for n in res if n % 2 != 0])
        if odd_count not in [2, 3, 4]: continue
        
        total_s = sum(res)
        if not (s_min <= total_s <= s_max): continue
        
        pattern = [0, 0, 0, 0, 0]
        for n in res:
            if n <= 9: pattern[0] += 1
            elif n <= 19: pattern[1] += 1
            elif n <= 29: pattern[2] += 1
            elif n <= 39: pattern[3] += 1
            else: pattern[4] += 1
        
        for rk in range(1, max_rank + 1):
            if CORE_PATTERNS[rk] == pattern:
                return res, total_s, rk, odd_count
    return None, None, None, None

# --- [TAB 1: 번호 생성] ---
with menu[0]:
    st.title("🏗️ AI 로또 설계 분석기")
    
    with st.expander("⚙️ 정밀 필터 설정", expanded=True):
        rank_limit = st.slider("패턴 범위 (1~20위)", 1, 20, 10)
        game_count = st.select_slider("생성 게임 수", options=[1, 2, 3, 4, 5], value=3)
        
        col1, col2 = st.columns(2)
        with col1:
            h_cnt = st.number_input("HOT 번호", 0, 6, 3)
        with col2:
            c_cnt = st.number_input("COLD 번호", 0, 6, 1)
            
        sum_range = st.slider("합계 범위 설정", 60, 230, (100, 170))

    if st.button("🎰 복합 설계 추출 시작", use_container_width=True):
        for _ in range(game_count):
            nums, ts, rk, oc = generate_lotto(rank_limit, h_cnt, c_cnt, sum_range[0], sum_range[1])
            if nums:
                ball_html = '<div class="ball-container">'
                for n in nums:
                    color = "#fbc400" if n <= 9 else "#69c8f2" if n <= 19 else "#ff7272" if n <= 29 else "#aaaaaa" if n <= 39 else "#b0d840"
                    ball_html += f'<div class="ball" style="background-color:{color};">{n}</div>'
                ball_html += '</div>'
                st.markdown(ball_html, unsafe_allow_html=True)
                st.markdown(f'<p class="report"><b>{rk}위 패턴</b> | 홀짝 {oc}:{6-oc} | 합계: {ts} | H{h_cnt} C{c_cnt}</p>', unsafe_allow_html=True)
            else:
                st.warning("조건에 맞는 번호를 찾지 못했습니다. 필터를 조절해주세요.")
        st.balloons()

# --- [TAB 2: 기록] ---
with menu[1]:
    st.subheader("📅 과거 당첨 기록")
    try:
        df = pd.read_csv("lotto_history.csv")
        st.dataframe(df, use_container_width=True)
    except:
        st.info("lotto_history.csv 파일이 없습니다.")

# --- [TAB 3: QR] ---
with menu[2]:
    st.subheader("📸 QR 확인")
    st.link_button("동행복권 QR 스캔 페이지 열기", "https://m.dhlottery.co.kr/qr.do?method=qrOrder", use_container_width=True)
