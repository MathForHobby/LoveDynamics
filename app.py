import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.figure_factory as ff
from scipy.integrate import odeint

# 1. 미분방정식 함수 정의
def love_dynamics(state, t, a, b, c, d, Sx, Sy, k=0.05):
    x, y = state
    # dx/dt = a*x + b*y - k*x*(x - Sx)
    dxdt = a*x + b*y - k*x*(x - Sx)
    # dy/dt = c*x + d*y - k*y*(y - Sy)
    dydt = c*x + d*y - k*y*(y - Sy)
    return [dxdt, dydt]

# --- 페이지 설정 ---
st.set_page_config(page_title="Love Dynamics Lab", page_icon="💖", layout="centered")

# --- 메인 화면 ---
st.title("💖 연애 성향 미분방정식 연구소")
st.write("심리학적 성향을 수치화하여 두 사람의 관계 역동을 시뮬레이션합니다.")

# URL 파라미터 확인
user1_params = st.query_params

# --- 사용자 1의 진단 구간 ---
if not user1_params:
    st.header("👤 파트너 1: 성향 진단")
    st.write("모든 질문에 대해 -5(전혀 아니다)부터 5(매우 그렇다)까지 답해주세요.")
    
    with st.form("user1_form"):
        st.subheader("📍 [자기 감정] 내 마음의 움직임")
        a_1 = st.slider("질문 1. 나는 혼자 있을 때도 내 감정을 평온하게 잘 유지하는 편이다.", -5, 5, 0)
        a_2 = st.slider("질문 2. 나는 한 번 사랑에 빠지면 감정이 걷잡을 수 없이 커지는 편이다.", -5, 5, 0)
        
        st.subheader("📍 [상대 반응] 파트너에 대한 태도")
        b_1 = st.slider("질문 3. 상대방이 애정을 표현하면 나도 즉각적으로 더 큰 애정을 느낀다.", -5, 5, 0)
        b_2 = st.slider("질문 4. 상대방이 너무 가깝게 다가오면 가끔은 부담스럽거나 회피하고 싶다.", -5, 5, 0)
        
        st.subheader("📍 [방어기제] 마음을 여는 속도")
        s_1 = st.slider("질문 5. 상대가 확실한 신뢰를 주기 전까지는 어느 정도 거리를 두려고 노력한다.", -5, 5, 0)
        s_2 = st.slider("질문 6. 새로운 사람에게 마음의 문을 완전히 열기까지 시간이 꽤 오래 걸린다.", -5, 5, 0)
        
        submit1 = st.form_submit_button("진단 완료 및 공유 링크 생성")
        
        if submit1:
            a_val = (a_1 + a_2) / 2
            b_val = (b_1 + b_2) / 2
            sx_val = (s_1 + s_2) / 2
            # 파라미터를 담은 주소 생성
            link = f"/?a={a_val}&b={b_val}&sx={sx_val}"
            st.success("진단이 완료되었습니다! 아래의 링크를 복사하여 파트너에게 전달하세요.")
            st.code(link)

