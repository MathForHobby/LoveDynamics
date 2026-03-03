import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.figure_factory as ff
from scipy.integrate import odeint

# 1. 미분방정식 모델 정의
def love_dynamics(state, t, a, b, c, d, Sx, Sy, k=0.1):
    x, y = state
    dxdt = np.clip(a*x + b*y - k*x*(x - Sx), -25, 25)
    dydt = np.clip(c*x + d*y - k*y*(y - Sy), -25, 25)
    return [dxdt, dydt]

# --- 페이지 설정 ---
st.set_page_config(page_title="Love Dynamics Lab", page_icon="💖", layout="centered")

st.title("💖 연애 성향 미분방정식 연구소")
st.write("벡터 필드를 확인하고, 원하는 지점을 선택해 새로운 운명을 시뮬레이션하세요.")

user1_params = st.query_params

# --- 상황 1: 파트너 1 진단 ---
if not user1_params:
    st.header("👤 파트너 1: 정밀 진단")
    with st.form("user1_form"):
        st.subheader("📍 성향 입력")
        a_1 = st.slider("질문 1. 감정 유지력", -5.0, 5.0, 0.0, step=0.1)
        a_2 = st.slider("질문 2. 감정 폭발성", -5.0, 5.0, 0.0, step=0.1)
        b_1 = st.slider("질문 3. 애정 반응성", -5.0, 5.0, 0.0, step=0.1)
        b_2 = st.slider("질문 4. 회피 성향", -5.0, 5.0, 0.0, step=0.1)
        s_1 = st.slider("질문 5. 거리 두기", -5.0, 5.0, 0.0, step=0.1)
        s_2 = st.slider("질문 6. 신뢰 속도", -5.0, 5.0, 0.0, step=0.1)
        
        if st.form_submit_button("진단 완료 및 링크 생성"):
            link = f"/?a={(a_1+a_2)/2}&b={(b_1+b_2)/2}&sx={(s_1+s_2)/2}"
            st.success("링크 생성 완료!")
            st.code(link)

# --- 상황 2: 파트너 2 진단 및 인터랙티브 분석 ---
else:
    st.header("👤 파트너 2: 정밀 진단")
    with st.form("user2_form"):
        d_1 = st.slider("질문 1. 감정 유지력", -5.0, 5.0, 0.0, step=0.1)
        d_2 = st.slider("질문 2. 감정 폭발성", -5.0, 5.0, 0.0, step=0.1)
        c_1 = st.slider("질문 3. 애정 반응성", -5.0, 5.0, 0.0, step=0.1)
        c_2 = st.slider("질문 4. 회피 성향", -5.0, 5.0, 0.0, step=0.1)
        sy_1 = st.slider("질문 5. 거리 두기", -5.0, 5.0, 0.0, step=0.1)
        sy_2 = st.slider("질문 6. 신뢰 속도", -5.0, 5.0, 0.0, step=0.1)
        analyze_clicked = st.form_submit_button("우리 관계 분석하기")

    # 분석 버튼이 눌렸거나, 이미 파라미터가 로드된 경우
    if analyze_clicked or 'analyzed' in st.session_state:
        st.session_state['analyzed'] = True
        
        try:
            def get_safe(k):
                v = user1_params.get(k)
                return float(v[0]) if isinstance(v, list) else float(v)
            
            a, b, Sx = get_safe("a"), get_safe("b"), get_safe("sx")
            d, c, Sy = (d_1+d_2)/2, (c_1+c_2)/2, (sy_1+sy_2)/2

            st.divider()
            st.subheader("🕹️ 인터랙티브 시뮬레이션")
            st.info("아래 슬라이더를 조절하여 '첫 만남 시점의 마음 크기'를 바꿔보세요. 궤적이 즉시 변합니다.")
            
            # 사용자가 임의의 위치를 선택할 수 있는 슬라이더 (Initial Condition 조절)
            col1, col2 = st.columns(2)
            with col1:
                start_x = st.slider("파트너 1의 초기 마음", -10.0, 10.0, 1.0, step=0.5)
            with col2:
                start_y = st.slider("파트너 2의 초기 마음", -10.0, 10.0, 1.0, step=0.5)

            # 1. 계산
            t = np.linspace(0, 30, 1000)
            initial_state = [start_x, start_y]
            sol = odeint(love_dynamics, initial_state, t, args=(a, b, c, d, Sx, Sy))

            # 2. 벡터 필드 생성
            limit = 15
            x_g, y_g = np.meshgrid(np.linspace(-limit, limit, 20), np.linspace(-limit, limit, 20))
            U = a*x_g + b*y_g - 0.1*x_g*(x_g - Sx)
            V = c*x_g + d*y_g - 0.1*y_g*(y_g - Sy)
            mag = np.sqrt(U**2 + V**2); mag[mag == 0] = 1
            U_norm, V_norm = U/mag, V/mag

            # 3. 시각화
            fig = ff.create_quiver(x_g, y_g, U_norm, V_norm, scale=0.6, name='기류', 
                                   line=dict(width=1, color='rgba(100,100,100,0.15)'))
            
            mask = (np.abs(sol[:, 0]) <= limit) & (np.abs(sol[:, 1]) <= limit)
            safe_sol = sol[mask]
            
            if len(safe_sol) > 0:
                fig.add_trace(go.Scatter(x=safe_sol[:, 0], y=safe_sol[:, 1], mode='lines', 
                                         line=dict(color='red', width=4, dash='solid'), name='선택된 궤적'))
                fig.add_trace(go.Scatter(x=[safe_sol[0,0]], y=[safe_sol[0,1]], mode='markers', 
                                         marker=dict(color='green', size=15, symbol='diamond'), name='시작점'))
                fig.add_trace(go.Scatter(x=[safe_sol[-1,0]], y=[safe_sol[-1,1]], mode='markers', 
                                         marker=dict(color='orange', size=15, symbol='star'), name='도착점'))

            fig.update_layout(
                xaxis=dict(range=[-limit-1, limit+1], zeroline=True),
                yaxis=dict(range=[-limit-1, limit+1], zeroline=True),
                height=700, template="plotly_white",
                title=f"시작점 ({start_x}, {start_y})으로부터의 감정 흐름"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 결과 브리핑
            final_x, final_y = sol[-1]
            st.write(f"**최종 상태:** 파트너 1: {final_x:.1f}, 파트너 2: {final_y:.1f}")

        except Exception as e:
            st.error(f"오류 발생: {e}")
