import streamlit as st
import random
import pandas as pd
import datetime

# --- 1. 상수 및 패턴 데이터 (사용자 제공 로직 유지) ---
CORE_PATTERNS = {
    1: [1, 2, 1, 1, 1], 2: [1, 1, 1, 2, 1], 3: [2, 1, 2, 1, 0], 4: [1, 2, 1, 2, 0],
    5: [1, 1, 2, 2, 0], 6: [2, 1, 1, 1, 1], 7: [1, 2, 2, 1, 0], 8: [2, 2, 1, 0, 1],
    9: [0, 2, 1, 1, 2], 10: [1, 1, 1, 1, 2], 11: [1, 2, 1, 1, 1], 12: [2, 1, 1, 1, 1],
    13: [0, 1, 2, 1, 2], 14: [2, 2, 1, 1, 0], 15: [1, 2, 2, 1, 0], 16: [2, 1, 1, 2, 0],
    17: [0, 1, 1, 3, 1], 18: [1, 2, 0, 2, 1], 19: [2, 2, 0, 1, 1], 20: [2, 0, 2, 1, 1]
}

# --- 2. 스타일링 ---
st.set_page_config(page_title="로또 설계자 PRO", layout="centered")
st.markdown("""
    <style>
    .ball-container { display: flex; justify-content: center; gap: 8px; margin: 10px 0; flex-wrap: wrap; }
    .ball { 
        width: 36px; height: 36px; border-radius: 50%; display: flex; 
        align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 14px;
    }
    .report-card { background: #f9f9f9; padding: 12px; border-radius: 8px; border-left: 5px solid #007bff; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 메인 화면 및 수동 입력 설정 ---
st.title("🎰 AI 복합 설계 생성기")
st.info("💡 API 장애를 방지하기 위해 분석하신 Hot/Cold 번호를 직접 입력하는 모드입니다.")

with st.expander("📝 분석 번호 직접 입력 (수동 설정)", expanded=True):
    col_input1, col_input2 = st.columns(2)
    with col_input1:
        # 쉼표로 구분하여 번호 입력
        hot_input = st.text_input("🔥 Hot 번호 (쉼표로 구분)", value="1, 10, 14, 25, 31, 38, 45")
        hot_list = [int(x.strip()) for x in hot_input.split(",") if x.strip().isdigit()]
    with col_input2:
        cold_input = st.text_input("❄️ Cold 번호 (쉼표로 구분)", value="3, 5, 9, 22, 41")
        cold_list = [int(x.strip()) for x in cold_input.split(",") if x.strip().isdigit()]

with st.expander("⚙️ 설계 세부 설정", expanded=False):
    game_count = st.select_slider("생성할 게임 수", options=[1, 3, 5], value=3)
    rank_limit = st.slider("확률 패턴 범위 (상위 n위)", 1, 20, 10)
    h_include = st.number_input("조합당 Hot 번호 포함 개수", 0, 4, 2)
    c_include = st.number_input("조합당 Cold 번호 포함 개수", 0, 4, 1)

# --- 4. 번호 생성 로직 ---
def generate_lotto_manual():
    # 입력된 번호 외 나머지를 일반 번호로 채움
    all_selected = set(hot_list + cold_list)
    others = [n for n in range(1, 46) if n not in all_selected]
    
    # 안전장치: 입력된 번호가 부족할 경우 에러 방지
    if len(hot_list) < h_include or len(cold_list) < c_include:
        return None, "입력된 Hot/Cold 번호 개수가 설정보다 적습니다."

    for _ in range(2000): # 패턴 매칭을 위한 반복 시도
        try:
            # Hot/Cold/Others에서 각각 추출
            s_hot = random.sample(hot_list, h_include)
            s_cold = random.sample(cold_list, c_include)
            s_others = random.sample(others, 6 - h_include - c_include)
            
            res = sorted(s_hot + s_cold + s_others)
            
            # 1. 합계 필터 (100~175)
            total_s = sum(res)
            if not (100 <= total_s <= 175): continue
            
            # 2. 번호대 패턴 분석
            pattern = [0, 0, 0, 0, 0]
            for n in res:
                if n <= 9: pattern[0] += 1
                elif n <= 19: pattern[1] += 1
                elif n <= 29: pattern[2] += 1
                elif n <= 39: pattern[3] += 1
                else: pattern[4] += 1
            
            # 3. CORE_PATTERNS 매칭
            rk = next((rk for rk, p in CORE_PATTERNS.items() if p == pattern and rk <= rank_limit), None)
            
            if rk:
                return res, rk, total_s
        except Exception:
            continue
    return None, "설정하신 조건(패턴 순위)에 맞는 조합을 찾지 못했습니다. 범위를 넓혀주세요."

# --- 5. 추출 결과 출력 ---
if st.button("🚀 수동 분석 데이터로 추출 시작", use_container_width=True):
    success_count = 0
    for i in range(game_count):
        nums, rk, ts = generate_lotto_manual()
        
        if nums:
            ball_html = '<div class="ball-container">'
            for n in nums:
                color = "#fbc400" if n <= 9 else "#69c8f2" if n <= 19 else "#ff7272" if n <= 29 else "#aaaaaa" if n <= 39 else "#b0d840"
                ball_html += f'<div class="ball" style="background-color:{color};">{n}</div>'
            ball_html += '</div>'
            st.markdown(ball_html, unsafe_allow_html=True)
            st.markdown(f"<div class='report-card'><b>{i+1}번 조합:</b> 패턴 {rk}위 적용 / 합계 {ts}</div>", unsafe_allow_html=True)
            success_count += 1
        else:
            st.warning(rk) # 에러 메시지 출력
            break
            
    if success_count > 0:
        st.balloons()
