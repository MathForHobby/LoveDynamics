import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.figure_factory as ff
from scipy.integrate import odeint

# 1. 미분방정식 모델 정의
def love_dynamics(state, t, a, b, c, d, Sx, Sy, k=0.1):
    x, y = state
    # 감정 변화량 계산 (가속도)
    dxdt = np.clip(a*x + b*y - k*x*(x - Sx), -25, 25)
    dydt = np.clip(c*x + d*y - k*y*(y - Sy), -25, 25)
    return [dxdt, dydt]

# --- 페이지 설정 ---
st.set_page_config(page_title="Love Dynamics Lab", page_icon="💖", layout="centered")

BASE_URL = "https://lovedynamics-4teoqsnmeny3e3ag4liatw.streamlit.app/"

st.title("💖 연애 성향 미분방정식 연구소")
st.write("우리 관계의 수학적 흐름을 분석하고, 그래프를 클릭해 미래를 시뮬레이션하세요.")

# URL 파라미터 확인
user1_params = st.query_params

# 세션 상태 초기화
if 'start_point' not in st.session_state:
    st.session_state['start_point'] = [1.0, 1.0]
if 'ready' not in st.session_state:
    st.session_state['ready'] = False

# --- 상황 1: 파트너 1 진단 (링크 생성자) ---
if not user1_params:
    st.header("👤 파트너 1: 정밀 성향 진단")
    with st.form("user1_form"):
        st.subheader("📍 [자기 감정] 내 마음의 움직임")
        a_1 = st.slider("질문 1. 나는 혼자 있을 때도 내 감정을 평온하게 잘 유지하는 편이다.", -5.0, 5.0, 0.0, step=0.1)
        a_2 = st.slider("질문 2. 나는 한 번 사랑에 빠지면 감정이 제어하기 힘들 정도로 커지는 편이다.", -5.0, 5.0, 0.0, step=0.1)
        
        st.subheader("📍 [상대 반응] 파트너에 대한 태도")
        b_1 = st.slider("질문 3. 상대방이 애정을 표현하면 나도 즉각적으로 더 큰 애정을 느낀다.", -5.0, 5.0, 0.0, step=0.1)
        b_2 = st.slider("질문 4. 상대방이 너무 가깝게 다가오면 가끔은 부담스럽거나 회피하고 싶다.", -5.0, 5.0, 0.0, step=0.1)
        
        st.subheader("📍 [방어기제] 마음을 여는 속도")
        s_1 = st.slider("질문 5. 상대가 확실한 신뢰를 주기 전까지는 어느 정도 거리를 두려고 노력한다.", -5.0, 5.0, 0.0, step=0.1)
        s_2 = st.slider("질문 6. 새로운 사람에게 마음의 문을 완전히 열기까지 시간이 꽤 오래 걸린다.", -5.0, 5.0, 0.0, step=0.1)
        
        if st.form_submit_button("진단 완료 및 공유 링크 생성"):
            # 역채점 로직 적용 (질문 4번: b1 - b2)
            calc_a = (a_1 + a_2) / 2
            calc_b = (b_1 - b_2) / 2
            calc_sx = (s_1 + s_2) / 2
            
            final_link = f"{BASE_URL}?a={calc_a}&b={calc_b}&sx={calc_sx}"
            st.success("진단 완료! 아래 링크를 복사하여 파트너에게 전달하세요.")
            st.code(final_link)

