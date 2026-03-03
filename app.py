import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.figure_factory as ff
from scipy.integrate import odeint

# 1. 미분방정식 모델 정의 (발산 억제 로직 포함)
def love_dynamics(state, t, a, b, c, d, Sx, Sy, k=0.1):
    x, y = state
    # 변화량 계산
    dxdt = a*x + b*y - k*x*(x - Sx)
    dydt = c*x + d*y - k*y*(y - Sy)
    
    # 그래프가 터지지 않게 수치 하드캡 설정 (Clipping)
    dxdt = np.clip(dxdt, -20, 20)
    dydt = np.clip(dydt, -20, 20)
    return [dxdt, dydt]

# --- 페이지 설정 ---
st.set_page_config(page_title="Love Dynamics Lab", page_icon="💖", layout="centered")

st.title("💖 연애 성향 미분방정식 연구소")
st.write("0.1 단위의 세밀한 수치로 분석하는 우리 관계의 역동성")

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

                # 벡터 필드 설정 (범위를 -15 ~ 15로 고정)
                limit = 15
                x_g, y_g = np.meshgrid(np.linspace(-limit, limit, 20), np.linspace(-limit, limit, 20))
                
                # 각 지점에서의 기울기 계산
                U = a*x_g + b*y_g - 0.1*x_g*(x_g - Sx)
                V = c*x_g + d*y_g - 0.1*y_g*(y_g - Sy)

                # 시각화 (ff.create_quiver) - 화살표가 잘 보이도록 정규화(Normalize)
                # 화살표 크기가 너무 커지거나 작아지는 것을 방지
                mag = np.sqrt(U**2 + V**2)
                mag[mag == 0] = 1 # 0 나누기 방지
                U_norm = U / mag
                V_norm = V / mag

                fig = ff.create_quiver(x_g, y_g, U_norm, V_norm, scale=0.5, arrow_scale=0.3,
                                       name='감정 기류', line=dict(width=1, color='rgba(100,100,100,0.2)'))
                
                # 궤적 데이터 필터링 (화면 밖으로 나가는 선 정리)
                mask = (np.abs(sol[:, 0]) <= limit) & (np.abs(sol[:, 1]) <= limit)
                safe_sol = sol[mask]
                
                if len(safe_sol) > 0:
                    fig.add_trace(go.Scatter(x=safe_sol[:, 0], y=safe_sol[:, 1], mode='lines', 
                                             line=dict(color='red', width=4), name='우리의 궤적'))
                    # 하트 대신 에러 없는 diamond 사용
                    fig.add_trace(go.Scatter(x=[safe_sol[0,0]], y=[safe_sol[0,1]], mode='markers', 
                                             marker=dict(color='green', size=12, symbol='diamond'), name='만남의 시작'))
                    # 별 모양 표시
                    fig.add_trace(go.Scatter(x=[safe_sol[-1,0]], y=[safe_sol[-1,1]], mode='markers', 
                                             marker=dict(color='orange', size=12, symbol='star'), name='관계의 미래'))

                fig.update_layout(
                    title="💓 관계 역동 시뮬레이션 (Phase Plane)",
                    xaxis=dict(title="파트너 1", range=[-limit-1, limit+1], zeroline=True),
                    yaxis=dict(title="파트너 2", range=[-limit-1, limit+1], zeroline=True),
                    width=800, height=800, template="plotly_white"
                )
                
                st.plotly_chart(fig)
                st.success("분석 완료! 배경의 화살표는 두 사람의 감정이 흐르는 '기류'를 나타냅니다.")
                
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
