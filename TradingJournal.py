# ============================================================
# TRADING PnL DASHBOARD – NUR ABGESCHLOSSENE TRADES
# MINIMAL, LUXURIÖS, DAUERHAFTE SPEICHERUNG (SQLite)
# KORRIGIERT: Überschriften hinzugefügt, Haupttitel weiter nach unten
# ============================================================

import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# ============================================================
# 1. SEITENKONFIGURATION
# ============================================================

st.set_page_config(page_title="Trading PnL Dashboard", layout="wide")

# ============================================================
# 2. CSS – DARK LUXURY STYLE
# ============================================================

def render_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        * { font-family: 'Inter', sans-serif; box-sizing: border-box; }
        
        .stApp {
            background: linear-gradient(160deg, #0A0A0A 0%, #1A1A1A 35%, #222222 65%, #0A0A0A 100%);
            min-height: 100vh;
        }
        
        .stApp::before {
            content: '';
            position: fixed;
            top: -20%;
            left: -20%;
            width: 140%;
            height: 140%;
            background: radial-gradient(ellipse at 40% 30%, rgba(212, 168, 83, 0.03) 0%, transparent 60%);
            pointer-events: none;
            z-index: 0;
        }
        
        .main > div {
            background: transparent;
            max-width: 1400px;
            margin: 0 auto;
            padding: 1rem 2rem 4rem 2rem;
            position: relative;
            z-index: 1;
        }
        
        .block-container {
            padding-top: 0.5rem;
            padding-bottom: 4rem;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .title-wrapper {
            display: flex;
            justify-content: center;
            width: 100%;
            margin: 2rem auto 2.5rem auto;
        }
        
        .main-title {
            font-size: 2.4rem;
            font-weight: 800;
            letter-spacing: 0.04em;
            text-align: center;
            margin: 0;
            color: #FFFFFF;
            line-height: 1.2;
            text-shadow: 0 2px 40px rgba(212, 168, 83, 0.05);
        }
        
        .main-title span {
            background: linear-gradient(135deg, #D4A853 0%, #F5D98E 50%, #D4A853 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .section-label {
            color: rgba(255, 255, 255, 0.35);
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.15em;
            margin-bottom: 0.8rem;
        }
        
        .metric-container {
            background: rgba(255, 255, 255, 0.02);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 16px;
            padding: 1.2rem 1.5rem;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        
        .metric-label {
            font-size: 0.65rem;
            text-transform: uppercase;
            letter-spacing: 0.15em;
            color: rgba(255, 255, 255, 0.3);
            margin-bottom: 0.3rem;
        }
        
        .metric-value {
            font-size: 1.6rem;
            font-weight: 700;
            color: #FFFFFF;
        }
        
        .metric-value.positive { color: #4CAF50; }
        .metric-value.negative { color: #F44336; }
        
        .stDataFrame {
            background: rgba(255, 255, 255, 0.02) !important;
            backdrop-filter: blur(8px);
            border-radius: 16px !important;
            border: 1px solid rgba(255, 255, 255, 0.04) !important;
            overflow: hidden;
            margin: 0 auto 1rem auto;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        
        .stDataFrame th {
            background: rgba(255, 255, 255, 0.03) !important;
            color: rgba(255, 255, 255, 0.2) !important;
            font-weight: 500 !important;
            font-size: 0.6rem !important;
            text-transform: uppercase !important;
            letter-spacing: 0.2em !important;
            text-align: center !important;
            padding: 0.6rem 1rem !important;
            border-bottom: 1px solid rgba(255, 255, 255, 0.03) !important;
        }
        
        .stDataFrame td {
            background: transparent !important;
            color: rgba(255, 255, 255, 0.8) !important;
            text-align: center !important;
            padding: 0.5rem 1rem !important;
            font-size: 0.85rem !important;
            border-bottom: 1px solid rgba(255, 255, 255, 0.02) !important;
        }
        
        .stDataFrame tr:hover td {
            background: rgba(255, 255, 255, 0.03) !important;
        }
        
        .stDataFrame tr:last-child td {
            border-bottom: none !important;
        }

        .input-area {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 16px;
            padding: 1.5rem 2rem;
            margin-bottom: 2rem;
        }
        
        .input-area .stTextInput input,
        .input-area .stNumberInput input,
        .input-area .stDateInput input,
        .input-area .stSelectbox div {
            background: rgba(255, 255, 255, 0.03) !important;
            border: 1px solid rgba(255, 255, 255, 0.06) !important;
            border-radius: 8px !important;
            color: white !important;
        }
        
        .input-area .stButton button {
            background: linear-gradient(135deg, #D4A853 0%, #F5D98E 100%) !important;
            color: #0A0A0A !important;
            font-weight: 600 !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.5rem 2rem !important;
            transition: all 0.3s ease !important;
            width: 100% !important;
        }
        
        .input-area .stButton button:hover {
            transform: scale(1.02);
            box-shadow: 0 4px 20px rgba(212, 168, 83, 0.3);
        }
    </style>
    """, unsafe_allow_html=True)

# ============================================================
# 3. DATENBANK-FUNKTIONEN (SQLite)
# ============================================================

DB_PATH = "trades.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            instrument TEXT,
            direction TEXT,
            risk_reward_ratio REAL,
            pnl_percent REAL
        )
    ''')
    conn.commit()
    conn.close()

def add_trade(date, instrument, direction, risk_reward_ratio, pnl_percent):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO trades (date, instrument, direction, risk_reward_ratio, pnl_percent)
        VALUES (?, ?, ?, ?, ?)
    ''', (date, instrument, direction, risk_reward_ratio, pnl_percent))
    conn.commit()
    conn.close()

def get_all_trades():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM trades ORDER BY date ASC", conn)
    conn.close()
    return df

# ============================================================
# 4. KENNZAHLEN BERECHNEN
# ============================================================

def calculate_metrics(df):
    if df.empty:
        return {
            "total_pnl": 0.0,
            "total_trades": 0,
            "win_rate": 0.0,
            "profit_factor": 0.0,
            "avg_pnl": 0.0,
            "cumulative_pnl": []
        }
    
    total_trades = len(df)
    wins = df[df['pnl_percent'] > 0]
    losses = df[df['pnl_percent'] < 0]
    
    total_pnl = df['pnl_percent'].sum()
    win_rate = (len(wins) / total_trades * 100) if total_trades > 0 else 0.0
    
    sum_wins = wins['pnl_percent'].sum() if not wins.empty else 0.0
    sum_losses = abs(losses['pnl_percent'].sum()) if not losses.empty else 0.0
    profit_factor = sum_wins / sum_losses if sum_losses > 0 else 0.0
    
    avg_pnl = df['pnl_percent'].mean() if total_trades > 0 else 0.0
    
    df['cumulative'] = df['pnl_percent'].cumsum()
    cumulative_pnl = df[['date', 'cumulative']].to_dict('records')
    
    return {
        "total_pnl": total_pnl,
        "total_trades": total_trades,
        "win_rate": win_rate,
        "profit_factor": profit_factor,
        "avg_pnl": avg_pnl,
        "cumulative_pnl": cumulative_pnl
    }

# ============================================================
# 5. DASHBOARD UI
# ============================================================

def main():
    render_css()
    
    init_db()
    
    # ============================================================
    # 5.1 TITEL (weiter nach unten)
    # ============================================================
    
    st.markdown("""
        <div class="title-wrapper">
            <h1 class="main-title">📊 TRADING <span>PnL DASHBOARD</span></h1>
        </div>
    """, unsafe_allow_html=True)
    
    # ============================================================
    # 5.2 EINGABE (Neuer Trade)
    # ============================================================
    
    with st.container():
        st.markdown('<div class="input-area">', unsafe_allow_html=True)
        st.markdown('<p style="color: rgba(255,255,255,0.4); font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 1rem;">➕ Neuen Trade erfassen</p>', unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5, col6 = st.columns([1.2, 1, 1, 1.5, 1.5, 0.8])
        
        with col1:
            date = st.date_input("Datum", value=datetime.today(), label_visibility="collapsed")
        with col2:
            instrument = st.text_input("Instrument", placeholder="z.B. AAPL", label_visibility="collapsed")
        with col3:
            direction = st.selectbox("Richtung", ["Long", "Short"], label_visibility="collapsed")
        with col4:
            risk_reward = st.number_input("Risk-Reward", min_value=0.0, value=2.0, step=0.1, format="%.1f", label_visibility="collapsed")
        with col5:
            pnl = st.number_input("PnL (%)", min_value=-100.0, max_value=100.0, value=0.0, step=0.1, format="%.1f", label_visibility="collapsed")
        with col6:
            if st.button("➕ Speichern"):
                if instrument.strip() == "":
                    st.warning("Bitte ein Instrument eingeben.")
                else:
                    add_trade(
                        date=str(date),
                        instrument=instrument.strip().upper(),
                        direction=direction,
                        risk_reward_ratio=risk_reward,
                        pnl_percent=pnl
                    )
                    st.success("Trade gespeichert!")
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ============================================================
    # 5.3 DATEN LADEN
    # ============================================================
    
    df = get_all_trades()
    
    if df.empty:
        st.info("📭 Noch keine Trades erfasst. Füge deinen ersten Trade hinzu!")
        return
    
    metrics = calculate_metrics(df)
    
    # ============================================================
    # 5.4 METRIKEN (ÜBERSICHT)
    # ============================================================
    
    st.markdown('<p class="section-label">📊 Performance-Übersicht</p>', unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_pnl = metrics["total_pnl"]
        color = "positive" if total_pnl >= 0 else "negative"
        st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">Total PnL (%)</div>
                <div class="metric-value {color}">{total_pnl:+.1f}%</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">Trades</div>
                <div class="metric-value">{metrics['total_trades']}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        win_rate = metrics["win_rate"]
        color = "positive" if win_rate >= 50 else "negative"
        st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">Win Rate</div>
                <div class="metric-value {color}">{win_rate:.1f}%</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        pf = metrics["profit_factor"]
        color = "positive" if pf >= 1.0 else "negative"
        st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">Profit Factor</div>
                <div class="metric-value {color}">{pf:.2f}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col5:
        avg = metrics["avg_pnl"]
        color = "positive" if avg >= 0 else "negative"
        st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">Ø PnL / Trade</div>
                <div class="metric-value {color}">{avg:+.1f}%</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ============================================================
    # 5.5 BALKENDIAGRAMM (PnL pro Trade)
    # ============================================================
    
    st.markdown('<p class="section-label">📊 PnL (%) pro Trade</p>', unsafe_allow_html=True)
    
    fig = go.Figure()
    
    colors = ['#4CAF50' if val >= 0 else '#F44336' for val in df['pnl_percent']]
    fig.add_trace(go.Bar(
        x=df.index,
        y=df['pnl_percent'],
        marker_color=colors,
        text=df['pnl_percent'].apply(lambda x: f"{x:+.1f}%"),
        textposition="outside",
        name="PnL (%)",
        hovertemplate="Trade %{x}<br>PnL: %{y:+.1f}%<extra></extra>"
    ))
    
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        showlegend=False,
        yaxis=dict(
            title="PnL (%)",
            gridcolor="rgba(255,255,255,0.05)",
            zerolinecolor="rgba(255,255,255,0.1)",
            zerolinewidth=1
        ),
        xaxis=dict(
            title="Trade",
            gridcolor="rgba(255,255,255,0.05)",
            tickmode='linear',
            tick0=0,
            dtick=1
        ),
        height=300,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # ============================================================
    # 5.6 KUMULATIVER PnL (%)
    # ============================================================
    
    st.markdown('<p class="section-label">📈 Kumulativer PnL (%)</p>', unsafe_allow_html=True)
    
    df['cumulative'] = df['pnl_percent'].cumsum()
    
    fig2 = go.Figure()
    
    fig2.add_trace(go.Scatter(
        x=df.index,
        y=df['cumulative'],
        mode='lines+markers',
        name='Kumulativ',
        line=dict(color='#D4A853', width=2.5),
        marker=dict(color='#D4A853', size=6),
        fill='tozeroy',
        fillcolor='rgba(212, 168, 83, 0.1)',
        hovertemplate="Trade %{x}<br>Kumulativ: %{y:+.1f}%<extra></extra>"
    ))
    
    fig2.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        showlegend=False,
        yaxis=dict(
            title="Kumulativer PnL (%)",
            gridcolor="rgba(255,255,255,0.05)",
            zerolinecolor="rgba(255,255,255,0.1)",
            zerolinewidth=1
        ),
        xaxis=dict(
            title="Trade",
            gridcolor="rgba(255,255,255,0.05)",
            tickmode='linear',
            tick0=0,
            dtick=1
        ),
        height=250,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # ============================================================
    # 5.7 ALLE TRADES (Tabelle)
    # ============================================================
    
    st.markdown('<p class="section-label">📋 Alle Trades</p>', unsafe_allow_html=True)
    
    display_df = df.copy()
    display_df['#'] = display_df.index + 1
    display_df = display_df[['#', 'date', 'instrument', 'direction', 'risk_reward_ratio', 'pnl_percent']]
    display_df.columns = ['#', 'Datum', 'Instrument', 'Richtung', 'Risk-Reward', 'PnL (%)']
    display_df['PnL (%)'] = display_df['PnL (%)'].apply(lambda x: f"{x:+.1f}%")
    display_df['Risk-Reward'] = display_df['Risk-Reward'].apply(lambda x: f"{x:.1f}")
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # ============================================================
    # 5.8 EXPORT
    # ============================================================
    
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("📥 CSV Export"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="CSV herunterladen",
                data=csv,
                file_name=f"trades_{datetime.today().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                key="download_csv"
            )

if __name__ == "__main__":
    main()