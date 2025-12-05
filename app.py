import streamlit as st
from streamlit_drawable_canvas import st_canvas
import numpy as np
import io
import base64

# --- 1. 앱 상태 초기화 및 관리 ---
# 캔버스 객체 목록. 모든 도형, 선, 텍스트(도장)가 여기에 저장됩니다.
if "canvas_objects" not in st.session_state:
    st.session_state["canvas_objects"] = []
# 현재 붓 색상
if "stroke_color" not in st.session_state:
    st.session_state["stroke_color"] = "#EE5757"
# 배경 이미지 데이터 (base64 인코딩된 문자열)
if "bg_image_b64" not in st.session_state:
    st.session_state["bg_image_b64"] = None
# 캔버스 너비/높이 상태 (캔버스 크기 변경 시 객체 위치 유지)
if "canvas_width" not in st.session_state:
    st.session_state["canvas_width"] = 700
if "canvas_height" not in st.session_state:
    st.session_state["canvas_height"] = 400


# --- 2. 앱 기본 설정 ---
st.set_page_config(
    page_title="안정화된 커스텀 그림판",
    layout="wide"
)

st.title("✅ 안정화된 커스텀 그림판 앱")
st.markdown("---")

# --- 3. 캔버스 설정 사이드바 ---
with st.sidebar:
    st.header("설정 및 도구 메뉴")
    
    # --- A. 도구 선택 및 설정 ---
    drawing_mode = st.selectbox("주요 도구 선택", ("freedraw", "eraser"), index=0)

    if drawing_mode == "eraser":
        stroke_width = st.slider("지우개 굵기", 1, 50, 20)
        current_stroke_color = "#FFFFFF" # 지우개 모드에서는 배경색(흰색)을 사용
    else:
        stroke_width = st.slider("붓 굵기", 1, 25, 3)
        # 붓 색상은 세션 상태의 값을 사용하여 Color Picker를 표시
        st.session_state["stroke_color"] = st.color_picker(
            "붓 색상", st.session_state["stroke_color"]
        )
        current_stroke_color = st.session_state["stroke_color"]

    # --- B. 캔버스 크기 및 배경색 ---
    st.subheader("캔버스 설정")
    bg_color = st.color_picker("기본 배경 색상", "#FFFFFF") 
    
    # 캔버스 크기 슬라이더를 세션 상태와 연결하여 값 유지
    st.session_state["canvas_width"] = st.slider("캔버스 너비", 100, 1000, st.session_state["canvas_width"])
    st.session_state["canvas_height"] = st.slider("캔버스 높이", 100, 800, st.session_state["canvas_height"])

    # --- C. 전체 초기화 ---
    if st.button("전체 초기화 (새로운 그림 시작)"):
        st.session_state["canvas_objects"] = []
        st.session_state["bg_image_b64"] = None
        st.session_state["stroke_color"] = "#EE5757"
        st.rerun() # 초기화 후에는 반드시 전체 재실행

# --- 4. 배경 이미지 업로드 및 적용 ---
with st.expander("🖼️ 배경 이미지 설정"):
    uploaded_file = st.file_uploader("캔버스 배경으로 사용할 이미지 파일을 업로드하세요.", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file is not None:
        # 파일 내용을 읽어 base64로 인코딩 후 상태 저장
        img_bytes = uploaded_file.read()
        st.session_state["bg_image_b64"] = base64.b64encode(img_bytes).decode('utf-8')
        st.success("배경 이미지 설정 완료.")

# --- 5. 이모티콘 스탬프 기능 ---
with st.expander("✨ 이모티콘 도장 (스탬프)"):
    emojis = {"❤️": 50, "⭐": 40, "🚀": 60, "💡": 50, "🐻": 55}
    emoji_label = st.selectbox("찍을 이모티콘 선택", list(emojis.keys()))
    emoji_size = emojis[emoji_label]
    
    st.info("도장을 찍을 위치를 지정하고 '도장 찍기' 버튼을 누르세요. 찍은 후에는 이동 가능합니다.")
    
    # 도장 위치 지정 슬라이더
    stamp_x = st.slider("도장 X 좌표", 0, st.session_state["canvas_width"], st.session_state["canvas_width"] // 2)
    stamp_y = st.slider("도장 Y 좌표", 0, st.session_state["canvas_height"], st.session_state["canvas_height"] // 2)

    if st.button(f"'{emoji_label}' 도장 찍기 (현재 좌표에)"):
        stamp_object = {
            "type": "text",
            "text": emoji_label,
            "left": stamp_x,
            "top": stamp_y,
            "fontSize": emoji_size,
            "fill": "#000000",
            "selectable": True, 
            "object_type": "stamp" # 커스텀 속성 추가 (디버깅용)
        }
        # 객체 목록에 도장 객체 추가
        st.session_state["canvas_objects"].append(stamp_object)
        st.success(f"'{emoji_label}' 도장이 캔버스에 추가되었습니다.")
        # 객체가 추가되면 캔버스에 즉시 반영되므로, 별도의 st.rerun()은 필요하지 않습니다.

# --- 6. 캔버스 호출 및 재렌더링 처리 ---

st.subheader("캔버스 영역")

# 배경 이미지 URL 생성
bg_image_url = None
if st.session_state["bg_image_b64"]:
    bg_image_url = f"data:image/png;base64,{st.session_state['bg_image_b64']}"

# st_canvas 컴포넌트 호출 (여기서 대부분의 깜빡임이 발생하므로 최대한 깔끔하게 유지)
canvas_result = st_canvas(
    stroke_width=stroke_width,            
    stroke_color=current_stroke_color,     
    background_color=bg_color,            
    background_image=bg_image_url, # 배경 이미지 URL
    initial_drawing={"objects": st.session_state["canvas_objects"]}, # 저장된 객체 데이터 로드
    update_streamlit=True,                
    height=st.session_state["canvas_height"],                 
    width=st.session_state["canvas_width"],                   
    drawing_mode=drawing_mode,            
    key="canvas_app_fixed", # 고유한 키
)

# 캔버스에 새로운 그림을 그렸을 경우, 객체 목록을 업데이트 (깜빡임 최소화)
if canvas_result.json_data is not None:
    # 캔버스 컴포넌트의 결과를 세션 상태에 저장하여 객체 유지
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
            st.rerun() # 붓 색상 변경을 즉시 반영하기 위해 재실행

# --- 8. 최종 결과 ---
if canvas_result.image_data is not None:
    st.markdown("---")
    st.subheader("✅ 최종 결과 이미지")
    st.image(canvas_result.image_data)
