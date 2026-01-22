import streamlit as st
import ezdxf
import io
import cv2
import numpy as np
from PIL import Image

st.title("🏗️ 내부 벽체 자동 생성 도면 변환기")

with st.sidebar:
    wall_t = st.number_input("벽체 두께 설정 (mm)", value=200)
    st.info("스케치의 선들을 분석해 중심선과 벽체를 동시에 그립니다.")

uploaded_file = st.file_uploader("스케치 사진을 올려주세요", type=['jpg', 'png', 'jpeg'], key="wall_fix")

if uploaded_file:
    # 1. 이미지 로드 및 전처리 (노이즈 제거)
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)[1]

    # 2. 중심선 검출 (긴 선들 위주로 추출)
    lines = cv2.HoughLinesP(thresh, 1, np.pi/180, threshold=80, minLineLength=100, maxLineGap=50)

    if st.button("🚀 내부 벽체 포함 DXF 생성"):
        doc = ezdxf.new('R2010')
        msp = doc.modelspace()
        
        # 레이어 설정
        doc.layers.new('CENTER_LINE', dxfattribs={'color': 1}) # 빨간색
        doc.layers.new('WALL_LINE', dxfattribs={'color': 7})   # 흰색

        h_img, w_img = gray.shape
        w_real, h_real = 12000, 9000 # 기준 치수 (스케치에 맞춰 자동 조절 가능)

        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                
                # 좌표 변환 (mm 단위)
                sx = (x1 / w_img) * w_real
                ex = (x2 / w_img) * w_real
                sy = (1 - (y1 / h_img)) * h_real
                ey = (1 - (y2 / h_img)) * h_real

                # [핵심] 1. 중심선 그리기
                msp.add_line((sx, sy), (ex, ey), dxfattribs={'layer': 'CENTER_LINE'})

                # [핵심] 2. 중심선 양옆으로 벽체선 생성 (Offset 효과)
                dist = wall_t / 2
                if abs(sx - ex) > abs(sy - ey): # 수평선인 경우
                    msp.add_line((sx, sy + dist), (ex, ey + dist), dxfattribs={'layer': 'WALL_LINE'})
                    msp.add_line((sx, sy - dist), (ex, ey - dist), dxfattribs={'layer': 'WALL_LINE'})
                else: # 수직선인 경우
                    msp.add_line((sx + dist, sy), (ex + dist, ey), dxfattribs={'layer': 'WALL_LINE'})
                    msp.add_line((sx - dist, sy), (ex - dist, ey), dxfattribs={'layer': 'WALL_LINE'})

            st.success(f"내부 벽체를 포함하여 도면 생성을 완료했습니다!")
            
            out = io.StringIO()
            doc.write(out)
            st.download_button("📥 완성된 DXF 다운로드", out.getvalue(), "full_wall_plan.dxf")
