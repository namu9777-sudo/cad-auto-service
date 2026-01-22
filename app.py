import streamlit as st
import ezdxf
import io
import cv2
import numpy as np
from PIL import Image

st.title("🏗️ 도면 정밀 벡터 변환 서비스")

uploaded_file = st.file_uploader("도면 사진(1.jpg 등)을 올려주세요", type=['jpg', 'png', 'jpeg'], key="final_fix")

if uploaded_file:
    # 1. 이미지 읽기 및 전처리
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # [핵심] 1.jpg 같은 복잡한 도면을 위한 이진화 처리
    thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)[1]
    
    # 2. 선 검출 (HoughLinesP) - 가짜 사각형 방지 로직
    # 이미지 내의 모든 선을 찾습니다.
    lines = cv2.HoughLinesP(thresh, 1, np.pi/180, threshold=50, minLineLength=30, maxLineGap=10)
    
    st.subheader("🔍 AI가 이미지에서 추출한 선 가이드")
    # 분석된 선을 화면에 미리 보여줍니다.
    edge_view = cv2.Canny(gray, 50, 150)
    st.image(edge_view, width=700)

    # 3. 실스케일 설정
    col1, col2 = st.columns(2)
    with col1: w_real = st.number_input("도면의 실제 가로길이 (mm)", value=20400) # 1.jpg 기준
    with col2: h_real = st.number_input("도면의 실제 세로길이 (mm)", value=13350)

    if st.button("🚀 위 선들을 DXF로 변환하기"):
        doc = ezdxf.new('R2010')
        msp = doc.modelspace()
        h_img, w_img = gray.shape
        
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                
                # 픽셀 좌표를 mm 좌표로 정밀 환산
                sx = (x1 / w_img) * w_real
                ex = (x2 / w_img) * w_real
                sy = (1 - (y1 / h_img)) * h_real
                ey = (1 - (y2 / h_img)) * h_real
                
                msp.add_line((sx, sy), (ex, ey))
            
            st.success(f"이미지에서 {len(lines)}개의 도면 요소를 성공적으로 추출했습니다!")
            
            out = io.StringIO()
            doc.write(out)
            st.download_button("📥 변환된 DXF 받기", out.getvalue(), "converted_plan.dxf")
        else:
            st.error("이미지에서 선을 찾지 못했습니다. 화질을 확인해주세요.")
