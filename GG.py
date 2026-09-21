import streamlit as st
import numpy as np
from scipy.stats import norm
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="GreeksGlance", layout="wide")

st.title("GreeksGlance")

st.divider()
st.subheader("Market Parameters")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    option_type = st.radio("Option Type", ["Call", "Put"])
with col2:
    K = st.number_input("Strike Price (K)", value=100.0, step=5.0)
with col3:
    T = st.number_input("Maturity (Years)", value=1.0, step=0.1, min_value=0.01)
with col4:
    sigma = st.number_input("Implied Volatility (%)", value=10.0, step=1.0, min_value=1.0)/100.0
with col5:
    r = st.number_input("Risk Free Rate (%)", value=1.0, step=0.5)/100.0

# Mathematical calculations
S = np.linspace(max(10.0, K*0.5), K*1.5, 300)

d1 = (np.log(S/K)+(r+0.5*sigma**2)*T)/(sigma*np.sqrt(T))
d2 = d1-sigma*np.sqrt(T)

pdf_d1 = norm.pdf(d1) # N'(d1)
cdf_d1 = norm.cdf(d1) #N(d1)
cdf_d2 = norm.cdf(d2)

if option_type=="Call":
    delta = cdf_d1
    theta = (-(S*pdf_d1*sigma)/(2*np.sqrt(T))-r*K*np.exp(-r*T)*cdf_d2)/365.0
else:
    delta = cdf_d1-1.0
    theta = (-(S*pdf_d1*sigma)/(2*np.sqrt(T))+r*K*np.exp(-r*T)*norm.cdf(-d2))/365.0

gamma = pdf_d1/(S*sigma*np.sqrt(T))
vega = (S*np.sqrt(T)*pdf_d1)/100.0 #en pourcentage

greeks_data = {
    "Delta": {"values": delta, "color": "#0055FF", "secondary": False},
    "Gamma": {"values": gamma, "color": "#FF5500", "secondary": True},
    "Vega": {"values": vega, "color": "#009944", "secondary": False},
    "Theta": {"values": theta, "color": "#CC0022", "secondary": True}
}

# Function to build charts dynamically
def build_chart(selected_greeks, title_text):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    for greek in selected_greeks:
        data = greeks_data[greek]
        fig.add_trace(go.Scatter(x=S,y=data["values"],mode="lines",name=greek,line=dict(color=data["color"], width=3)),secondary_y=data["secondary"])
    fig.add_vline(x=K, line_dash="dash", line_color="#444444", line_width=1.5, annotation_text=f" Strike K={int(K)}", annotation_position="top left")

    fig.update_layout(
        height=550,
        title_text=title_text,
        template="plotly_white",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=60, b=20)
    )

    fig.update_xaxes(title_text="Spot Price (S)", showgrid=True, gridcolor="#E0E0E0")
    fig.update_yaxes(title_text="Primary (Delta / Vega)", secondary_y=False, showgrid=True, gridcolor="#E0E0E0")
    fig.update_yaxes(title_text="Secondary (Gamma / Theta)", secondary_y=True, showgrid=False)
    
    return fig

st.divider()
st.subheader("Chart Options")

layout_mode = st.radio("Display Mode", ["Single Chart", "Side by Side"], horizontal=True)

if layout_mode=="Single Chart":
    st.write("Toggle Greeks to display:")
    c1, c2, c3, c4 = st.columns(4)
    s_d = c1.toggle("Delta", value=True, key="single_d")
    s_g = c2.toggle("Gamma", value=True, key="single_g")
    s_v = c3.toggle("Vega", value=False, key="single_v")
    s_t = c4.toggle("Theta", value=False, key="single_t")
    
    selected = []
    if s_d: selected.append("Delta")
    if s_g: selected.append("Gamma")
    if s_v: selected.append("Vega")
    if s_t: selected.append("Theta")
    
    st.plotly_chart(build_chart(selected, "Combined Risk Profiles"), use_container_width=True)

else:
    left_col, right_col = st.columns(2)
    
    with left_col:
        st.write("Chart 1 :")
        cl1, cl2, cl3, cl4 = st.columns(4)
        s_d1 = cl1.toggle("Delta", value=True, key="left_d")
        s_g1 = cl2.toggle("Gamma", value=False, key="left_g")
        s_v1 = cl3.toggle("Vega", value=False, key="left_v")
        s_t1 = cl4.toggle("Theta", value=False, key="left_t")
        
        sel1 = []
        if s_d1: sel1.append("Delta")
        if s_g1: sel1.append("Gamma")
        if s_v1: sel1.append("Vega")
        if s_t1: sel1.append("Theta")
        
        st.plotly_chart(build_chart(sel1, "Chart 1"), use_container_width=True)
        
    with right_col:
        st.write("Chart 2 :")
        cr1, cr2, cr3, cr4 = st.columns(4)
        s_d2 = cr1.toggle("Delta", value=False, key="right_d")
        s_g2 = cr2.toggle("Gamma", value=True, key="right_g")
        s_v2 = cr3.toggle("Vega", value=False, key="right_v")
        s_t2 = cr4.toggle("Theta", value=False, key="right_t")
        
        sel2 = []
        if s_d2: sel2.append("Delta")
        if s_g2: sel2.append("Gamma")
        if s_v2: sel2.append("Vega")
        if s_t2: sel2.append("Theta")
        
        st.plotly_chart(build_chart(sel2, "Chart 2"), use_container_width=True)

st.divider()
st.subheader(f"At The Money (Spot={K})")
idx_atm = np.abs(S-K).argmin()

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric("ATM Delta", f"{delta[idx_atm]:.4f}")
col_m2.metric("ATM Gamma", f"{gamma[idx_atm]:.4f}")
col_m3.metric("ATM Vega", f"{vega[idx_atm]:.4f}")
col_m4.metric("ATM Theta", f"{theta[idx_atm]:.4f}")