# --- 상황 2: 파트너 2 진단 및 인터랙티브 분석 (링크 접속자) ---
else:
    st.header("👤 파트너 2: 정밀 성향 진단")
    with st.form("user2_form"):
        st.subheader("📍 [자기 감정] 내 마음의 움직임")
        d_1 = st.slider("질문 1. 나는 혼자 있을 때도 내 감정을 평온하게 잘 유지하는 편이다.", -5.0, 5.0, 0.0, step=0.1)
        d_2 = st.slider("질문 2. 나는 한 번 사랑에 빠지면 감정이 제어하기 힘들 정도로 커지는 편이다.", -5.0, 5.0, 0.0, step=0.1)
        
        st.subheader("📍 [상대 반응] 파트너에 대한 태도")
        c_1 = st.slider("질문 3. 상대방이 애정을 표현하면 나도 즉각적으로 더 큰 애정을 느낀다.", -5.0, 5.0, 0.0, step=0.1)
        c_2 = st.slider("질문 4. 상대방이 너무 가깝게 다가오면 가끔은 부담스럽거나 회피하고 싶다.", -5.0, 5.0, 0.0, step=0.1)
        
        st.subheader("📍 [방어기제] 마음을 여는 속도")
        sy_1 = st.slider("질문 5. 상대가 확실한 신뢰를 주기 전까지는 어느 정도 거리를 두려고 노력한다.", -5.0, 5.0, 0.0, step=0.1)
        sy_2 = st.slider("질문 6. 새로운 사람에게 마음의 문을 완전히 열기까지 시간이 꽤 오래 걸린다.", -5.0, 5.0, 0.0, step=0.1)
        
        if st.form_submit_button("우리 관계 분석 결과 보기"):
            st.session_state['ready'] = True
            st.session_state['p2_data'] = {
                'd': (d_1 + d_2) / 2, 
                'c': (c_1 - c_2) / 2, # 역채점
                'sy': (sy_1 + sy_2) / 2
            }

    if st.session_state.get('ready'):
        try:
            # 파트너 1 데이터 파싱
            a = float(user1_params.get("a", [0])[0])
            b = float(user1_params.get("b", [0])[0])
            Sx = float(user1_params.get("sx", [0])[0])
            
            # 파트너 2 데이터 로드
            p2 = st.session_state['p2_data']
            d, c, Sy = p2['d'], p2['c'], p2['sy']

            st.divider()
            st.subheader("📍 실시간 궤적 시뮬레이션")
            st.info("💡 **클릭 가이드:** 그래프의 화살표나 선을 클릭하면 그 지점을 '만남의 시작점'으로 삼아 궤적이 다시 그려집니다.")

            # 수동 입력기 (클릭 보조용)
            col1, col2 = st.columns(2)
            with col1:
                cx = st.number_input("파트너1 초기 마음", value=float(st.session_state['start_point'][0]), step=0.5)
            with col2:
                cy = st.number_input("파트너2 초기 마음", value=float(st.session_state['start_point'][1]), step=0.5)
            st.session_state['start_point'] = [cx, cy]

            # 1. 궤적 및 벡터장 계산
            limit = 15
            t = np.linspace(0, 30, 1000)
            sol = odeint(love_dynamics, st.session_state['start_point'], t, args=(a, b, c, d, Sx, Sy))

            x_g, y_g = np.meshgrid(np.linspace(-limit, limit, 18), np.linspace(-limit, limit, 18))
            U = a*x_g + b*y_g - 0.1*x_g*(x_g - Sx)
            V = c*x_g + d*y_g - 0.1*y_g*(y_g - Sy)
            mag = np.sqrt(U**2 + V**2); mag[mag == 0] = 1

            # 2. 그래프 시각화
            fig = ff.create_quiver(x_g, y_g, U/mag, V/mag, scale=0.7, name='감정 기류', 
                                   line=dict(width=1.5, color='rgba(150,150,150,0.3)'))
            
            mask = (np.abs(sol[:, 0]) <= limit+5) & (np.abs(sol[:, 1]) <= limit+5)
            safe_sol = sol[mask]
            
            if len(safe_sol) > 0:
                fig.add_trace(go.Scatter(x=safe_sol[:, 0], y=safe_sol[:, 1], mode='lines', 
                                         line=dict(color='red', width=4), name='사랑의 궤적'))
                fig.add_trace(go.Scatter(x=[safe_sol[0,0]], y=[safe_sol[0,1]], mode='markers', 
                                         marker=dict(color='green', size=15, symbol='diamond'), name='시작점'))
                fig.add_trace(go.Scatter(x=[safe_sol[-1,0]], y=[safe_sol[-1,1]], mode='markers', 
                                         marker=dict(color='orange', size=15, symbol='star'), name='도착점'))

            fig.update_layout(
                title=f"현재 설정된 시작점: ({st.session_state['start_point'][0]:.1f}, {st.session_state['start_point'][1]:.1f})",
                xaxis=dict(range=[-limit-1, limit+1], zeroline=True),
                yaxis=dict(range=[-limit-1, limit+1], zeroline=True),
                height=700, template="plotly_white", clickmode='event+select'
            )

            # 클릭 이벤트 처리
            event = st.plotly_chart(fig, use_container_width=True, on_select="rerun")
            if event and "selection" in event and len(event["selection"]["points"]) > 0:
                p = event["selection"]["points"][0]
                st.session_state['start_point'] = [p['x'], p['y']]
                st.rerun()

            # 3. 브리핑
            st.subheader("🔬 연구소의 최종 브리핑")
            final_x, final_y = sol[-1]
            if final_x > 2 and final_y > 2:
                st.success("✨ 분석 결과: 두 분의 감정은 서로를 향해 강력하게 수렴하고 있습니다. 시간이 흐를수록 더 깊은 안정을 찾게 될 운명입니다.")
            elif (final_x < 0 and final_y > 0) or (final_x > 0 and final_y < 0):
                st.info("💫 분석 결과: 절묘한 균형을 이루는 밀당 관계입니다. 이 긴장감이 관계를 활기차게 유지해주는 원동력이 됩니다.")
            else:
                st.warning("⚠️ 분석 결과: 감정적 주의 구간입니다. 서로의 방어기제를 자극하지 않도록 세심한 대화와 배려가 필요한 시점입니다.")

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
