import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.figure_factory as ff
from scipy.integrate import odeint

# 1. 미분방정식 함수를 가장 먼저 정의 (NameError 방지)
def love_dynamics(state, t, a, b, c, d, Sx, Sy, k=0.05):
    x, y = state
    dxdt = a*x + b*y - k*x*(x - Sx)
    dydt = c*x + d*y - k*y*(y - Sy)
    return [dxdt, dydt]

# --- 페이지 설정 ---
st.set_page_config(page_title="Love Dynamics Lab", page_icon="💖")

# --- 메인 화면 ---
st.title("💖 연애 성향 미분방정식 연구소")
st.write("수학으로 풀어보는 우리들의 감정 궤적")

# URL 파라미터 확인
user1_params = st.query_params

# 사용자 1의 데이터가 없는 경우 (처음 접속)
if not user1_params:
    st.header("👤 파트너 1 진단")
    st.write("질문에 답하고 생성된 링크를 상대방에게 보내주세요.")
    
    with st.form("user1_form"):
        col1, col2 = st.columns(2)
        with col1:
            a_1 = st.slider("질문A: 혼자일 때 평온한가?", -5, 5, 0)
            b_1 = st.slider("질문C: 즉각 반응하는가?", -5, 5, 0)
            s_1 = st.slider("질문E: 거리 두기를 하는가?", -5, 5, 0)
        with col2:
            a_2 = st.slider("질문B: 감정이 폭발하는가?", -5, 5, 0)
            b_2 = st.slider("질문D: 회피 성향이 있는가?", -5, 5, 0)
            s_2 = st.slider("질문F: 신뢰 속도가 느린가?", -5, 5, 0)
        
        submit1 = st.form_submit_button("진단 완료 및 링크 생성")
        
        if submit1:
            a_val = (a_1 + a_2) / 2
            b_val = (b_1 + b_2) / 2
            sx_val = (s_1 + s_2) / 2
            # 현재 페이지 주소를 기반으로 파라미터 생성
            link = f"/?a={a_val}&b={b_val}&sx={sx_val}"
            st.success("아래 링크를 복사해서 파트너에게 보내세요!")
            st.code(link)

# 사용자 1의 데이터가 있는 경우 (링크를 타고 들어온 사용자 2)
else:
    st.header("👤 파트너 2 진단")
    st.info("파트너의 데이터가 로드되었습니다. 당신의 성향을 입력하세요.")
    
    with st.form("user2_form"):
        col1, col2 = st.columns(2)
        with col1:
            d_1 = st.slider("질문A: 혼자일 때 평온한가?", -5, 5, 0)
            c_1 = st.slider("질문C: 즉각 반응하는가?", -5, 5, 0)
            sy_1 = st.slider("질문E: 거리 두기를 하는가?", -5, 5, 0)
        with col2:
            d_2 = st.slider("질문B: 감정이 폭발하는가?", -5, 5, 0)
            c_2 = st.slider("질문D: 회피 성향이 있는가?", -5, 5, 0)
            sy_2 = st.slider("질문F: 신뢰 속도가 느린가?", -5, 5, 0)
        
        analyze = st.form_submit_button("우리 관계 분석하기")
        
        if analyze:
            try:
                # 파트너 1 계수 (URL에서 가져옴)
                a = float(user1_params["a"])
                b = float(user1_params["b"])
                Sx = float(user1_params["sx"])
                
                # 파트너 2 계수 (입력값)
                d = (d_1 + d_2) / 2
                c = (c_1 + c_2) / 2
                Sy = (sy_1 + sy_2) / 2
                
                # 궤적 계산
                t = np.linspace(0, 50, 1000)
                sol = odeint(love_dynamics, [1.0, 1.0], t, args=(a, b, c, d, Sx, Sy))
                
                # 벡터장 생성용 격자
                x_range = np.linspace(-10, 10, 15)
                y_range = np.linspace(-10, 10, 15)
                X, Y = np.meshgrid(x_range, y_range)
                U = a*X + b*Y - 0.05*X*(X - Sx)
                V = c*X + d*Y - 0.05*Y*(Y - Sy)
                
                # 그래프 시각화
                fig = ff.create_quiver(X, Y, U, V, scale=.1, name='감정의 기류', line=dict(width=1, color='rgba(150,150,150,0.5)'))
                fig.add_trace(go.Scatter(x=sol[:, 0], y=sol[:, 1], mode='lines', line=dict(color='red', width=4), name='우리의 궤적'))
                fig.add_trace(go.Scatter(x=[sol[0,0]], y=[sol[0,1]], mode='markers', marker=dict(color='green', size=10), name='만남의 시작'))
                
                fig.update_layout(xaxis_title="파트너 1", yaxis_title="파트너 2", width=700, height=700)
                st.plotly_chart(fig)
                
                st.success("분석 완료! 그래프의 붉은 선이 우리 관계의 미래입니다.")
                
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
