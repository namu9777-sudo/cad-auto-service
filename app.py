import streamlit as st
import ezdxf
import io
import cv2
import numpy as np
from PIL import Image

st.title("🏗️ 도면 정밀 선 최적화 변환기")

uploaded_file = st.file_uploader("도면 스케치 업로드", type=['jpg', 'png', 'jpeg'], key="final_vector")

if uploaded_file:
    # 1. 이미지 로드 및 노이즈 제거
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # [핵심] 1. 선을 굵게 만들어 끊어진 부분을 연결 (Morphology)
    kernel = np.ones((3,3), np.uint8)
    thresh = cv2.threshold(gray, 210, 255, cv2.THRESH_BINARY_INV)[1]
    dilated = cv2.dilate(thresh, kernel, iterations=1)
    
    # 2. 정밀 선 추출 (파편화 방지 옵션 강화)
    # minLineLength를 높여 짧은 먼지 선을 제거하고, maxLineGap을 높여 끊어진 선을 잇습니다.
    lines = cv2.HoughLinesP(dilated, 1, np.pi/180, threshold=50, 
                            minLineLength=80, maxLineGap=40)
    
    st.subheader("🔍 AI 선 최적화 미리보기")
    st.image(dilated, caption="연결된 도면 골조", width=600)

    # 3. 실스케일 설정
    col1, col2 = st.columns(2)
    with col1: w_real = st.number_input("가로 치수(mm)", value=12000)
    with col2: h_real = st.number_input("세로 치수(mm)", value=9000)

    if st.button("🚀 깔끔한 직선으로 DXF 생성"):
        doc = ezdxf.new('R2010')
        msp = doc.modelspace()
        h_img, w_img = gray.shape
        
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                
                # 좌표 변환
                sx = (x1 / w_img) * w_real
                ex = (x2 / w_img) * w_real
                sy = (1 - (y1 / h_img)) * h_real
                ey = (1 - (y2 / h_img)) * h_real
                
                # 수평/수직 보정 (살짝 삐뚤어진 선을 직선으로 잡기)
                if abs(sx - ex) < 50: ex = sx  # 수직보정
                if abs(sy - ey) < 50: ey = sy  # 수평보정
                
                msp.add_line((sx, sy), (ex, ey))
            
            st.success("도면 선 최적화 완료!")
            
            out = io.StringIO()
            doc.write(out)
            st.download_button("📥 최적화 DXF 다운로드", out.getvalue(), "vector_plan.dxf")
