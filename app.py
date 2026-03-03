import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.figure_factory as ff
from scipy.integrate import odeint

# 1. 미분방정식 모델 정의
def love_dynamics(state, t, a, b, c, d, Sx, Sy, k=0.05):
    x, y = state
    # 비선형 항이 포함된 감정 변화식
    dxdt = a*x + b*y - k*x*(x - Sx)
    dydt = c*x + d*y - k*y*(y - Sy)
    return [dxdt, dydt]

# --- 페이지 설정 ---
st.set_page_config(page_title="Love Dynamics Lab", page_icon="💖", layout="centered")

# --- 메인 화면 ---
st.title("💖 연애 성향 미분방정식 연구소")
st.write("심리학적 성향을 수치화하여 두 사람의 감정 궤적과 '연애 기류'를 분석합니다.")

# URL 파라미터 확인 (파트너 1의 데이터를 가져옴)
user1_params = st.query_params

# --- 상황 1: 파트너 1이 처음 접속했을 때 ---
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
            # 계수 산출 (산술 평균)
            final_a = (a_1 + a_2) / 2
            final_b = (b_1 + b_2) / 2
            final_sx = (s_1 + s_2) / 2
            
            # 파라미터를 포함한 링크 생성
            # (실제 배포된 주소에 맞게 st.code에 표시됨)
            link = f"/?a={final_a}&b={final_b}&sx={final_sx}"
            st.success("진단이 완료되었습니다! 아래의 링크를 복사하여 파트너에게 전달하세요.")
            st.code(link)

# --- 상황 2: 파트너 2가 링크를 통해 접속했을 때 ---
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
        
        analyze_clicked = st.form_submit_button("우리 관계 분석 결과 보기")
        
        if analyze_clicked:
            try:
                # 1. 파라미터 로드 및 데이터 전처리
                def get_safe_val(key):
                    val = user1_params.get(key)
                    return float(val[0]) if isinstance(val, list) else float(val)

                a = get_safe_val("a")
                b = get_safe_val("b")
                Sx = get_safe_val("sx")
                
                d = (d_1 + d_2) / 2
                c = (c_1 + c_2) / 2
                Sy = (sy_1 + sy_2) / 2
                
                # 2. 궤적 시뮬레이션 계산
                t = np.linspace(0, 20, 1000) # 시간을 20으로 조절하여 적절한 변화 관찰
                initial_state = [1.0, 1.0]   # 초기 호감도 1.0에서 시작
                sol = odeint(love_dynamics, initial_state, t, args=(a, b, c, d, Sx, Sy))
                
                # 3. 전체 벡터 필드(기류) 데이터 생성
                x_grid, y_grid = np.linspace(-10, 10, 20), np.linspace(-10, 10, 20)
                X, Y = np.meshgrid(x_grid, y_grid)
                U = a*X + b*Y - 0.05*X*(X - Sx)
                V = c*X + d*Y - 0.05*Y*(Y - Sy)
                
                # 4. 시각화 (Plotly)
                # (1) 배경 벡터 필드 (화살표)
                fig = ff.create_quiver(X, Y, U, V, 
                                       scale=0.15, 
                                       arrow_scale=0.3,
                                       name='감정의 기류', 
                                       line=dict(width=1, color='rgba(150, 150, 150, 0.4)'))
                
                # (2) 우리 관계의 실제 궤적 추가
                fig.add_trace(go.Scatter(x=sol[:, 0], y=sol[:, 1], mode='lines', 
                                         line=dict(color='red', width=4), name='우리의 궤적'))
                
                # (3) 시작점과 미래점 표시
                fig.add_trace(go.Scatter(x=[sol[0,0]], y=[sol[0,1]], mode='markers', 
                                         marker=dict(color='green', size=12, symbol='heart'), name='첫 만남'))
                fig.add_trace(go.Scatter(x=[sol[-1,0]], y=[sol[-1,1]], mode='markers', 
                                         marker=dict(color='orange', size=12, symbol='star'), name='관계의 미래'))

                # (4) 레이아웃 설정
                fig.update_layout(
                    title="💓 관계 역동성 분석: 위상 평면(Phase Plane)",
                    xaxis_title="파트너 1의 마음 강도",
                    yaxis_title="파트너 2의 마음 강도",
                    width=800, height=800,
                    xaxis=dict(range=[-11, 11], zeroline=True),
                    yaxis=dict(range=[-11, 11], zeroline=True),
                    template="plotly_white"
                )
                
                st.plotly_chart(fig)
                
                # 5. 결과 해석 문구
                st.subheader("🔬 미분방정식 분석 리포트")
                final_x, final_y = sol[-1]
                if final_x > 2 and final_y > 2:
                    st.success("✨ 분석 결과: '동반자적 성장' 유형입니다. 두 분의 감정은 서로를 지지하며 안정적인 사랑의 결실로 수렴합니다.")
                elif final_x < -2 and final_y < -2:
                    st.error("⚠️ 분석 결과: '감정적 소모' 경고입니다. 서로의 방어기제가 충돌하여 멀어지는 기류가 강하니 대화가 필요합니다.")
                else:
                    st.info("💫 분석 결과: '열정적 밀당' 유형입니다. 감정의 파동이 다이나믹하며, 관계의 긴장감이 유지되는 흥미로운 역동을 보입니다.")
                
            except Exception as e:
                st.error(f"데이터를 불러오는 중 오류가 발생했습니다. (Error: {e})")
