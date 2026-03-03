import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.figure_factory as ff
from scipy.integrate import odeint

# 1. 미분방정식 모델 정의
def love_dynamics(state, t, a, b, c, d, Sx, Sy, k=0.1):
    x, y = state
    # 변화량 계산 (감정의 가속도)
    dxdt = np.clip(a*x + b*y - k*x*(x - Sx), -25, 25)
    dydt = np.clip(c*x + d*y - k*y*(y - Sy), -25, 25)
    return [dxdt, dydt]

# --- 페이지 설정 ---
st.set_page_config(page_title="Love Dynamics Lab", page_icon="💖", layout="centered")

# 실배포 주소 설정
BASE_URL = "https://lovedynamics-4teoqsnmeny3e3ag4liatw.streamlit.app/"

st.title("💖 연애 성향 미분방정식 연구소")
st.write("우리 관계의 수학적 흐름을 분석하고, 그래프를 클릭해 미래를 시뮬레이션하세요.")

# URL 파라미터 확인
user1_params = st.query_params

# 세션 상태 초기화 (클릭 좌표 및 분석 상태 저장)
if 'start_point' not in st.session_state:
    st.session_state['start_point'] = [1.0, 1.0]

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
            # 요청하신 실배포 주소를 결합하여 링크 생성
            final_link = f"{BASE_URL}?a={(a_1+a_2)/2}&b={(b_1+b_2)/2}&sx={(s_1+s_2)/2}"
            st.success("진단이 완료되었습니다! 아래 링크를 복사하여 파트너에게 전달하세요.")
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
            st.session_state['params_p2'] = {'d': (d_1+d_2)/2, 'c': (c_1+c_2)/2, 'sy': (sy_1+sy_2)/2}

    if st.session_state.get('ready'):
        try:
            # 데이터 로드
            def get_val(k):
                v = user1_params.get(k)
                return float(v[0]) if isinstance(v, list) else float(v)
            
            a, b, Sx = get_val("a"), get_val("b"), get_val("sx")
            p2 = st.session_state['params_p2']
            d, c, Sy = p2['d'], p2['c'], p2['sy']

            st.divider()
            st.subheader("📍 실시간 궤적 시뮬레이션")
            st.info("💡 **팁:** 그래프의 빈 공간을 클릭해보세요. 그 지점이 '만남의 시작점'이 되어 궤적이 새로 그려집니다.")

            # 1. 벡터 필드 생성
            limit = 15
            x_g, y_g = np.meshgrid(np.linspace(-limit, limit, 20), np.linspace(-limit, limit, 20))
            U = a*x_g + b*y_g - 0.1*x_g*(x_g - Sx)
            V = c*x_g + d*y_g - 0.1*y_g*(y_g - Sy)
            mag = np.sqrt(U**2 + V**2); mag[mag == 0] = 1
            U_norm, V_norm = U/mag, V/mag

            # 2. 궤적 계산 (세션 저장된 클릭 지점 기준)
            t = np.linspace(0, 30, 1000)
            sol = odeint(love_dynamics, st.session_state['start_point'], t, args=(a, b, c, d, Sx, Sy))

            # 3. 그래프 시각화
            fig = ff.create_quiver(x_g, y_g, U_norm, V_norm, scale=0.6, name='감정 기류', 
                                   line=dict(width=1, color='rgba(100,100,100,0.15)'))
            
            mask = (np.abs(sol[:, 0]) <= limit) & (np.abs(sol[:, 1]) <= limit)
            safe_sol = sol[mask]
            
            if len(safe_sol) > 0:
                fig.add_trace(go.Scatter(x=safe_sol[:, 0], y=safe_sol[:, 1], mode='lines', 
                                         line=dict(color='red', width=4), name='사랑의 궤적'))
                fig.add_trace(go.Scatter(x=[safe_sol[0,0]], y=[safe_sol[0,1]], mode='markers', 
                                         marker=dict(color='green', size=15, symbol='diamond'), name='시작점'))
                fig.add_trace(go.Scatter(x=[safe_sol[-1,0]], y=[safe_sol[-1,1]], mode='markers', 
                                         marker=dict(color='orange', size=15, symbol='star'), name='도착점'))

            fig.update_layout(
                title=f"설정된 시작점: ({st.session_state['start_point'][0]:.1f}, {st.session_state['start_point'][1]:.1f})",
                xaxis=dict(title="파트너 1의 마음", range=[-limit-1, limit+1], zeroline=True),
                yaxis=dict(title="파트너 2의 마음", range=[-limit-1, limit+1], zeroline=True),
                height=700, template="plotly_white",
                clickmode='event+select'
            )

            # 클릭 이벤트 감지 및 세션 갱신
            selected = st.plotly_chart(fig, use_container_width=True, on_select="rerun")
            
            if selected and "selection" in selected and "points" in selected["selection"]:
                points = selected["selection"]["points"]
                if points:
                    st.session_state['start_point'] = [points[0]["x"], points[0]["y"]]
                    st.rerun()

            # 4. 분석 브리핑
            st.subheader("🔬 연구소의 최종 브리핑")
            final_x, final_y = sol[-1]
            if final_x > 2 and final_y > 2:
                st.success("✨ 분석 결과: 두 분은 서로를 향해 강력하게 이끌리고 있습니다. 안정적인 사랑의 결실을 맺을 확률이 매우 높습니다.")
            elif (final_x < 0 and final_y > 0) or (final_x > 0 and final_y < 0):
                st.info("💫 분석 결과: 에너지가 넘치는 밀당 관계입니다. 때로는 서운함이 생길 수 있지만, 이 긴장감이 서로를 끊임없이 궁금하게 만듭니다.")
            else:
                st.warning("⚠️ 분석 결과: 감정이 흩어지는 기류가 발견됩니다. 서로의 마음이 어디를 향하고 있는지 깊은 대화가 필요한 타이밍입니다.")

        except Exception as e:
            st.error(f"데이터 처리 중 오류가 발생했습니다: {e}")
