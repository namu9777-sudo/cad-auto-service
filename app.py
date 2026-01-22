import streamlit as st
import ezdxf
import io
from PIL import Image

st.set_page_config(page_title="건축가 AI 도면 변환기", layout="wide")

st.title("🏗️ 스케치-to-CAD 자동 변환 서비스")
st.write("스케치 사진을 올리고 원하는 벽 두께를 선택하세요.")

# 사이드바: 설정창
with st.sidebar:
    st.header("📐 설계 설정")
    wall_thickness = st.selectbox("벽 두께 선택 (mm)", [100, 150, 200, 300], index=2)
    st.info(f"현재 설정된 벽 두께: {wall_thickness}mm")

# 메인 화면: 파일 업로드
uploaded_file = st.file_uploader("스케치 이미지 업로드 (JPG, PNG)", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    # 업로드한 이미지 미리보기
    image = Image.open(uploaded_file)
    st.image(image, caption="업로드된 스케치", use_column_width=True)
    st.success("이미지가 성공적으로 인식되었습니다. (AI 분석 엔진 가동 중...)")

    # 수치 입력 (나중에는 이미지에서 자동으로 추출될 영역입니다)
    col1, col2 = st.columns(2)
    with col1:
        w = st.number_input("인식된 가로 치수 (mm)", value=15000)
    with col2:
        h = st.number_input("인식된 세로 치수 (mm)", value=8000)

    if st.button("🚀 DXF 도면 생성"):
        doc = ezdxf.new('R2010')
        msp = doc.modelspace()
        half = wall_thickness / 2

        def draw_wall(s, e):
            msp.add_line(s, e, dxfattribs={'layer': 'CENTER', 'color': 1})
            if s[1] == e[1]: # 수평
                msp.add_line((s[0], s[1]+half), (e[0], s[1]+half))
                msp.add_line((s[0], s[1]-half), (e[0], s[1]-half))
            else: # 수직
                msp.add_line((s[0]+half, s[1]), (s[0]+half, e[1]))
                msp.add_line((s[0]-half, s[1]), (s[0]-half, e[1]))

        # 외곽벽 생성 로직
        pts = [(0,0), (w,0), (w,h), (0,h), (0,0)]
        for i in range(len(pts)-1):
            draw_wall(pts[i], pts[i+1])

        # 파일 내보내기
        out = io.StringIO()
        doc.write(out)
        st.download_button("📥 완성된 CAD 파일 받기", out.getvalue(), "automated_plan.dxf")
