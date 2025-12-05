import streamlit as st
from streamlit_drawable_canvas import st_canvas
import numpy as np
import base64
import copy

# --- 1. 앱 상태 초기화 및 관리 ---
# 캔버스에 그려진 모든 객체 (도형, 선, 텍스트 등)를 저장
if "canvas_objects" not in st.session_state:
    st.session_state["canvas_objects"] = []
# 현재 붓 색상
if "stroke_color" not in st.session_state:
    st.session_state["stroke_color"] = "#EE5757"
# 배경 이미지 데이터 (base64 인코딩된 문자열)
if "bg_image_b64" not in st.session_state:
    st.session_state["bg_image_b64"] = None
# 캔버스 너비/높이
if "canvas_width" not in st.session_state:
    st.session_state["canvas_width"] = 700
if "canvas_height" not in st.session_state:
    st.session_state["canvas_height"] = 400

# --- 2. 앱 기본 설정 ---
st.set_page_config(
    page_title="나만의 커스텀 그림판",
    layout="wide"
)

st.title("🖌️ 나만의 커스텀 그림판 앱")
st.markdown("---")

# --- 3. 캔버스 설정 사이드바 ---
with st.sidebar:
    st.header("설정 및 도구 메뉴")
    
    # --- A. 캔버스 크기 및 배경색 설정 ---
    st.subheader("캔버스 크기 및 배경")
    bg_color = st.color_picker("캔버스 배경 색상", "#FFFFFF") 
    
    st.session_state["canvas_width"] = st.slider("캔버스 너비", 100, 1000, st.session_state["canvas_width"])
    st.session_state["canvas_height"] = st.slider("캔버스 높이", 100, 800, st.session_state["canvas_height"])

    # --- B. 도구 선택 및 설정 ---
    st.subheader("도구 선택 및 굵기")
    drawing_mode = st.selectbox("주요 도구 선택", ("freedraw", "eraser"), index=0)

    # 도구별 붓/지우개 설정 로직
    if drawing_mode == "eraser":
        stroke_width = st.slider("지우개 굵기", 1, 50, 20)
        # 지우개 모드: 붓 색상 대신 '배경색'을 사용 (지우개 오류 해결)
        current_stroke_color = bg_color 
    else:
        stroke_width = st.slider("붓 굵기", 1, 25, 3)
        # 붓 색상은 세션 상태의 값을 사용하여 Color Picker를 표시
        st.session_state["stroke_color"] = st.color_picker(
            "붓 색상", st.session_state["stroke_color"]
        )
        current_stroke_color = st.session_state["stroke_color"]
    
    # --- C. 전체 초기화 ---
    if st.button("전체 초기화 (새로운 그림 시작)"):
        st.session_state["canvas_objects"] = []
        st.session_state["bg_image_b64"] = None
        st.session_state["stroke_color"] = "#EE5757"
        st.rerun() 

# --- 4. 배경 이미지 업로드 및 적용 ---
with st.expander("🖼️ 배경 이미지 설정"):
    uploaded_file = st.file_uploader("캔버스 배경으로 사용할 이미지 파일을 업로드하세요.", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file is not None:
        img_bytes = uploaded_file.read()
        st.session_state["bg_image_b64"] = base64.b64encode(img_bytes).decode('utf-8')
        st.success("배경 이미지 설정 완료. 이미지를 제거하려면 파일을 다시 업로드하거나 초기화하세요.")

# --- 5. 이모티콘 스탬프 기능 ---
with st.expander("✨ 이모티콘 도장 (스탬프)"):
    emojis = {"❤️": 50, "⭐": 40, "🚀": 60, "💡": 50, "🐻": 55}
    emoji_label = st.selectbox("찍을 이모티콘 선택", list(emojis.keys()))
    emoji_size = emojis[emoji_label]
    
    st.info("도장을 찍을 위치를 지정하고 '도장 찍기' 버튼을 누르세요. 찍은 후에는 이동 가능합니다.")
    
    stamp_x = st.slider("도장 X 좌표", 0, st.session_state["canvas_width"], st.session_state["canvas_width"] // 2)
    stamp_y = st.slider("도장 Y 좌표", 0, st.session_state["canvas_height"], st.session_state["canvas_height"] // 2)

    if st.button(f"'{emoji_label}' 도장 찍기"):
        stamp_object = {
            "type": "text",
            "text": emoji_label,
            "left": stamp_x,
            "top": stamp_y,
            "fontSize": emoji_size,
            "fill": "#000000",
            "selectable": True, 
        }
        # 객체 목록에 도장 객체 추가
        st.session_state["canvas_objects"].append(stamp_object)
        st.success(f"'{emoji_label}' 도장이 캔버스에 추가되었습니다.")

# --- 6. 캔버스 호출 및 재렌더링 처리 ---
st.subheader("캔버스 영역")

# 배경 이미지 URL 생성
bg_image_url = None
if st.session_state["bg_image_b64"]:
    bg_image_url = f"data:image/png;base64,{st.session_state['bg_image_b64']}"

# st_canvas 컴포넌트 호출
canvas_result = st_canvas(
    stroke_width=stroke_width,            
    stroke_color=current_stroke_color,     
    background_color=bg_color,            
    background_image=bg_image_url,
    initial_drawing={"objects": st.session_state["canvas_objects"]}, 
    update_streamlit=True,                
    height=st.session_state["canvas_height"],                 
    width=st.session_state["canvas_width"],                   
    drawing_mode=drawing_mode,            
    key="canvas_app_final_version", 
)

# 캔버스에 새로운 그림을 그렸을 경우, 객체 목록을 업데이트
if canvas_result.json_data is not None:
    st.session_state["canvas_objects"] = canvas_result.json_data.get("objects", [])

# --- 7. 색상 복사 (스포이드) 기능 ---
with st.expander("💧 색상 복사 (스포이드) 도구"):
    if canvas_result.image_data is not None:
        st.write("캔버스 중앙 픽셀의 색상을 추출하여 현재 **붓 색상**으로 복사합니다.")
        
        img_data = canvas_result.image_data
        center_y, center_x = img_data.shape[0] // 2, img_data.shape[1] // 2
        
        if st.button(f"중앙 픽셀 ({center_x}, {center_y}) 색상 복사 및 적용"):
            rgba = img_data[center_y, center_x]
            r, g, b = rgba[0], rgba[1], rgba[2]
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            
            # 추출된 색상을 붓 색상 세션 상태에 저장
            st.session_state["stroke_color"] = hex_color
            st.success(f"색상 복사 성공! 붓 색상이 **{hex_color}**로 변경되었습니다.")
            st.rerun() # 변경된 색상을 Color Picker에 즉시 반영하기 위해 재실행

# --- 8. 최종 결과 ---
if canvas_result.image_data is not None:
    st.markdown("---")
    st.subheader("✅ 최종 결과 이미지")
    st.image(canvas_result.image_data)
