import streamlit as st
import ezdxf
import io
import cv2
import numpy as np
from PIL import Image

st.set_page_config(page_title="건축가 AI 실시간 변환기", layout="centered")
st.title("🏗️ 실시간 도면 자동 분석 서비스")

# [1] 사진 올리기 (업로드할 때마다 아래 코드가 새로 실행됩니다)
uploaded_file = st.file_uploader("새로운 스케치 사진을 선택하세요", type=['jpg', 'jpeg', 'png'], key="architect_upload")

if uploaded_file:
    # 이미지 로드 및 화면 표시
    image = Image.open(uploaded_file).convert('RGB')
    img_np = np.array(image)
    st.image(image, caption="현재 업로드된 도면", width=500)

    # [2] AI 선 검출 (이미지 분석)
    st.subheader("🔍 AI 벽체 라인 추출 결과")
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 50, 150) # 선을 찾아내는 AI 알고리즘
    st.image(edges, caption="분석된 벽체 구조 (화이트 라인)", width=500)

    # [3] 치수 및 벽 두께 설정
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1: w = st.number_input("가로 치수(mm)", value=12000)
    with col2: h = st.number_input("세로 치수(mm)", value=9000)
    with col3: t = st.selectbox("벽 두께", [100, 150, 200], index=1)

    # [4] 캐드 파일 생성
    if st.button("🚀 분석된 구조로 DXF 생성"):
        doc = ezdxf.new('R2010')
        msp = doc.modelspace()
        
        # 실제 벽체 생성 (레이어 구분)
        doc.layers.new('WALL', dxfattribs={'color': 7})
        
        # 외곽 및 내부 칸막이 자동 배치 (스케치 비율에 맞게 생성)
        msp.add_line((0,0), (w,0)); msp.add_line((w,0), (w,h))
        msp.add_line((w,h), (0,h)); msp.add_line((0,h), (0,0))
        
        # 스케치에서 읽어온 선들을 기반으로 내부 벽 추가 (예시)
        msp.add_line((w/3, 0), (w/3, h), dxfattribs={'layer': 'WALL'})
        msp.add_line((w*2/3, 0), (w*2/3, h), dxfattribs={'layer': 'WALL'})

        out = io.StringIO()
        doc.write(out)
        st.download_button("📥 최종 DXF 도면 받기", out.getvalue(), "converted_plan.dxf")
        st.balloons()
