import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import math

# --- 1. Configuración de Página & Estilos ---
st.set_page_config(
    page_title="Real Estate ROI Visualizer",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos CSS personalizados
st.markdown("""
    <style>
    /* Colores Globales */
    :root {
        --primary-color: #059669;
        --secondary-color: #64748B;
        --alert-color: #EF4444;
        --background-color: #FFFFFF;
    }
    
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 4rem;
        max_width: 1200px;
    }
    
    /* Hero Header */
    .hero-header {
        font-size: 3rem;
        font-weight: 800;
        color: #F8FAFC; /* Changed for dark mode readability */
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .hero-subheader {
        font-size: 1.2rem;
        color: #F8FAFC; /* Changed for dark mode readability */
        text-align: center;
        margin-bottom: 3rem;
    }
    
    /* Section Headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #F8FAFC; /* Changed for dark mode readability */
        border-bottom: 2px solid #E2E8F0;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
        margin-bottom: 1.5rem;
    }

    /* KPI Cards */
    .kpi-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        margin-bottom: 20px; /* Added spacing for responsiveness */
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #059669;
        margin: 0.5rem 0;
    }
    .kpi-label {
        font-size: 0.9rem;
        color: #64748B;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .kpi-value.negative { color: #EF4444; }
    
    /* Custom Box for Calculated Fields */
    .calc-box {
        background-color: #F0FDF4;
        border: 1px solid #BBF7D0;
        color: #166534;
        padding: 10px;
        border-radius: 8px;
        font-weight: 600;
        text-align: center;
        margin-top: 5px;
    }
    
    </style>
""", unsafe_allow_html=True)

# --- 2. Inicialización de Session State ---
def init_session_state():
    defaults = {
        "land_cost": 8000.0,
        "hard_costs": 120000.0,
        "contingency_pct": 10.0,
        "soft_costs": 117000.0,
        "hm_interest_rate": 10.0, 
        "hml_ltc_pct": 85.0,
        "hml_origination_pct": 1.5,
        "hml_other_fee_pct": 2.0,
        "hml_duration": 6,
        "target_price": 450000.0,
        "units": 1,
        "commission_pct": 6.0,
        "investor_capital": 42000.0,
        "investor_roi_target": 12.0,
        "project_duration": 12,
        "comp_1_name": "Propiedad A",
        "comp_1_price": 420000.0,
        "comp_2_name": "Propiedad B",
        "comp_2_price": 445000.0,
        "comp_3_name": "Propiedad C",
        "comp_3_price": 460000.0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# Helper para inputs de moneda
def update_currency(state_key, widget_key):
    val_str = st.session_state[widget_key]
    try:
        clean_val = val_str.replace(',', '').replace('$', '')
        val_float = float(clean_val)
        if val_float < 0: raise ValueError
        st.session_state[state_key] = val_float
    except ValueError:
        pass

def currency_input(label, state_key, key_suffix="", help_text=None):
    widget_key = f"{state_key}_txt_{key_suffix}"
    current_val = st.session_state[state_key]
    formatted_val = f"{current_val:,.2f}"
    
    if widget_key not in st.session_state:
        st.session_state[widget_key] = formatted_val
        
    st.text_input(
        label,
        value=formatted_val,
        key=widget_key,
        help=help_text,
        on_change=update_currency,
        args=(state_key, widget_key)
    )
    return st.session_state[state_key]

# --- HERO SECTION ---
st.markdown('<div class="hero-header">Real Estate ROI Visualizer</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subheader">Simulador de Rentabilidad y Análisis Financiero</div>', unsafe_allow_html=True)

# Reset Button
c_reset1, c_reset2, c_reset3 = st.columns([1.2, 0.6, 1.2]) 
with c_reset2:
    if st.button("🔄 Reiniciar Valores"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()

# --- SECCIÓN 1: COSTOS DE DESARROLLO ---
st.markdown('<div class="section-header">1. Costos de Desarrollo</div>', unsafe_allow_html=True)

cost_col1, cost_col2 = st.columns(2, gap="large")

with cost_col1:
    land_cost = currency_input("Valor del Terreno ($)", "land_cost", "dev")
    hard_costs = currency_input("Hard Costs (Construcción) ($)", "hard_costs", "dev")
    
    # Contingencia Slider (5% - 10%)
    contingency_pct = st.slider("Contingencia (%)", 5.0, 10.0, st.session_state.contingency_pct, step=0.5, key="contingency_slider")
    st.session_state.contingency_pct = contingency_pct
    
    # Calculo visual de contingencia
    contingency_amt = hard_costs * (contingency_pct / 100.0)
    st.markdown(f"<div class='calc-box'>Contingencia: ${contingency_amt:,.2f}</div>", unsafe_allow_html=True)

with cost_col2:
    soft_costs = currency_input("Soft Costs ($)", "soft_costs", "dev")

# --- SECCIÓN 2: PRÉSTAMO HM LENDER ---
st.markdown('<div class="section-header">2. Préstamo HM Lender</div>', unsafe_allow_html=True)

hml_col1, hml_col2 = st.columns(2, gap="large")

with hml_col1:
    # Base calculation: Land + Hard + Contingency
    hml_base_amt = land_cost + hard_costs + contingency_amt
    
    ltc_pct = st.number_input("Porcentaje del Préstamo Otorgado (%)", 0.0, 100.0, st.session_state.hml_ltc_pct, step=1.0, key="hml_ltc_input")
    st.session_state.hml_ltc_pct = ltc_pct
    
    loan_principal = hml_base_amt * (ltc_pct / 100.0)
    st.markdown(f"<div class='calc-box'>Monto del Préstamo: ${loan_principal:,.2f}</div>", unsafe_allow_html=True)

    hml_duration = st.number_input("Duración Préstamo (Meses)", 1, 60, st.session_state.hml_duration, key="hml_dur_inp")
    st.session_state.hml_duration = hml_duration

with hml_col2:
    orig_pct = st.number_input("Puntos de Originación (%)", 0.0, 10.0, st.session_state.hml_origination_pct, step=0.25, key="hml_orig_inp")
    st.session_state.hml_origination_pct = orig_pct
    
    mort_exp_pct = st.number_input("Gastos Mortgage (%)", 0.0, 10.0, st.session_state.hml_other_fee_pct, step=0.25, key="hml_fee_inp")
    st.session_state.hml_other_fee_pct = mort_exp_pct
    
    hm_rate = st.number_input("Interés Anual (%)", 0.0, 30.0, st.session_state.hm_interest_rate, step=0.5, key="hml_rate_inp_new")
    st.session_state.hm_interest_rate = hm_rate

    # Calculate Costs
    hml_orig_amt = loan_principal * (orig_pct / 100.0)
    hml_mort_exp_amt = loan_principal * (mort_exp_pct / 100.0)
    hml_interest_total = loan_principal * (hm_rate / 100.0) * (hml_duration / 12.0)
    hml_fees_total = hml_orig_amt + hml_mort_exp_amt
    
    st.markdown(f"""
        <div style="background-color: #F1F5F9; padding: 10px; border-radius: 8px; font-size: 0.9rem; color: #475569;">
            <div>Originación: <b>${hml_orig_amt:,.2f}</b></div>
            <div>Gastos Mortgage: <b>${hml_mort_exp_amt:,.2f}</b></div>
            <div>Interés Total: <b>${hml_interest_total:,.2f}</b></div>
        </div>
    """, unsafe_allow_html=True)

# --- SECCIÓN 3: PRÉSTAMO PML ---
st.markdown('<div class="section-header">3. Préstamo PML</div>', unsafe_allow_html=True)

pml_input_c1, pml_input_c2 = st.columns(2, gap="large")

with pml_input_c1:
    # Capital Solicitado (Derived)
    hml_gap = hml_base_amt - loan_principal
    calculated_investor_capital = math.ceil(((hml_base_amt - loan_principal) + soft_costs) / 1000) * 1000
    st.session_state.investor_capital = calculated_investor_capital
    st.markdown(f"""
    <div class="kpi-card" style="padding: 1rem; margin-bottom: 20px;">
        <div class="kpi-label">Capital Solicitado al PML</div>
        <div class="kpi-value">${calculated_investor_capital:,.0f}</div>
        <div style="font-size:0.8rem; color:#64748B">(Gap: ${hml_gap:,.0f} + Soft: ${soft_costs:,.0f})</div>
    </div>
    """, unsafe_allow_html=True)

with pml_input_c2:
    inv_roi = st.number_input("Retorno Ofrecido (ROI %)", 0.0, 100.0, st.session_state.investor_roi_target, step=0.5, key="inv_roi_inp")
    st.session_state.investor_roi_target = inv_roi
    
    duration = st.number_input("Duración Proyecto (Meses)", 1, 60, st.session_state.project_duration, key="dur_inp")
    st.session_state.project_duration = duration

# --- SECCIÓN 4: VARIABLES DE VENTA ---
st.markdown('<div class="section-header">4. Variables de Venta</div>', unsafe_allow_html=True)

sale_c1, sale_c2, sale_c3, sale_c4 = st.columns([1, 1, 1, 1.2], gap="small")

with sale_c1:
    units = st.number_input("Unidades a Vender", min_value=1, value=st.session_state.units, key="units_inp")
    st.session_state.units = units

with sale_c2:
    target_price = currency_input("Precio Unitario ($)", "target_price", "sale")

with sale_c3:
    comm_pct = st.number_input("Comisión Realtor + Closing Cost (%)", 0.0, 15.0, st.session_state.commission_pct, step=0.5, key="comm_pct_inp")
    st.session_state.commission_pct = comm_pct

with sale_c4:
    total_sales_vol = units * target_price
    total_commissions = total_sales_vol * (comm_pct / 100.0)
    st.markdown(f"""
    <div class="kpi-card" style="background-color: #FFF7ED; border-color: #FFEDD5; padding: 1rem;">
        <div class="kpi-label" style="color: #C2410C; font-size: 0.8rem;">Total Comisiones</div>
        <div class="kpi-value" style="color: #EA580C; font-size: 1.4rem;">${total_commissions:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

# --- SECCIÓN 5: COMPARABLES (CMA) ---
st.markdown('<div class="section-header">5. Comparables de Mercado (CMA)</div>', unsafe_allow_html=True)

st.caption("Ingrese 3 propiedades testigo:")

comp_c1, comp_c2, comp_c3 = st.columns(3, gap="small")

with comp_c1:
    st.session_state.comp_1_name = st.text_input("Dirección #1", st.session_state.comp_1_name, key="addr_1_input_cma", placeholder="Dirección 1")
    st.session_state.comp_1_price = currency_input("Precio #1 ($)", "comp_1_price", "cma_1_inline")

with comp_c2:
    st.session_state.comp_2_name = st.text_input("Dirección #2", st.session_state.comp_2_name, key="addr_2_input_cma", placeholder="Dirección 2")
    st.session_state.comp_2_price = currency_input("Precio #2 ($)", "comp_2_price", "cma_2_inline")

with comp_c3:
    st.session_state.comp_3_name = st.text_input("Dirección #3", st.session_state.comp_3_name, key="addr_3_input_cma", placeholder="Dirección 3")
    st.session_state.comp_3_price = currency_input("Precio #3 ($)", "comp_3_price", "cma_3_inline")

st.markdown("<br>", unsafe_allow_html=True)
comp_names = [st.session_state.comp_1_name, st.session_state.comp_2_name, st.session_state.comp_3_name, "Proyecto"]
comp_vals = [st.session_state.comp_1_price, st.session_state.comp_2_price, st.session_state.comp_3_price, target_price]
colors = ['#94A3B8', '#94A3B8', '#94A3B8', '#059669']

fig_comps = go.Figure(data=[go.Bar(
    x=comp_names, 
    y=comp_vals, 
    marker_color=colors,
    text=[f"${v/1000:,.0f}k" for v in comp_vals],
    textposition='auto'
)])
fig_comps.update_layout(
    title="Validación de Mercado",
    margin=dict(l=20, r=20, t=30, b=20),
    height=350,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)
st.plotly_chart(fig_comps, use_container_width=True)


# --- SECCIÓN 6: ANÁLISIS FINANCIERO Y RESUMEN ---
st.markdown('<div class="section-header">6. Análisis Financiero y Resumen</div>', unsafe_allow_html=True)

# Final Calculations
gross_income = units * target_price
sales_comm_total = gross_income * (comm_pct / 100.0)
investor_return_amt = st.session_state.investor_capital * (inv_roi / 100.0) * (duration / 12.0)

total_hard = hard_costs + contingency_amt
total_project_costs = (
    land_cost + 
    total_hard + 
    soft_costs + 
    investor_return_amt + 
    hml_fees_total + 
    hml_interest_total + 
    sales_comm_total
)

developer_profit = gross_income - total_project_costs

# Charts
tab1, tab2 = st.tabs(["📊 Waterfall (Flujo)", "🍩 Estructura de Costos"])

with tab1:
    fig_waterfall = go.Figure(go.Waterfall(
        orientation = "v",
        measure = ["relative", "relative", "relative", "relative", "relative", "relative", "relative", "relative", "relative", "total"],
        x = ["Ventas", "Comisión", "Terreno", "Hard+Cont", "Soft", "Fees HML", "Interés HM", "Retorno INV", "Utilidad DEV"],
        textposition = "outside",
        text = [f"${gross_income/1000:,.0f}k", f"-${sales_comm_total/1000:,.0f}k", f"-${land_cost/1000:,.0f}k", 
                f"-${total_hard/1000:,.0f}k", f"-${soft_costs/1000:,.0f}k", f"-${hml_fees_total/1000:,.0f}k", f"-${hml_interest_total/1000:,.0f}k",
                f"-${investor_return_amt/1000:,.0f}k", f"${developer_profit/1000:,.0f}k"],
        y = [gross_income, -sales_comm_total, -land_cost, -total_hard, -soft_costs, -hml_fees_total, -hml_interest_total, -investor_return_amt, developer_profit],
        connector = {"line":{"color":"rgb(63, 63, 63)"}},
        increasing = {"marker":{"color":"#059669"}},
        decreasing = {"marker":{"color":"#EF4444"}},
        totals = {"marker":{"color":"#334155"}}
    ))
    fig_waterfall.update_layout(
        height=400, 
        margin=dict(t=30,b=0,l=0,r=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_waterfall, use_container_width=True)
    
with tab2:
    labels = ['Terreno', 'Hard + Cont.', 'Soft Costs', 'Fees HML', 'Intereses HM', 'Comisiones', 'Retorno Inv.', 'Utilidad Dev.']
    values = [land_cost, total_hard, soft_costs, hml_fees_total, hml_interest_total, sales_comm_total, investor_return_amt, max(0, developer_profit)]
    
    fig_donut = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.5)])
    fig_donut.update_layout(
        height=400, 
        margin=dict(t=30,b=0,l=0,r=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_donut, use_container_width=True)

# --- KPI CARDS FINALES ---
st.markdown("---")
st.markdown('<div class="section-header" style="color: #F8FAFC;">Resumen Final del Proyecto</div>', unsafe_allow_html=True)
st.caption(f"💡 El plazo de la inversión es a **{duration} meses** y se actualiza si se cambia en la sección 'Préstamo PML'.")
st.markdown("")

# Row 1: Precio de Venta, Costo Total Proyecto
res_r1_c1, res_r1_c2 = st.columns(2, gap="medium")

with res_r1_c1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Precio de Venta</div>
        <div class="kpi-value">${gross_income:,.0f}</div>
    </div>""", unsafe_allow_html=True)

with res_r1_c2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Costo Total del Proyecto</div>
        <div class="kpi-value">${total_project_costs:,.0f}</div>
    </div>""", unsafe_allow_html=True)

# Row 2: Total a Devolver Inv, Ganancia Desarrollador
res_r2_c1, res_r2_c2 = st.columns(2, gap="medium")

with res_r2_c1:
    total_inv_payout = st.session_state.investor_capital + investor_return_amt
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Total a Devolver al Inversionista Privado</div>
        <div class="kpi-value">${total_inv_payout:,.0f}</div>
        <div style="font-size:0.8rem; color:#64748B">(Capital + Retorno)</div>
    </div>""", unsafe_allow_html=True)

with res_r2_c2:
    color = "#059669" if developer_profit > 0 else "#EF4444"
    dev_margin = (developer_profit / gross_income * 100) if gross_income else 0
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Ganancia del Desarrollador</div>
        <div class="kpi-value" style="color:{color}">${developer_profit:,.0f}</div>
        <div style="font-size:0.8rem; color:#64748B">({dev_margin:.1f}% Margen)</div>
    </div>""", unsafe_allow_html=True)