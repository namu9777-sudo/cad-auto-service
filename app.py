import streamlit as st
import ezdxf
import io
import numpy as np
import easyocr
from PIL import Image

# 1. 서버 부하를 줄이기 위한 가벼운 설정
@st.cache_resource
def get_reader():
    # gpu=False를 명시하여 CPU 모드로 안정성을 높입니다.
    return easyocr.Reader(['en'], gpu=False, download_enabled=True)

st.title("🏗️ AI 건축 도면 자동 분석 서비스")

uploaded_file = st.file_uploader("스케치 사진을 올려주세요", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    image = Image.open(uploaded_file).convert('RGB') # 이미지 형식 통일
    st.image(image, caption="업로드된 도면", width=500)
    
    # 2. 분석 시작 전 사용자 알림
    if st.button("🔍 AI 치수 분석 시작"):
        with st.spinner('AI가 치수를 읽고 있습니다 (약 30초 소요)...'):
            try:
                reader = get_reader()
                img_np = np.array(image)
                result = reader.readtext(img_np)
                
                # 숫자만 골라내기
                nums = [t[1] for t in result if t[1].isdigit()]
                st.session_state['detected'] = nums
                st.success(f"분석 완료! 발견된 숫자: {', '.join(nums)}")
            except Exception as e:
                st.error("분석 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.")

    # 3. 인식된 숫자가 있을 경우 입력창에 자동 배치
    detected = st.session_state.get('detected', [])
    default_w = int(detected[0]) if len(detected) > 0 else 12000
    default_h = int(detected[1]) if len(detected) > 1 else 9000

    col1, col2 = st.columns(2)
    with col1: w = st.number_input("가로 (mm)", value=default_w)
    with col2: h = st.number_input("세로 (mm)", value=default_h)

    if st.button("🚀 DXF 도면 생성"):
        # 도면 생성 로직 실행
        st.balloons()
