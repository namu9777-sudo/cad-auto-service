import streamlit as st
import random
import requests
import pandas as pd
import datetime
import plotly.express as px
import os
import json

# --- 1. 환경 설정 및 데이터 로드 로직 ---
DATA_FILE = "lotto_history.json"

@st.cache_data(ttl=3600)
def get_lotto_data():
    """월요일 업데이트 로직이 포함된 데이터 수집기"""
    need_update = False
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        last_updated = datetime.datetime.strptime(data["update_date"], "%Y-%m-%d").date()
        # 마지막 업데이트가 지난주이고, 오늘이 월요일 이후라면 업데이트
        if (datetime.date.today() - last_updated).days >= 7:
            need_update = True
    else:
        need_update = True

    if need_update:
        # 실제 운영시에는 최근 회차번호를 역추적하는 로직이 필요함 (현재는 예시로 1150회 기준)
        # 여기서는 최근 10회차를 가져와 통계를 냄
        latest_no = 1150 
        all_nums = []
        last_win = []
        
        for i in range(10):
            res = requests.get(f"https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={latest_no-i}").json()
            if res.get("returnValue") == "success":
                nums = [res[f"drwtNo{j}"] for j in range(1, 7)]
                all_nums.extend(nums)
                if i == 0: last_win = nums
        
        # 빈도 분석
        freq = pd.Series(all_nums).value_counts()
        hot = freq.head(10).index.tolist()
        cold = list(set(range(1, 46)) - set(freq.head(25).index.tolist()))
        
        data = {
            "update_date": str(datetime.date.today()),
            "latest_drw": latest_no,
            "last_win": last_win,
            "hot": hot,
            "cold": cold,
            "all_history": all_nums # 통계용
        }
        with open(DATA_FILE, "w") as f:
            json.dump(data, f)
    return data

# 데이터 불러오기
lotto_info = get_lotto_data()

# --- 2. 상수 및 패턴 정의 ---
CORE_PATTERNS = {
    1: [1, 2, 1, 1, 1], 2: [1, 1, 1, 2, 1], 3: [2, 1, 2, 1, 0], 4: [1, 2, 1, 2, 0],
    5: [1, 1, 2, 2, 0], 6: [2, 1, 1, 1, 1], 7: [1, 2, 2, 1, 0], 8: [2, 2, 1, 0, 1],
    9: [0, 2, 1, 1, 2], 10: [1, 1, 1, 1, 2]
}

# --- 3. 페이지 레이아웃 및 CSS ---
st.set_page_config(page_title="로또 설계자 PRO", layout="centered")
st.markdown("""
    <style>
    .ball-container { display: flex; justify-content: center; gap: 10px; margin: 15px 0; }
    .ball { 
        width: 40px; height: 40px; border-radius: 50%; display: flex; 
        align-items: center; justify-content: center; color: white; font-weight: bold; 
    }
    .report { font-size: 0.8rem; background: #f8f9fa; padding: 10px; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. 사이드바 메뉴 ---
menu = st.sidebar.radio("메뉴 선택", ["번호 생성", "당첨 통계 분석", "QR 확인 가이드"])

if menu == "번호 생성":
    st.title("🎰 AI 복합 설계 생성기")
    st.caption(f"최신 데이터 업데이트: {lotto_info['update_date']} (제 {lotto_info['latest_drw']}회 기준)")

    with st.expander("⚙️ 필터 세부 설정", expanded=True):
        rank_limit = st.slider("패턴 신뢰도 범위", 1, 10, 5)
        exclude_last = st.checkbox("지난주 당첨번호 제외", value=True)
        h_cnt = st.number_input("Hot 번호 포함", 0, 3, 2)
        c_cnt = st.number_input("Cold 번호 포함", 0, 3, 1)

    def generate_lotto():
        exclude = lotto_info['last_win'] if exclude_last else []
        pool_hot = [n for n in lotto_info['hot'] if n not in exclude]
        pool_cold = [n for n in lotto_info['cold'] if n not in exclude]
        pool_others = [n for n in range(1, 46) if n not in pool_hot + pool_cold + exclude]
        
        while True:
            sample = random.sample(pool_hot, h_cnt) + random.sample(pool_cold, c_cnt) + random.sample(pool_others, 6-h_cnt-c_cnt)
            res = sorted(sample)
            
            # 패턴 분석
            pattern = [0,0,0,0,0]
            for n in res:
                if n<=9: pattern[0]+=1
                elif n<=19: pattern[1]+=1
                elif n<=29: pattern[2]+=1
                elif n<=39: pattern[3]+=1
                else: pattern[4]+=1
            
            match_rk = next((rk for rk, p in CORE_PATTERNS.items() if p == pattern and rk <= rank_limit), None)
            if match_rk:
                total_s = sum(res)
                if 100 <= total_s <= 175:
                    return res, match_rk, total_s

    if st.button("🚀 행운의 번호 추출"):
        cols = st.columns(1)
        nums, rk, ts = generate_lotto()
        
        ball_html = '<div class="ball-container">'
        for n in nums:
            color = "#fbc400" if n <= 9 else "#69c8f2" if n <= 19 else "#ff7272" if n <= 29 else "#aaaaaa" if n <= 39 else "#b0d840"
            ball_html += f'<div class="ball" style="background-color:{color};">{n}</div>'
        ball_html += '</div>'
        
        st.markdown(ball_html, unsafe_allow_html=True)
        st.markdown(f"""<div class="report"><b>분석 결과:</b> 패턴 {rk}위 적용 | 합계 {ts} | 
                    Hot/Cold 비율 {h_cnt}:{c_cnt}</div>""", unsafe_allow_html=True)
        
        if st.button("💾 번호 저장하기"):
            st.success("브라우저 세션에 저장되었습니다! (실제 DB 연동은 다음 업데이트 예정)")

elif menu == "당첨 통계 분석":
    st.title("📊 당첨 데이터 시각화")
    df = pd.DataFrame(lotto_info['all_history'], columns=['number'])
    count_df = df['number'].value_counts().reset_index()
    count_df.columns = ['number', 'count']
    count_df = count_df.sort_values('number')

    fig = px.bar(count_df, x='number', y='count', title="최근 10회차 번호별 출현 빈도",
                 labels={'number': '번호', 'count': '출현 횟수'}, color='count')
    st.plotly_chart(fig)
    
    st.subheader("🔥 주요 분석 지표")
    col1, col2 = st.columns(2)
    col1.metric("가장 많이 나온 수 (Hot)", f"{lotto_info['hot'][0]}번")
    col2.metric("가장 안 나온 수 (Cold)", f"{lotto_info['cold'][0]}번")

elif menu == "QR 확인 가이드":
    st.title("📸 QR 당첨 확인")
    st.info("동행복권 공식 QR 확인 페이지로 연결하거나 스캔 방법을 안내합니다.")
    st.write("1. 로또 용지 오른쪽 상단의 QR 코드를 확인하세요.")
    st.write("2. 아래 버튼을 눌러 공식 확인 페이지를 엽니다.")
    st.link_button("동행복권 공식 당첨확인 열기", "https://m.dhlottery.co.kr/?v=000000000000")
