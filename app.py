import streamlit as st
from streamlit_webrtc import webrtc_streamer
import av
import cv2
import numpy as np

st.title("📐 ArchEye: Live Vision")
st.write("Point your camera at a building to see its **Structural Soul**.")

def video_frame_callback(frame):
    img = frame.to_ndarray(format="bgr24")

    # 1. 건물의 선 추출 (Edge Detection)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200) # 수치는 현장 광량에 따라 조절
    
    # 2. 선을 흰색으로 강조하고 원본과 합성
    edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    output = cv2.addWeighted(img, 0.7, edges_colored, 0.3, 0)

    return av.VideoFrame.from_ndarray(output, format="bgr24")

# 실시간 스트리밍 시작
webrtc_streamer(key="archeye-live", video_frame_callback=video_frame_callback)
