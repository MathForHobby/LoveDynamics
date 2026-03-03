import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.figure_factory as ff
from scipy.integrate import odeint

# 1. 미분방정식 모델 정의
def love_dynamics(state, t, a, b, c, d, Sx, Sy, k=0.1):
    x, y = state
    # 변화량 계산
    dxdt = a*x + b*y - k*x*(x - Sx)
    dydt = c*x + d*y - k*y*(y - Sy)
    
    # 수치 폭주 방지 (안전 장치)
    dxdt = np.clip(dxdt, -50, 50)
    dydt = np.clip(dydt, -50, 50)
    return [dxdt, dydt]

# --- 페이지 설정 ---
st.set_page_config(page_title="Love Dynamics Lab", page_icon="💖", layout="centered")

st.title("💖 연애 성향 미분방정식 연구소")
st.write("세밀한 수치로 분석하는 우리 관계의 역동성")

# URL 파라미터 확인
user1_params = st.query_params

# --- 상황 1: 파트너 1 진단 ---
if not user1_params:
    st.header("👤 파트너 1: 정밀 성향 진단")
    with st.form("user1_form"):
        st.subheader("📍 [자기 감정]")
        a_1 = st.slider("질문 1. 내 감정을 평온하게 유지하는 편이다.", -5.0, 5.0, 0.0, step=0.1)
        a_2 = st.slider("질문 2. 사랑에 빠지면 감정이 제어하기 힘들 정도로 커진다.", -5.0, 5.0, 0.0, step=0.1)
        st.subheader("📍 [상대 반응]")
        b_1 = st.slider("질문 3. 상대의 애정 표현에 즉각 반응한다.", -5.0, 5.0, 0.0, step=0.1)
        b_2 = st.slider("질문 4. 상대가 다가오면 가끔 회피하고 싶다.", -5.0, 5.0, 0.0, step=0.1)
        st.subheader("📍 [방어기제]")
        s_1 = st.slider("질문 5. 신뢰 전까지는 거리를 두려 한다.", -5.0, 5.0, 0.0, step=0.1)
        s_2 = st.slider("질문 6. 마음의 문을 여는 데 시간이 오래 걸린다.", -5.0, 5.0, 0.0, step=0.1)
        
        submit1 = st.form_submit_button("진단 완료 및 링크 생성")
        if submit1:
            link = f"/?a={(a_1+a_2)/2}&b={(b_1+b_2)/2}&sx={(s_1+s_2)/2}"
            st.success("진단 완료! 파트너에게 이 주소를 전달하세요.")
            st.code(link)

# --- 상황 2: 파트너 2 진단 및 결과 ---
else:
    st.header("👤 파트너 2: 정밀 성향 진단")
    with st.form("user2_form"):
        d_1 = st.slider("질문 1. 평온함 유지", -5.0, 5.0, 0.0, step=0.1)
        d_2 = st.slider("질문 2. 감정의 폭발성", -5.0, 5.0, 0.0, step=0.1)
        c_1 = st.slider("질문 3. 상대에 대한 반응", -5.0, 5.0, 0.0, step=0.1)
        c_2 = st.slider("질문 4. 거리감/회피", -5.0, 5.0, 0.0, step=0.1)
        sy_1 = st.slider("질문 5. 방어 기제", -5.0, 5.0, 0.0, step=0.1)
        sy_2 = st.slider("질문 6. 신뢰 속도", -5.0, 5.0, 0.0, step=0.1)
        
        analyze_clicked = st.form_submit_button("우리 관계 분석 결과 보기")
        
        if analyze_clicked:
            try:
                def get_safe(k):
                    v = user1_params.get(k)
                    return float(v[0]) if isinstance(v, list) else float(v)
                
                a, b, Sx = get_safe("a"), get_safe("b"), get_safe("sx")
                d, c, Sy = (d_1+d_2)/2, (c_1+c_2)/2, (sy_1+sy_2)/2

                # 궤적 계산
                t = np.linspace(0, 50, 1000)
                sol = odeint(love_dynamics, [1.0, 1.0], t, args=(a, b, c, d, Sx, Sy))

                # 벡터 필드 설정
                limit = 12
                x_g, y_g = np.meshgrid(np.linspace(-limit, limit, 20), np.linspace(-limit, limit, 20))
                U = a*x_g + b*y_g - 0.1*x_g*(x_g - Sx)
                V = c*x_g + d*y_g - 0.1*y_g*(y_g - Sy)

                # 시각화 (ff.create_quiver 배경)
                fig = ff.create_quiver(x_g, y_g, U, V, scale=0.15, arrow_scale=0.3,
                                       name='감정 기류', line=dict(width=1, color='rgba(100,100,
