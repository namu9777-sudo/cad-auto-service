import streamlit as st
import ezdxf
import io

st.set_page_config(page_title="건축가 자동 도면 생성기", layout="centered")
st.title("🏗️ 1초 CAD 도면 변환 서비스")
st.info("치수를 입력하면 200mm 벽체가 포함된 DXF 파일을 즉시 생성합니다.")

# 입력창 구성
col1, col2 = st.columns(2)
with col1:
    w = st.number_input("가로 전체 치수 (mm)", value=15000, step=100)
with col2:
    h = st.number_input("세로 전체 치수 (mm)", value=8000, step=100)

if st.button("🚀 도면 생성 및 다운로드"):
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()
    t = 200 # 벽 두께
    h_t = t / 2

    def add_wall(s, e):
        msp.add_line(s, e, dxfattribs={'layer': 'CENTER', 'color': 1})
        if s[1] == e[1]: # 수평벽
            msp.add_line((s[0], s[1]+h_t), (e[0], s[1]+h_t))
            msp.add_line((s[0], s[1]-h_t), (e[0], s[1]-h_t))
        else: # 수직벽
            msp.add_line((s[0]+h_t, s[1]), (s[0]+h_t, e[1]))
            msp.add_line((s[0]-h_t, s[1]), (s[0]-h_t, e[1]))

    # 외곽벽 자동 생성
    add_wall((0,0), (w,0))
    add_wall((w,0), (w,h))
    add_wall((w,h), (0,h))
    add_wall((0,h), (0,0))
    
    # 다운로드 처리
    out = io.StringIO()
    doc.write(out)
    st.download_button("📥 내 컴퓨터로 캐드 파일 받기", out.getvalue(), "plan.dxf")