# --- 사용자 2의 진단 구간 (링크 접속 시) ---
else:
    st.header("👤 파트너 2: 성향 진단")
    st.info("파트너의 데이터가 정상적으로 로드되었습니다. 이제 당신의 성향을 입력해주세요.")
    
    with st.form("user2_form"):
        st.subheader("📍 [자기 감정] 내 마음의 움직임")
        d_1 = st.slider("질문 1. 나는 혼자 있을 때도 내 감정을 평온하게 잘 유지하는 편이다.", -5, 5, 0)
        d_2 = st.slider("질문 2. 나는 한 번 사랑에 빠지면 감정이 걷잡을 수 없이 커지는 편이다.", -5, 5, 0)
        
        st.subheader("📍 [상대 반응] 파트너에 대한 태도")
        c_1 = st.slider("질문 3. 상대방이 애정을 표현하면 나도 즉각적으로 더 큰 애정을 느낀다.", -5, 5, 0)
        c_2 = st.slider("질문 4. 상대방이 너무 가깝게 다가오면 가끔은 부담스럽거나 회피하고 싶다.", -5, 5, 0)
        
        st.subheader("📍 [방어기제] 마음을 여는 속도")
        sy_1 = st.slider("질문 5. 상대가 확실한 신뢰를 주기 전까지는 어느 정도 거리를 두려고 노력한다.", -5, 5, 0)
        sy_2 = st.slider("질문 6. 새로운 사람에게 마음의 문을 완전히 열기까지 시간이 꽤 오래 걸린다.", -5, 5, 0)
        
        analyze = st.form_submit_button("우리 관계 분석 결과 보기")
        
        if analyze:
            try:
                # 파라미터 읽기 보강 (리스트 형태여도 첫 번째 값을 가져오도록 함)
                def get_param_value(key):
                    val = user1_params.get(key)
                    if isinstance(val, list): # 만약 값이 리스트 형태라면
                        return float(val[0])
                    return float(val)

                # 데이터 수집 (형변환 오류 방지)
                a = get_param_value("a")
                b = get_param_value("b")
                Sx = get_param_value("sx")
                
                d = (d_1 + d_2) / 2
                c = (c_1 + c_2) / 2
                Sy = (sy_1 + sy_2) / 2
                
                # 시뮬레이션 계산
                t = np.linspace(0, 50, 1000)
                # 초기값 [1.0, 1.0]은 서로가 처음 호감을 느낀 상태를 가정
                sol = odeint(love_dynamics, [1.0, 1.0], t, args=(a, b, c, d, Sx, Sy))
                
                # 벡터장 생성
                x_range = np.linspace(-10, 10, 20)
                y_range = np.linspace(-10, 10, 20)
                X, Y = np.meshgrid(x_range, y_range)
                U = a*X + b*Y - 0.05*X*(X - Sx)
                V = c*X + d*Y - 0.05*Y*(Y - Sy)
                
                # 그래프 시각화
                fig = ff.create_quiver(X, Y, U, V, scale=.1, name='감정의 기류', 
                                       line=dict(width=1, color='rgba(150,150,150,0.3)'))
                
                fig.add_trace(go.Scatter(x=sol[:, 0], y=sol[:, 1], mode='lines', 
                                         line=dict(color='red', width=4), name='사랑의 궤적'))
                
                fig.add_trace(go.Scatter(x=[sol[0,0]], y=[sol[0,1]], mode='markers', 
                                         marker=dict(color='green', size=12, symbol='heart'), name='첫 만남'))
                
                fig.add_trace(go.Scatter(x=[sol[-1,0]], y=[sol[-1,1]], mode='markers', 
                                         marker=dict(color='red', size=12, symbol='star'), name='미래의 우리'))

                fig.update_layout(
                    xaxis_title="파트너 1의 마음 강도",
                    yaxis_title="파트너 2의 마음 강도",
                    width=700, height=700,
                    xaxis=dict(range=[-10, 10]),
                    yaxis=dict(range=[-10, 10])
                )
                
                st.plotly_chart(fig)
                
                # 간단한 해석 로직
                st.subheader("🔬 연구소 분석 결과")
                final_x, final_y = sol[-1]
                if final_x > 2 and final_y > 2:
                    st.success("두 분의 사랑은 시간이 흐를수록 깊어지며 안정적인 평형 상태에 도달합니다. 소중한 인연이네요!")
                elif final_x < 0 or final_y < 0:
                    st.warning("관계에서 에너지 소모가 발생할 수 있습니다. 서로의 방어기제를 이해하고 배려하는 노력이 필요해 보입니다.")
                else:
                    st.info("다이내믹하고 열정적인 관계입니다. 때로는 밀당이 즐거움이 되기도 하지만, 신뢰를 쌓는 것이 중요합니다.")
                
            except Exception as e:
                st.error("데이터 로드 중 오류가 발생했습니다. 링크를 다시 확인해주세요.")
