import streamlit as st
import random
import pandas as pd # CSV 처리를 위해 필요

# 1. 상위 20위 패턴 데이터 (기존 데이터 유지)
CORE_PATTERNS = {
    1: [1, 2, 1, 1, 1], 2: [1, 1, 1, 2, 1], 3: [2, 1, 2, 1, 0], 4: [1, 2, 1, 2, 0],
    5: [1, 1, 2, 2, 0], 6: [2, 1, 1, 1, 1], 7: [1, 2, 2, 1, 0], 8: [2, 2, 1, 0, 1],
    9: [0, 2, 1, 1, 2], 10: [1, 1, 1, 1, 2], 11: [1, 2, 1, 1, 1], 12: [2, 1, 1, 1, 1],
    13: [0, 1, 2, 1, 2], 14: [2, 2, 1, 1, 0], 15: [1, 2, 2, 1, 0], 16: [2, 1, 1, 2, 0],
    17: [0, 1, 1, 3, 1], 18: [1, 2, 0, 2, 1], 19: [2, 2, 0, 1, 1], 20: [2, 0, 2, 1, 1]
}

# 2. Hot/Cold 번호 (실시간 업데이트가 필요한 부분 - 현재는 예시 데이터)
# 앱 출시 후에는 이 리스트를 최신 정보로 관리하면 좋습니다.
recent_hot = [1, 2, 3, 10, 17, 20, 22, 24, 26, 27, 30, 35, 36, 37, 38, 39, 42, 45]
recent_cold = [11, 13, 14, 15, 19, 34, 43]

st.set_page_config(page_title="로또 설계자 PRO", layout="centered")

# --- UI 스타일 개선 (모바일 최적화) ---
st.markdown("""
    <style>
    .main { padding: 0.5rem; }
    h1 { font-size: 1.3rem !important; color: #111 !important; text-align: center; }
    .ball-container { display: flex; justify-content: space-around; margin: 10px 0; }
    .ball { 
        width: 35px; height: 35px; border-radius: 50%; 
        display: flex; align-items: center; justify-content: center; 
        color: white; font-weight: bold; font-size: 14px;
        box-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    .report { font-size: 0.7rem; color: #444; border-bottom: 1px solid #eee; padding-bottom: 8px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 상단 메뉴 (기능 분리) ---
menu = st.tabs(["🎰 번호 생성", "📅 당첨 기록", "🔍 QR 확인"])

# --- [TAB 1: 번호 생성] ---
with menu[0]:
    st.title("🏗️ 로또 설계 분석기")
    
    with st.expander("⚙️ 정밀 필터 설정 (직접 조절)", expanded=False):
        # 기능 1 & 3: 범위 및 개수 조절
        rank_limit = st.slider("패턴 범위 (1~20위)", 1, 20, 10)
        game_count = st.select_slider("생성 게임 수", options=list(range(1, 6)), value=3)
        
        # 기능 4: HOT/COLD 개수 조절
        col1, col2 = st.columns(2)
        with col1:
            h_cnt = st.number_input("HOT 번호 (최근 4주)", 0, 6, 3)
        with col2:
            c_cnt = st.number_input("COLD 번호 (13주+)", 0, 6, 1)
            
        # 기능 5: 합계 범위 조절
        sum_range = st.slider("합계 범위 설정", 60, 230, (100, 170))

    def generate_lotto(max_rank, h_num, c_num, s_min, s_max):
    all_nums = set(range(1, 46))
    others = list(all_nums - set(recent_hot) - set(recent_cold))
    
    attempts = 0
    while attempts < 2000:  # 홀짝 조건이 추가되었으므로 시도 횟수를 넉넉히 잡습니다.
        attempts += 1
        
        # 1. 번호 소스 조합 (Hot/Cold/Others)
        pool = random.sample(recent_hot, h_num) + \
               random.sample(recent_cold, c_num) + \
               random.sample(others, 6 - (h_num + c_num))
        
        res = sorted(list(set(pool)))
        if len(res) != 6: continue
        
        # 2. 홀짝 갯수 체크 (핵심 추가!)
        odd_count = len([n for n in res if n % 2 != 0])
        if odd_count not in [2, 3, 4]: continue # 홀짝 비율이 2:4, 3:3, 4:2 일 때만 통과
        
        # 3. 합계 범위 체크 (기능 5)
        total_s = sum(res)
        if not (s_min <= total_s <= s_max): continue
        
        # 4. 번호대 패턴 체크
        pattern = [0, 0, 0, 0, 0]
        for n in res:
            if n <= 9: pattern[0] += 1
            elif n <= 19: pattern[1] += 1
            elif n <= 29: pattern[2] += 1
            elif n <= 39: pattern[3] += 1
            else: pattern[4] += 1
        
        # 5. 상위 20위 패턴 매칭
        for rk in range(1, max_rank + 1):
            if CORE_PATTERNS[rk] == pattern:
                return res, total_s, rk, odd_count # 홀짝 갯수도 반환
                
    return None, None, None, None

    if st.button("🎰 복합 설계 추출 시작", use_container_width=True):
        for i in range(game_count):
            nums, ts, rk, oc = generate_lotto(rank_limit, h_cnt, c_cnt, sum_range[0], sum_range[1])
        if nums:
                ball_html = '<div class="ball-container">'
                for n in nums:
                    color = "#fbc400" if n <= 9 else "#69c8f2" if n <= 19 else "#ff7272" if n <= 29 else "#aaaaaa" if n <= 39 else "#b0d840"
                    ball_html += f'<div class="ball" style="background-color:{color};">{n}</div>'
                ball_html += '</div>'
                st.markdown(ball_html, unsafe_allow_html=True)
                st.markdown(f'''
        <p class="report">
            <b>{rk}위 패턴</b> | 
            설계: 홀짝 {oc}:{6-oc} / 합계 {ts} | 
            필터: H{h_cnt} C{c_cnt}
        </p>''', unsafe_allow_html=True)
        st.balloons()

# --- [TAB 2: 과거 당첨번호 보기] (기능 2) ---
with menu[1]:
    st.subheader("📅 과거 당첨 번호 (보너스 포함)")
    try:
        # csv 파일 읽기 (파일명은 실제 경로에 맞게 수정)
        df = pd.read_csv("lotto_history.csv") 
        st.dataframe(df.head(20), use_container_width=True) # 최신 20회차만 표시
    except:
        st.info("lotto_history.csv 파일을 서버에 업로드해주세요.")

# --- [TAB 3: QR코드 확인] (기능 6) ---
with menu[2]:
    st.subheader("📸 QR코드 당첨 확인")
    st.write("아래 버튼을 누르면 동행복권 QR 스캔 페이지로 연결됩니다.")
    st.link_button("동행복권 QR 스캔 열기", "https://m.dhlottery.co.kr/qr.do?method=qrOrder")
