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

# --- 카카오톡 공유 함수 ---
def render_kakao_button(url, title):
    KAKAO_JS_KEY = "9c2fe3b219730ecdc60f8fc6587877e1" # 👈 여기에 키를 꼭 넣어주세요!
    
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

has_p1_data = all(k in params for k in ["a", "b", "sx", "init_x"])
has_p2_data = "d" in params

# --- 상황 1: 파트너 1 진단 ---
if not has_p1_data:
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
        st.subheader("📍 [첫 만남] 관계의 시작점")
        init_x = st.slider("질문 7. 파트너를 처음 알게 되었을 때 느꼈던 호감의 정도는 어떠했나요?", -5.0, 5.0, 1.0, step=0.1)
        
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
            st.subheader("📍 [자기 감정] 내 마음의 움직임")
            d_1 = st.slider("질문 1. 나는 혼자 있을 때도 내 감정을 평온하게 잘 유지하는 편이다.", -5.0, 5.0, 0.0, step=0.1)
            d_2 = st.slider("질문 2. 나는 한 번 사랑에 빠지면 감정이 제어하기 힘들 정도로 커지는 편이다.", -5.0, 5.0, 0.0, step=0.1)
            st.subheader("📍 [상대 반응] 파트너에 대한 태도")
            c_1 = st.slider("질문 3. 상대방이 애정을 표현하면 나도 즉각적으로 더 큰 애정을 느낀다.", -5.0, 5.0, 0.0, step=0.1)
            c_2 = st.slider("질문 4. 상대방이 너무 가깝게 다가오면 가끔은 부담스럽거나 회피하고 싶다.", -5.0, 5.0, 0.0, step=0.1)
            st.subheader("📍 [방어기제] 마음을 여는 속도")
            sy_1 = st.slider("질문 5. 상대가 확실한 신뢰를 주기 전까지는 어느 정도 거리를 두려고 노력한다.", -5.0, 5.0, 0.0, step=0.1)
            sy_2 = st.slider("질문 6. 새로운 사람에게 마음의 문을 완전히 열기까지 시간이 꽤 오래 걸린다.", -5.0, 5.0, 0.0, step=0.1)
            st.subheader("📍 [첫 만남] 관계의 시작점")
            init_y = st.slider("질문 7. 파트너를 처음 알게 되었을 때 느꼈던 호감의 정도는 어떠했나요?", -5.0, 5.0, 1.0, step=0.1)
            
            if st.form_submit_button("우리 관계 분석 결과 보기"):
                p1_a, p1_b, p1_sx, p1_ix = safe_float("a"), safe_float("b"), safe_float("sx"), safe_float("init_x")
                calc_d, calc_c, calc_sy = round((d_1+d_2)/2, 2), round((c_1-c_2)/2, 2), round((sy_1+sy_2)/2, 2)
                res_link = f"{BASE_URL}?a={p1_a}&b={p1_b}&sx={p1_sx}&init_x={p1_ix}&d={calc_d}&c={calc_c}&sy={calc_sy}&init_y={init_y}"
                st.session_state['result_ready'] = True
                st.session_state['res_link'] = res_link
                st.session_state['p2_vals'] = [calc_d, calc_c, calc_sy, init_y]
                st.rerun()

    if has_p2_data or st.session_state.get('result_ready'):
        a, b, sx, init_x = safe_float("a"), safe_float("b"), safe_float("sx"), safe_float("init_x")
        if has_p2_data: d, c, sy, init_y = safe_float("d"), safe_float("c"), safe_float("sy"), safe_float("init_y")
        else: d, c, sy, init_y = st.session_state['p2_vals']

        st.subheader("🔬 최종 관계 시뮬레이션 결과")

        # --- 벡터장(화살표 기류) 계산 ---
        limit = 15
        x_g, y_g = np.meshgrid(np.linspace(-limit, limit, 18), np.linspace(-limit, limit, 18))
        U = a*x_g + b*y_g - 0.1*x_g*(x_g - sx)
        V = c*x_g + d*y_g - 0.1*y_g*(y_g - sy)
        mag = np.sqrt(U**2 + V**2); mag[mag == 0] = 1
        
        # 궤적 계산
        t = np.linspace(0, 50, 1000)
        sol = odeint(love_dynamics, [init_x, init_y], t, args=(a, b, c, d, sx, sy))
        
        # 벡터 필드 시각화 (ff.create_quiver)
        fig = ff.create_quiver(x_g, y_g, U/mag, V/mag, scale=0.7, name='기류', line=dict(width=1, color='rgba(150,150,150,0.3)'))
        
        # 궤적 추가
        fig.add_trace(go.Scatter(x=sol[:, 0], y=sol[:, 1], mode='lines', line=dict(color='red', width=4), name='사랑의 궤적'))
        fig.add_trace(go.Scatter(x=[sol[0,0]], y=[sol[0,1]], mode='markers', marker=dict(color='green', size=15, symbol='diamond'), name='첫 만남'))
        fig.add_trace(go.Scatter(x=[sol[-1,0]], y=[sol[-1,1]], mode='markers', marker=dict(color='orange', size=15, symbol='star'), name='미래의 우리'))

        fig.update_layout(xaxis=dict(title="파트너 1의 마음", range=[-limit-1, limit+1], zeroline=True), 
                          yaxis=dict(title="파트너 2의 마음", range=[-limit-1, limit+1], zeroline=True), 
                          height=600, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

        

        st.divider()
        st.subheader("📊 연구소의 최종 관계 예보")
        fx, fy = sol[-1]
        
        col1, col2 = st.columns(2)
        with col1: st.metric("파트너 1의 최종 마음", f"{fx:.1f}")
        with col2: st.metric("파트너 2의 최종 마음", f"{fy:.1f}")

        if fx > 3 and fy > 3:
            st.success("✨ **결과: 해피엔딩 수렴형**\n\n두 분의 감정은 시간이 흐를수록 서로를 향해 강력하게 고정됩니다. 축하드려요!")
        elif fx < -3 and fy < -3:
            st.error("⚠️ **결과: 차가운 발산형**\n\n현재의 성향으로는 시간이 지날수록 거리가 멀어질 위험이 큽니다. 서로의 방어기제를 이해해보세요.")
        elif (fx * fy < 0):
            st.info("💫 **결과: 애매한 엇갈림형**\n\n한 명은 열정적이지만 한 명은 차가워지는 등 타이밍이 어긋나는 기류가 보입니다.")
        else:
            st.warning("🌀 **결과: 다이나믹 진동형**\n\n감정이 뜨거웠다 차가웠다를 반복하는 롤러코스터 같은 관계입니다.")

        # --- 카카오톡 공유 버튼 ---
        final_url = st.session_state.get('res_link', BASE_URL)
        render_kakao_button(url=final_url, title="💖 우리 사랑의 미분방정식 결과 확인하기")

        # --- 하단 홍보 ---
        st.write("---")
        st.markdown(
            """
            <div style="text-align: center;">
                <p style="color: gray; font-size: 0.8em;">Created by 김사무 @취미로배우는수학</p>
                <p>수학으로 세상을 해석하는 <a href="https://math4hobby.tistory.com/" target="_blank">취미로 배우는 수학 블로그</a>를 방문해보세요!</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
