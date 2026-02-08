import streamlit as st
import random
import requests
import pandas as pd
import datetime
import plotly.express as px
import time

# --- 1. 상수 및 패턴 데이터 (핵심 로직) ---
GROUPS = {
    1: list(range(1, 10)), 10: list(range(10, 20)), 
    20: list(range(20, 30)), 30: list(range(30, 40)), 40: list(range(40, 46))
}

# 상위 20위 패턴 데이터
CORE_PATTERNS = {
    1: [1, 2, 1, 1, 1], 2: [1, 1, 1, 2, 1], 3: [2, 1, 2, 1, 0], 4: [1, 2, 1, 2, 0],
    5: [1, 1, 2, 2, 0], 6: [2, 1, 1, 1, 1], 7: [1, 2, 2, 1, 0], 8: [2, 2, 1, 0, 1],
    9: [0, 2, 1, 1, 2], 10: [1, 1, 1, 1, 2], 11: [1, 2, 1, 1, 1], 12: [2, 1, 1, 1, 1],
    13: [0, 1, 2, 1, 2], 14: [2, 2, 1, 1, 0], 15: [1, 2, 2, 1, 0], 16: [2, 1, 1, 2, 0],
    17: [0, 1, 1, 3, 1], 18: [1, 2, 0, 2, 1], 19: [2, 2, 0, 1, 1], 20: [2, 0, 2, 1, 1]
}

# --- 2. 데이터 수집 엔진 ---
@st.cache_data(ttl=3600)
def get_lotto_data():
    base_date = datetime.date(2023, 12, 2)  
    base_no = 1096
    days_diff = (datetime.date.today() - base_date).days
    latest_no = base_no + (days_diff // 7)
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"}
    all_nums, last_win = [], [1, 10, 20, 30, 40, 45]

    try:
        for i in range(10):
            res = requests.get(f"https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={latest_no-i}", headers=headers, timeout=5)
            if res.status_code == 200:
                try:
                    data = res.json()
                    if data.get("returnValue") == "success":
                        nums = [data[f"drwtNo{j}"] for j in range(1, 7)]
                        all_nums.extend(nums)
                        if i == 0: last_win = nums
                except: continue
            time.sleep(0.1)
    except: pass

    if not all_nums: all_nums = last_win * 5
    freq = pd.Series(all_nums).value_counts()
    return {
        "latest_drw": latest_no, "last_win": last_win,
        "hot": freq.head(15).index.tolist(),
        "cold": list(set(range(1, 46)) - set(freq.head(28).index.tolist())),
        "all_history": all_nums
    }

lotto_info = get_lotto_data()

# --- 3. 디자인 및 UI ---
st.set_page_config(page_title="로또 설계자 PRO", layout="centered")
st.markdown("""
    <style>
    .ball-container { display: flex; justify-content: center; gap: 8px; margin: 15px 0; flex-wrap: wrap; }
    .ball { 
        width: 38px; height: 38px; border-radius: 50%; display: flex; 
        align-items: center; justify-content: center; color: white; font-weight: 800; font-size: 14px;
        box-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    .report-card { background: #fdfdfd; padding: 12px; border-radius: 10px; border: 1px solid #eee; margin-top: 10px; font-size: 14px; }
    .pattern-tag { background: #e1f5fe; color: #01579b; padding: 2px 8px; border-radius: 5px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

menu = st.sidebar.radio("📋 메뉴", ["🏠 번호 생성기", "📊 통계 분석", "✅ 당첨 확인"])

if menu == "🏠 번호 생성기":
    st.title("🎰 AI 복합 설계 생성기")
    
    with st.expander("⚙️ 필터 및 패턴 설정", expanded=True):
        rank_limit = st.slider("확률 패턴 범위 (상위 n위)", 1, 20, 10) #
        col1, col2 = st.columns(2)
        with col1:
            h_cnt = st.number_input("Hot 번호 포함", 0, 4, 2)
            exclude_last = st.checkbox("지난주 번호 제외", value=True)
        with col2:
            c_cnt = st.number_input("Cold 번호 포함", 0, 4, 1)

    if st.button("🚀 설계 조건으로 번호 추출", use_container_width=True):
        def generate_with_pattern():
            excl = lotto_info['last_win'] if exclude_last else []
            pool_hot = [n for n in lotto_info['hot'] if n not in excl]
            pool_cold = [n for n in lotto_info['cold'] if n not in excl]
            others = [n for n in range(1, 45) if n not in (pool_hot + pool_cold + excl)]
            
            for _ in range(1000): # 패턴 매칭을 위해 반복 시도
                sample = random.sample(pool_hot, h_cnt) + random.sample(pool_cold, c_cnt) + random.sample(others, 6-h_cnt-c_cnt)
                res = sorted(list(set(sample)))
                if len(res) != 6: continue
                
                # 번호대 패턴 계산
                pattern = [0, 0, 0, 0, 0]
                for n in res:
                    if n <= 9: pattern[0] += 1
                    elif n <= 19: pattern[1] += 1
                    elif n <= 29: pattern[2] += 1
                    elif n <= 39: pattern[3] += 1
                    else: pattern[4] += 1
                
                # CORE_PATTERNS 매칭 확인
                matched_rank = next((rk for rk, p in CORE_PATTERNS.items() if p == pattern and rk <= rank_limit), None)
                
                if matched_rank:
                    total_s = sum(res)
                    odd_c = len([n for n in res if n % 2 != 0])
                    # 추가 필터: 합계 100~175 & 홀짝 비율 2:4 ~ 4:2
                    if 100 <= total_s <= 175 and odd_c in [2, 3, 4]:
                        return res, matched_rank, total_s, odd_c
            return None

        result = generate_with_pattern()
        if result:
            nums, rk, ts, oc = result
            ball_html = '<div class="ball-container">'
            for n in nums:
                color = "#fbc400" if n <= 9 else "#69c8f2" if n <= 19 else "#ff7272" if n <= 29 else "#aaaaaa" if n <= 39 else "#b0d840"
                ball_html += f'<div class="ball" style="background-color:{color};">{n}</div>'
            ball_html += '</div>'
            st.markdown(ball_html, unsafe_allow_html=True)
            st.markdown(f"""<div class='report-card'>
                <span class='pattern-tag'>역대 {rk}위 패턴 적용</span><br>
                <b>합계:</b> {ts} | <b>홀짝:</b> {oc}:{6-oc} | <b>Hot/Cold:</b> {h_cnt}:{c_cnt}
                </div>""", unsafe_allow_html=True)
            st.balloons()
        else:
            st.warning("설정하신 조건(패턴 순위 및 Hot/Cold 개수)이 너무 까다롭습니다. 범위를 넓혀주세요.")

elif menu == "📊 통계 분석":
    st.title("📊 번호별 출현 빈도 (최근 10회)")
    df = pd.DataFrame(lotto_info['all_history'], columns=['번호'])
    cnt = df['번호'].value_counts().sort_index().reset_index()
    cnt.columns = ['번호', '출현횟수']
    fig = px.bar(cnt, x='번호', y='출현횟수', color='출현횟수', color_continuous_scale='Reds')
    st.plotly_chart(fig)

elif menu == "✅ 당첨 확인":
    st.title("✅ 당첨 확인")
    st.link_button("📲 동행복권 공식 모바일 확인", "https://m.dhlottery.co.kr/")
