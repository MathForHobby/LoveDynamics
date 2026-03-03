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
BASE_URL = "https://lovedynamics-4teoqsnmeny3e3ag4liatw.streamlit.app/"

st.title("💖 연애 성향 미분방정식 연구소")

# URL 파라미터 확인 (딕셔너리 형태로 안전하게 가져오기)
params = st.query_params

# 세션 상태 초기화
if 'start_point' not in st.session_state:
    st.session_state['start_point'] = [1.0, 1.0]

# 문자열을 안전하게 숫자로 변환하는 함수
def safe_float(key, default=0.0):
    try:
        val = params.get(key)
        if val is None: return default
        # 리스트 형태일 경우 첫 번째 요소 추출, 아니면 그대로 변환
        raw_val = val[0] if isinstance(val, list) else val
        return float(raw_val)
    except (ValueError, TypeError, IndexError):
        return default

# --- 상황 1: 파트너 1 진단 (최초 접속 혹은 파라미터 부족) ---
# 필수 파라미터(a, b, sx)가 하나라도 없으면 진단 폼을 보여줌
if not all(k in params for k in ["a", "b", "sx"]):
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
            calc_a, calc_b, calc_sx = round((a_1 + a_2) / 2, 2), round((b_1 - b_2) / 2, 2), round((s_1 + s_2) / 2, 2)
            link = f"{BASE_URL}?a={calc_a}&b={calc_b}&sx={calc_sx}"
            st.success("진단 완료! 파트너에게 이 링크를 보내세요.")
            st.code(link)

# --- 상황 2: 파트너 2 진단 혹은 결과 확인 ---
else:
    has_p2_data = "d" in params
    
    if not has_p2_data and not st.session_state.get('result_ready'):
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
                calc_d, calc_c, calc_sy = round((d_1 + d_2) / 2, 2), round((c_1 - c_2) / 2, 2), round((sy_1 + sy_2) / 2, 2)
                res_link = f"{BASE_URL}?a={params['a']}&b={params['b']}&sx={params['sx']}&d={calc_d}&c={calc_c}&sy={calc_sy}"
                st.session_state['result_ready'] = True
                st.session_state['res_link'] = res_link
                st.session_state['p2_vals'] = [calc_d, calc_c, calc_sy]
                st.rerun()
    
    # 결과 화면 출력
    if has_p2_data or st.session_state.get('result_ready'):
        # 안전한 데이터 로드
        a = safe_float("a")
        b = safe_float("b")
        sx = safe_float("sx")
        
        if has_p2_data:
            d, c, sy = safe_float("d"), safe_float("c"), safe_float("sy")
        else:
            d, c, sy = st.session_state['p2_vals']

        st.subheader("🔬 최종 관계 시뮬레이션")
        if not has_p2_data:
            st.warning("🔗 파트너 1에게 결과를 공유하려면 아래 링크를 보내주세요.")
            st.code(st.session_state['res_link'])

        # 미분방정식 및 그래프 로직 (생략 없이 실행)
        limit = 15
        t = np.linspace(0, 30, 1000)
        sol = odeint(love_dynamics, st.session_state['start_point'], t, args=(a, b, c, d, sx, sy))
        
        # 벡터장 및 궤적 시각화
        x_g, y_g = np.meshgrid(np.linspace(-limit, limit, 18), np.linspace(-limit, limit, 18))
        U = a*x_g + b*y_g - 0.1*x_g*(x_g - sx)
        V = c*x_g + d*y_g - 0.1*y_g*(y_g - sy)
        mag = np.sqrt(U**2 + V**2); mag[mag == 0] = 1
        
        

        fig = ff.create_quiver(x_g, y_g, U/mag, V/mag, scale=0.7, name='기류', line=dict(width=1.5, color='rgba(150,150,150,0.3)'))
        mask = (np.abs(sol[:, 0]) <= limit+5) & (np.abs(sol[:, 1]) <= limit+5)
        safe_sol = sol[mask]
        if len(safe_sol) > 0:
            fig.add_trace(go.Scatter(x=safe_sol[:, 0], y=safe_sol[:, 1], mode='lines', line=dict(color='red', width=4), name='궤적'))
            fig.add_trace(go.Scatter(x=[safe_sol[0,0]], y=[safe_sol[0,1]], mode='markers', marker=dict(color='green', size=15, symbol='diamond'), name='시작점'))
            fig.add_trace(go.Scatter(x=[safe_sol[-1,0]], y=[safe_sol[-1,1]], mode='markers', marker=dict(color='orange', size=15, symbol='star'), name='도착점'))

        fig.update_layout(xaxis=dict(range=[-limit-1, limit+1], zeroline=True), yaxis=dict(range=[-limit-1, limit+1], zeroline=True), height=700, template="plotly_white", clickmode='event+select')
        
        event = st.plotly_chart(fig, use_container_width=True, on_select="rerun")
        if event and "selection" in event and len(event["selection"]["points"]) > 0:
            p = event["selection"]["points"][0]
            st.session_state['start_point'] = [p['x'], p['y']]
            st.rerun()

        st.info(f"💡 분석 요약: 파트너 1 성향({a:.1f}, {b:.1f}) | 파트너 2 성향({d:.1f}, {c:.1f})")
