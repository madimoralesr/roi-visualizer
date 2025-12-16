import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# --- 1. Configuración de Página & Estilos ---
st.set_page_config(
    page_title="Real Estate ROI Visualizer",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados para ajustar a la guía de estilo
st.markdown("""
    <style>
    /* Colores Globales */
    :root {
        --primary-color: #059669; /* Emerald Green (Darker for Contrast) */
        --secondary-color: #64748B; /* Slate Grey */
        --alert-color: #EF4444; /* Burnt Orange/Red */
        --background-color: #FFFFFF;
    }
    
    /* Ajustes generales */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Estilo para las tarjetas de KPI */
    .kpi-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        min-height: 150px; /* Asegura que todas las tarjetas tengan la misma altura */
    }
    .kpi-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #059669;
    }
    .kpi-label {
        font-size: 1rem;
        color: #64748B;
        font-weight: 600;
    }
    .kpi-value.negative {
        color: #EF4444;
    }
    
    </style>
""", unsafe_allow_html=True)

# --- 2. Inicialización de Session State (Persistencia) ---
def init_session_state():
    defaults = {
        "land_cost": 100000.0,
        "hard_costs": 150000.0,
        "contingency_pct": 5.0,
        "soft_costs": 20000.0,
        "interest_cost": 10000.0,
        "target_price": 450000.0,
        "units": 1,
        "commission_pct": 6.0,
        "investor_capital": 100000.0,
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

# Helper para inputs de moneda con formato
def update_currency(state_key, widget_key):
    """Callback para actualizar el estado numérico desde el input de texto formateado."""
    val_str = st.session_state[widget_key]
    try:
        clean_val = val_str.replace(',', '')
        val_float = float(clean_val)
        if val_float < 0:
            raise ValueError("Negative value")
        st.session_state[state_key] = val_float
    except ValueError:
        st.toast("⚠️ Valor inválido. Use números positivos.")
        pass # Si falla la conversión, no actualizamos el estado numérico (se revertirá en el siguiente render)

def currency_input(label, state_key, help_text=None):
    # Clave única para el widget de texto
    widget_key = f"{state_key}_txt"
    
    # Si el widget aún no existe en el estado o no coincide con el valor numérico actual (ej. cambio externo),
    # inicializamos el valor del widget formateado.
    # Usamos el valor numérico actual de la fuente de la verdad (state_key)
    current_numeric_val = st.session_state[state_key]
    formatted_val = f"{current_numeric_val:,.2f}"
    
    # Inicializar el widget en session_state si no existe, para que tenga un valor por defecto
    if widget_key not in st.session_state:
        st.session_state[widget_key] = formatted_val
    
    # Sin embargo, para asegurar que refleje cambios externos o reinicios, 
    # verificamos si el valor parseado del widget coincide con el state numérico.
    # Si no coinciden (y no estamos justo en medio de un evento de edición de este widget), sincronizamos.
    # Una forma simple en Streamlit es simplemente pasar 'value' al text_input.
    # Pero 'value' y 'key' juntos en text_input lanzan warning si modificamos state[key] manualmente.
    # La mejor forma es dejar que el widget maneje su estado visual y solo forzarlo si cambia el numérico subyacente.
    
    # Enfoque simplificado: Usar on_change para actualizar el numérico.
    # Y reconstruir el widget en cada pasada con el valor formateado del numérico ACTUAL.
    # Esto sobreescribe lo que el usuario escribe SI Streamlit re-ejecuta, pero como es on_change, 
    # la re-ejecución ocurre DESPUÉS de capturar el input.
    
    st.text_input(
        label,
        value=formatted_val,
        key=widget_key,
        help=help_text,
        on_change=update_currency,
        args=(state_key, widget_key)
    )
    
    return st.session_state[state_key]

# --- 3. Panel de Control (Sidebar) ---
with st.sidebar:
    st.header("🎛️ Panel de Control")
    
    # Reset button
    if st.button("🔄 Reiniciar Valores por Defecto"):
        init_session_state()
        st.experimental_rerun() # Force rerun to reflect default values
    
    with st.expander("A. Variables del Proyecto", expanded=True):
        st.subheader("Costos de Desarrollo")
        # Reemplazo de number_input por currency_input
        land_cost = currency_input("Costo Terreno ($)", "land_cost")
        hard_costs = currency_input("Hard Costs ($)", "hard_costs", help_text="Costos directos de construcción: materiales, mano de obra, cimientos, estructura, acabados.")
        
        contingency_pct = st.slider("Contingencia (%)", 0.0, 20.0, st.session_state.contingency_pct, key="contingency_pct_input")
        # Actualizar state manualmente para slider (aunque key lo hace, explicitud para variables locales)
        st.session_state.contingency_pct = contingency_pct
        
        soft_costs = currency_input("Soft Costs ($)", "soft_costs", help_text="Costos indirectos: permisos, licencias, honorarios de arquitectos/ingenieros, estudios de suelo, marketing.")
        interest_cost = currency_input("Intereses/Financiamiento ($)", "interest_cost")
        
        st.subheader("Variables de Venta")
        units = st.number_input("Unidades", min_value=1, value=st.session_state.units, step=1, key="units_input")
        st.session_state.units = units
        
        # Mantenemos slider para target_price
        target_price_options = list(range(0, 1001000, 1000))
        target_price = st.select_slider(
            "Precio de Venta Target (Unitario) ($)", 
            options=target_price_options, 
            value=int(st.session_state.target_price), 
            format_func=lambda x: f"${x:,.0f}",
            key="target_price_input"
        )
        st.session_state.target_price = target_price
        
        commission_pct = st.number_input("Comisión de Venta (%)", 0.0, 20.0, st.session_state.commission_pct, step=0.5, key="commission_pct_input")
        st.session_state.commission_pct = commission_pct

    with st.expander("B. Estructura de Capital", expanded=True):
        investor_capital = currency_input("Capital Solicitado ($)", "investor_capital")
        investor_roi_target = st.number_input("Tasa ROI Ofrecida (% Anual)", min_value=0.0, value=st.session_state.investor_roi_target, step=0.1, key="investor_roi_target_input")
        st.session_state.investor_roi_target = investor_roi_target
        
        project_duration = st.number_input("Duración del Proyecto (Meses)", min_value=1, value=st.session_state.project_duration, step=1, key="project_duration_input")
        st.session_state.project_duration = project_duration

    with st.expander("C. Comparables de Mercado (CMA)", expanded=True):
        st.text("Testigos / Comparables")
        c1_col1, c1_col2 = st.columns([1.5, 1])
        with c1_col1: st.session_state.comp_1_name = st.text_input("Comp 1 Dirección", st.session_state.comp_1_name, key="c1_name")
        with c1_col2: st.session_state.comp_1_price = currency_input("Precio ($)", "comp_1_price")
        
        c2_col1, c2_col2 = st.columns([1.5, 1])
        with c2_col1: st.session_state.comp_2_name = st.text_input("Comp 2 Dirección", st.session_state.comp_2_name, key="c2_name")
        with c2_col2: st.session_state.comp_2_price = currency_input("Precio ($)", "comp_2_price")

        c3_col1, c3_col2 = st.columns([1.5, 1])
        with c3_col1: st.session_state.comp_3_name = st.text_input("Comp 3 Dirección", st.session_state.comp_3_name, key="c3_name")
        with c3_col2: st.session_state.comp_3_price = currency_input("Precio ($)", "comp_3_price")

# Variables derivadas para cálculos (leemos del state para asegurar consistencia)
land_cost = st.session_state.land_cost
hard_costs = st.session_state.hard_costs
contingency_pct = st.session_state.contingency_pct
soft_costs = st.session_state.soft_costs
interest_cost = st.session_state.interest_cost
target_price = st.session_state.target_price
units = st.session_state.units
commission_pct = st.session_state.commission_pct
investor_capital = st.session_state.investor_capital
investor_roi_target = st.session_state.investor_roi_target
project_duration = st.session_state.project_duration




st.title("🏗️ Real Estate ROI Visualizer")
st.markdown("---")

# --- 4. Lógica de Negocio (Backend) ---
# Cálculo de Costos
contingency_amount = hard_costs * (contingency_pct / 100.0)
hard_costs_total = hard_costs + contingency_amount
total_project_cost = land_cost + hard_costs_total + soft_costs + interest_cost

# Cálculo de Retornos e Ingresos
investor_return = investor_capital * (investor_roi_target / 100.0 / 12.0) * project_duration
gross_income = target_price * units
sales_commission = gross_income * (commission_pct / 100.0)

# Utilidad Neta Desarrollador
developer_net_profit = gross_income - total_project_cost - sales_commission - investor_return

# Cheque Final Inversionista
final_check_investor = investor_capital + investor_return

# --- 5. Visualización de Datos (Dashboard Principal) ---




# B. Sección 2: Análisis de Rentabilidad y Costos
st.subheader("Análisis de Rentabilidad y Estructura de Costos")

# Waterfall Chart
fig_waterfall = go.Figure(go.Waterfall(
    name = "20", orientation = "v",
    measure = ["relative", "relative", "relative", "relative", "relative", "relative", "relative", "total"],
    x = ["Ingreso Bruto", "Comisiones", "Terreno", "Construcción (Hard)", "Contingencia", "Blandos/Financiero", "Retorno Inversionista", "Utilidad Desarrollador"],
    textposition = "auto",
    cliponaxis=False,
    text = [f"${gross_income/1000:,.0f}k", f"-${sales_commission/1000:,.0f}k", f"-${land_cost/1000:,.0f}k", 
            f"-${hard_costs/1000:,.0f}k", f"-${contingency_amount/1000:,.0f}k", f"-${(soft_costs+interest_cost)/1000:,.0f}k", 
            f"-${investor_return/1000:,.0f}k", f"${developer_net_profit/1000:,.0f}k"],
    y = [gross_income, -sales_commission, -land_cost, -hard_costs, -contingency_amount, -(soft_costs + interest_cost), -investor_return, developer_net_profit],
    connector = {"line":{"color":"rgb(63, 63, 63)"}},
    increasing = {"marker":{"color":"#059669"}}, # Emerald Green
    decreasing = {"marker":{"color":"#EF4444"}}, # Red/Orange
    totals = {"marker":{"color":"#059669" if developer_net_profit >= 0 else "#EF4444"}}
))

fig_waterfall.update_layout(
    title = "Flujo de Caja del Proyecto (Waterfall)",
    showlegend = False,
    height=500,
    margin=dict(l=20, r=20, t=100, b=20)
)
st.plotly_chart(fig_waterfall, use_container_width=True)

# Donut Chart - Desglose de Costos (Salidas de dinero antes de utilidad)
# Agrupamos Costos de Proyecto + Comisiones + Retorno Inversionista
labels = ['Terreno', 'Construcción', 'Contingencia', 'Blandos', 'Financiero', 'Comisiones', 'Retorno Inv.']
values = [land_cost, hard_costs, contingency_amount, soft_costs, interest_cost, sales_commission, investor_return]

fig_donut = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.4,
                                    hovertemplate="<b>%{label}</b><br>%{value:,.0f} (%{percent})<extra></extra>")])
