# Real Estate ROI Visualizer - Project Guidelines

## Overview
This is a Streamlit application designed to visualize the Return on Investment (ROI) for Real Estate development projects (Fix & Flip). It calculates project costs, financing (Hard Money & Private Money), sales metrics, and final profitability for the developer and investors.

## Application Structure

The application is a "One Page" layout divided into 6 logical sections:

### 1. Costos de Desarrollo (Development Costs)
*   **Inputs:**
    *   Valor del Terreno ($)
    *   Hard Costs (Construcción) ($)
    *   Contingencia (%): Applied to Hard Costs.
    *   Soft Costs ($)
*   **Logic:** Contingency Amount = Hard Costs * %.

### 2. Préstamo HM Lender (Hard Money Loan)
*   **Monto Base:** Calculated as `Land Cost + Hard Costs + Contingency Amount`. (Soft costs are excluded from the collateral base).
*   **Inputs:**
    *   Porcentaje del Préstamo Otorgado (LTC %): Default 85%.
    *   Puntos de Originación (%): Default 1.5%.
    *   Gastos Mortgage (%): Default 2.0%.
    *   Interés Anual (%): Default 10.0%.
    *   Duración Préstamo (Meses): Default 6.
*   **Calculations:**
    *   `Loan Principal` = Base Amount * LTC %.
    *   `Origination Fees` = Principal * %.
    *   `Mortgage Fees` = Principal * %.
    *   `HML Interest Total` = Principal * Annual Rate * (Duration / 12).

### 3. Préstamo PML (Private Money Lender)
*   **Capital Solicitado (Calculated):** Automatically derived as the **Hard Money Gap only**.
    *   Formula: `HML Base Amount - HML Loan Principal`.
    *   *Note:* Rounded up to the nearest $1,000.
*   **Inputs:**
    *   Retorno Ofrecido (ROI % Anual).
    *   Duración Proyecto (Meses).
*   **Calculations:**
    *   `Investor Return Amount` = Capital * ROI % * (Duration / 12).

### 4. Variables de Venta (Sales)
*   **Inputs:**
    *   Unidades.
    *   Precio Unitario.
    *   Comisión Realtor + Closing Cost (%).
*   **Calculations:**
    *   `Gross Income` = Units * Price.
    *   `Sales Commission` = Gross Income * Commission %.

### 5. Comparables de Mercado (CMA)
*   Inputs for 3 comparable properties (Address & Price).
*   Visual bar chart comparing them to the project's target price.

### 6. Análisis Financiero y Resumen
*   **Charts:** Waterfall (Cash Flow) and Donut (Cost Structure).
*   **Key Financial Metrics:**

    *   **Total Project Costs (Costo Total del Proyecto):**
        `Land + Hard + Contingency + Soft + PML Interest + HML Fees (Orig+Mortgage) + HML Interest + Sales Commissions`.

    *   **Project Profit (Ganancia del Proyecto):**
        `Gross Income - Total Project Costs`.
        *Note:* Renamed from "Ganancia del Desarrollador".

    *   **Total Investor Payout (Total a Devolver al Inversionista):**
        `PML Capital + PML Interest`.

    *   **Profitability Status:**
        Display a Success message if Profit > 0, otherwise an Error message.

## Default Values
*   Land: $8,000
*   Hard: $120,000
*   Soft: $117,000
*   Contingency: 10%
*   PML Capital: Dynamic based on HML Gap.
*   HML LTC: 85%

## Technical Notes
*   **Number Formatting:** All currency inputs utilize a helper function to enforce thousands separators and 2 decimal places (e.g., `1,234.56`) upon confirmation.
*   **Streamlit Cloud:** Uses `st.rerun()` for compatibility.
*   **Data Types:** Duration inputs use `float` to prevent type errors during session state updates.