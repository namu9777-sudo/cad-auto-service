import streamlit as st
import random
import time

st.set_page_config(page_title="스마트 로또 설계자", page_icon="📐")

st.title("📐 건축가 설계: 스마트 로또 추첨기")
st.write("단순 무작위가 아닌, 통계적 필터링을 거친 번호 조합입니다.")

# 1. 가상의 핫/콜드 데이터 (나중에 실제 데이터와 연동 가능)
hot_numbers = [1, 14, 27, 34, 45, 11, 23, 5, 18, 39] # 최근 자주 나온 번호
cold_numbers = [2, 9, 16, 22, 31, 40, 3, 10, 25, 44] # 최근 안 나온 번호

def generate_smart_nums():
    while True:
        # 핫 번호에서 2개, 콜드에서 1개, 나머지는 랜덤으로 섞기
        selection = random.sample(hot_numbers, 2) + \
                    random.sample(cold_numbers, 1) + \
                    random.sample(range(1, 46), 3)
        
        nums = sorted(list(set(selection))) # 중복 제거 및 정렬
        
        if len(nums) != 6: continue # 중복 발생 시 재추출
        
        # [필터링 1] 홀짝 비율 분석 (3:3, 2:4, 4:2만 허용)
        odd_c = len([n for n in nums if n % 2 != 0])
        
        # [필터링 2] 번호 총합 분석 (100 ~ 175 사이의 황금 영역)
        total_sum = sum(nums)
        
        if odd_c in [2, 3, 4] and 100 <= total_sum <= 175:
            return nums, odd_c, total_sum

# 메인 UI
with st.sidebar:
    st.header("⚙️ 분석 설정")
    num_games = st.slider("생성할 게임 수", 1, 10, 5)
    st.info("현재 '핫앤콜드'와 '홀짝 비율' 필터가 활성화되어 있습니다.")

if st.button("🚀 데이터 분석 기반 번호 추출"):
    for i in range(num_games):
        nums, odd_c, t_sum = generate_smart_nums()
        
        with st.expander(f"📍 {i+1}번째 행운의 조합 (분석 완료)", expanded=True):
            cols = st.columns(6)
            for idx, n in enumerate(nums):
                # 번호대별 색상 입히기
                color = "orange" if n <= 10 else "blue" if n <= 20 else "red" if n <= 30 else "gray" if n <= 40 else "green"
                cols[idx].markdown(f"### :{color}[{n}]")
            
            # 분석 근거 노출 (사용자 신뢰도 향상)
            st.caption(f"📊 분석 리포트: 홀짝비율({odd_c}:{6-odd_c}) | 번호총합({t_sum}) | 핫앤콜드 포함")

    st.balloons()
