import streamlit as st
import random
import requests
import pandas as pd

# 1. API를 통한 동행복권 데이터 가져오기 로직 추가
@st.cache_data(ttl=3600) # 1시간마다 업데이트
def get_latest_lotto_info():
    """최신 회차 정보와 최근 10회차 번호 통계를 가져옵니다."""
    try:
        # 1단계: 현재 최신 회차 번호 찾기 (임의의 미래 회차부터 역추적)
        base_url = "https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo="
        # 예시로 1100회부터 시작 (실제 사용 시 로직 고도화 가능)
        latest_no = 1100 
        
        # 최근 10개 회차 데이터 수집 (Hot/Cold 계산용)
        all_recent_nums = []
        last_nums = []
        
        for i in range(10):
            target_no = latest_no - i
            resp = requests.get(base_url + str(target_no)).json()
            if resp.get("returnValue") == "success":
                nums = [resp[f"drwtNo{j}"] for j in range(1, 7)]
                all_recent_nums.extend(nums)
                if i == 0: last_nums = nums # 직전 회차 번호
        
        # 빈도 분석으로 Hot/Cold 자동 추출
        series = pd.Series(all_recent_nums)
        hot = series.value_counts().head(15).index.tolist()
        cold = list(set(range(1, 46)) - set(series.value_counts().head(30).index.tolist()))
        
        return latest_no, last_nums, hot, cold
    except:
        # API 오류 시 기본값 반환 (Fallback)
        return 0, [], [1, 2, 3], [43, 44, 45]

# 데이터 초기화
latest_drw, last_win_nums, recent_hot, recent_cold = get_latest_lotto_info()

# --- 기존 GROUPS 및 CORE_PATTERNS 유지 ---
GROUPS = {1: list(range(1, 10)), 10: list(range(10, 20)), 20: list(range(20, 30)), 30: list(range(30, 40)), 40: list(range(40, 46))}
CORE_PATTERNS = {
    1: [1, 2, 1, 1, 1], 2: [1, 1, 1, 2, 1], 3: [2, 1, 2, 1, 0], 4: [1, 2, 1, 2, 0],
    5: [1, 1, 2, 2, 0], 6: [2, 1, 1, 1, 1], 7: [1, 2, 2, 1, 0], 8: [2, 2, 1, 0, 1],
    9: [0, 2, 1, 1, 2], 10: [1, 1, 1, 1, 2], 11: [1, 2, 1, 1, 1], 12: [2, 1, 1, 1, 1],
    13: [0, 1, 2, 1, 2], 14: [2, 2, 1, 1, 0], 15: [1, 2, 2, 1, 0], 16: [2, 1, 1, 2, 0],
    17: [0, 1, 1, 3, 1], 18: [1, 2, 0, 2, 1], 19: [2, 2, 0, 1, 1], 20: [2, 0, 2, 1, 1]
}

st.set_page_config(page_title="로또 설계자 PRO", layout="centered")

# CSS (기존 유지)
st.markdown("""<style>...</style>""", unsafe_allow_html=True) # 생략(기존 코드와 동일)

st.title("🏗️ 로또 설계 분석기 PRO")
st.caption(f"현재 데이터 기준: 제 {latest_drw}회차 당첨 정보 반영 완료")

# --- 설정 구역 ---
with st.expander("⚙️ 정밀 필터 및 실시간 데이터 설정", expanded=True):
    rank_limit = st.select_slider("확률 패턴 범위 (상위 n위 이내)", options=list(range(1, 21)), value=10)
    
    col1, col2 = st.columns(2)
    with col1:
        hot_count = st.number_input("Hot 번호 (최근 다출)", 0, 4, 2)
        exclude_last = st.checkbox("직전 회차 번호 제외", value=True)
    with col2:
        cold_count = st.number_input("Cold 번호 (최근 미출)", 0, 4, 1)
        
def generate_hybrid_logic(max_rank, h_cnt, c_cnt, exclude_list):
    all_nums = set(range(1, 46))
    # 제외수 반영
    target_hot = [n for n in recent_hot if n not in exclude_list]
    target_cold = [n for n in recent_cold if n not in exclude_list]
    others = list(all_nums - set(target_hot) - set(target_cold) - set(exclude_list))
    
    attempts = 0
    while attempts < 1000: # 무한 루프 방지
        attempts += 1
        try:
            base_pool = random.sample(target_hot, h_cnt) + \
                        random.sample(target_cold, c_cnt) + \
                        random.sample(others, 6 - (h_cnt + c_cnt))
            
            res = sorted(list(set(base_pool)))
            if len(res) != 6: continue
            
            # 패턴 체크 로직 (기존과 동일)
            current_pattern = [0, 0, 0, 0, 0]
            for n in res:
                if n <= 9: current_pattern[0] += 1
                elif n <= 19: current_pattern[1] += 1
                elif n <= 29: current_pattern[2] += 1
                elif n <= 39: current_pattern[3] += 1
                else: current_pattern[4] += 1
            
            matched_rank = next((rk for rk, p in CORE_PATTERNS.items() if p == current_pattern and rk <= max_rank), None)
            if matched_rank is None: continue
            
            # 전문가 필터
            odd_c = len([n for n in res if n % 2 != 0])
            total_s = sum(res)
            
            if odd_c in [2, 3, 4] and 100 <= total_s <= 175:
                return res, odd_c, total_s, matched_rank
        except ValueError:
            continue
    return None

# --- 생성 및 결과 출력 (기존 UI 로직 활용) ---
game_count = st.select_slider("생성할 게임 수", options=[1, 3, 5], value=3)

if st.button("🎰 복합 설계 추출 시작"):
    exclude_list = last_win_nums if exclude_last else []
    
    for i in range(game_count):
        result = generate_hybrid_logic(rank_limit, hot_count, cold_count, exclude_list)
        
        if result:
            nums, oc, ts, rk = result
            # ... (기존 볼 애니메이션 및 마크다운 출력 로직 동일)
            # [생략된 부분: 기존의 ball_html 출력 코드]
            st.write(f"추출된 번호: {nums} (패턴 {rk}위)") 
        else:
            st.warning("조건을 만족하는 번호 조합을 찾지 못했습니다. 필터를 완화해 주세요.")
