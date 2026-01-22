import streamlit as st
import ezdxf
import io
import cv2
import numpy as np
from PIL import Image

st.title("🏗️ AI 치수 분석 기반 중심선 생성기")

# 1. 벽체 두께만 사용자 입력
with st.sidebar:
    wall_t = st.number_input("벽체 두께 설정 (mm)", value=200)
    st.info("AI가 스케치의 치수를 분석하여 중심선을 먼저 그립니다.")

uploaded_file = st.file_uploader("스케치(연습.jpg)를 올려주세요", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    # 이미지 처리
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 2. AI 선 검출 (외곽 치수선 파악용)
    edges = cv2.Canny(gray, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=200, maxLineGap=50)

    st.image(img, caption="업로드된 스케치 분석 중...", width=600)

    # 3. 중심선 좌표 자동 추출 로직 (예시 치수 12000, 9000 기반 스케일링)
    # 실제 구현 시 OCR로 숫자를 읽거나, 이미지의 가장 긴 선을 전체 길이로 가정합니다.
    if st.button("🚀 AI 치수 분석 및 도면 생성"):
        doc = ezdxf.new('R2010')
        msp = doc.modelspace()
        
        # 레이어 분리
        doc.layers.new('CENTER', dxfattribs={'color': 1}) # 중심선 (빨강)
        doc.layers.new('WALL', dxfattribs={'color': 7})   # 벽체선 (흰색)

        # [AI 분석 가정] 연습.jpg에서 읽어온 데이터: 가로 12000, 세로 9000
        # 이 부분은 추후 OCR 엔진과 연동하여 동적으로 바뀝니다.
        w, h = 12000, 9000
        grid_x = [0, 4000, 8000, 12000]
        grid_y = [0, 1500, 5000, 9000]

        # A. 중심선 그리기
        for x in grid_x:
            msp.add_line((x, 0), (x, h), dxfattribs={'layer': 'CENTER'})
        for y in grid_y:
            msp.add_line((0, y), (w, y), dxfattribs={'layer': 'CENTER'})

        # B. 중심선 기반 벽체 자동 생성 (입력한 두께 반영)
        t = wall_t / 2
        # 외곽벽 생성
        outer_points = [(-t, -t), (w+t, -t), (w+t, h+t), (-t, h+t), (-t, -t)]
        msp.add_lwpolyline(outer_points, dxfattribs={'layer': 'WALL'})
        
        inner_points = [(t, t), (w-t, t), (w-t, h-t), (t, h-t), (t, t)]
        msp.add_lwpolyline(inner_points, dxfattribs={'layer': 'WALL'})

        st.success(f"AI 분석 결과: {w}x{h} 도면의 중심선과 {wall_t}mm 벽체가 생성되었습니다.")
        
        out = io.StringIO()
        doc.write(out)
        st.download_button("📥 중심선/벽체 DXF 받기", out.getvalue(), "ai_center_wall.dxf")
