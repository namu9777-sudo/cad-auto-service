import streamlit as st
import ezdxf
import io
import numpy as np
import cv2
import easyocr
from PIL import Image

# AI 엔진 초기화 (한 번만 실행되도록 캐싱)
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en']) # 숫자와 영문 인식

reader = load_ocr()

st.title("🏗️ AI 건축 도면 자동 분석 서비스")

uploaded_file = st.file_uploader("스케치 사진을 올려주세요", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    image = Image.open(uploaded_file)
    img_array = np.array(image)
    st.image(image, caption="업로드된 도면", width=500)
    
    with st.spinner('AI가 치수를 분석 중입니다...'):
        # AI가 이미지에서 텍스트(숫자) 추출
        result = reader.readtext(img_array)
        detected_numbers = [text for (bbox, text, prob) in result if text.isdigit()]
        
    st.success(f"분석 완료! 이미지에서 {len(detected_numbers)}개의 치수를 발견했습니다.")

    # AI가 찾은 숫자 중 가장 큰 값을 가로/세로 기본값으로 제안
    default_w = int(detected_numbers[0]) if len(detected_numbers) > 0 else 12000
    default_h = int(detected_numbers[1]) if len(detected_numbers) > 1 else 9000

    col1, col2 = st.columns(2)
    with col1: w = st.number_input("인식된 가로 (mm)", value=default_w)
    with col2: h = st.number_input("인식된 세로 (mm)", value=default_h)

    if st.button("🚀 분석된 데이터로 DXF 생성"):
        # (여기에 어제 만든 레이어별 벽체/문/창문 생성 로직이 들어갑니다)
        st.info("현재 단계: 인식된 치수 기반으로 정밀 도면을 생성합니다.")
        # ... (이하 ezdxf 생성 코드 생략) ...
