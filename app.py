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
st.write("그래프의 원하는 지점을 **클릭(터치)**하여 새로운 감정 궤적을 그려보세요.")

user1_params = st.query_params

# 세션 상태 초기화 (클릭 좌표 저장용)
if 'start_point' not in st.session_state:
    st.session_state['start_point'] = [1.0, 1.0]

# --- 상황 1: 파트너 1 진단 ---
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
            link = f"/?a={(a_1+a_2)/2}&b={(b_1+b_2)/2}&sx={(s_1+s_2)/2}"
            st.success("링크 생성 완료! 파트너에게 전달하세요.")
            st.code(link)

# --- 상황 2: 파트너 2 진단 및 클릭 인터랙티브 분석 ---
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
            st.session_state['d'] = (d_1+d_2)/2
            st.session_state['c'] = (c_1+c_2)/2
            st.session_state['sy'] = (sy_1+sy_2)/2

    if st.session_state.get('ready'):
        try:
            def get_safe(k):
                v = user1_params.get(k)
                return float(v[0]) if isinstance(v, list) else float(v)
            
            a, b, Sx = get_safe("a"), get_safe("b"), get_safe("sx")
            d, c, Sy = st.session_state['d'], st.session_state['c'], st.session_state['sy']

            st.divider()
            st.subheader("📍 터치 시뮬레이션 모드")
            st.write("아래 그래프의 **배경(빈 공간)**을 클릭하면 그 지점에서 새로운 사랑이 시작됩니다.")

            # 1. 벡터 필드 생성
            limit = 15
            x_g, y_g = np.meshgrid(np.linspace(-limit, limit, 20), np.linspace(-limit, limit, 20))
            U = a*x_g + b*y_g - 0.1*x_g*(x_g - Sx)
            V = c*x_g + d*y_g - 0.1*y_g*(y_g - Sy)
            mag = np.sqrt(U**2 + V**2); mag[mag == 0] = 1
            U_norm, V_norm = U/mag, V/mag

            # 2. 시뮬레이션 계산 (세션에 저장된 클릭 지점 사용)
            t = np.linspace(0, 30, 1000)
            sol = odeint(love_dynamics, st.session_state['start_point'], t, args=(a, b, c, d, Sx, Sy))

            # 3. Plotly 그래프 구성
            fig = ff.create_quiver(x_g, y_g, U_norm, V_norm, scale=0.6, name='기류', 
                                   line=dict(width=1, color='rgba(100,100,100,0.15)'))
            
            mask = (np.abs(sol[:, 0]) <= limit) & (np.abs(sol[:, 1]) <= limit)
            safe_sol = sol[mask]
            
            if len(safe_sol) > 0:
                fig.add_trace(go.Scatter(x=safe_sol[:, 0], y=safe_sol[:, 1], mode='lines', 
                                         line=dict(color='red', width=4), name='우리의 궤적'))
                fig.add_trace(go.Scatter(x=[safe_sol[0,0]], y=[safe_sol[0,1]], mode='markers', 
                                         marker=dict(color='green', size=15, symbol='diamond'), name='시작점'))
                fig.add_trace(go.Scatter(x=[safe_sol[-1,0]], y=[safe_sol[-1,1]], mode='markers', 
                                         marker=dict(color='orange', size=15, symbol='star'), name='관계의 미래'))

            fig.update_layout(
                title=f"현재 시작점: ({st.session_state['start_point'][0]:.1f}, {st.session_state['start_point'][1]:.1f})",
                xaxis=dict(range=[-limit-1, limit+1], zeroline=True),
                yaxis=dict(range=[-limit-1, limit+1], zeroline=True),
                height=700, template="plotly_white",
                clickmode='event+select' # 클릭 이벤트 활성화
            )

            # --- 클릭 이벤트 감지 로직 ---
            # Streamlit에서 Plotly 이벤트를 완벽하게 받으려면 추가 라이브러리가 필요할 수 있으나, 
            # 기본적으로는 st.plotly_chart의 결과값을 이용해 좌표를 갱신하는 트릭을 씁니다.
            selected_points = st.plotly_chart(fig, use_container_width=True, on_select="rerun")
            
            # 사용자가 그래프의 한 점을 클릭했을 경우 좌표 갱신
            if selected_points and "selection" in selected_points and "points" in selected_points["selection"]:
                points = selected_points["selection"]["points"]
                if points:
                    new_x = points[0]["x"]
                    new_y = points[0]["y"]
                    st.session_state['start_point'] = [new_x, new_y]
                    st.rerun() # 좌표가 바뀌면 즉시 재실행하여 궤적을 다시 그림

            st.write("💡 **팁:** 화살표가 모이는 곳은 '안정적인 사랑', 멀어지는 곳은 '결별'의 가능성을 의미합니다.")

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
