import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.figure_factory as ff
from scipy.integrate import odeint

# 1. 미분방정식 모델 정의 (발산 방지를 위해 감쇠 계수 k 조정 가능)
def love_dynamics(state, t, a, b, c, d, Sx, Sy, k=0.1):
    x, y = state
    # 수치가 너무 커지지 않도록 안전장치(tanh)를 추가하거나 비선형 항의 강도를 유지
    dxdt = a*x + b*y - k*x*(x - Sx)
    dydt = c*x + d*y - k*y*(y - Sy)
    
    # 무한 발산 방지를 위한 하드캡 (수치 안정화)
    dxdt = np.clip(dxdt, -50, 50)
    dydt = np.clip(dydt, -50, 50)
    return [dxdt, dydt]

# --- 페이지 설정 ---
st.set_page_config(page_title="Love Dynamics Lab", page_icon="💖", layout="centered")

# --- 스타일링 ---
st.markdown("""
    <style>
    .stSlider [data-baseweb="slider"] { margin-bottom: 40px; }
    </style>
    """, unsafe_allow_html=True)

st.title("💖 연애 성향 미분방정식 연구소")
st.write("0.1 단위의 세밀한 진단으로 두 사람의 감정 기류를 시뮬레이션합니다.")

# URL 파라미터 확인
user1_params = st.query_params

# --- 상황 1: 파트너 1 진단 ---
if not user1_params:
    st.header("👤 파트너 1: 정밀 성향 진단")
    with st.form("user1_form"):
        st.subheader("📍 [자기 감정] - 상세 조절")
        # step=0.1을 추가하여 세밀한 조절 가능하게 변경
        a_1 = st.slider("질문 1. 나는 혼자 있을 때도 내 감정을 평온하게 잘 유지하는 편이다.", -5.0, 5.0, 0.0, step=0.1)
        a_2 = st.slider("질문 2. 나는 한 번 사랑에 빠지면 감정이 걷잡을 수 없이 커지는 편이다.", -5.0, 5.0, 0.0, step=0.1)
        
        st.subheader("📍 [상대 반응] - 상세 조절")
        b_1 = st.slider("질문 3. 상대방이 애정을 표현하면 나도 즉각적으로 더 큰 애정을 느낀다.", -5.0, 5.0, 0.0, step=0.1)
        b_2 = st.slider("질문 4. 상대방이 너무 가깝게 다가오면 가끔은 부담스럽거나 회피하고 싶다.", -5.0, 5.0, 0.0, step=0.1)
        
        st.subheader("📍 [방어기제] - 상세 조절")
        s_1 = st.slider("질문 5. 상대가 확실한 신뢰를 주기 전까지는 어느 정도 거리를 두려고 노력한다.", -5.0, 5.0, 0.0, step=0.1)
        s_2 = st.slider("질문 6. 새로운 사람에게 마음의 문을 완전히 열기까지 시간이 꽤 오래 걸린다.", -5.0, 5.0, 0.0, step=0.1)
        
        submit1 = st.form_submit_button("진단 완료 및 공유 링크 생성")
        if submit1:
            link = f"/?a={(a_1+a_2)/2}&b={(b_1+b_2)/2}&sx={(s_1+s_2)/2}"
            st.success("진단 완료! 파트너에게 이 주소를 보내주세요.")
            st.code(link)

# --- 상황 2: 파트너 2 진단 및 결과 출력 ---
else:
    st.header("👤 파트너 2: 정밀 성향 진단")
    with st.form("user2_form"):
        d_1 = st.slider("질문 1. 평온함 유지 정도", -5.0, 5.0, 0.0, step=0.1)
        d_2 = st.slider("질문 2. 감정의 폭발성", -5.0, 5.0, 0.0, step=0.1)
        c_1 = st.slider("질문 3. 상대 표현에 대한 반응", -5.0, 5.0, 0.0, step=0.1)
        c_2 = st.slider("질문 4. 심리적 거리감/회피", -5.0, 5.0, 0.0, step=0.1)
        sy_1 = st.slider("질문 5. 신뢰 형성 전 방어", -5.0, 5.0, 0.0, step=0.1)
        sy_2 = st.slider("질문 6. 마음을 여는 속도", -5.0, 5.0, 0.0, step=0.1)
        
        analyze_clicked = st.form_submit_button("우리 관계 분석 결과 보기")
        
        if analyze_clicked:
            try:
                # 데이터 로드
                def get_safe(k):
                    v = user1_params.get(k)
                    return float(v[0]) if isinstance(v, list) else float(v)
                
                a, b, Sx = get_safe("a"), get_safe("b"), get_safe("sx")
                d, c, Sy = (d_1+d_2)/2, (c_1+c_2)/2, (sy_1+sy_2)/2

                # 1. 궤적 시뮬레이션 (시간을 50으로 하되 데이터 포인트를 늘려 정밀하게 계산)
                t = np.linspace(0, 50, 2000)
                sol = odeint(love_dynamics, [1.0, 1.0], t, args=(a, b, c, d, Sx, Sy))

                # 2. 벡터 필드 생성 (스케일을 고정하여 화살표가 보이게 함)
                # 범위를 -15 ~ 15로 고정하여 발산하더라도 전체 기류가 보이게 함
                limit = 15
                x_g, y_g = np.meshgrid(np.linspace(-limit, limit, 20), np.linspace(-limit, limit, 20))
                U = a*x_g + b*y_g - 0.1*x_g*(x_g - Sx)
                V = c*x_g + d*y_g - 0.1*y_g*(y_g - Sy)

                # 3. 시각화
                # 배경 화살표 (Quiver)
                fig = ff.create_quiver(x_g, y_g, U, V, scale=0.15, arrow_scale=0.3,
                                       name='감정 기류', line=dict(width=1, color='rgba(100,100,100,0.2)'))
                
                # 궤적 (발산 시 그래프를 뚫고 나가지 않도록 데이터 필터링)
                mask = (np.abs(sol[:, 0]) <= limit) & (np.abs(sol[:, 1]) <= limit)
                safe_sol = sol[mask]
                
                if len(safe_sol) > 0:
                    fig.add_trace(go.Scatter(x=safe_sol[:, 0], y=safe_sol[:, 1], mode='lines', 
                                             line=dict(color='red', width=4), name='사랑의 궤적'))
                    fig.add_trace(go.Scatter(x=[safe_sol[0,0]], y=[safe_sol[0,1]], mode='markers', 
                                             marker=dict(color='green', size=12, symbol='heart'), name='만남의 시작'))

                fig.update_layout(
                    title="💓 관계 역동성 시뮬레이션 (Phase Plane)",
                    xaxis=dict(title="파트너 1의 감정", range=[-limit-1, limit+1], zeroline=True),
                    yaxis=dict(title="파트너 2의 감정", range=[-limit-1, limit+1], zeroline=True),
                    width=800, height=800, template="plotly_white"
                )
                
                st.plotly_chart(fig)
                st.success("분석 완료! 화살표가 가리키는 방향이 두 사람의 감정이 자연스럽게 흐르는 방향입니다.")
                
            except Exception as e:
                st.error(f"오류가 발생했습니다. 링크를 확인해주세요: {e}")
