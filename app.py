import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.figure_factory as ff
from scipy.integrate import odeint

# 1. 미분방정식 모델 정의 (발산 억제 및 수치 안정화)
def love_dynamics(state, t, a, b, c, d, Sx, Sy, k=0.1):
    x, y = state
    # 변화량 계산
    dxdt = a*x + b*y - k*x*(x - Sx)
    dydt = c*x + d*y - k*y*(y - Sy)
    
    # 그래프 시각화를 위해 수치 하드캡 설정 (Clipping)
    dxdt = np.clip(dxdt, -25, 25)
    dydt = np.clip(dydt, -25, 25)
    return [dxdt, dydt]

# --- 페이지 설정 ---
st.set_page_config(page_title="Love Dynamics Lab", page_icon="💖", layout="centered")

st.title("💖 연애 성향 미분방정식 연구소")
st.write("0.1 단위의 정밀 진단으로 분석하는 우리 관계의 수학적 운명")

# URL 파라미터 확인
user1_params = st.query_params

# --- 상황 1: 파트너 1 진단 (링크 생성자) ---
if not user1_params:
    st.header("👤 파트너 1: 정밀 성향 진단")
    st.info("당신의 성향을 입력하면 파트너에게 보낼 전용 링크가 생성됩니다.")
    
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
        
        submit1 = st.form_submit_button("진단 완료 및 공유 링크 생성")
        if submit1:
            link = f"/?a={(a_1+a_2)/2}&b={(b_1+b_2)/2}&sx={(s_1+s_2)/2}"
            st.success("진단 완료! 아래의 전용 링크를 복사하여 파트너에게 전달하세요.")
            st.code(link)

# --- 상황 2: 파트너 2 진단 및 결과 분석 (링크 접속자) ---
else:
    st.header("👤 파트너 2: 정밀 성향 진단")
    st.info("파트너의 데이터가 로드되었습니다. 당신의 성향을 입력하여 관계를 분석하세요.")
    
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
        
        analyze_clicked = st.form_submit_button("우리 관계 분석 결과 보기")
        
        if analyze_clicked:
            try:
                # 파트너 1의 파라미터 안전하게 추출
                def get_safe(k):
                    v = user1_params.get(k)
                    return float(v[0]) if isinstance(v, list) else float(v)
                
                a, b, Sx = get_safe("a"), get_safe("b"), get_safe("sx")
                d, c, Sy = (d_1+d_2)/2, (c_1+c_2)/2, (sy_1+sy_2)/2

                # 1. 궤적 시뮬레이션 계산
                t = np.linspace(0, 50, 1000)
                sol = odeint(love_dynamics, [1.0, 1.0], t, args=(a, b, c, d, Sx, Sy))

                # 2. 벡터 필드(기류) 설정 (범위 고정)
                limit = 15
                x_g, y_g = np.meshgrid(np.linspace(-limit, limit, 22), np.linspace(-limit, limit, 22))
                U = a*x_g + b*y_g - 0.1*x_g*(x_g - Sx)
                V = c*x_g + d*y_g - 0.1*y_g*(y_g - Sy)

                # 벡터 정규화 (화살표 크기를 일정하게 하여 기류 방향 강조)
                mag = np.sqrt(U**2 + V**2)
                mag[mag == 0] = 1
                U_norm, V_norm = U / mag, V / mag

                # 3. 시각화 (Phase Plane)
                fig = ff.create_quiver(x_g, y_g, U_norm, V_norm, scale=0.6, arrow_scale=0.3,
                                       name='감정 기류', line=dict(width=1, color='rgba(100,100,100,0.2)'))
                
                # 궤적 필터링 및 추가
                mask = (np.abs(sol[:, 0]) <= limit) & (np.abs(sol[:, 1]) <= limit)
                safe_sol = sol[mask]
                
                if len(safe_sol) > 0:
                    fig.add_trace(go.Scatter(x=safe_sol[:, 0], y=safe_sol[:, 1], mode='lines', 
                                             line=dict(color='red', width=4), name='사랑의 궤적'))
                    # 시작점 (다이아몬드)
                    fig.add_trace(go.Scatter(x=[safe_sol[0,0]], y=[safe_sol[0,1]], mode='markers', 
                                             marker=dict(color='green', size=12, symbol='diamond'), name='만남의 시작'))
                    # 미래점 (별)
                    fig.add_trace(go.Scatter(x=[safe_sol[-1,0]], y=[safe_sol[-1,1]], mode='markers', 
                                             marker=dict(color='orange', size=14, symbol='star'), name='관계의 미래'))

                fig.update_layout(
                    title="💓 관계 역동 시뮬레이션: 위상 평면(Phase Plane)",
                    xaxis_title="파트너 1의 마음 강도",
                    yaxis_title="파트너 2의 마음 강도",
                    width=800, height=800, template="plotly_white",
                    xaxis=dict(range=[-limit-1, limit+1], zeroline=True),
                    yaxis=dict(range=[-limit-1, limit+1], zeroline=True)
                )
                
                st.plotly_chart(fig)
                
                # 4. 결과 분석 문구
                st.subheader("🔬 연구소의 최종 브리핑")
                final_x, final_y = sol[-1]
                if final_x > 2 and final_y > 2:
                    st.success("✨ 분석 결과: '수렴형 안정 관계'입니다. 두 분의 감정 기류는 서로를 향해 강력하게 모여들고 있습니다. 시간이 흐를수록 더 깊은 신뢰와 안정을 찾게 될 운명입니다.")
                elif (final_x < 0 and final_y > 0) or (final_x > 0 and final_y < 0):
                    st.info("💫 분석 결과: '역동적 밀당 관계'입니다. 한 명의 감정이 커지면 다른 한 명이 조절하는 절묘한 균
