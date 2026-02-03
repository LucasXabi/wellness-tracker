"""
🏉 Rugby Wellness Tracker - Version Complète avec Fiche Joueur
Application Streamlit avec toutes les fonctionnalités du React
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import re
import urllib.parse
import calendar

# ==================== CONFIG ====================
st.set_page_config(page_title="Rugby Wellness Tracker", page_icon="🏉", layout="wide", initial_sidebar_state="expanded")

# ==================== CSS PERSONNALISÉ ====================
st.markdown("""
<style>
    .main .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .player-card {
        background: linear-gradient(135deg, #1f2937, #111827);
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid #374151;
        margin-bottom: 8px;
    }
    .metric-badge {
        display: inline-block;
        width: 32px;
        height: 32px;
        border-radius: 6px;
        text-align: center;
        line-height: 32px;
        font-size: 14px;
        font-weight: bold;
        color: white;
        margin: 2px;
    }
    .alert-critical { background: rgba(239, 68, 68, 0.15); border: 1px solid #ef4444; }
    .alert-warning { background: rgba(245, 158, 11, 0.15); border: 1px solid #f59e0b; }
    .team-avg-card {
        background: linear-gradient(135deg, #065f46, #047857);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
    }
    .player-header {
        background: linear-gradient(135deg, #1f2937, #111827);
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid #374151;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: #1f2937;
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #374151;
        text-align: center;
    }
    .calendar-day {
        width: 40px;
        height: 40px;
        border-radius: 8px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        margin: 2px;
    }
</style>
""", unsafe_allow_html=True)

# ==================== CONSTANTES ====================
METRICS = [
    {'key': 'sleep', 'label': 'Sommeil', 'icon': '😴', 'color': '#3b82f6'},
    {'key': 'mentalLoad', 'label': 'Charge Mentale', 'icon': '🧠', 'color': '#8b5cf6'},
    {'key': 'motivation', 'label': 'Motivation', 'icon': '💪', 'color': '#f59e0b'},
    {'key': 'hdcState', 'label': 'HDC', 'icon': '❤️', 'color': '#ef4444'},
    {'key': 'bdcState', 'label': 'BDC', 'icon': '💚', 'color': '#10b981'},
]

RUGBY_POSITIONS = {
    'Avants': {
        '1ère ligne': ['Pilier gauche', 'Talonneur', 'Pilier droit'],
        '2ème ligne': ['2ème ligne'],
        '3ème ligne': ['3ème ligne aile', '3ème ligne centre'],
    },
    'Trois-quarts': {
        'Demis': ['Demi de mêlée', "Demi d'ouverture"],
        'Centres': ['Centre'],
        'Ailiers': ['Ailier'],
        'Arrière': ['Arrière'],
    }
}

ALL_POSITIONS = []
for group in RUGBY_POSITIONS.values():
    for positions in group.values():
        ALL_POSITIONS.extend(positions)

ALL_LINES = list(RUGBY_POSITIONS['Avants'].keys()) + list(RUGBY_POSITIONS['Trois-quarts'].keys())

INJURY_ZONES = {
    'Ischio-jambiers': {'icon': '🦵', 1: 14, 2: 28, 3: 56},
    'Quadriceps': {'icon': '🦵', 1: 10, 2: 21, 3: 42},
    'Mollet': {'icon': '🦵', 1: 10, 2: 21, 3: 42},
    'Adducteurs': {'icon': '🦵', 1: 10, 2: 21, 3: 42},
    'Genou - LCA': {'icon': '🦿', 1: 180, 2: 240, 3: 300},
    'Genou - Ménisque': {'icon': '🦿', 1: 21, 2: 42, 3: 90},
    'Genou - Entorse': {'icon': '🦿', 1: 14, 2: 28, 3: 56},
    'Cheville': {'icon': '🦶', 1: 10, 2: 21, 3: 42},
    'Épaule - Luxation': {'icon': '💪', 1: 21, 2: 42, 3: 120},
    'Épaule - Autre': {'icon': '💪', 1: 14, 2: 28, 3: 56},
    'Dos': {'icon': '🔙', 1: 7, 2: 21, 3: 42},
    'Cou': {'icon': '🔙', 1: 7, 2: 14, 3: 28},
    'Commotion': {'icon': '🧠', 1: 12, 2: 21, 3: 35},
    'Côtes': {'icon': '🫁', 1: 14, 2: 28, 3: 42},
    'Poignet/Main': {'icon': '✋', 1: 14, 2: 28, 3: 56},
    'Pied': {'icon': '🦶', 1: 14, 2: 28, 3: 56},
    'Autre': {'icon': '🏥', 1: 14, 2: 28, 3: 56},
}

CIRCUMSTANCES = ['Match', 'Entraînement', 'Musculation', 'Hors sport', 'Autre']
STATUSES = ['Apte', 'Blessé', 'Réhabilitation', 'Réathlétisation']

FRENCH_MONTHS = {
    'janvier': 1, 'février': 2, 'fevrier': 2, 'mars': 3, 'avril': 4,
    'mai': 5, 'juin': 6, 'juillet': 7, 'août': 8, 'aout': 8,
    'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12, 'decembre': 12
}

DEFAULT_SETTINGS = {
    'lowValueThreshold': 2,
    'variationThreshold': 1.5,
    'weightThreshold': 2.0,
    'zscoreDays': 14,
    'zscoreAlert': -1.5,
    'zscoreWarning': -1.0,
}

# ==================== SESSION STATE ====================
def init_session():
    defaults = {
        'players': [],
        'data': {},
        'injuries': [],
        'settings': DEFAULT_SETTINGS.copy(),
        'selected_player_id': None,
        'selected_modal_date': None,
        'status_filter': None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_session()

# ==================== UTILITAIRES ====================
def get_player_group(position):
    for group_name, lines in RUGBY_POSITIONS.items():
        for line_positions in lines.values():
            if position in line_positions:
                return group_name
    return 'Avants'

def get_player_line(position):
    for lines in RUGBY_POSITIONS.values():
        for line_name, line_positions in lines.items():
            if position in line_positions:
                return line_name
    return '1ère ligne'

def format_date(date_str, fmt='short'):
    if not date_str:
        return '-'
    try:
        d = datetime.strptime(date_str, '%Y-%m-%d')
        if fmt == 'short':
            return d.strftime('%d %b')
        elif fmt == 'full':
            return d.strftime('%A %d %B %Y').replace('Monday', 'lundi').replace('Tuesday', 'mardi').replace('Wednesday', 'mercredi').replace('Thursday', 'jeudi').replace('Friday', 'vendredi').replace('Saturday', 'samedi').replace('Sunday', 'dimanche').replace('January', 'janvier').replace('February', 'février').replace('March', 'mars').replace('April', 'avril').replace('May', 'mai').replace('June', 'juin').replace('July', 'juillet').replace('August', 'août').replace('September', 'septembre').replace('October', 'octobre').replace('November', 'novembre').replace('December', 'décembre')
        else:
            return d.strftime('%d/%m/%Y')
    except:
        return date_str

def get_player_average(player_data):
    if not player_data:
        return None
    vals = [player_data.get(m['key']) for m in METRICS if player_data.get(m['key']) is not None]
    return sum(vals) / len(vals) if vals else None

def get_team_avg(date_key, group=None, line=None):
    data = st.session_state.data.get(date_key, [])
    if not data:
        return None
    
    filtered = []
    for d in data:
        p = next((p for p in st.session_state.players if p['name'] == d['name']), None)
        if not p:
            continue
        if group and get_player_group(p['position']) != group:
            continue
        if line and get_player_line(p['position']) != line:
            continue
        filtered.append(d)
    
    if not filtered:
        return None
    
    result = {'count': len(filtered)}
    for m in METRICS:
        vals = [d[m['key']] for d in filtered if d.get(m['key']) is not None]
        result[m['key']] = sum(vals) / len(vals) if vals else None
    
    all_avgs = [get_player_average(d) for d in filtered]
    all_avgs = [a for a in all_avgs if a is not None]
    result['global'] = sum(all_avgs) / len(all_avgs) if all_avgs else None
    
    return result

def get_group_avg(date_key, group=None, line=None, position=None):
    return get_team_avg(date_key, group=group, line=line)

def get_alerts(date_key):
    data = st.session_state.data.get(date_key, [])
    settings = st.session_state.settings
    alerts = []
    
    for d in data:
        p = next((p for p in st.session_state.players if p['name'] == d['name']), None)
        if not p:
            continue
        
        # Valeurs basses
        for m in METRICS:
            val = d.get(m['key'])
            if val is not None and val <= settings['lowValueThreshold']:
                alerts.append({
                    'player': d['name'],
                    'type': 'critical',
                    'metric': m,
                    'value': val,
                    'message': f"{m['label']} à {val}/5"
                })
        
        # Poids
        if d.get('weight') and p.get('targetWeight'):
            diff = abs(d['weight'] - p['targetWeight'])
            if diff > settings['weightThreshold']:
                alerts.append({
                    'player': d['name'],
                    'type': 'weight',
                    'diff': round(d['weight'] - p['targetWeight'], 1),
                    'message': f"Poids {d['weight']:.1f}kg (forme: {p['targetWeight']}kg)"
                })
    
    return alerts

def get_availability_data():
    """Retourne les données pour le pie chart de disponibilité"""
    counts = {}
    for p in st.session_state.players:
        status = p.get('status', 'Apte')
        counts[status] = counts.get(status, 0) + 1
    
    colors = {
        'Apte': '#10b981',
        'Blessé': '#ef4444',
        'Réhabilitation': '#f59e0b',
        'Réathlétisation': '#3b82f6'
    }
    
    return [{'name': k, 'value': v, 'color': colors.get(k, '#6b7280')} for k, v in counts.items() if v > 0]

def get_player_history(player_name, days=30):
    """Récupère l'historique d'un joueur sur N jours"""
    dates = sorted(st.session_state.data.keys(), reverse=True)[:days]
    history = []
    for date in reversed(dates):
        data = st.session_state.data.get(date, [])
        pd_data = next((d for d in data if d['name'] == player_name), None)
        if pd_data:
            avg = get_player_average(pd_data)
            history.append({'date': date, 'avg': avg, **pd_data})
    return history

def calculate_zscore(value, prev_values):
    if not prev_values or len(prev_values) < 3:
        return 0
    mean = sum(prev_values) / len(prev_values)
    std = (sum((v - mean) ** 2 for v in prev_values) / len(prev_values)) ** 0.5
    if std == 0:
        return 0
    return (value - mean) / std

# ==================== GRAPHIQUES ====================
def radar_chart(data1, data2, label1, label2):
    categories = [m['label'] for m in METRICS]
    
    fig = go.Figure()
    
    if data1:
        vals1 = [data1.get(m['key'], 0) or 0 for m in METRICS]
        vals1.append(vals1[0])
        fig.add_trace(go.Scatterpolar(r=vals1, theta=categories + [categories[0]], fill='toself', name=label1, line=dict(color='#10b981'), fillcolor='rgba(16,185,129,0.3)'))
    
    if data2:
        vals2 = [data2.get(m['key'], 0) or 0 for m in METRICS]
        vals2.append(vals2[0])
        fig.add_trace(go.Scatterpolar(r=vals2, theta=categories + [categories[0]], fill='toself', name=label2, line=dict(color='#3b82f6'), fillcolor='rgba(59,130,246,0.2)'))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 5], showticklabels=False), bgcolor='rgba(31,41,55,1)'),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#9ca3af'),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        margin=dict(l=60, r=60, t=40, b=60),
        height=280
    )
    return fig

def availability_pie_chart():
    """Crée le pie chart de disponibilité"""
    avail_data = get_availability_data()
    if not avail_data:
        return None
    
    fig = go.Figure(data=[go.Pie(
        labels=[d['name'] for d in avail_data],
        values=[d['value'] for d in avail_data],
        hole=0.5,
        marker=dict(colors=[d['color'] for d in avail_data]),
        textinfo='none',
        hovertemplate='%{label}: %{value}<extra></extra>'
    )])
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#9ca3af'),
        showlegend=False,
        margin=dict(l=10, r=10, t=10, b=10),
        height=150
    )
    return fig

def zscore_series(metric='global', group=None, line=None, player=None, days=30):
    dates = sorted(st.session_state.data.keys())[-days:]
    if len(dates) < 5:
        return []
    
    result = []
    for i, date in enumerate(dates):
        data = st.session_state.data.get(date, [])
        if not data:
            continue
        
        day_values = []
        for d in data:
            p = next((p for p in st.session_state.players if p['name'] == d['name']), None)
            if not p:
                continue
            if group and get_player_group(p['position']) != group:
                continue
            if line and get_player_line(p['position']) != line:
                continue
            if player and d['name'] != player:
                continue
            
            if metric == 'global':
                val = get_player_average(d)
            else:
                val = d.get(metric)
            
            if val is not None:
                day_values.append(val)
        
        if day_values:
            day_avg = sum(day_values) / len(day_values)
            prev_avgs = [r['value'] for r in result[-14:]]
            zscore = calculate_zscore(day_avg, prev_avgs) if len(prev_avgs) >= 3 else 0
            result.append({'date': date, 'value': day_avg, 'zscore': round(zscore, 2)})
    
    return result

def zscore_chart(data):
    if not data or len(data) < 5:
        return None
    
    df = pd.DataFrame(data)
    df['fmt'] = df['date'].apply(lambda x: format_date(x, 'short'))
    
    settings = st.session_state.settings
    colors = ['#ef4444' if z < settings['zscoreAlert'] else '#f59e0b' if z < settings['zscoreWarning'] else '#10b981' for z in df['zscore']]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df['fmt'], y=df['zscore'], marker_color=colors, name='Z-Score'))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(31,41,55,1)',
        font=dict(color='#9ca3af'), margin=dict(l=40, r=40, t=20, b=40),
        height=250, xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#374151', range=[-3, 3]),
        showlegend=False
    )
    return fig

def weight_chart(player_name, days=30):
    dates = sorted(st.session_state.data.keys())[-days:]
    if not dates:
        return None
    
    p = next((p for p in st.session_state.players if p['name'] == player_name), None)
    target = p.get('targetWeight', 90) if p else 90
    
    chart_data = []
    for date in dates:
        data = st.session_state.data.get(date, [])
        pd_data = next((d for d in data if d['name'] == player_name), None)
        if pd_data and pd_data.get('weight'):
            chart_data.append({
                'date': format_date(date),
                'weight': pd_data['weight'],
                'min': target - 2,
                'max': target + 2
            })
    
    if not chart_data:
        return None
    
    df = pd.DataFrame(chart_data)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['date'], y=df['min'], mode='lines', line=dict(color='#6b7280', dash='dash'), name='Min'))
    fig.add_trace(go.Scatter(x=df['date'], y=df['max'], mode='lines', line=dict(color='#6b7280', dash='dash'), name='Max', fill='tonexty', fillcolor='rgba(107,114,128,0.1)'))
    fig.add_trace(go.Scatter(x=df['date'], y=df['weight'], mode='lines+markers', line=dict(color='#10b981', width=2), name='Poids'))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(31,41,55,1)',
        font=dict(color='#9ca3af'), margin=dict(l=40, r=40, t=20, b=40),
        height=220, showlegend=False,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#374151')
    )
    return fig

def player_zscore_bars(player_name, days=30):
    """Crée le graphique de barres Z-Score pour un joueur"""
    history = get_player_history(player_name, days)
    if len(history) < 5:
        return None
    
    result = []
    for i, day in enumerate(history):
        prev_avgs = [h['avg'] for h in history[:i] if h.get('avg') is not None]
        if day.get('avg') is not None and len(prev_avgs) >= 3:
            zscore = calculate_zscore(day['avg'], prev_avgs[-14:])
            result.append({'date': format_date(day['date']), 'zscore': round(zscore, 2)})
    
    if not result:
        return None
    
    df = pd.DataFrame(result)
    settings = st.session_state.settings
    colors = ['#ef4444' if z < settings['zscoreAlert'] else '#f59e0b' if z < settings['zscoreWarning'] else '#10b981' for z in df['zscore']]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df['date'], y=df['zscore'], marker_color=colors))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(31,41,55,1)',
        font=dict(color='#9ca3af'), margin=dict(l=40, r=40, t=20, b=40),
        height=150, xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#374151', range=[-3, 3]),
        showlegend=False
    )
    return fig

# ==================== FICHE JOUEUR (MODAL) ====================
@st.dialog("📋 Fiche Joueur", width="large")
def show_player_modal(player_id):
    player = next((p for p in st.session_state.players if p['id'] == player_id), None)
    if not player:
        st.error("Joueur non trouvé")
        return
    
    dates = sorted(st.session_state.data.keys(), reverse=True)
    if not dates:
        st.warning("Aucune donnée disponible")
        return
    
    # Sélecteur de date
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;">
            <div style="width:56px;height:56px;border-radius:12px;background:linear-gradient(135deg,#10b981,#059669);display:flex;align-items:center;justify-content:center;font-size:24px;font-weight:bold;color:white;">{player['name'][0]}</div>
            <div>
                <div style="font-size:20px;font-weight:bold;color:white;">{player['name']}</div>
                <div style="font-size:13px;color:#9ca3af;">{player['position']} • {get_player_group(player['position'])} • {get_player_line(player['position'])}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        sel_date = st.selectbox("Date", dates[:30], format_func=lambda x: format_date(x, 'short'), key="modal_date")
    
    # Badge statut
    status_colors = {'Apte': '#10b981', 'Blessé': '#ef4444', 'Réhabilitation': '#f59e0b', 'Réathlétisation': '#3b82f6'}
    st.markdown(f'<span style="background:{status_colors.get(player["status"], "#6b7280")};color:white;padding:4px 12px;border-radius:20px;font-size:12px;">{player["status"]}</span>', unsafe_allow_html=True)
    
    st.divider()
    
    # Données du jour
    today_data = st.session_state.data.get(sel_date, [])
    pd = next((d for d in today_data if d['name'] == player['name']), {})
    avg = get_player_average(pd)
    team_avg = get_team_avg(sel_date)
    diff_vs_team = (avg - team_avg['global']) if avg and team_avg and team_avg.get('global') else None
    
    # Moyenne joueur vs équipe
    c1, c2 = st.columns(2)
    with c1:
        avg_str = f"{avg:.2f}" if avg else "-"
        diff_str = f"({'+' if diff_vs_team and diff_vs_team > 0 else ''}{diff_vs_team:.2f} vs équipe)" if diff_vs_team else ""
        diff_color = "#10b981" if diff_vs_team and diff_vs_team >= 0 else "#ef4444"
        st.markdown(f"""
        <div style="background:#1f2937;padding:12px;border-radius:8px;border:1px solid #374151;">
            <div style="font-size:11px;color:#9ca3af;">Moyenne joueur</div>
            <div style="font-size:28px;font-weight:bold;color:white;">{avg_str}/5 <span style="font-size:14px;color:{diff_color};">{diff_str}</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    with c2:
        team_str = f"{team_avg['global']:.2f}" if team_avg and team_avg.get('global') else "-"
        st.markdown(f"""
        <div style="background:#1f2937;padding:12px;border-radius:8px;border:1px solid #374151;text-align:right;">
            <div style="font-size:11px;color:#9ca3af;">Moyenne équipe</div>
            <div style="font-size:28px;font-weight:bold;color:#10b981;">{team_str}/5</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Métriques du jour
    st.markdown("#### 📊 Métriques du jour")
    cols = st.columns(7)
    
    # Poids
    weight_val = pd.get('weight')
    with cols[0]:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size:10px;color:#9ca3af;">⚖️ Poids</div>
            <div style="font-size:18px;font-weight:bold;color:white;">{f"{weight_val:.1f}kg" if weight_val else "-"}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # 5 métriques
    for i, m in enumerate(METRICS):
        val = pd.get(m['key'])
        with cols[i + 1]:
            color = '#ef4444' if val and val <= 2 else '#f59e0b' if val and val <= 3 else '#10b981' if val else '#6b7280'
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size:10px;color:#9ca3af;">{m['icon']} {m['label'][:6]}</div>
                <div style="font-size:18px;font-weight:bold;color:{color};">{val or '-'}/5</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Moyenne
    with cols[6]:
        st.markdown(f"""
        <div class="metric-card" style="background:#065f46;border-color:#10b981;">
            <div style="font-size:10px;color:#6ee7b7;">⚡ Moy</div>
            <div style="font-size:18px;font-weight:bold;color:#10b981;">{f"{avg:.1f}" if avg else "-"}/5</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Graphiques radar et poids
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Radar vs")
        compare_type = st.selectbox("Comparer avec", ["Équipe", "Avants", "Trois-quarts", get_player_line(player['position']), player['position']], key="modal_compare")
        
        # Calculer comparaison
        if compare_type == "Équipe":
            compare_avg = team_avg
        elif compare_type == "Avants":
            compare_avg = get_team_avg(sel_date, group="Avants")
        elif compare_type == "Trois-quarts":
            compare_avg = get_team_avg(sel_date, group="Trois-quarts")
        elif compare_type == player['position']:
            compare_avg = get_team_avg(sel_date)  # Simplification
        else:
            compare_avg = get_team_avg(sel_date, line=compare_type)
        
        player_data = {m['key']: pd.get(m['key'], 0) for m in METRICS}
        fig = radar_chart(player_data, compare_avg, player['name'], compare_type)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### ⚖️ Tunnel poids (±2kg)")
        weight_fig = weight_chart(player['name'])
        if weight_fig:
            st.plotly_chart(weight_fig, use_container_width=True)
        else:
            st.info("Pas de données de poids")
    
    # Z-Score individuel
    st.markdown("#### 📈 Z-Score (évolution fatigue)")
    zscore_fig = player_zscore_bars(player['name'])
    if zscore_fig:
        st.plotly_chart(zscore_fig, use_container_width=True)
        st.caption("🟢 Normal | 🟡 Attention (< -1) | 🔴 Alerte (< -1.5)")
    else:
        st.info("Pas assez de données pour le Z-Score")
    
    st.divider()
    
    # Calendrier wellness du joueur
    st.markdown("#### 📅 Calendrier Wellness")
    history = get_player_history(player['name'], 60)
    
    # Créer calendrier du mois en cours
    if history:
        today = datetime.now()
        cal = calendar.Calendar()
        month_days = list(cal.itermonthdays(today.year, today.month))
        
        # Créer un dict date -> avg
        avg_by_date = {h['date']: h.get('avg') for h in history}
        
        # Afficher le calendrier
        cols = st.columns(7)
        day_names = ['L', 'M', 'M', 'J', 'V', 'S', 'D']
        for i, name in enumerate(day_names):
            with cols[i]:
                st.markdown(f"<div style='text-align:center;color:#9ca3af;font-size:12px;'>{name}</div>", unsafe_allow_html=True)
        
        week_cols = st.columns(7)
        day_idx = 0
        for day in month_days:
            if day == 0:
                with week_cols[day_idx % 7]:
                    st.write("")
            else:
                date_str = f"{today.year}-{today.month:02d}-{day:02d}"
                avg_val = avg_by_date.get(date_str)
                
                if avg_val is not None:
                    if avg_val >= 4:
                        bg = "#10b981"
                    elif avg_val >= 3:
                        bg = "#f59e0b"
                    else:
                        bg = "#ef4444"
                    text = f"{avg_val:.1f}"
                else:
                    bg = "#374151"
                    text = ""
                
                with week_cols[day_idx % 7]:
                    st.markdown(f"""
                    <div style="background:{bg};border-radius:6px;padding:4px;text-align:center;margin:2px;">
                        <div style="font-size:11px;color:white;font-weight:bold;">{day}</div>
                        <div style="font-size:9px;color:rgba(255,255,255,0.8);">{text}</div>
                    </div>
                    """, unsafe_allow_html=True)
            day_idx += 1
            if day_idx % 7 == 0:
                week_cols = st.columns(7)
        
        st.caption("🟢 ≥4 | 🟠 3-4 | 🔴 <3 | ⬜ Pas de données")
    
    # Remarque du jour
    if pd.get('remark'):
        st.markdown("#### 💬 Remarque du jour")
        st.info(pd['remark'])
    
    st.divider()
    
    # Modifier le statut
    st.markdown("#### 🔄 Modifier le statut")
    new_status = st.radio("Statut", STATUSES, index=STATUSES.index(player['status']), horizontal=True, key="modal_status")
    
    if new_status != player['status']:
        if st.button("💾 Sauvegarder le statut", type="primary"):
            for p in st.session_state.players:
                if p['id'] == player_id:
                    p['status'] = new_status
            st.success(f"Statut mis à jour: {new_status}")
            st.rerun()


# ==================== PAGES ====================
def page_dashboard():
    st.title("📊 Dashboard Wellness")
    
    dates = sorted(st.session_state.data.keys(), reverse=True)
    if not dates:
        st.warning("⚠️ Aucune donnée. Allez sur **📥 Import** pour charger vos données depuis Google Sheets.")
        st.info("💡 **Astuce**: Importez votre Google Sheet pour commencer le suivi de vos joueurs !")
        return
    
    # Sélecteur de date
    date_key = st.selectbox("📅 Date", dates, format_func=lambda x: format_date(x, 'full'))
    today_data = st.session_state.data.get(date_key, [])
    team = get_team_avg(date_key)
    
    # ===== MOYENNE ÉQUIPE =====
    if team:
        def format_metric(m):
            val = team.get(m["key"])
            val_str = f"{val:.1f}" if val is not None else "-"
            return f'<div style="text-align:center;min-width:60px;"><div style="font-size:24px;">{m["icon"]}</div><div style="font-size:20px;font-weight:bold;color:white;">{val_str}</div><div style="font-size:10px;color:#9ca3af;">{m["label"]}</div></div>'
        
        metrics_html = ''.join([format_metric(m) for m in METRICS])
        global_val = team.get('global')
        global_str = f"{global_val:.2f}" if global_val is not None else "-"
        count_val = team.get('count', 0)
        
        st.markdown(f"""
        <div class="team-avg-card">
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem;">
                <div>
                    <div style="color:#6ee7b7;font-size:14px;font-weight:500;">⚡ MOYENNE ÉQUIPE ({count_val} joueurs)</div>
                    <div style="font-size:48px;font-weight:bold;color:white;">{global_str}<span style="font-size:24px;color:#9ca3af;">/5</span></div>
                </div>
                <div style="display:flex;gap:24px;flex-wrap:wrap;">{metrics_html}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # ===== ALERTES + DISPONIBILITÉ =====
    col_alerts, col_avail = st.columns([2, 1])
    
    with col_alerts:
        alerts = get_alerts(date_key)
        st.markdown(f"### ⚠️ Alertes du jour")
        if alerts:
            st.markdown(f'<span style="background:#ef4444;color:white;padding:4px 10px;border-radius:20px;font-size:12px;margin-left:8px;">{len(alerts)}</span>', unsafe_allow_html=True)
            
            # Grouper par joueur
            by_player = {}
            for a in alerts:
                by_player.setdefault(a['player'], []).append(a)
            
            for player_name, player_alerts in list(by_player.items())[:6]:
                msgs = " • ".join([a['message'] for a in player_alerts])
                has_critical = any(a['type'] == 'critical' for a in player_alerts)
                color = "#ef4444" if has_critical else "#f59e0b"
                badge = "🔴 Critique" if has_critical else "🟠 Attention"
                
                st.markdown(f"""
                <div style="background:{color}15;border:1px solid {color};padding:10px;border-radius:8px;margin-bottom:6px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span style="font-weight:600;color:white;">{player_name}</span>
                        <span style="font-size:10px;background:{color}30;color:{color};padding:2px 8px;border-radius:10px;">{badge}</span>
                    </div>
                    <div style="color:{color};font-size:12px;margin-top:4px;">{msgs}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ Aucune alerte")
    
    with col_avail:
        st.markdown("### 👥 Disponibilité")
        avail_data = get_availability_data()
        if avail_data:
            fig = availability_pie_chart()
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            # Légende
            legend_html = " ".join([f'<span style="margin-right:12px;"><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:{d["color"]};margin-right:4px;"></span>{d["name"]}: {d["value"]}</span>' for d in avail_data])
            st.markdown(f'<div style="text-align:center;font-size:11px;color:#9ca3af;">{legend_html}</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # ===== FILTRES ET TABLEAU =====
    st.subheader("📋 Vue équipe")
    
    c1, c2, c3, c4 = st.columns([1.5, 1.5, 1.5, 1])
    with c1:
        sort_by = st.selectbox("Trier", ["Nom A→Z", "🚨 Alertes", "📉 Moyenne ↑", "👥 Groupe"], key="sort")
    with c2:
        filter_group = st.selectbox("Groupe", ["Tous", "Avants", "Trois-quarts"], key="fg")
    with c3:
        filter_line = st.selectbox("Ligne", ["Toutes"] + ALL_LINES, key="fl")
    with c4:
        show_issues = st.checkbox("⚠️ Problèmes", key="si")
    
    # Construire les données du tableau
    rows = []
    player_ids = {}  # Pour mapper nom -> id
    
    for d in today_data:
        p = next((p for p in st.session_state.players if p['name'] == d['name']), None)
        if not p:
            continue
        if filter_group != "Tous" and get_player_group(p['position']) != filter_group:
            continue
        if filter_line != "Toutes" and get_player_line(p['position']) != filter_line:
            continue
        
        avg = get_player_average(d)
        has_issue = any(d.get(m['key']) is not None and d.get(m['key']) <= 2 for m in METRICS)
        
        if show_issues and not has_issue:
            continue
        
        diff_vs_team = (avg - team['global']) if avg and team and team.get('global') else None
        
        player_ids[d['name']] = p['id']
        group_abbr = "Av" if get_player_group(p['position']) == "Avants" else "3/4"
        
        rows.append({
            'Joueur': d['name'],
            'Poste': f"{p['position']} ({group_abbr})",
            'Statut': p['status'],
            '⚖️': round(d.get('weight'), 1) if d.get('weight') else None,
            '😴': d.get('sleep'),
            '🧠': d.get('mentalLoad'),
            '💪': d.get('motivation'),
            '❤️': d.get('hdcState'),
            '💚': d.get('bdcState'),
            'Moy': round(avg, 2) if avg else None,
            'vs Éq.': f"{'+' if diff_vs_team and diff_vs_team > 0 else ''}{diff_vs_team:.1f}" if diff_vs_team else '-',
            'Note': (d.get('remark', '') or '')[:25],
            '_has_issue': has_issue,
            '_avg': avg or 5
        })
    
    # Trier
    if sort_by == "🚨 Alertes":
        rows.sort(key=lambda x: (not x['_has_issue'], x['Joueur']))
    elif sort_by == "📉 Moyenne ↑":
        rows.sort(key=lambda x: x['_avg'])
    elif sort_by == "👥 Groupe":
        rows.sort(key=lambda x: x['Poste'])
    else:
        rows.sort(key=lambda x: x['Joueur'])
    
    # Afficher le tableau avec boutons cliquables
    if rows:
        st.markdown(f"**{len(rows)} joueurs**")
        
        # Header
        h_cols = st.columns([2, 2, 1, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.7, 0.7, 1.5])
        headers = ['Joueur', 'Poste', 'Statut', '⚖️', '😴', '🧠', '💪', '❤️', '💚', 'Moy', 'vs Éq.', 'Note']
        for i, h in enumerate(headers):
            with h_cols[i]:
                st.markdown(f"<div style='font-size:11px;color:#9ca3af;font-weight:500;'>{h}</div>", unsafe_allow_html=True)
        
        st.markdown("<div style='border-top:1px solid #374151;margin:4px 0;'></div>", unsafe_allow_html=True)
        
        # Rows
        for row in rows:
            r_cols = st.columns([2, 2, 1, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.7, 0.7, 1.5])
            
            # Joueur (clickable)
            with r_cols[0]:
                if st.button(row['Joueur'], key=f"btn_{row['Joueur']}", use_container_width=True):
                    show_player_modal(player_ids[row['Joueur']])
            
            # Poste
            with r_cols[1]:
                st.markdown(f"<div style='font-size:12px;color:#9ca3af;padding-top:8px;'>{row['Poste']}</div>", unsafe_allow_html=True)
            
            # Statut
            with r_cols[2]:
                status_colors = {'Apte': '#10b981', 'Blessé': '#ef4444', 'Réhabilitation': '#f59e0b', 'Réathlétisation': '#3b82f6'}
                st.markdown(f"<div style='font-size:10px;background:{status_colors.get(row['Statut'], '#6b7280')}30;color:{status_colors.get(row['Statut'], '#6b7280')};padding:4px 6px;border-radius:4px;text-align:center;margin-top:4px;'>{row['Statut'][:4]}</div>", unsafe_allow_html=True)
            
            # Poids
            with r_cols[3]:
                st.markdown(f"<div style='font-size:12px;color:#d1d5db;padding-top:8px;text-align:center;'>{row['⚖️'] or '-'}</div>", unsafe_allow_html=True)
            
            # Métriques avec couleurs
            metric_cols = ['😴', '🧠', '💪', '❤️', '💚']
            for i, m in enumerate(metric_cols):
                val = row[m]
                with r_cols[4 + i]:
                    if val is not None:
                        bg = '#ef4444' if val <= 2 else '#f59e0b' if val <= 3 else '#10b981'
                        st.markdown(f"<div style='background:{bg};color:white;font-size:13px;font-weight:bold;padding:4px;border-radius:4px;text-align:center;margin-top:4px;'>{val}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div style='color:#6b7280;text-align:center;padding-top:8px;'>-</div>", unsafe_allow_html=True)
            
            # Moyenne
            with r_cols[9]:
                moy = row['Moy']
                if moy:
                    bg = '#ef4444' if moy <= 2 else '#f59e0b' if moy <= 3 else '#10b981'
                    st.markdown(f"<div style='background:{bg};color:white;font-size:12px;font-weight:bold;padding:4px;border-radius:4px;text-align:center;margin-top:4px;'>{moy}</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div style='color:#6b7280;text-align:center;padding-top:8px;'>-</div>", unsafe_allow_html=True)
            
            # vs Éq.
            with r_cols[10]:
                vs_eq = row['vs Éq.']
                if vs_eq != '-':
                    color = '#10b981' if vs_eq.startswith('+') else '#ef4444'
                    st.markdown(f"<div style='font-size:11px;color:{color};font-weight:bold;padding-top:8px;text-align:center;'>{vs_eq}</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div style='color:#6b7280;text-align:center;padding-top:8px;'>-</div>", unsafe_allow_html=True)
            
            # Note
            with r_cols[11]:
                st.markdown(f"<div style='font-size:11px;color:#9ca3af;padding-top:8px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;'>{row['Note'] or ''}</div>", unsafe_allow_html=True)
    else:
        st.info("Aucun joueur ne correspond aux filtres.")
    
    # ===== GRAPHIQUES =====
    st.divider()
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("📈 Courbe Z-Score")
        mc1, mc2, mc3 = st.columns(3)
        with mc1:
            zmetric = st.selectbox(
                "Métrique", ['global'] + [m['key'] for m in METRICS],
                format_func=lambda x: "⚡ Global" if x == 'global' else next((f"{m['icon']} {m['label']}" for m in METRICS if m['key'] == x), x),
                key="zm"
            )
        with mc2:
            zgroup = st.selectbox("Groupe", ["Équipe", "Avants", "Trois-quarts"], key="zg")
        with mc3:
            zdays = st.selectbox("Période", [7, 14, 30, 60], index=2, key="zd")
        
        zdata = zscore_series(metric=zmetric, group=None if zgroup == "Équipe" else zgroup, days=zdays)
        fig = zscore_chart(zdata)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
            st.caption("🟢 Normal | 🟡 Attention (< -1) | 🔴 Alerte (< -1.5)")
        else:
            st.info("Pas assez de données pour le Z-Score (min 5 jours)")
    
    with c2:
        st.subheader("📊 Radar Comparaison")
        rc1, rc2 = st.columns(2)
        with rc1:
            cmp1 = st.selectbox("Comparer", ["Équipe", "Avants", "Trois-quarts"], key="r1")
        with rc2:
            cmp2 = st.selectbox("Avec", ["Équipe", "Avants", "Trois-quarts"], index=1, key="r2")
        
        d1 = get_group_avg(date_key, group=None if cmp1 == "Équipe" else cmp1)
        d2 = get_group_avg(date_key, group=None if cmp2 == "Équipe" else cmp2)
        
        if d1 or d2:
            st.plotly_chart(radar_chart(d1, d2, cmp1, cmp2), use_container_width=True)
            if d1 and d2:
                d1_global = d1.get('global')
                d2_global = d2.get('global')
                d1_str = f"{d1_global:.2f}" if d1_global else "-"
                d2_str = f"{d2_global:.2f}" if d2_global else "-"
                st.caption(f"🟢 {cmp1}: {d1_str}/5 | 🔵 {cmp2}: {d2_str}/5")


def page_import():
    st.title("📥 Import / Export")
    
    # ===== GOOGLE SHEETS =====
    st.subheader("📊 Importer depuis Google Sheets")
    
    url = st.text_input(
        "URL du Google Sheet",
        value="https://docs.google.com/spreadsheets/d/1Esm3NnED51jFpTs-oSjIdVybH51BSEcjhWOQhP1P3zI/edit?usp=sharing",
        help="Collez l'URL complète de votre Google Sheet"
    )
    
    sheet_name = st.text_input("Nom de l'onglet", value="Bien-être", help="Nom exact de l'onglet contenant les données")
    
    if st.button("📥 Importer depuis Google Sheets", type="primary"):
        try:
            # Extraire l'ID du document
            match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
            if not match:
                st.error("❌ URL invalide. Assurez-vous que c'est une URL Google Sheets.")
                return
            
            doc_id = match.group(1)
            encoded_sheet = urllib.parse.quote(sheet_name)
            csv_url = f"https://docs.google.com/spreadsheets/d/{doc_id}/gviz/tq?tqx=out:csv&sheet={encoded_sheet}"
            
            with st.spinner("Téléchargement..."):
                df = pd.read_csv(csv_url, header=None)
            
            st.success(f"✅ {len(df)} lignes téléchargées")
            
            # Traitement
            with st.spinner("Traitement des données..."):
                result = process_imported_data(df)
            
            if result['success']:
                st.success(f"✅ Import réussi ! {result['dates']} jours, {result['players']} joueurs, {result['entries']} entrées")
                st.balloons()
            else:
                st.error(f"❌ Erreur: {result['error']}")
                
        except Exception as e:
            st.error(f"❌ Erreur: {str(e)}")
    
    st.divider()
    
    # ===== EXCEL =====
    st.subheader("📄 Importer un fichier Excel")
    
    uploaded = st.file_uploader("Choisir un fichier", type=['xlsx', 'xls'])
    if uploaded:
        try:
            df = pd.read_excel(uploaded, header=None)
            st.info(f"📊 {len(df)} lignes trouvées")
            
            if st.button("📥 Traiter le fichier Excel"):
                with st.spinner("Traitement..."):
                    result = process_imported_data(df)
                
                if result['success']:
                    st.success(f"✅ Import réussi ! {result['dates']} jours, {result['players']} joueurs")
                else:
                    st.error(f"❌ {result['error']}")
        except Exception as e:
            st.error(f"❌ Erreur lecture: {e}")
    
    st.divider()
    
    # ===== EXPORT =====
    st.subheader("📤 Exporter les données")
    
    if st.session_state.data:
        # Créer DataFrame d'export
        export_rows = []
        for date, entries in st.session_state.data.items():
            for e in entries:
                export_rows.append({
                    'Date': date,
                    'Joueur': e.get('name'),
                    'Poids': e.get('weight'),
                    'Sommeil': e.get('sleep'),
                    'Charge Mentale': e.get('mentalLoad'),
                    'Motivation': e.get('motivation'),
                    'HDC': e.get('hdcState'),
                    'BDC': e.get('bdcState'),
                    'Remarque': e.get('remark')
                })
        
        if export_rows:
            export_df = pd.DataFrame(export_rows)
            csv = export_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Télécharger CSV", csv, "wellness_export.csv", "text/csv")
            
            st.markdown(f"**Statistiques:** {len(st.session_state.data)} jours • {len(st.session_state.players)} joueurs • {len(export_rows)} entrées")
    else:
        st.info("Aucune donnée à exporter")


def process_imported_data(df):
    """Traite les données importées (Google Sheets ou Excel)"""
    try:
        # Chercher la date dans les premières lignes
        date_found = None
        header_row = None
        
        for i in range(min(10, len(df))):
            row = df.iloc[i]
            row_str = ' '.join([str(x) for x in row if pd.notna(x)])
            
            # Chercher date française
            date_match = re.search(r'(\d{1,2})\s+(janvier|février|fevrier|mars|avril|mai|juin|juillet|août|aout|septembre|octobre|novembre|décembre|decembre)\s+(\d{4})', row_str.lower())
            if date_match:
                day = int(date_match.group(1))
                month = FRENCH_MONTHS.get(date_match.group(2), 1)
                year = int(date_match.group(3))
                date_found = f"{year}-{month:02d}-{day:02d}"
            
            # Chercher la ligne d'en-tête
            if any('joueur' in str(x).lower() for x in row if pd.notna(x)):
                if any('poids' in str(x).lower() for x in row if pd.notna(x)):
                    header_row = i
                    break
        
        if not date_found:
            date_found = datetime.now().strftime('%Y-%m-%d')
        
        if header_row is None:
            return {'success': False, 'error': "Impossible de trouver la ligne d'en-tête (cherche 'Joueur' et 'Poids')"}
        
        # Mapper les colonnes
        headers = df.iloc[header_row]
        col_map = {}
        
        for idx, h in enumerate(headers):
            if pd.isna(h):
                continue
            h_lower = str(h).lower().strip()
            
            if 'joueur' in h_lower or 'nom' in h_lower:
                col_map['name'] = idx
            elif 'poids' in h_lower:
                col_map['weight'] = idx
            elif 'sommeil' in h_lower:
                col_map['sleep'] = idx
            elif 'charge' in h_lower or 'mental' in h_lower:
                col_map['mentalLoad'] = idx
            elif 'motivation' in h_lower:
                col_map['motivation'] = idx
            elif 'hdc' in h_lower or 'haut' in h_lower:
                col_map['hdcState'] = idx
            elif 'bdc' in h_lower or 'bas' in h_lower:
                col_map['bdcState'] = idx
            elif 'remarque' in h_lower or 'note' in h_lower or 'commentaire' in h_lower:
                col_map['remark'] = idx
        
        if 'name' not in col_map:
            return {'success': False, 'error': "Colonne 'Joueur' non trouvée"}
        
        # Extraire les données
        data_rows = df.iloc[header_row + 1:]
        entries = []
        players_created = 0
        
        for _, row in data_rows.iterrows():
            name = row.iloc[col_map['name']] if col_map.get('name') is not None else None
            if pd.isna(name) or not str(name).strip():
                continue
            
            name = str(name).strip()
            
            # Créer joueur si n'existe pas
            if not any(p['name'] == name for p in st.session_state.players):
                st.session_state.players.append({
                    'id': f"p_{len(st.session_state.players) + 1}",
                    'name': name,
                    'position': 'Pilier gauche',
                    'status': 'Apte',
                    'targetWeight': 95
                })
                players_created += 1
            
            entry = {'name': name}
            
            # Extraire valeurs numériques
            for key, idx in col_map.items():
                if key == 'name' or idx is None:
                    continue
                val = row.iloc[idx] if idx < len(row) else None
                
                if key == 'remark':
                    entry[key] = str(val) if pd.notna(val) else ''
                else:
                    if pd.notna(val):
                        try:
                            num = float(str(val).replace(',', '.'))
                            entry[key] = num
                        except:
                            pass
            
            entries.append(entry)
        
        # Sauvegarder
        if entries:
            st.session_state.data[date_found] = entries
        
        return {
            'success': True,
            'dates': 1,
            'players': len(st.session_state.players),
            'entries': len(entries),
            'new_players': players_created
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}


def page_effectif():
    st.title("👥 Effectif & Comparaisons")
    
    if not st.session_state.players:
        st.warning("Aucun joueur. Importez des données d'abord.")
        return
    
    tabs = st.tabs(["📋 Liste", "📊 Comparer", "📈 Période", "👥 Groupes"])
    
    with tabs[0]:
        # Liste des joueurs
        search = st.text_input("🔍 Rechercher", key="search_eff")
        
        players = st.session_state.players
        if search:
            players = [p for p in players if search.lower() in p['name'].lower()]
        
        dates = sorted(st.session_state.data.keys(), reverse=True)
        latest_date = dates[0] if dates else None
        
        for p in sorted(players, key=lambda x: x['name']):
            # Données du jour
            pd_data = {}
            if latest_date:
                today_data = st.session_state.data.get(latest_date, [])
                pd_data = next((d for d in today_data if d['name'] == p['name']), {})
            
            avg = get_player_average(pd_data)
            status_colors = {'Apte': '#10b981', 'Blessé': '#ef4444', 'Réhabilitation': '#f59e0b', 'Réathlétisation': '#3b82f6'}
            
            # Métriques en badges colorés
            metrics_html = ""
            for m in METRICS:
                val = pd_data.get(m['key'])
                if val is not None:
                    bg = '#ef4444' if val <= 2 else '#f59e0b' if val <= 3 else '#10b981'
                    metrics_html += f'<span class="metric-badge" style="background:{bg};">{int(val)}</span>'
                else:
                    metrics_html += '<span class="metric-badge" style="background:#374151;">-</span>'
            
            col1, col2, col3, col4 = st.columns([3, 2, 3, 1])
            
            with col1:
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:10px;">
                    <div style="width:40px;height:40px;border-radius:10px;background:linear-gradient(135deg,#10b981,#059669);display:flex;align-items:center;justify-content:center;font-weight:bold;color:white;">{p['name'][0]}</div>
                    <div>
                        <div style="font-weight:600;color:white;">{p['name']}</div>
                        <div style="font-size:12px;color:#9ca3af;">{p['position']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f'<span style="background:{status_colors.get(p["status"], "#6b7280")}30;color:{status_colors.get(p["status"], "#6b7280")};padding:4px 12px;border-radius:20px;font-size:12px;">{p["status"]}</span>', unsafe_allow_html=True)
            
            with col3:
                st.markdown(f'<div style="padding-top:8px;">{metrics_html}</div>', unsafe_allow_html=True)
            
            with col4:
                if st.button("👁️", key=f"view_{p['id']}"):
                    show_player_modal(p['id'])
            
            st.markdown("<div style='border-bottom:1px solid #374151;margin:8px 0;'></div>", unsafe_allow_html=True)
    
    with tabs[1]:
        # Comparaison radar
        st.subheader("📊 Comparer joueurs")
        
        player_names = [p['name'] for p in st.session_state.players]
        
        col1, col2 = st.columns(2)
        with col1:
            sel1 = st.multiselect("Sélectionner joueurs (2-4)", player_names, max_selections=4, key="cmp1")
        with col2:
            dates = sorted(st.session_state.data.keys(), reverse=True)
            if dates:
                cmp_date = st.selectbox("Date", dates[:30], format_func=lambda x: format_date(x, 'short'), key="cmp_date")
        
        if len(sel1) >= 2 and dates:
            today_data = st.session_state.data.get(cmp_date, [])
            
            fig = go.Figure()
            colors = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444']
            
            for i, name in enumerate(sel1):
                pd_data = next((d for d in today_data if d['name'] == name), {})
                vals = [pd_data.get(m['key'], 0) or 0 for m in METRICS]
                vals.append(vals[0])
                
                categories = [m['label'] for m in METRICS]
                categories.append(categories[0])
                
                fig.add_trace(go.Scatterpolar(
                    r=vals,
                    theta=categories,
                    fill='toself',
                    name=name,
                    line=dict(color=colors[i % len(colors)]),
                    fillcolor=f'rgba{tuple(int(colors[i % len(colors)].lstrip("#")[j:j+2], 16) for j in (0, 2, 4)) + (0.2,)}'
                ))
            
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#9ca3af'),
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with tabs[2]:
        # Évolution sur période
        st.subheader("📈 Évolution période")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            player_names = [p['name'] for p in st.session_state.players]
            sel_player = st.selectbox("Joueur", player_names, key="period_player")
        with col2:
            period = st.selectbox("Période", [7, 14, 30, 60], index=2, key="period_days")
        with col3:
            sel_metric = st.selectbox(
                "Métrique",
                ['global'] + [m['key'] for m in METRICS],
                format_func=lambda x: "⚡ Global" if x == 'global' else next((f"{m['icon']} {m['label']}" for m in METRICS if m['key'] == x), x),
                key="period_metric"
            )
        
        if sel_player:
            history = get_player_history(sel_player, period)
            if history:
                chart_data = []
                for h in history:
                    val = h['avg'] if sel_metric == 'global' else h.get(sel_metric)
                    if val is not None:
                        chart_data.append({'date': format_date(h['date']), 'value': val})
                
                if chart_data:
                    df = pd.DataFrame(chart_data)
                    fig = px.line(df, x='date', y='value', markers=True)
                    fig.update_traces(line_color='#10b981')
                    fig.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(31,41,55,1)',
                        font=dict(color='#9ca3af'),
                        height=300
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Pas de données pour cette période")
    
    with tabs[3]:
        # Vue par groupes
        st.subheader("👥 Vue par groupes")
        
        dates = sorted(st.session_state.data.keys(), reverse=True)
        if not dates:
            st.info("Aucune donnée")
            return
        
        grp_date = st.selectbox("Date", dates[:30], format_func=lambda x: format_date(x, 'short'), key="grp_date")
        
        for group_name in ['Avants', 'Trois-quarts']:
            grp_avg = get_team_avg(grp_date, group=group_name)
            if grp_avg:
                global_val = grp_avg.get('global')
                global_str = f"{global_val:.2f}" if global_val else "-"
                st.markdown(f"### {group_name} - Moy: {global_str}/5")
                
                for line_name in RUGBY_POSITIONS[group_name].keys():
                    line_avg = get_team_avg(grp_date, line=line_name)
                    if line_avg:
                        line_global = line_avg.get('global')
                        line_str = f"{line_global:.2f}" if line_global else "-"
                        st.markdown(f"**{line_name}**: {line_str}/5 ({line_avg.get('count', 0)} joueurs)")


def page_infirmerie():
    st.title("🏥 Infirmerie")
    
    # Compteurs de statut
    status_counts = {}
    for p in st.session_state.players:
        s = p.get('status', 'Apte')
        status_counts[s] = status_counts.get(s, 0) + 1
    
    cols = st.columns(4)
    status_colors = {'Apte': '#10b981', 'Blessé': '#ef4444', 'Réhabilitation': '#f59e0b', 'Réathlétisation': '#3b82f6'}
    
    for i, status in enumerate(STATUSES):
        count = status_counts.get(status, 0)
        with cols[i]:
            if st.button(f"{status}\n{count}", key=f"filter_{status}", use_container_width=True):
                st.session_state.status_filter = status if st.session_state.status_filter != status else None
    
    st.divider()
    
    # Joueurs filtrés
    current_filter = st.session_state.status_filter
    filtered_players = [p for p in st.session_state.players if not current_filter or p.get('status') == current_filter]
    
    if current_filter:
        st.info(f"Filtré par: **{current_filter}** ({len(filtered_players)} joueurs)")
    
    # Liste des joueurs
    for p in filtered_players:
        col1, col2, col3 = st.columns([3, 2, 2])
        
        with col1:
            st.markdown(f"**{p['name']}** - {p['position']}")
        
        with col2:
            new_status = st.selectbox(
                "Statut",
                STATUSES,
                index=STATUSES.index(p.get('status', 'Apte')),
                key=f"status_{p['id']}",
                label_visibility="collapsed"
            )
            if new_status != p.get('status'):
                for player in st.session_state.players:
                    if player['id'] == p['id']:
                        player['status'] = new_status
                st.rerun()
        
        with col3:
            if p.get('status') != 'Apte':
                if st.button("➕ Déclarer blessure", key=f"inj_{p['id']}"):
                    st.session_state[f'show_injury_form_{p["id"]}'] = True
        
        # Formulaire de blessure
        if st.session_state.get(f'show_injury_form_{p["id"]}'):
            with st.form(f'injury_form_{p["id"]}'):
                st.markdown(f"**Nouvelle blessure pour {p['name']}**")
                
                ic1, ic2 = st.columns(2)
                with ic1:
                    zone = st.selectbox("Zone", list(INJURY_ZONES.keys()), key=f"iz_{p['id']}")
                with ic2:
                    grade = st.selectbox("Grade", [1, 2, 3], key=f"ig_{p['id']}")
                
                circ = st.selectbox("Circonstance", CIRCUMSTANCES, key=f"ic_{p['id']}")
                
                # Estimation durée
                duration = INJURY_ZONES[zone].get(grade, 14)
                return_date = (datetime.now() + timedelta(days=duration)).strftime('%Y-%m-%d')
                st.info(f"⏱️ Durée estimée: {duration} jours (retour: {format_date(return_date)})")
                
                if st.form_submit_button("💾 Enregistrer"):
                    st.session_state.injuries.append({
                        'id': f"i_{len(st.session_state.injuries) + 1}",
                        'playerId': p['id'],
                        'playerName': p['name'],
                        'zone': zone,
                        'grade': grade,
                        'circumstance': circ,
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'returnDate': return_date,
                        'status': 'Active'
                    })
                    st.session_state[f'show_injury_form_{p["id"]}'] = False
                    st.success("Blessure enregistrée")
                    st.rerun()
        
        st.markdown("---")
    
    # Liste des blessures actives
    st.subheader("🩹 Blessures actives")
    
    active_injuries = [i for i in st.session_state.injuries if i.get('status') == 'Active']
    
    if active_injuries:
        for inj in active_injuries:
            days_remaining = (datetime.strptime(inj['returnDate'], '%Y-%m-%d') - datetime.now()).days
            days_total = INJURY_ZONES[inj['zone']].get(inj['grade'], 14)
            progress = max(0, min(100, ((days_total - days_remaining) / days_total) * 100))
            
            col1, col2, col3 = st.columns([3, 4, 2])
            
            with col1:
                icon = INJURY_ZONES[inj['zone']]['icon']
                st.markdown(f"**{inj['playerName']}**\n{icon} {inj['zone']} (Grade {inj['grade']})")
            
            with col2:
                st.progress(progress / 100)
                st.caption(f"{days_remaining} jours restants" if days_remaining > 0 else "Retour prévu dépassé")
            
            with col3:
                if st.button("✅ Guéri", key=f"heal_{inj['id']}"):
                    for injury in st.session_state.injuries:
                        if injury['id'] == inj['id']:
                            injury['status'] = 'Healed'
                    st.rerun()
    else:
        st.success("✅ Aucune blessure active")


def page_joueurs():
    st.title("👤 Gestion des joueurs")
    
    # Ajouter un joueur
    st.subheader("➕ Ajouter un joueur")
    
    with st.form("add_player"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Nom")
            position = st.selectbox("Poste", ALL_POSITIONS)
        with col2:
            weight = st.number_input("Poids forme (kg)", value=90.0, step=0.5)
            status = st.selectbox("Statut", STATUSES)
        
        if st.form_submit_button("➕ Ajouter"):
            if name:
                st.session_state.players.append({
                    'id': f"p_{len(st.session_state.players) + 1}_{datetime.now().timestamp()}",
                    'name': name,
                    'position': position,
                    'targetWeight': weight,
                    'status': status
                })
                st.success(f"✅ {name} ajouté !")
                st.rerun()
            else:
                st.error("Nom requis")
    
    st.divider()
    
    # Liste des joueurs
    st.subheader("📋 Liste des joueurs")
    
    for p in sorted(st.session_state.players, key=lambda x: x['name']):
        col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 1])
        
        with col1:
            st.write(f"**{p['name']}**")
        
        with col2:
            new_pos = st.selectbox(
                "Poste",
                ALL_POSITIONS,
                index=ALL_POSITIONS.index(p['position']) if p['position'] in ALL_POSITIONS else 0,
                key=f"pos_{p['id']}",
                label_visibility="collapsed"
            )
            if new_pos != p['position']:
                for player in st.session_state.players:
                    if player['id'] == p['id']:
                        player['position'] = new_pos
        
        with col3:
            new_weight = st.number_input(
                "Poids",
                value=float(p.get('targetWeight', 90)),
                step=0.5,
                key=f"weight_{p['id']}",
                label_visibility="collapsed"
            )
            if new_weight != p.get('targetWeight'):
                for player in st.session_state.players:
                    if player['id'] == p['id']:
                        player['targetWeight'] = new_weight
        
        with col4:
            new_status = st.selectbox(
                "Statut",
                STATUSES,
                index=STATUSES.index(p.get('status', 'Apte')),
                key=f"st_{p['id']}",
                label_visibility="collapsed"
            )
            if new_status != p.get('status'):
                for player in st.session_state.players:
                    if player['id'] == p['id']:
                        player['status'] = new_status
        
        with col5:
            if st.button("🗑️", key=f"del_{p['id']}"):
                st.session_state.players = [x for x in st.session_state.players if x['id'] != p['id']]
                st.rerun()


def page_parametres():
    st.title("⚙️ Paramètres")
    
    # Seuils d'alerte
    st.subheader("🚨 Seuils d'alerte")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        low_val = st.number_input(
            "Seuil valeur basse",
            value=float(st.session_state.settings['lowValueThreshold']),
            min_value=1.0, max_value=5.0, step=0.5,
            help="Alerte si métrique ≤ ce seuil"
        )
        st.session_state.settings['lowValueThreshold'] = low_val
    
    with col2:
        var_val = st.number_input(
            "Seuil variation",
            value=float(st.session_state.settings['variationThreshold']),
            min_value=0.5, max_value=3.0, step=0.5,
            help="Alerte si variation jour/jour > ce seuil"
        )
        st.session_state.settings['variationThreshold'] = var_val
    
    with col3:
        weight_val = st.number_input(
            "Seuil poids (kg)",
            value=float(st.session_state.settings['weightThreshold']),
            min_value=1.0, max_value=5.0, step=0.5,
            help="Alerte si écart poids > ce seuil"
        )
        st.session_state.settings['weightThreshold'] = weight_val
    
    st.divider()
    
    # Z-Score
    st.subheader("📈 Configuration Z-Score")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        zdays = st.number_input(
            "Jours pour calcul",
            value=int(st.session_state.settings['zscoreDays']),
            min_value=7, max_value=60, step=1
        )
        st.session_state.settings['zscoreDays'] = zdays
    
    with col2:
        zwarn = st.number_input(
            "Seuil attention",
            value=float(st.session_state.settings['zscoreWarning']),
            min_value=-3.0, max_value=0.0, step=0.5
        )
        st.session_state.settings['zscoreWarning'] = zwarn
    
    with col3:
        zalert = st.number_input(
            "Seuil alerte",
            value=float(st.session_state.settings['zscoreAlert']),
            min_value=-3.0, max_value=0.0, step=0.5
        )
        st.session_state.settings['zscoreAlert'] = zalert
    
    st.divider()
    
    # Actions
    st.subheader("🔧 Actions")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Réinitialiser paramètres"):
            st.session_state.settings = DEFAULT_SETTINGS.copy()
            st.success("✅ Paramètres réinitialisés")
    
    with col2:
        if st.button("🗑️ Effacer toutes les données", type="primary"):
            st.session_state.data = {}
            st.session_state.players = []
            st.session_state.injuries = []
            st.success("✅ Données effacées")
            st.rerun()
    
    st.divider()
    
    # Aide
    st.subheader("❓ Aide")
    st.markdown("""
    **Alertes valeurs basses**: Si un joueur entre une valeur ≤ au seuil (ex: Sommeil = 2), une alerte critique est générée.
    
    **Z-Score**: Mesure l'écart par rapport à la moyenne habituelle. Un Z-Score négatif = valeur en dessous de la normale:
    - **> -1**: Normal (vert)
    - **-1 à -1.5**: Attention (jaune)  
    - **< -1.5**: Alerte (rouge)
    
    **Poids**: Alerte si le poids du jour s'écarte trop du poids forme défini pour le joueur.
    """)


# ==================== MAIN ====================
def main():
    # Sidebar
    with st.sidebar:
        st.markdown("## ⚡ Wellness Tracker")
        st.caption("Rugby Performance")
        
        st.divider()
        
        page = st.radio(
            "Navigation",
            ["📊 Dashboard", "📥 Import", "👥 Effectif", "🏥 Infirmerie", "👤 Joueurs", "⚙️ Paramètres"],
            label_visibility="collapsed"
        )
        
        # Alertes
        dates = sorted(st.session_state.data.keys(), reverse=True)
        if dates:
            alerts = get_alerts(dates[0])
            if alerts:
                st.error(f"🚨 {len(alerts)} alertes")
        
        st.divider()
        
        # Stats
        st.caption(f"📊 {len(dates)} jours de données")
        st.caption(f"👥 {len(st.session_state.players)} joueurs")
        st.caption(f"🏥 {len(st.session_state.injuries)} blessures")
        
        st.divider()
        st.caption("💾 Données en session")
    
    # Pages
    pages = {
        "📊 Dashboard": page_dashboard,
        "📥 Import": page_import,
        "👥 Effectif": page_effectif,
        "🏥 Infirmerie": page_infirmerie,
        "👤 Joueurs": page_joueurs,
        "⚙️ Paramètres": page_parametres
    }
    pages[page]()


if __name__ == "__main__":
    main()
