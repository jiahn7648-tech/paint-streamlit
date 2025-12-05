import streamlit as st
from streamlit_drawable_canvas import st_canvas
import numpy as np
import io
import copy

# --- 1. 앱 상태 초기화 ---
# 캔버스에 그려진 모든 객체 (도형, 도장 등)를 저장할 세션 상태 초기화
if "canvas_objects" not in st.session_state:
    st.session_state["canvas_objects"] = []
# 현재 붓 색상 상태 저장
if "stroke_color" not in st.session_state:
    st.session_state["stroke_color"] = "#EE5757"
# 배경 이미지 데이터 저장
if "bg_image_data" not in st.session_state:
    st.session_state["bg_image_data"] = None

# --- 2. 앱 기본 설정 ---
st.set_page_config(
    page_title="나만의 커스텀 그림판",
    layout="wide"
)

st.title("🌟 나만의 커스텀 그림판 앱")
st.markdown("---")

# --- 3. 캔버스 설정 사이드바 ---
with st.sidebar:
    st.header("설정 및 도구 메뉴")
    
    # 붓/지우개 도구 선택
    drawing_mode = st.selectbox("주요 도구 선택", ("freedraw", "eraser"), index=0)

    # 붓/지우개 굵기 설정
    if drawing_mode == "eraser":
        stroke_width = st.slider("지우개 굵기", 1, 50, 20)
        current_stroke_color = "#FFFFFF" 
    else:
        stroke_width = st.slider("붓 굵기", 1, 25, 3)
        # 붓 색상은 세션 상태에서 가져옴
        st.session_state["stroke_color"] = st.color_picker(
            "붓 색상", st.session_state["stroke_color"]
        )
        current_stroke_color = st.session_state["stroke_color"]

    # 캔버스 배경색 (배경 이미지 없을 때만 적용)
    bg_color = st.color_picker("기본 배경 색상", "#FFFFFF") 
    
    # 캔버스 크기
    canvas_width = st.slider("캔버스 너비", 100, 1000, 700)
    canvas_height = st.slider("캔버스 높이", 100, 800, 400)

    # 캔버스 초기화 버튼
    if st.button("전체 초기화 (새로운 그림 시작)"):
        st.session_state["canvas_objects"] = []
        st.session_state["bg_image_data"] = None
        st.session_state["stroke_color"] = "#EE5757"
        st.experimental_rerun() 

# --- 4. 배경 이미지 업로드 및 적용 ---
with st.expander("🖼️ 배경 이미지 설정"):
    uploaded_file = st.file_uploader("캔버스 배경으로 사용할 이미지 파일을 업로드하세요.", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file is not None:
        # 업로드된 파일을 BytesIO로 읽어 Streamlit에 표시 가능한 형태로 변환
        st.session_state["bg_image_data"] = uploaded_file.read()
        st.success("배경 이미지 설정 완료. 아래 캔버스에 적용됩니다.")
    
# --- 5. 이모티콘 스탬프 기능 ---
with st.expander("✨ 이모티콘 도장 (스탬프)"):
    # 이모티콘과 폰트 크기 목록
    emojis = {"❤️": 50, "⭐": 40, "🚀": 60, "💡": 50}
    emoji_label = st.selectbox("찍을 이모티콘 선택", list(emojis.keys()))
    emoji_size = emojis[emoji_label]
    
    st.info("도장을 찍을 위치를 지정하고 '도장 찍기' 버튼을 누르세요.")
    
    # 도장 위치 지정 (캔버스 좌표는 클릭으로 받을 수 없으므로 임시로 슬라이더 사용)
    stamp_x = st.slider("도장 X 좌표", 0, canvas_width, canvas_width // 2)
    stamp_y = st.slider("도장 Y 좌표", 0, canvas_height, canvas_height // 2)

    if st.button(f"'{emoji_label}' 도장 찍기"):
        # 텍스트 객체 형태로 캔버스 객체 목록에 추가
        stamp_object = {
            "type": "text",
            "text": emoji_label,
            "left": stamp_x,
            "top": stamp_y,
            "fontSize": emoji_size,
            "fill": "#000000", # 이모티콘은 검은색으로 고정
            "selectable": True # 이동 가능하게 설정
        }
        st.session_state["canvas_objects"].append(stamp_object)
        st.success(f"'{emoji_label}' 도장이 캔버스에 추가되었습니다.")

# --- 6. 캔버스 호출 ---

st.subheader("캔버스 영역")

# 배경 이미지 데이터 처리
bg_image = st.session_state["bg_image_data"] if st.session_state["bg_image_data"] else None
bg_image_b64 = None
if bg_image:
    # Bytes 데이터를 base64로 인코딩하여 캔버스에 전달 (브라우저 호환성)
    import base64
    bg_image_b64 = base64.b64encode(bg_image).decode('utf-8')

# st_canvas 컴포넌트 호출
canvas_result = st_canvas(
    stroke_width=stroke_width,            
    stroke_color=current_stroke_color,     
    background_color=bg_color,            
    background_image=f"data:image/png;base64,{bg_image_b64}" if bg_image_b64 else None,
    initial_drawing={"objects": st.session_state["canvas_objects"]}, # 저장된 객체 데이터 로드
    update_streamlit=True,                
    height=canvas_height,                 
    width=canvas_width,                   
    drawing_mode=drawing_mode,            
    key="canvas_app_custom",               
)

# 캔버스에 새로운 그림을 그렸을 경우, 해당 객체 데이터를 세션 상태에 저장하여 유지
if canvas_result.json_data is not None:
    st.session_state["canvas_objects"] = canvas_result.json_data.get("objects", [])

# --- 7. 색상 복사 (스포이드) 기능 ---

with st.expander("💧 색상 복사 (스포이드) 도구"):
    if canvas_result.image_data is not None:
        st.write("캔버스 중앙의 픽셀 색상을 추출하여 현재 붓 색상으로 복사합니다.")
        
        # 중앙 좌표 계산
        img_data = canvas_result.image_data
        center_y, center_x = img_data.shape[0] // 2, img_data.shape[1] // 2
        
        if st.button(f"중앙 픽셀 ({center_x}, {center_y}) 색상 복사"):
            rgba = img_data[center_y, center_x]
            r, g, b = rgba[0], rgba[1], rgba[2]
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            
            # 추출된 색상을 붓 색상 세션 상태에 저장하여 반영
            st.session_state["stroke_color"] = hex_color
            st.success(f"색상 복사 성공! 붓 색상이 **{hex_color}**로 변경되었습니다. (RGB: {r}, {g}, {b})")
            st.color_picker("복사된 색상", hex_color, disabled=True)
            st.rerun() # 색상 피커에 변경 사항을 반영하기 위해 페이지 재실행
