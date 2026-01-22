import streamlit as st
import random

# 블로그 삽입을 위한 여백 최소화 설정
st.set_page_config(page_title="로또 분석기", layout="centered")

# CSS: 글씨 크기를 블로그 본문에 맞게 단정하게 조절
st.markdown("""
    <style>
    .main { padding-top: 0rem; }
    h1 { font-size: 1.6rem !important; color: #333; margin-bottom: 0.5rem; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; background-color: #f0f2f6; }
    .stSelectSlider { margin-bottom: 2rem; }
    </style>
    """, unsafe_allow_html=True)

st.title("📐 스마트 로또 분석기기")
st.caption("통계적 필터링 기반 번호 조합")

# 데이터 정의 (오타 수정 완료: cold_nums로 통일)
hot_nums = [1, 14, 27, 34, 45, 11, 23, 5, 18, 39]
cold_nums = [2, 9, 16, 22, 31, 40, 3, 10, 25, 44]

def get_balanced_nums():
    while True:
        # 핫/콜드 추출 시 변수명 일치 확인
        sample = random.sample(hot_nums, 2) + random.sample(cold_nums, 1) + random.sample(range(1, 46), 3)
        res = sorted(list(set(sample)))
        if len(res) != 6: continue
        
        odd_c = len([n for n in res if n % 2 != 0])
        total_s = sum(res)
        
        # 필터링 조건: 홀짝 비율 2:4~4:2 및 총합 100~175
        if odd_c in [2, 3, 4] and 100 <= total_s <= 175:
            return res, odd_c, total_s

# 슬라이더 디자인 개선
game_count = st.select_slider("생성할 게임 수", options=[1, 3, 5], value=3)

if st.button("🚀 행운의 조합 설계 시작"):
    st.write("")
    for i in range(game_count):
        nums, oc, ts = get_balanced_nums()
        
        # 번호를 공 모양으로 예쁘게 표시
        cols = st.columns(6)
        for idx, n in enumerate(nums):
            # 로또 공 공식 색상 적용
            color = "#fbc400" if n <= 10 else "#69c8f2" if n <= 20 else "#ff7272" if n <= 30 else "#aaaaaa" if n <= 40 else "#b0d840"
            cols[idx].markdown(f"""
                <div style="background-color:{color}; color:white; border-radius:50%; 
                width:32px; height:32px; display:flex; align-items:center; justify-content:center; 
                font-weight:bold; font-size:13px; margin:auto; box-shadow: 1px 1px 2px #ccc;">{n}</div>
                """, unsafe_allow_html=True)
        st.caption(f"📊 분석결과: 홀짝 {oc}:{6-oc} / 번호총합 {ts}")
        st.write("") 

    st.toast("추출이 완료되었습니다!")
