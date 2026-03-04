import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.figure_factory as ff
from scipy.integrate import odeint
import streamlit.components.v1 as components

# 1. 미분방정식 모델 정의
def love_dynamics(state, t, a, b, c, d, Sx, Sy, k=0.1):
    x, y = state
    dxdt = np.clip(a*x + b*y - k*x*(x - Sx), -25, 25)
    dydt = np.clip(c*x + d*y - k*y*(y - Sy), -25, 25)
    return [dxdt, dydt]

# --- 페이지 설정 ---
st.set_page_config(page_title="Love Dynamics Lab", page_icon="💖", layout="centered")
BASE_URL = "https://lovedynamics-4teoqsnmeny3e3ag4liatw.streamlit.app/"

# --- 카카오톡 공유 함수 정의 ---
def render_kakao_button(url, title):
    # 본인의 JavaScript 키를 여기에 넣으세요 (없으면 버튼이 작동하지 않음)
    KAKAO_JS_KEY = "9c2fe3b219730ecdc60f8fc6587877e1" 
    
    kakao_script = f"""
    <script src="https://t1.kakaocdn.net/kakao_js_sdk/2.7.0/kakao.min.js" integrity="sha384-lLeYSTPNCatv7SOn9mZ6YmJ79H8sLpB1lS8MSQ9S3T+Gg" crossorigin="anonymous"></script>
    <script>
      if (!Kakao.isInitialized()) {{ Kakao.init('{KAKAO_JS_KEY}'); }}
      function shareKakao() {{
        Kakao.Share.sendDefault({{
          objectType: 'feed',
          content: {{
            title: '{title}',
            description: '수학으로 분석한 우리 사랑의 미래는?',
            imageUrl: 'https://cdn.pixabay.com/photo/2017/09/23/16/39/heart-2779422_1280.png',
            link: {{ mobileWebUrl: '{url}', webUrl: '{url}' }},
          }},
          buttons: [{{ title: '결과 확인하기', link: {{ mobileWebUrl: '{url}', webUrl: '{url}' }} }}],
        }});
      }}
    </script>
    <div style="text-align: center; margin-bottom: 20px;">
        <button onclick="shareKakao()" style="background-color: #FEE500; color: #191919; border: none; border-radius: 8px; padding: 12px 24px; font-weight: bold; cursor: pointer; font-size: 16px;">
            🐥 카카오톡으로 결과 공유하기
        </button>
    </div>
    """
    components.html(kakao_script, height=100)

# --- 타이틀 및 상단 홍보 ---
st.title("💖 연애 성향 미분방정식 연구소")
st.caption("Created by 김사무 @취미로배우는수학 | [📖 수학 블로그](https://math4hobby.tistory.com/)")
st.write("---")

params = st.query_params

def safe_float(key, default=0.0):
    try:
        val = params.get(key)
        if val is None: return default
        if isinstance(val, list): return float(val[0])
        return float(val)
    except: return default

# 에러 방지를 위해 변수 초기화
has_p1_data = all(k in params for k in ["a", "b", "sx", "init_x"])
has_p2_data = "d" in params  # 여기서 확실히 정의함

# --- 상황 1: 파트너 1 진단 ---
if not has_p1_data:
    st.header("👤 파트너 1: 정밀 성향 진단")
    with st.form("user1_form"):
        # (질문 섹션 - 이전과 동일)
        a_1 = st.slider("질문 1. 내 감정 유지력", -5.0, 5.0, 0.0, step=0.1)
        a_2 = st.slider("질문 2. 감정 몰입도", -5.0, 5.0, 0.0, step=0.1)
        b_1 = st.slider("질문 3. 상대 반응에 대한 리액션", -5.0, 5.0, 0.0, step=0.1)
        b_2 = st.slider("질문 4. 관계에 대한 부담감", -5.0, 5.0, 0.0, step=0.1)
        s_1 = st.slider("질문 5. 신뢰 형성 속도", -5.0, 5.0, 0.0, step=0.1)
        s_2 = st.slider("질문 6. 마음의 문 열기", -5.0, 5.0, 0.0, step=0.1)
        init_x = st.slider("질문 7. 첫 만남 호감도", -5.0, 5.0, 1.0, step=0.1)
        
        if st.form_submit_button("진단 완료 및 공유 링크 생성"):
            calc_a, calc_b, calc_sx = round((a_1+a_2)/2, 2), round((b_1-b_2)/2, 2), round((s_1+s_2)/2, 2)
            link = f"{BASE_URL}?a={calc_a}&b={calc_b}&sx={calc_sx}&init_x={init_x}"
            st.success("진단 완료! 파트너 2에게 이 링크를 보내세요.")
            st.code(link)

