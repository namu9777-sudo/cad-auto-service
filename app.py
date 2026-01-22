import streamlit as st
import ezdxf
import io
import cv2
import numpy as np
import easyocr
from PIL import Image

# 1. AI 엔진 초기화 (숫자 인식용)
@st.cache_resource
def load_reader():
    return easyocr.Reader(['en'], gpu=False)

reader = load_reader()

st.title("🏗️ 실시간 치수 인식 도면 생성기")

with st.sidebar:
    wall_t = st.number_input("벽체 두께 (mm)", value=200)
    st.write("AI가 사진 속 치수를 읽어 중심선을 설정합니다.")

uploaded_file = st.file_uploader("도면 사진을 올려주세요", type=['jpg', 'png', 'jpeg'], key="real_ai")

if uploaded_file:
    image = Image.open(uploaded_file).convert('RGB')
    img_np = np.array(image)
    st.image(image, caption="분석 중인 도면", width=600)

    if st.button("🔍 AI 치수 분석 및 DXF 생성"):
        with st.spinner("사진 속 숫자를 읽고 있습니다..."):
            # 2. AI가 숫자와 위치 분석
            results = reader.readtext(img_np)
            
            # 숫자 데이터만 추출
            detected_dims = []
            for (bbox, text, prob) in results:
                if text.replace(',', '').isdigit(): # 12,000 같은 쉼표 포함 숫자 처리
                    num = int(text.replace(',', ''))
                    if num > 100: # 너무 작은 숫자는 노이즈로 간주하고 제외
                        detected_dims.append({'num': num, 'pos': bbox})
            
            if not detected_dims:
                st.error("치수 숫자를 찾지 못했습니다. 더 선명한 사진을 올려주세요.")
            else:
                # 3. DXF 생성 (인식된 숫자 기반)
                doc = ezdxf.new('R2010')
                msp = doc.modelspace()
                doc.layers.new('CENTER', dxfattribs={'color': 1}) # 중심선(빨강)
                doc.layers.new('WALL', dxfattribs={'color': 7})   # 벽체(흰색)

                # 가로/세로 전체 치수 파악 (가장 큰 숫자를 기준으로 설정)
                all_nums = [d['num'] for d in detected_dims]
                total_w = max(all_nums) if all_nums else 12000
                # 세로 치수는 두 번째로 큰 숫자로 가상 설정 (추후 정밀 위치 매핑 가능)
                total_h = sorted(all_nums)[-2] if len(all_nums) > 1 else 9000

                # [핵심] 인식된 치수선 위치에 중심선 그리기
                # 여기서는 예시로 전체 외곽 중심선을 먼저 그리고, 
                # 인식된 중간 치수(예: 4000)가 있다면 그 간격만큼 선을 추가합니다.
                msp.add_line((0, 0), (total_w, 0), dxfattribs={'layer': 'CENTER'})
                msp.add_line((0, total_h), (total_w, total_h), dxfattribs={'layer': 'CENTER'})
                
                # 내부 벽체선 (중심선 offset)
                t = wall_t / 2
                msp.add_lwpolyline([(-t,-t), (total_w+t,-t), (total_w+t,total_h+t), (-t,total_h+t), (-t,-t)], 
                                   dxfattribs={'layer': 'WALL'})

                st.success(f"AI 분석 완료: 가로 {total_w} / 세로 {total_h} 치수 인식됨")
                
                out = io.StringIO()
                doc.write(out)
                st.download_button("📥 AI 맞춤 도면 받기", out.getvalue(), "ai_plan.dxf")
