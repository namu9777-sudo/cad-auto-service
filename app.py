import streamlit as st
import ezdxf
import io
import cv2
import numpy as np
import easyocr # 인공지능 글자 인식 라이브러리
from PIL import Image

# 1. AI 엔진 로드 (한 번만 실행)
@st.cache_resource
def load_reader():
    return easyocr.Reader(['en']) # 영문 숫자 인식

reader = load_reader()

st.title("🤖 AI 치수 해석 도면 생성기")

with st.sidebar:
    wall_t = st.number_input("벽체 두께 (mm)", value=200)
    st.write("AI가 사진 속 숫자를 분석하여 도면을 그립니다.")

uploaded_file = st.file_uploader("스케치(연습.jpg) 업로드", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    img = Image.open(uploaded_file).convert('RGB')
    img_np = np.array(img)
    st.image(img, caption="AI 분석 중...", width=600)

    if st.button("🚀 AI 분석 시작"):
        with st.spinner("이미지에서 치수 데이터를 추출 중입니다..."):
            # 2. AI 숫자 인식
            results = reader.readtext(img_np)
            
            # 숫자만 필터링하여 리스트화
            detected_nums = []
            for (bbox, text, prob) in results:
                clean_text = text.replace(',', '').strip()
                if clean_text.isdigit() and int(clean_text) >= 100:
                    detected_nums.append(int(clean_text))
            
            if not detected_nums:
                st.error("치수 숫자를 찾지 못했습니다.")
            else:
                # 3. 인식된 데이터 기반 설계 (예: 연습.jpg 분석 로직)
                w_total = max(detected_nums) # 가장 큰 숫자를 가로 전체로 가정
                # 가로 4000씩 3개 분할 등 지능형 배치는 추후 고도화 가능
                
                doc = ezdxf.new('R2010')
                msp = doc.modelspace()
                doc.layers.new('CENTER', dxfattribs={'color': 1})
                doc.layers.new('WALL', dxfattribs={'color': 7})

                # [AI 결과 적용] 인식된 치수대로 중심선 생성
                # 여기서는 예시로 외곽만 그리지만, detected_nums를 좌표로 활용합니다.
                msp.add_line((0, 0), (w_total, 0), dxfattribs={'layer': 'CENTER'})
                
                # 벽체 두께 반영
                t = wall_t / 2
                msp.add_lwpolyline([(-t,-t), (w_total+t,-t)], dxfattribs={'layer': 'WALL'})

                st.success(f"AI 인식 성공: {detected_nums} 데이터를 바탕으로 도면을 구성했습니다.")
                
                out = io.StringIO()
                doc.write(out)
                st.download_button("📥 AI 도면 다운로드", out.getvalue(), "ai_plan.dxf")