# --- 상황 2: 파트너 2 진단 및 결과 ---
else:
    if not has_p2_data and not st.session_state.get('result_ready'):
        st.header("👤 파트너 2: 정밀 성향 진단")
        with st.form("user2_form"):
            # (파트너 2 질문 섹션 - 이전과 동일)
            d_1 = st.slider("질문 1. 내 감정 유지력", -5.0, 5.0, 0.0, step=0.1)
            d_2 = st.slider("질문 2. 감정 몰입도", -5.0, 5.0, 0.0, step=0.1)
            c_1 = st.slider("질문 3. 상대 반응에 대한 리액션", -5.0, 5.0, 0.0, step=0.1)
            c_2 = st.slider("질문 4. 관계에 대한 부담감", -5.0, 5.0, 0.0, step=0.1)
            sy_1 = st.slider("질문 5. 신뢰 형성 속도", -5.0, 5.0, 0.0, step=0.1)
            sy_2 = st.slider("질문 6. 마음의 문 열기", -5.0, 5.0, 0.0, step=0.1)
            init_y = st.slider("질문 7. 첫 만남 호감도", -5.0, 5.0, 1.0, step=0.1)
            
            if st.form_submit_button("우리 관계 분석 결과 보기"):
                p1_a, p1_b, p1_sx, p1_ix = safe_float("a"), safe_float("b"), safe_float("sx"), safe_float("init_x")
                calc_d, calc_c, calc_sy = round((d_1+d_2)/2, 2), round((c_1-c_2)/2, 2), round((sy_1+sy_2)/2, 2)
                res_link = f"{BASE_URL}?a={p1_a}&b={p1_b}&sx={p1_sx}&init_x={p1_ix}&d={calc_d}&c={calc_c}&sy={calc_sy}&init_y={init_y}"
                st.session_state['result_ready'] = True
                st.session_state['res_link'] = res_link
                st.session_state['p2_vals'] = [calc_d, calc_c, calc_sy, init_y]
                st.rerun()

    # 결과 출력 (이 영역에서 has_p2_data와 result_ready를 모두 체크)
    if has_p2_data or st.session_state.get('result_ready'):
        a, b, sx, init_x = safe_float("a"), safe_float("b"), safe_float("sx"), safe_float("init_x")
        if has_p2_data: d, c, sy, init_y = safe_float("d"), safe_float("c"), safe_float("sy"), safe_float("init_y")
        else: d, c, sy, init_y = st.session_state['p2_vals']

        st.subheader("🔬 최종 관계 시뮬레이션 결과")
        
        # 그래프 및 분석 로직 (생략 - 이전과 동일)
        t = np.linspace(0, 50, 1000)
        sol = odeint(love_dynamics, [init_x, init_y], t, args=(a, b, c, d, sx, sy))
        
        # 
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=sol[:, 0], y=sol[:, 1], mode='lines', line=dict(color='red', width=4), name='사랑의 궤적'))
        fig.add_trace(go.Scatter(x=[sol[0,0]], y=[sol[0,1]], mode='markers', marker=dict(color='green', size=15, symbol='diamond'), name='첫 만남'))
        fig.add_trace(go.Scatter(x=[sol[-1,0]], y=[sol[-1,1]], mode='markers', marker=dict(color='orange', size=15, symbol='star'), name='미래'))
        fig.update_layout(xaxis=dict(range=[-16, 16]), yaxis=dict(range=[-16, 16]), height=500, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

        # 분석 멘트
        st.divider()
        st.subheader("📊 연구소의 최종 관계 예보")
        fx, fy = sol[-1]
        if fx > 3 and fy > 3: st.success("✨ **결과: 해피엔딩 수렴형**")
        elif fx < -3 and fy < -3: st.error("⚠️ **결과: 차가운 발산형**")
        else: st.info("💫 **결과: 복합적 기류 발견**")

        # --- 카카오톡 공유 버튼 출력 ---
        share_url = params.get('res_link', [BASE_URL])[0] if has_p2_data else st.session_state.get('res_link', BASE_URL)
        render_kakao_button(url=share_url, title="💖 우리 사랑의 미분방정식 결과")

        # --- 하단 홍보 ---
        st.write("---")
        st.markdown('<div style="text-align: center;"><p style="color: gray; font-size: 0.8em;">Created by 김사무 @취미로배우는수학</p><p><a href="https://math4hobby.tistory.com/" target="_blank">취미로 배우는 수학 블로그 방문</a></p></div>', unsafe_allow_html=True)
