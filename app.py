import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.figure_factory as ff
from scipy.integrate import odeint

# 1. 함수 정의를 가장 먼저 (NameError 방지)
def love_dynamics(state, t, a, b, c, d, Sx, Sy, k=0.05):
    x, y = state
    dxdt = a*x + b*y - k*x*(x - Sx)
    dydt = c*x + d*y - k*y*(y - Sy)
    return [dxdt, dydt]

# --- 페이지 설정 ---
st.set_page_config(page_title="Love Dynamics Lab", page_icon="💖")

# --- 메인 화면 ---
st.title("💖 연애 성향 미분방정식 연구소")

# URL 파라미터 확인 (Streamlit 최신 버전 방식)
user1_params = st.query_params

# 사용자 1의 데이터가 없는 경우
if not user1_params:
    st.header("👤 파트너 1: 성향 진단")
    with st.form("user1_form"):
        st.subheader("📍 [자기 감정]")
        a_1 = st.slider("질문 1. 혼자 있을 때 평온한가?", -5, 5, 0)
        a_2 = st.slider("질문 2. 사랑에 빠지면 감정이 커지는가?", -5, 5, 0)
        st.subheader("📍 [상대 반응]")
        b_1 = st.slider("질문 3. 상대 애정 표현에 즉각 반응하는가?", -5, 5, 0)
        b_2 = st.slider("질문 4. 상대가 가깝게 오면 회피하고 싶은가?", -5, 5, 0)
        st.subheader("📍 [방어기제]")
        s_1 = st.slider("질문 5. 신뢰 전까지 거리를 두는가?", -5, 5, 0)
        s_2 = st.slider("질문 6. 마음을 여는 데 오래 걸리는가?", -5, 5, 0)
        
        submit1 = st.form_submit_button("진단 완료 및 링크 생성")
        if submit1:
            a_val, b_val, sx_val = (a_1+a_2)/2, (b_1+b_2)/2, (s_1+s_2)/2
            # 쿼리 파라미터 생성
            link = f"/?a={a_val}&b={b_val}&sx={sx_val}"
            st.success("아래 링크를 복사해서 파트너에게 보내세요!")
            st.code(link)

# 사용자 1의 데이터가 있는 경우
else:
    st.header("👤 파트너 2: 성향 진단")
    with st.form("user2_form"):
        d_1 = st.slider("질문 1. 혼자 있을 때 평온한가?", -5, 5, 0)
        d_2 = st.slider("질문 2. 사랑에 빠지면 감정이 커지는가?", -5, 5, 0)
        c_1 = st.slider("질문 3. 상대 애정 표현에 즉각 반응하는가?", -5, 5, 0)
        c_2 = st.slider("질문 4. 상대가 가깝게 오면 회피하고 싶은가?", -5, 5, 0)
        sy_1 = st.slider("질문 5. 신뢰 전까지 거리를 두는가?", -5, 5, 0)
        sy_2 = st.slider("질문 6. 마음을 여는 데 오래 걸리는가?", -5, 5, 0)
        
        # 버튼 정의
        analyze_clicked = st.form_submit_button("우리 관계 분석 결과 보기")
        
        # 버튼이 눌렸을 때의 로직을 반드시 'with st.form' 내부에 두거나, 
        # 버튼 클릭 여부를 변수(analyze_clicked)로 받아서 처리해야 함
        if analyze_clicked:
            try:
                # 파라미터 안전하게 추출 (리스트/단일값 모두 대응)
                def get_val(key):
                    v = user1_params.get(key)
                    return float(v[0]) if isinstance(v, list) else float(v)

                a = get_val("a")
                b = get_val("b")
                Sx = get_val("sx")
                d, c, Sy = (d_1+d_2)/2, (c_1+c_2)/2, (sy_1+sy_2)/2
                
                # 계산 및 그래프 생성 (이전과 동일)
                t = np.linspace(0, 50, 1000)
                sol = odeint(love_dynamics, [1.0, 1.0], t, args=(a, b, c, d, Sx, Sy))
                
                x_range = np.linspace(-10, 10, 20)
                y_range = np.linspace(-10, 10, 20)
                X, Y = np.meshgrid(x_range, y_range)
                U = a*X + b*Y - 0.05*X*(X - Sx)
                V = c*X + d*Y - 0.05*Y*(Y - Sy)
                
                fig = ff.create_quiver(X, Y, U, V, scale=.1, name='기류', line=dict(width=1, color='rgba(150,150,150,0.3)'))
                fig.add_trace(go.Scatter(x=sol[:, 0], y=sol[:, 1], mode='lines', line=dict(color='red', width=4), name='궤적'))
                fig.update_layout(xaxis_title="파트너 1", yaxis_title="파트너 2", width=700, height=700)
                
                st.plotly_chart(fig)
                st.success("분석이 완료되었습니다!")
                
            except Exception as e:
                st.error(f"데이터 로드 중 오류가 발생했습니다: {e}")
