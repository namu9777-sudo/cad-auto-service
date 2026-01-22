import streamlit as st
import ezdxf
import io
import cv2
import numpy as np
from PIL import Image

st.title("🏗️ 도면 중심선(Center Line) 정밀 추출기")

with st.sidebar:
    st.header("⚙️ 분석 설정")
    # 선이 너무 안 나오면 민감도를 낮추고, 너무 많이 나오면 높이세요.
    sensitivity = st.slider("선 감지 민감도", 50, 200, 100)
    min_len = st.slider("최소 선 길이 (mm 단위 환산)", 50, 500, 200)

uploaded_file = st.file_uploader("연습.jpg를 올려주세요", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    # 1. 이미지 읽기 및 노이즈 필터링
    image = Image.open(uploaded_file).convert('RGB')
    img_np = np.array(image)
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    
    # 가우시안 블러로 잔선(글자 등)을 흐리게 처리
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    
    st.image(edges, caption="AI가 인식한 골조 가이드 (흰색 선만 DXF로 변환됩니다)", width=600)

    if st.button("🚀 중심선 DXF 생성"):
        # 2. 직선 검출 (HoughLinesP)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=sensitivity, 
                                minLineLength=min_len/10, maxLineGap=40)

        doc = ezdxf.new('R2010')
        msp = doc.modelspace()
        doc.layers.new('CENTER_LINE', dxfattribs={'color': 1}) # 빨간색 중심선

        h_img, w_img = gray.shape
        w_real, h_real = 12000, 9000 # 연습.jpg 기준 전체 치수

        if lines is not None:
            count = 0
            for line in lines:
                x1, y1, x2, y2 = line[0]
                
                # 픽셀 좌표 -> 실제 mm 좌표 변환
                sx, ex = (x1 / w_img) * w_real, (x2 / w_img) * w_real
                sy, ey = (1 - y1 / h_img) * h_real, (1 - y2 / h_img) * h_real
                
                # 삐뚤어진 선 보정 (수직/수평 최적화)
                if abs(sx - ex) < 150: ex = sx # 수직 보정
                if abs(sy - ey) < 150: ey = sy # 수평 보정

                msp.add_line((sx, sy), (ex, ey), dxfattribs={'layer': 'CENTER_LINE'})
                count += 1
            
            st.success(f"총 {count}개의 정제된 중심선을 추출했습니다!")
            
            out = io.StringIO()
            doc.write(out)
            st.download_button("📥 중심선 DXF 다운로드", out.getvalue(), "center_lines.dxf")
