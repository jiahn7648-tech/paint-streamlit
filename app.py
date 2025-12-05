import streamlit as st
from streamlit_drawable_canvas import st_canvas
import pandas as pd

# --- 앱 기본 설정 ---
st.set_page_config(
    page_title="간편 그림판 (붓 & 지우개)",
    layout="wide"
)

st.title("✏️ Streamlit 간편 그림판 앱")
st.markdown("붓과 지우개만 사용해 자유롭게 그림을 그려보세요.")
st.markdown("---")

# --- 캔버스 설정 사이드바 ---
with st.sidebar:
    st.header("설정 메뉴")
    
    # --- 1. 주요 도구 선택 ---
    drawing_mode = st.selectbox(
        "주요 도구 선택", 
        ("freedraw", "eraser"), # freedraw는 붓, eraser는 지우개
        index=0 
    )

    # --- 2. 붓/지우개 설정 ---
    if drawing_mode == "eraser":
        # 지우개일 경우: 굵기만 설정
        stroke_width = st.slider("지우개 굵기", 1, 50, 20)
        # 지우개 모드에서는 색상 설정은 무의미하므로 기본값 유지 (캔버스 배경색과 동일)
        stroke_color = "#FFFFFF" 
    else:
        # 붓(freedraw)일 경우: 굵기와 색상 설정
        stroke_width = st.slider("붓 굵기", 1, 25, 3)
        stroke_color = st.color_picker("붓 색상", "#EE5757")

    # --- 3. 배경 설정 및 캔버스 크기 ---
    st.subheader("캔버스 설정")
    bg_color = st.color_picker("배경 색상", "#FFFFFF") # 캔버스 배경색 설정

    canvas_width = st.slider("캔버스 너비", 100, 1000, 700)
    canvas_height = st.slider("캔버스 높이", 100, 800, 400)

    # 캔버스 초기화 버튼
    if st.button("캔버스 초기화"):
        st.experimental_rerun() 


# --- 캔버스 표시 ---

st.subheader("캔버스 영역")

# st_canvas 컴포넌트 호출
# Note: fill_color는 'rect'나 'circle' 모드에서 채우기 색상으로 사용되므로, freedraw/eraser 모드에서는 영향 없음.
canvas_result = st_canvas(
    stroke_width=stroke_width,            # 붓/지우개 굵기
    stroke_color=stroke_color,            # 붓 색상 (지우개 모드에서는 무시됨)
    background_color=bg_color,            # 배경 색상
    update_streamlit=True,                
    height=canvas_height,                 
    width=canvas_width,                   
    drawing_mode=drawing_mode,            # 붓/지우개 모드
    key="canvas_app_final",               
)

st.markdown("---")

# --- 결과 출력 섹션 ---
if canvas_result.image_data is not None:
    st.subheader("🖼️ 그린 이미지 결과")
    st.image(canvas_result.image_data)

st.info("왼쪽 사이드바에서 도구를 선택하고 굵기 및 색상을 설정할 수 있습니다. 지우개는 캔버스 배경색으로 칠하는 방식으로 작동합니다.")
