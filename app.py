import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.integrate import odeint

# --- 페이지 설정 ---
st.set_page_config(page_title="Love Dynamics Lab", page_icon="💖")

# --- 스타일링 ---
st.markdown("""
    <style>
    .main { background-color: #fff5f5; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #ff4b4b; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 유틸리티 함수: URL 파라미터 읽기/쓰기 ---
def get_params():
    query_params = st.query_params
    if "a" in query_params:
        return {
            "a": float(query_params["a"]),
            "b": float(query_params["b"]),
            "sx": float(query_params["sx"]),
            "user1_done": True
        }
    return None

# --- 미분방정식 정의 ---
def love_dynamics(state, t, a, b, c, d, Sx, Sy, k=0.05):
    x, y = state
    dxdt = a*x + b*y - k*x*(x - Sx)
    dydt = c*x + d*y - k*y*(y - Sy)
    return [dxdt, dydt]

# --- 메인 로직 ---
st.title("💖 연애 성향 미분방정식 연구소")
st.write("두 사람의 감정 상호작용을 수학적으로 모델링하여 미래 궤적을 예측합니다.")

user1_data = get_params()

if not user1_data:
    # --- 사용자 1의 입력 구간 ---
    st.header("👤 첫 번째 파트너의 진단")
    with st.form("user1_form"):
        st.subheader("1. 자기 감정 피드백 (Self-Feedback)")
        a_1 = st.slider("질문A: 혼자 있을 때 평온한가?", -5, 5, 0)
        a_2 = st.slider("질문B: 누군가를 좋아하면 감정이 폭발하는가?", -5, 5, 0)
        
        st.subheader("2. 상대에 대한 반응성 (Interaction)")
        b_1 = st.slider("질문C: 상대의 표현에 즉각 반응하는가?", -5, 5, 0)
        b_2 = st.slider("질문D: 상대가 다가오면 도망치고 싶은가?", -5, 5, 0)
        
        st.subheader("3. 방어기제 (Threshold)")
        s_1 = st.slider("질문E: 확실한 호감 전까지 거리를 두는가?", -5, 5, 0)
        s_2 = st.slider("질문F: 마음을 여는 데 오래 걸리는가?", -5, 5, 0)
        
        submitted = st.form_submit_button("진단 완료 및 링크 생성")
        
        if submitted:
            # 계수 계산
            final_a = (a_1 + a_2) / 2
            final_b = (b_1 + b_2) / 2
            final_sx = (s_1 + s_2) / 2
            
            # 공유 링크 생성
            base_url = "https://your-app-name.streamlit.app" # 배포 후 수정 필요
            link = f"/?a={final_a}&b={final_b}&sx={final_sx}"
            st.success("진단이 완료되었습니다! 아래 링크를 상대방에게 보내주세요.")
            st.code(link)
            st.info("상대방이 이 링크로 접속하여 진단을 마치면 결과가 생성됩니다.")

else:
    # --- 사용자 2의 입력 구간 ---
    st.header("👤 두 번째 파트너의 진단")
    st.info("파트너의 진단 결과가 수신되었습니다. 이제 당신의 차례입니다.")
    
    with st.form("user2_form"):
        d_1 = st.slider("질문A: 혼자 있을 때 평온한가?", -5, 5, 0)
        d_2 = st.slider("질문B: 누군가를 좋아하면 감정이 폭발하는가?", -5, 5, 0)
        
        c_1 = st.slider("질문C: 상대의 표현에 즉각 반응하는가?", -5, 5, 0)
        c_2 = st.slider("질문D: 상대가 다가오면 도망치고 싶은가?", -5, 5, 0)
        
        sy_1 = st.slider("질문E: 확실한 호감 전까지 거리를 두는가?", -5, 5, 0)
        sy_2 = st.slider("질문F: 마음을 여는 데 오래 걸리는가?", -5, 5, 0)
        
        analyze = st.form_submit_button("결과 확인하기")
        
        if analyze:
            # 계수 확정
            a, b, Sx = user1_data["a"], user1_data["b"], user1_data["sx"]
            d = (d_1 + d_2) / 2
            c = (c_1 + c_2) / 2
            Sy = (sy_1 + sy_2) / 2
            
            # 미분방정식 풀이
            t = np.linspace(0, 50, 1000)
            initial_state = [1.0, 1.0] # 초기 호감도 1에서 시작
            sol = odeint(love_dynamics, initial_state, t, args=(a, b, c, d, Sx, Sy))
            
            # --- Plotly 그래프 생성 ---
            fig = go.Figure()
            
            # 배경 벡터장 (Streamline 대용으로 격자점 화살표 표현)
            x_mesh, y_mesh = np.meshgrid(np.linspace(-10, 10, 15), np.linspace(-10, 10, 15))
            u = a*x_mesh + b*y_mesh - 0.05*x_mesh*(x_mesh - Sx)
            v = c*x_mesh + d*y_mesh - 0.05*y_mesh*(y_mesh - Sy)
            
            # 궤적 추가
            fig.add_trace(go.Scatter(x=sol[:, 0], y=sol[:, 1], mode='lines', line=dict(color='red', width=4), name='관계 궤적'))
            fig.add_trace(go.Scatter(x=[sol[0,0]], y=[sol[0,1]], mode='markers', marker=dict(size=12, color='green'), name='시작점'))
            
            fig.update_layout(
                title="사랑의 위상 평면 (Phase Plane)",
                xaxis_title="사용자 1의 호감도",
                yaxis_title="사용자 2의 호감도",
                width=700, height=700
            )
            st.plotly_chart(fig)
            
            # 결과 해석
            final_x, final_y = sol[-1]
            if final_x > 5 and final_y > 5:
                st.balloons()
                st.success("축하합니다! 두 분의 관계는 안정적이고 깊은 사랑으로 수렴합니다.")
            elif final_x < 0 or final_y < 0:
                st.error("주의! 감정의 소모가 파국으로 치달을 위험이 있습니다. 서로의 방어기제를 점검해보세요.")
            else:
                st.warning("밀당의 굴레에 빠질 수 있는 역동적인 관계입니다.")
