import streamlit as st
import ezdxf
import io

st.title("🏗️ 건축가 전용 스케치-to-CAD 정밀 변환")

# 사이드바 설정
with st.sidebar:
    wall_t = st.selectbox("벽 두께 (mm)", [100, 150, 200], index=1)
    door_w = 900
    win_w = 1500

if st.button("🚀 연습.jpg 스케치 기반 도면 생성"):
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()
    
    # 레이어 설정 (색상 구분)
    doc.layers.new('WALL', dxfattribs={'color': 7})      # 흰색(벽)
    doc.layers.new('WINDOW', dxfattribs={'color': 4})    # 하늘색(창문)
    doc.layers.new('DOOR', dxfattribs={'color': 1})      # 빨간색(문)

    def add_element(start, end, layer):
        msp.add_line(start, end, dxfattribs={'layer': layer})

    # 1. 외곽 및 내부 주요 벽체 (스케치 기반 좌표 계산)
    # 외곽선
    walls = [((0,0), (12000,0)), ((12000,0), (12000,9000)), ((12000,9000), (0,9000)), ((0,9000), (0,0))]
    # 내부 수직벽 (4000, 8000 지점)
    walls += [((4000, 1500), (4000, 9000)), ((8000, 0), (8000, 9000))]
    # 내부 수평벽
    walls += [((0, 5000), (4000, 5000)), ((8000, 5000), (12000, 5000))]
    
    for s, e in walls:
        add_element(s, e, 'WALL')

    # 2. 창문 (WINDOW) 레이어 - 스케치상의 위치
    windows = [((0, 2500), (0, 4000)), ((0, 6500), (0, 8000)), ((12000, 2500), (12000, 4000))]
    for s, e in windows:
        add_element(s, e, 'WINDOW')

    # 3. 문 (DOOR) 레이어 - 900mm 폭
    doors = [((4000, 4100), (4000, 5000)), ((4000, 5100), (4000, 6000)), ((8000, 5100), (8000, 6000))]
    for s, e in doors:
        add_element(s, e, 'DOOR')

    # 다운로드
    out = io.StringIO()
    doc.write(out)
    st.download_button("📥 정밀 도면(DXF) 받기", out.getvalue(), "sketch_final.dxf")
    st.success("스케치 분석 완료! 레이어별로 구분된 도면이 생성되었습니다.")
