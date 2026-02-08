import streamlit as st
import random
import requests
from bs4 import BeautifulSoup
import csv

def get_lotto_numbers(draw_no):
    api_url = f"https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={draw_no}"

    try:
        response = requests.get(api_url)
        response.raise_for_status()

        data = response.json()
        print(f"{draw_no}회 결과추출")
        # Request 데이터 출력
        return {
            'drwNo' : data['drwNo'],
            'date': data['drwNoDate'], 
            'lottoNumb': [str(data[f"drwtNo{i}"]) for i in range(1, 7)], 
            'bonusNumb': data['bnusNo']
        }
        
        
    except requests.exceptions.RequestException as e:
        print(f"오류가 발생했습니다: {e}")
        
def maxRound():
    url = "https://dhlottery.co.kr/common.do?method=main"
    html = requests.get(url).text
    soup = BeautifulSoup(html, "lxml")
    max_numb = soup.find(name="strong", attrs={"id": "lottoDrwNo"}).text
    return int(max_numb)

        
# 최신 회차 가져오기
maxCount = maxRound()
draw_no  = 1

# CSV 파일 쓰기
with open('lottoRes.csv', 'w', newline='') as csvfile:
    # CSV 파일 쓰기
    writer = csv.writer(csvfile, delimiter=',')
    
    # 1화부터 최신화까지 크롤링
    for draw_no in range(1, maxCount+1):
        res = get_lotto_numbers(draw_no)
        # 순서 : 회차, 날짜, 로또번호1, 로또번호2, 로또번호3, 로또번호4, 로또번호5, 로또번호6, 보너스번호
        writer.writerow([res.get('drwNo'), res.get('date')] + res.get('lottoNumb') + [res.get('bonusNumb')])


# 1. 번호대 그룹 설정 (Saved Information 반영) [cite: 2026-01-23]
GROUPS = {
    1: list(range(1, 10)),
    10: list(range(10, 20)),
    20: list(range(20, 30)),
    30: list(range(30, 40)),
    40: list(range(40, 46))
}

# 2. 상위 20위 패턴 데이터
CORE_PATTERNS = {
    1: [1, 2, 1, 1, 1], 2: [1, 1, 1, 2, 1], 3: [2, 1, 2, 1, 0], 4: [1, 2, 1, 2, 0],
    5: [1, 1, 2, 2, 0], 6: [2, 1, 1, 1, 1], 7: [1, 2, 2, 1, 0], 8: [2, 2, 1, 0, 1],
    9: [0, 2, 1, 1, 2], 10: [1, 1, 1, 1, 2], 11: [1, 2, 1, 1, 1], 12: [2, 1, 1, 1, 1],
    13: [0, 1, 2, 1, 2], 14: [2, 2, 1, 1, 0], 15: [1, 2, 2, 1, 0], 16: [2, 1, 1, 2, 0],
    17: [0, 1, 1, 3, 1], 18: [1, 2, 0, 2, 1], 19: [2, 2, 0, 1, 1], 20: [2, 0, 2, 1, 1]
}

st.set_page_config(page_title="로또 설계자 PRO", layout="centered")

# CSS 유지
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
    .report { font-size: 0.75rem; color: #222 !important; font-weight: 600; margin-bottom: 15px; border-bottom: 2px solid #eee; padding-bottom: 5px; }
    .pattern-tag { background-color: #f0f0f0; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; color: #555; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏗️ 로또 설계 분석기 PRO")

# Hot/Cold 번호 리스트
recent_hot = [1, 2, 3, 10, 17, 20, 22, 24, 26, 27, 30, 35, 36, 37, 38, 39, 42, 45]
recent_cold = [11, 13, 14, 15, 19, 34, 43]

# --- 설정 구역 ---
with st.expander("⚙️ 정밀 필터 설정", expanded=True):
    rank_limit = st.select_slider("확률 패턴 범위 (상위 n위 이내)", options=list(range(1, 21)), value=10)
    
    col1, col2 = st.columns(2)
    with col1:
        hot_count = st.number_input("Hot 번호 포함 개수", 0, 6, 3)
    with col2:
        cold_count = st.number_input("Cold 번호 포함 개수", 0, 6, 1)

def generate_hybrid_logic(max_rank, h_cnt, c_cnt):
    all_nums = set(range(1, 46))
    others = list(all_nums - set(recent_hot) - set(recent_cold))
    
    while True:
        # 1단계: 번호 소스 구성 (사용자 설정 반영)
        base_pool = random.sample(recent_hot, h_cnt) + \
                    random.sample(recent_cold, c_cnt) + \
                    random.sample(others, 6 - (h_cnt + c_cnt))
        
        res = sorted(list(set(base_pool)))
        if len(res) != 6: continue
        
        # 2단계: 번호대 패턴 체크
        current_pattern = [0, 0, 0, 0, 0]
        for n in res:
            if n <= 9: current_pattern[0] += 1
            elif n <= 19: current_pattern[1] += 1
            elif n <= 29: current_pattern[2] += 1
            elif n <= 39: current_pattern[3] += 1
            else: current_pattern[4] += 1
            
        # 선택한 순위 범위 내에 이 패턴이 있는지 확인
        matched_rank = None
        for rk in range(1, max_rank + 1):
            if CORE_PATTERNS[rk] == current_pattern:
                matched_rank = rk
                break
        
        if matched_rank is None: continue
        
        # 3단계: 기존 전문가 필터 (홀짝, 합계)
        odd_c = len([n for n in res if n % 2 != 0])
        total_s = sum(res)
        
        if odd_c in [2, 3, 4] and 110 <= total_s <= 165:
            return res, odd_c, total_s, matched_rank

# 생성 UI
game_count = st.select_slider("생성할 게임 수", options=[1, 3, 5], value=3)

if st.button("🎰 복합 설계 추출 시작"):
    for i in range(game_count):
        nums, oc, ts, rk = generate_hybrid_logic(rank_limit, hot_count, cold_count)
        
        ball_html = '<div class="ball-container">'
        for n in nums:
            color = "#fbc400" if n <= 9 else "#69c8f2" if n <= 19 else "#ff7272" if n <= 29 else "#aaaaaa" if n <= 39 else "#b0d840"
            ball_html += f'<div class="ball" style="background-color:{color};">{n}</div>'
        ball_html += '</div>'
        
        st.markdown(ball_html, unsafe_allow_html=True)
        st.markdown(f'<p class="report"><span class="pattern-tag">역대 {rk}위 패턴</span> 📊 설계: 홀짝 {oc}:{6-oc} / 합계 {ts} / Hot {hot_count}·Cold {cold_count}</p>', unsafe_allow_html=True)
    st.balloons()
