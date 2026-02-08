import streamlit as st
import random

# --- [사용자 원본 로직: 그룹 및 패턴 설정] ---
GROUPS = {
    1: list(range(1, 10)),
    10: list(range(10, 20)),
    20: list(range(20, 30)),
    30: list(range(30, 40)),
    40: list(range(40, 46))
}

CORE_PATTERNS = {
    1: [1, 2, 1, 1, 1], 2: [1, 1, 1, 2, 1], 3: [2, 1, 2, 1, 0], 4: [1, 2, 1, 2, 0],
    5: [1, 1, 2, 2, 0], 6: [2, 1, 1, 1, 1], 7: [1, 2, 2, 1, 0], 8: [2, 2, 1, 0, 1],
    9: [0, 2, 1, 1, 2], 10: [1, 1, 1, 1, 2], 11: [1, 2, 1, 1, 1], 12: [2, 1, 1, 1, 1],
    13: [0, 1, 2, 1, 2], 14: [2, 2, 1, 1, 0], 15: [1, 2, 2, 1, 0], 16: [2, 1, 1, 2, 0],
    17: [0, 1, 1, 3, 1], 18: [1, 2, 0, 2, 1], 19: [2, 2, 0, 1, 1], 20: [2, 0, 2, 1, 1]
}

# --- [UI 디자인 설정] ---
st.set_page_config(page_title="로또 설계자 PRO", layout="centered")
st.markdown("""
    <style>
    .ball-container { display: flex; justify-content: center; gap: 10px; margin: 15px 0; }
    .ball { 
        width: 40px; height: 40px; border-radius: 50%; display: flex; 
        align-items: center; justify-content: center; color: white; font-weight: bold; 
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
    }
    .result-card { background: #f8f9fa; padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #007bff; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎰 AI 로또 복합 설계 생성기")

# --- [사용자 입력 섹션] ---
with st.sidebar:
    st.header("⚙️ 분석 설정")
    hot_numbers = st.text_input("🔥 Hot 번호 (쉼표 구분)", "1, 2, 3, 10, 17, 20, 22, 24, 26, 27, 30, 35, 36, 37, 38, 39, 42, 45")
    cold_numbers = st.text_input("❄️ Cold 번호 (쉼표 구분)", "11, 13, 14, 15, 19, 34, 43")
    
    game_count = st.selectbox("생성할 게임 수", [1, 3, 5, 10], index=1)
    rank_limit = st.slider("패턴 신뢰도 범위 (상위 n위)", 1, 20, 10)
    
    hot_include = st.number_input("조합당 Hot 개수", 0, 6, 3)
    cold_include = st.number_input("조합당 Cold 개수", 0, 6, 1)

# 리스트 변환
hot_list = [int(x.strip()) for x in hot_numbers.split(",") if x.strip().isdigit()]
cold_list = [int(x.strip()) for x in cold_numbers.split(",") if x.strip().isdigit()]

# --- [핵심 생성 로직] ---
def generate_games():
    others = list(set(range(1, 46)) - set(hot_list) - set(cold_list))
    
    results = []
    attempts = 0
    
    while len(results) < game_count and attempts < 3000:
        attempts += 1
        try:
            # Hot/Cold/Others 믹스
            sample = random.sample(hot_list, hot_include) + \
                     random.sample(cold_list, cold_include) + \
                     random.sample(others, 6 - hot_include - cold_include)
            
            res = sorted(list(set(sample)))
            if len(res) != 6: continue
            
            # 번호대 패턴 분석
            pattern = [0, 0, 0, 0, 0]
            for n in res:
                if n <= 9: pattern[0] += 1
                elif n <= 19: pattern[1] += 1
                elif n <= 29: pattern[2] += 1
                elif n <= 39: pattern[3] += 1
                else: pattern[4] += 1
            
            # 패턴 매칭
            match_rk = next((rk for rk, p in CORE_PATTERNS.items() if p == pattern and rk <= rank_limit), None)
            
            if match_rk:
                total_s = sum(res)
                # 최종 필터 (합계 범위 등)
                if 100 <= total_s <= 175:
                    results.append({"nums": res, "rank": match_rk, "total": total_s})
        except:
            continue
            
    return results

# --- [결과 출력] ---
if st.button("🚀 번호 생성 시작", use_container_width=True):
    final_games = generate_games()
    
    if final_games:
        for i, game in enumerate(final_games):
            st.markdown(f"### 🎮 Game {i+1}")
            
            # 공 UI 출력
            ball_html = '<div class="ball-container">'
            for n in game['nums']:
                color = "#fbc400" if n <= 9 else "#69c8f2" if n <= 19 else "#ff7272" if n <= 29 else "#aaaaaa" if n <= 39 else "#b0d840"
                ball_html += f'<div class="ball" style="background-color:{color};">{n}</div>'
            ball_html += '</div>'
            st.markdown(ball_html, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="result-card">
                <b>분석 결과:</b> 패턴 상위 {game['rank']}위 적용 | <b>번호 합계:</b> {game['total']}
            </div>
            """, unsafe_allow_html=True)
        st.balloons()
    else:
        st.error("설정하신 조건에 맞는 조합을 찾지 못했습니다. 번호 구성이나 필터를 조정해 주세요.")