fig_donut.update_layout(
    title="Estructura de Egresos",
    height=600,
    legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05),
    margin=dict(l=20, r=150, t=50, b=20)
)
st.plotly_chart(fig_donut, use_container_width=True)


# C. Sección 3: Validación de Mercado (Comparables)
st.markdown("---")
st.subheader("Validación de Mercado (Comparables)")

# Preparar datos para gráfico de barras
comp_names = [st.session_state.comp_1_name, st.session_state.comp_2_name, st.session_state.comp_3_name, "Proyecto Actual"]
comp_prices = [st.session_state.comp_1_price, st.session_state.comp_2_price, st.session_state.comp_3_price, target_price]
colors = ['#64748B', '#64748B', '#64748B', '#10B981'] # Grises para comps, Verde para proyecto

fig_comps = go.Figure(data=[go.Bar(
    x=comp_names,
    y=comp_prices,
    marker_color=colors,
    text=[f"${x:,.0f}" for x in comp_prices],
    textposition='auto',
)])

# Calcular promedio de comparables para indicador
avg_comps = sum(comp_prices[:3]) / 3
diff_pct = ((target_price - avg_comps) / avg_comps) * 100

position_text = ""
if diff_pct > 0:
    position_text = f"El precio del proyecto está un {diff_pct:.1f}% POR ENCIMA del promedio de comparables."
else:
    position_text = f"El precio del proyecto está un {abs(diff_pct):.1f}% POR DEBAJO del promedio de comparables."

fig_comps.update_layout(
    title=f"Comparativa de Precios - {position_text}",
    yaxis_title="Precio de Venta ($)",
    height=400
)

st.plotly_chart(fig_comps, use_container_width=True)


# A. Sección 1: KPIs Financieros (Top Level)
st.markdown("---")
st.subheader("Resumen de Inversión / Datos Clave")
kpi1, kpi2, kpi3 = st.columns(3)

with kpi1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Tasa Anual Efectiva (Inversionista)</div>
        <div class="kpi-value">{investor_roi_target}%</div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    profit_color = "negative" if developer_net_profit < 0 else ""
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Ganancia Neta (Desarrollador)</div>
        <div class="kpi-value {profit_color}">${developer_net_profit:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Cheque Final (Inversionista)</div>
        <div class="kpi-value">${final_check_investor:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

# Alerta de Viabilidad
if developer_net_profit < 0:
    st.error("🚨 ALERTA: Proyecto No Viable. La utilidad del desarrollador es negativa. Revisa el precio de venta o los costos.")
