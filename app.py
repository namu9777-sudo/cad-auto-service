import streamlit as st
import ezdxf
import io
import cv2
import numpy as np
from PIL import Image

st.title("🏗️ AI 도면 뼈대 정밀 추출기")

with st.sidebar:
    wall_t = st.number_input("벽체 두께 (mm)", value=200)
    # [새 기능] 선 인식 민감도 조절 (너무 많이 나오면 숫자를 높이세요)
    line_sens = st.slider("선 인식 민감도", 50, 200, 120) 

uploaded_file = st.file_uploader("스케치 사진 업로드", type=['jpg', 'png', 'jpeg'], key="clean_wall")

if uploaded_file:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # [핵심] 노이즈 제거를 위해 이미지를 살짝 뭉뚱그립니다.
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY_INV)[1]

    # [핵심] 주요 중심선만 추출 (짧은 선 무시)
    lines = cv2.HoughLinesP(thresh, 1, np.pi/180, threshold=line_sens, 
                            minLineLength=150, maxLineGap=30)

    if st.button("🚀 깔끔한 도면으로 생성"):
        doc = ezdxf.new('R2010')
        msp = doc.modelspace()
        doc.layers.new('CENTER', dxfattribs={'color': 1}) # 중심선(빨강)
        doc.layers.new('WALL', dxfattribs={'color': 7})   # 벽체선(흰색)

        h_img, w_img = gray.shape
        w_real, h_real = 12000, 9000 # 기준 스케일

        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                sx, ex = (x1/w_img)*w_real, (x2/w_img)*w_real
                sy, ey = (1-y1/h_img)*h_real, (1-y2/h_img)*h_real

                # 수평/수직이 확실한 선만 벽체로 인정
                is_horizontal = abs(sy - ey) < 100
                is_vertical = abs(sx - ex) < 100

                if is_horizontal or is_vertical:
                    # 중심선 그리기
                    msp.add_line((sx, sy), (ex, ey), dxfattribs={'layer': 'CENTER'})
                    
                    # 벽체 오프셋 (양옆으로)
                    d = wall_t / 2
                    if is_horizontal:
                        msp.add_line((sx, sy+d), (ex, ey+d), dxfattribs={'layer': 'WALL'})
                        msp.add_line((sx, sy-d), (ex, ey-d), dxfattribs={'layer': 'WALL'})
                    else:
                        msp.add_line((sx+d, sy), (ex+d, ey), dxfattribs={'layer': 'WALL'})
                        msp.add_line((sx-d, sy), (ex-d, ey), dxfattribs={'layer': 'WALL'})

            st.success("노이즈를 제거하고 주요 벽체를 추출했습니다!")
            out = io.StringIO()
            doc.write(out)
            st.download_button("📥 정돈된 DXF 다운로드", out.getvalue(), "clean_plan.dxf")
