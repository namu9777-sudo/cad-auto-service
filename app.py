import streamlit as st
import ezdxf
import io
import numpy as np
from PIL import Image

st.set_page_config(layout="wide") # 넓은 화면 모드
st.title("🏗️ 스케치-수치 동기화 도면 생성기")

# 1. 화면 분할: 왼쪽(스케치 확인), 오른쪽(수치 입력 및 생성)
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📸 스케치 확인")
    uploaded_file = st.file_uploader("도면 스케치 업로드", type=['jpg', 'png', 'jpeg'])
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, use_container_width=True, caption="스케치에 적힌 치수를 확인하세요.")

with col2:
    st.subheader("📏 수치 입력 (설계 데이터)")
    wall_t = st.number_input("벽체 두께 (mm)", value=200)
    
    # [핵심] 스케치를 보고 수치를 입력하면 즉시 반영됩니다.
    x_input = st.text_input("가로 치수 구성 (예: 4000, 4000, 4000)", "4000, 4000, 4000")
    y_input = st.text_input("세로 치수 구성 (예: 4000, 3500, 1500)", "4000, 3500, 1500")

    if st.button("🚀 입력한 치수로 정밀 DXF 생성"):
        try:
            x_list = [float(x.strip()) for x in x_input.split(",")]
            y_list = [float(y.strip()) for y in y_input.split(",")]
            total_w, total_h = sum(x_list), sum(y_list)

            doc = ezdxf.new('R2010')
            msp = doc.modelspace()
            doc.layers.new('CENTER', dxfattribs={'color': 1}) # 중심선: 빨강
            doc.layers.new('WALL', dxfattribs={'color': 7})   # 벽체선: 흰색

            # 가로/세로 중심선 생성 로직
            cur_x = 0
            for dx in [0] + x_list:
                cur_x += dx
                msp.add_line((cur_x, 0), (cur_x, total_h), dxfattribs={'layer': 'CENTER'})
            
            cur_y = 0
            for dy in [0] + y_list:
                cur_y += dy
                msp.add_line((0, cur_y), (total_w, cur_y), dxfattribs={'layer': 'CENTER'})

            # 벽체 자동 오프셋 생성
            t = wall_t / 2
            # 외곽벽 생성
            msp.add_lwpolyline([(-t,-t), (total_w+t,-t), (total_w+t,total_h+t), (-t,total_h+t), (-t,-t)], dxfattribs={'layer': 'WALL'})
            msp.add_lwpolyline([(t,t), (total_w-t,t), (total_w-t,total_h-t), (t,total_h-t), (t,t)], dxfattribs={'layer': 'WALL'})

            st.success(f"성공! {total_w}x{total_h} 도면이 생성되었습니다.")
            out = io.StringIO()
            doc.write(out)
            st.download_button("📥 정밀 DXF 받기", out.getvalue(), "architect_plan.dxf")
        except:
            st.error("치수 입력 형식을 확인해 주세요 (예: 4000, 3000)")
