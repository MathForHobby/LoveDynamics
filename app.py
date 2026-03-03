import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.figure_factory as ff
from scipy.integrate import odeint

# --- 페이지 설정 ---
st.set_page_config(page_title="Love Dynamics Lab", page_icon="💖")

# --- 미분방정식 정의 ---
def love_dynamics(state, t, a, b, c, d, Sx, Sy, k=0.05):
    x, y = state
    dxdt = a*x + b*y - k*x*(x - Sx)
    dydt = c*x + d*y - k*y*(y - Sy)
    return [dxdt, dydt]

# --- 메인 화면 ---
st.title("💖 연애 성향 미분방정식 연구소")

# URL 파라미터 확인
user1_params = st.query_params

if not user1_params:
    st.header("👤 파트너 1 진단")
    with st.form("user1_form"):
        a_val = (st.slider("질문A (혼자 평온)", -5, 5, 0) + st.slider("질문B (감정 폭발)", -5, 5, 0)) / 2
        b_val = (st.slider("질문C (즉각 반응)", -5, 5, 0) + st.slider("질문D (회피 성향)", -5, 5, 0)) / 2
        sx_val = (st.slider("질문E (거리 두기)", -5, 5, 0) + st.slider("질문F (신뢰 속도)", -5, 5, 0)) / 2
        
        submit1 = st.form_submit_button("링크 생성")
        if submit1:
            link = f"/?a={a_val}&b={b_val}&sx={sx_val}"
            st.success("상대방에게 이 주소를 공유하세요!")
            st.code(link)

else:
    st.header("👤 파트너 2 진단")
    with st.form("user2_form"):
        d_val = (st.slider("질문A (혼자 평온)", -5, 5, 0) + st.slider("질문B (감정 폭발)", -5, 5, 0)) / 2
        c_val = (st.slider("질문C (즉각 반응)", -5, 5, 0) + st.slider("질문D (회피 성향)", -5, 5, 0)) / 2
        sy_val = (st.slider("질문E (거리 두기)", -5, 5, 0) + st.slider("질문F (신뢰 속도)", -5, 5, 0)) / 2
        
        analyze = st.form_submit_button("결과 분석하기")
        
        if analyze:
            # 계수 설정
            a, b, Sx = float(user1_params["a"]), float(user1_params["b"]), float(user1_params["sx"])
            d, c, Sy = d_val, c_val, sy_val
            
            # 궤적 계산
            t = np.linspace(0, 50, 1000)
            sol = odeint(love_dynamics, [1.0, 1.0], t, args=(a, b, c, d, Sx, Sy))
            
            # 벡터장 생성
            x_range = np.linspace(-10, 10, 15)
            y_range = np.linspace(-10, 10, 15)
            X, Y = np.meshgrid(x_range, y_range)
            U = a*X + b*Y - 0.05*X*(X - Sx)
            V = c*X + d*Y - 0.05*Y*(Y - Sy)
            
            # 그래프 그리기
            fig = ff.create_quiver(X, Y, U, V, scale=.1, name='전체 기류', line=dict(width=1, color='gray'))
            fig.add_trace(go.Scatter(x=sol[:, 0], y=sol[:, 1], mode='lines', line=dict(color='red', width=3), name='우리의 운명'))
            
            st.plotly_chart(fig)
