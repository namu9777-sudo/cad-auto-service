import streamlit as st
import ezdxf
import io
import cv2
import numpy as np
from PIL import Image

st.title("🏗️ 실무형 중심선 추출 및 벽체 생성기")

# 1. 오직 벽체 두께만 설정
with st.sidebar:
    wall_t = st.number_input("벽체 두께 (mm)", value=200)
    st.info("AI가 긴 벽체 중심선만 추출하고, 치수선 등 짧은 선은 자동으로 제거합니다.")

uploaded_file = st.file_uploader("연습.jpg를 올려주세요", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 노이즈 및 자잘한 선 제거를 위한 강력한 전처리
    blurred = cv2.medianBlur(gray, 5) 
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

    # 2. 중심선 추출 (벽체로 의심되는 긴 선만 필터링)
    # threshold를 높여서 확실한 선만 잡고, minLineLength로 치수선을 걸러냅니다.
    lines = cv2.HoughLinesP(thresh, 1, np.pi/180, threshold=150, minLineLength=250, maxLineGap=50)

    if st.button("🚀 정밀 중심선/벽체 DXF 생성"):
        doc = ezdxf.new('R2010')
        msp = doc.modelspace()
        doc.layers.new('CENTER', dxfattribs={'color': 1}) # 빨간색 중심선
        doc.layers.new('WALL', dxfattribs={'color': 7})   # 흰색 벽체선

        h_img, w_img = gray.shape
        w_real, h_real = 12000, 9000 # 연습.jpg 스케일 기준

        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                sx, ex = (x1/w_img)*w_real, (x2/w_img)*w_real
                sy, ey = (1-y1/h_img)*h_real, (1-y2/h_img)*h_real

                # [핵심] 수평/수직 보정 및 대각선(치수선 등) 제거
                is_h = abs(sy - ey) < 150 # 수평선 판단
                is_v = abs(sx - ex) < 150 # 수직선 판단

                if is_h or is_v:
                    if is_h: ey = sy # 완전한 수평으로 강제 보정
                    if is_v: ex = sx # 완전한 수직으로 강제 보정
                    
                    # 1. 빨간색 중심선 그리기
                    msp.add_line((sx, sy), (ex, ey), dxfattribs={'layer': 'CENTER'})
                    
                    # 2. 중심선 기반 벽체선 생성 (Offset)
                    d = wall_t / 2
                    if is_h:
                        msp.add_line((sx, sy+d), (ex, ey+d), dxfattribs={'layer': 'WALL'})
                        msp.add_line((sx, sy-d), (ex, ey-d), dxfattribs={'layer': 'WALL'})
                    else:
                        msp.add_line((sx+d, sy), (ex+d, ey), dxfattribs={'layer': 'WALL'})
                        msp.add_line((sx-d, sy), (ex-d, ey), dxfattribs={'layer': 'WALL'})

            st.success("치수선을 제외한 주요 중심선과 벽체가 생성되었습니다.")
            out = io.StringIO()
            doc.write(out)
            st.download_button("📥 정제된 DXF 다운로드", out.getvalue(), "architect_final.dxf")
