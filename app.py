import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.figure_factory as ff # 벡터장을 위한 팩토리 추가
from scipy.integrate import odeint

# (상단 생략: 미분방정식 정의 및 파라미터 수집 로직은 동일)

        if analyze:
            # 계수 확정
            a, b, Sx = user1_data["a"], user1_data["b"], user1_data["sx"]
            d, c, Sy = (d_1 + d_2) / 2, (c_1 + c_2) / 2, (sy_1 + sy_2) / 2
            
            # 1. 궤적 계산 (odeint)
            t = np.linspace(0, 50, 1000)
            initial_state = [1.0, 1.0]
            sol = odeint(love_dynamics, initial_state, t, args=(a, b, c, d, Sx, Sy))

            # 2. 벡터장(화살표) 데이터 생성
            x_range = np.linspace(-10, 10, 20)
            y_range = np.linspace(-10, 10, 20)
            X, Y = np.meshgrid(x_range, y_range)
            
            # 각 격자점에서의 기울기(화살표 방향) 계산
            U = a*X + b*Y - 0.05*X*(X - Sx)
            V = c*X + d*Y - 0.05*Y*(Y - Sy)

            # 3. Plotly Figure Factory로 화살표 그리기
            fig = ff.create_quiver(X, Y, U, V, scale=.1, arrow_scale=.3, line=dict(width=1, color='rgba(100, 100, 100, 0.3)'), name='연애의 기류')

            # 4. 그 위에 실제 두 사람의 궤적 추가
            fig.add_trace(go.Scatter(
                x=sol[:, 0], y=sol[:, 1], 
                mode='lines+markers', 
                marker=dict(size=[10 if i==0 or i==999 else 0 for i in range(1000)]),
                line=dict(color='red', width=4), 
                name='우리들의 궤적'
            ))

            # 레이아웃 정돈
            fig.update_layout(
                title="💓 관계의 운명: 위상 평면(Phase Plane) 분석",
                xaxis=dict(title="사용자 1의 마음", range=[-10, 10]),
                yaxis=dict(title="사용자 2의 마음", range=[-10, 10]),
                showlegend=True,
                width=800, height=800
            )

            st.plotly_chart(fig)
            
            # (하단 결과 해석 로직 동일)
