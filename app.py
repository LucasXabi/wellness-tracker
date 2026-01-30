"""
🏉 Rugby Wellness Tracker
Application de suivi du bien-être des joueurs de rugby
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import re
from config import (
    METRICS, RUGBY_POSITIONS, ALL_POSITIONS, ALL_LINES,
    INJURY_ZONES, CIRCUMSTANCES, STATUSES, FRENCH_MONTHS,
    DEFAULT_SETTINGS, get_player_group, get_player_line,
    get_player_average, calculate_zscore, parse_french_date,
    format_date, get_color_for_value, get_status_color,
    init_session_state
)

# ==================== CONFIGURATION PAGE ====================

st.set_page_config(
    page_title="Rugby Wellness Tracker",
    page_icon="🏉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .stApp {
        background-color: #111827;
    }
    .metric-card {
        background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
        padding: 1rem;
        border-radius: 0.75rem;
        border: 1px solid #374151;
    }
    .alert-card {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid #ef4444;
        padding: 0.75rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .player-card {
        background: #1f2937;
        padding: 1rem;
        border-radius: 0.75rem;
        border: 1px solid #374151;
        cursor: pointer;
        transition: all 0.2s;
    }
    .player-card:hover {
        border-color: #10b981;
        transform: translateY(-2px);
    }
    .heat-cell {
        display: inline-block;
        width: 24px;
        height: 24px;
        border-radius: 4px;
        text-align: center;
        line-height: 24px;
        font-size: 11px;
        font-weight: bold;
        color: white;
    }
    .status-badge {
        padding: 2px 8px;
        border-radius: 9999px;
        font-size: 11px;
        font-weight: 500;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1f2937;
        border-radius: 8px;
        padding: 8px 16px;
    }
</style>
""", unsafe_allow_html=True)

# ==================== INITIALISATION ====================

init_session_state()

# ==================== FONCTIONS D'IMPORT ====================

def import_from_google_sheets(sheet_url):
    """Importe les données depuis Google Sheets"""
    try:
        # Extraire l'ID du sheet
        match = re.search(r'/d/([a-zA-Z0-9-_]+)', sheet_url)
        if not match:
            return None, "URL invalide"
        
        sheet_id = match.group(1)
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Bien-être"
        
        # Charger les données brutes
        df_raw = pd.read_csv(csv_url, header=None)
        
        return process_imported_data(df_raw)
    
    except Exception as e:
        return None, f"Erreur: {str(e)}"

def import_from_excel(uploaded_file):
    """Importe les données depuis un fichier Excel"""
    try:
        # Chercher l'onglet Bien-être
        xl = pd.ExcelFile(uploaded_file)
        sheet_name = None
        for name in xl.sheet_names:
            if 'bien' in name.lower() or 'être' in name.lower() or 'etre' in name.lower():
                sheet_name = name
                break
        
        if not sheet_name:
            sheet_name = xl.sheet_names[0]
        
        df_raw = pd.read_excel(uploaded_file, sheet_name=sheet_name, header=None)
        
        return process_imported_data(df_raw)
    
    except Exception as e:
        return None, f"Erreur: {str(e)}"

def process_imported_data(df_raw):
    """Traite les données brutes importées"""
    try:
        # Chercher la date dans les premières lignes
        date_found = None
        for i in range(min(5, len(df_raw))):
            for val in df_raw.iloc[i]:
                if pd.notna(val):
                    parsed = parse_french_date(str(val))
                    if parsed:
                        date_found = parsed
                        break
            if date_found:
                break
        
        if not date_found:
            date_found = datetime.now().date()
        
        # Trouver la ligne d'en-tête (contient "Joueur" ou "Poids")
        header_row = None
        for i in range(min(10, len(df_raw))):
            row_str = ' '.join([str(v).lower() for v in df_raw.iloc[i] if pd.notna(v)])
            if 'joueur' in row_str or ('poids' in row_str and 'sommeil' in row_str):
                header_row = i
                break
        
        if header_row is None:
            header_row = 2
        
        # Colonnes par défaut basées sur le format connu
        # B=Joueur, C=Poids, D=Sommeil, E=Charge mentale, F=Motivation, G=HDC, H=BDC, I=Moyenne, J=Remarque
        col_indices = {
            'name': 1,
            'weight': 2,
            'sleep': 3,
            'mental_load': 4,
            'motivation': 5,
            'hdc': 6,
            'bdc': 7,
            'remark': 9
        }
        
        # Traiter les données
        data_rows = []
        new_players = []
        existing_names = {p['name'] for p in st.session_state.players}
        
        for i in range(header_row + 2, len(df_raw)):  # +2 pour passer EQUIPE
            row = df_raw.iloc[i]
            
            # Récupérer le nom
            name_val = row.iloc[col_indices['name']] if col_indices['name'] < len(row) else None
            if pd.isna(name_val) or str(name_val).upper().strip() in ['', 'EQUIPE', 'NAN']:
                continue
            
            name = str(name_val).upper().strip()
            
            def get_value(col_key):
                idx = col_indices.get(col_key)
                if idx is None or idx >= len(row):
                    return None
                val = row.iloc[idx]
                if pd.isna(val) or str(val).strip() in ['', '#DIV/0!', 'nan']:
                    return None
                try:
                    return float(val)
                except:
                    return None
            
            data_row = {
                'name': name,
                'date': date_found.isoformat(),
                'weight': get_value('weight'),
                'sleep': get_value('sleep'),
                'mental_load': get_value('mental_load'),
                'motivation': get_value('motivation'),
                'hdc': get_value('hdc'),
                'bdc': get_value('bdc'),
                'remark': str(row.iloc[col_indices['remark']]) if col_indices['remark'] < len(row) and pd.notna(row.iloc[col_indices['remark']]) else ''
            }
            
            data_rows.append(data_row)
            
            # Créer le joueur s'il n'existe pas
            if name not in existing_names:
                existing_names.add(name)
                new_players.append({
                    'id': f"{datetime.now().timestamp()}_{len(new_players)}",
                    'name': name,
                    'position': 'Pilier gauche',
                    'status': 'Apte',
                    'target_weight': data_row['weight'] or 90
                })
        
        # Ajouter les nouveaux joueurs
        st.session_state.players.extend(new_players)
        
        # Ajouter les données
        date_key = date_found.isoformat()
        st.session_state.wellness_data[date_key] = data_rows
        
        return {
            'date': date_found,
            'players_imported': len(data_rows),
            'new_players': len(new_players)
        }, None
    
    except Exception as e:
        return None, f"Erreur de traitement: {str(e)}"

# ==================== FONCTIONS DE CALCUL ====================

def get_team_averages(date_key):
    """Calcule les moyennes de l'équipe pour une date"""
    data = st.session_state.wellness_data.get(date_key, [])
    if not data:
        return None
    
    result = {'global': None}
    for m in METRICS:
        values = [d[m['key']] for d in data if d.get(m['key']) is not None]
        result[m['key']] = np.mean(values) if values else None
    
    all_avgs = [get_player_average(d) for d in data]
    all_avgs = [a for a in all_avgs if a is not None]
    result['global'] = np.mean(all_avgs) if all_avgs else None
    
    return result

def get_group_averages(date_key, group=None, line=None):
    """Calcule les moyennes pour un groupe/ligne"""
    data = st.session_state.wellness_data.get(date_key, [])
    if not data:
        return None
    
    # Filtrer par groupe/ligne
    filtered = []
    for d in data:
        player = next((p for p in st.session_state.players if p['name'] == d['name']), None)
        if not player:
            continue
        
        if group and get_player_group(player['position']) != group:
            continue
        if line and get_player_line(player['position']) != line:
            continue
        
        filtered.append(d)
    
    if not filtered:
        return None
    
    result = {'global': None, 'count': len(filtered)}
    for m in METRICS:
        values = [d[m['key']] for d in filtered if d.get(m['key']) is not None]
        result[m['key']] = np.mean(values) if values else None
    
    all_avgs = [get_player_average(d) for d in filtered]
    all_avgs = [a for a in all_avgs if a is not None]
    result['global'] = np.mean(all_avgs) if all_avgs else None
    
    return result

def get_alerts_for_date(date_key):
    """Génère les alertes pour une date"""
    data = st.session_state.wellness_data.get(date_key, [])
    settings = st.session_state.settings
    alerts = []
    
    for d in data:
        player = next((p for p in st.session_state.players if p['name'] == d['name']), None)
        if not player:
            continue
        
        # Alertes valeurs basses
        for m in METRICS:
            val = d.get(m['key'])
            if val is not None and val <= settings['low_value_threshold']:
                alerts.append({
                    'type': 'critical',
                    'player': d['name'],
                    'metric': m['label'],
                    'icon': m['icon'],
                    'value': val,
                    'message': f"{m['icon']} {m['label']} = {val}/5"
                })
        
        # Alerte poids
        if d.get('weight') and player.get('target_weight'):
            diff = abs(d['weight'] - player['target_weight'])
            if diff > settings['weight_threshold']:
                alerts.append({
                    'type': 'weight',
                    'player': d['name'],
                    'value': d['weight'],
                    'target': player['target_weight'],
                    'message': f"⚖️ Poids: {d['weight']:.1f}kg (cible: {player['target_weight']}kg)"
                })
    
    return alerts

def calculate_zscore_series(metric='global', group=None, line=None, player_id=None, days=30):
    """Calcule la série Z-Score pour une métrique"""
    dates = sorted(st.session_state.wellness_data.keys())
    if not dates:
        return []
    
    settings = st.session_state.settings
    zscore_days = settings['zscore_days']
    
    result = []
    for i, date in enumerate(dates[-days:]):
        data = st.session_state.wellness_data.get(date, [])
        
        # Filtrer les données
        filtered = []
        for d in data:
            player = next((p for p in st.session_state.players if p['name'] == d['name']), None)
            if not player:
                continue
            
            if group and get_player_group(player['position']) != group:
                continue
            if line and get_player_line(player['position']) != line:
                continue
            if player_id and player['id'] != player_id:
                continue
            
            filtered.append(d)
        
        if not filtered:
            result.append({'date': date, 'value': None, 'zscore': None})
            continue
        
        # Calculer la valeur du jour
        if metric == 'global':
            values = [get_player_average(d) for d in filtered]
            values = [v for v in values if v is not None]
            day_value = np.mean(values) if values else None
        else:
            values = [d.get(metric) for d in filtered if d.get(metric) is not None]
            day_value = np.mean(values) if values else None
        
        # Calculer l'historique pour le Z-Score
        idx = dates.index(date)
        history_dates = dates[max(0, idx - zscore_days):idx]
        history_values = []
        
        for h_date in history_dates:
            h_data = st.session_state.wellness_data.get(h_date, [])
            h_filtered = []
            for d in h_data:
                player = next((p for p in st.session_state.players if p['name'] == d['name']), None)
                if not player:
                    continue
                if group and get_player_group(player['position']) != group:
                    continue
                if line and get_player_line(player['position']) != line:
                    continue
                if player_id and player['id'] != player_id:
                    continue
                h_filtered.append(d)
            
            if h_filtered:
                if metric == 'global':
                    vals = [get_player_average(d) for d in h_filtered]
                    vals = [v for v in vals if v is not None]
                    if vals:
                        history_values.append(np.mean(vals))
                else:
                    vals = [d.get(metric) for d in h_filtered if d.get(metric) is not None]
                    if vals:
                        history_values.append(np.mean(vals))
        
        zscore = calculate_zscore(day_value, history_values) if day_value and len(history_values) >= 5 else None
        
        result.append({
            'date': date,
            'date_formatted': format_date(date),
            'value': round(day_value, 2) if day_value else None,
            'zscore': round(zscore, 2) if zscore else None
        })
    
    return result

# ==================== COMPOSANTS UI ====================

def render_metric_card(label, value, icon, delta=None):
    """Affiche une carte métrique"""
    color = get_color_for_value(value)
    delta_html = ""
    if delta is not None:
        delta_color = "#10b981" if delta >= 0 else "#ef4444"
        delta_sign = "+" if delta >= 0 else ""
        delta_html = f'<span style="color: {delta_color}; font-size: 12px;">{delta_sign}{delta:.1f}</span>'
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1f2937 0%, #374151 100%); 
                padding: 1rem; border-radius: 0.75rem; border: 1px solid #374151; text-align: center;">
        <div style="font-size: 24px;">{icon}</div>
        <div style="color: #9ca3af; font-size: 12px; margin: 4px 0;">{label}</div>
        <div style="color: {color}; font-size: 24px; font-weight: bold;">
            {f"{value:.1f}" if value else "-"}/5
            {delta_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_heat_cell(value):
    """Affiche une cellule colorée"""
    color = get_color_for_value(value)
    text = str(int(value)) if value else "-"
    return f'<span style="display: inline-block; width: 28px; height: 28px; background: {color}; border-radius: 4px; text-align: center; line-height: 28px; font-size: 12px; font-weight: bold; color: white; margin: 1px;">{text}</span>'

def render_status_badge(status):
    """Affiche un badge de statut"""
    color = get_status_color(status)
    return f'<span style="background: {color}20; color: {color}; padding: 2px 8px; border-radius: 9999px; font-size: 11px; border: 1px solid {color}40;">{status}</span>'

def render_radar_chart(data1, data2=None, label1="", label2=""):
    """Crée un graphique radar"""
    categories = [m['label'] for m in METRICS]
    
    fig = go.Figure()
    
    if data1:
        values1 = [data1.get(m['key'], 0) or 0 for m in METRICS]
        values1.append(values1[0])  # Fermer le radar
        fig.add_trace(go.Scatterpolar(
            r=values1,
            theta=categories + [categories[0]],
            fill='toself',
            name=label1,
            line_color='#10b981',
            fillcolor='rgba(16, 185, 129, 0.2)'
        ))
    
    if data2:
        values2 = [data2.get(m['key'], 0) or 0 for m in METRICS]
        values2.append(values2[0])
        fig.add_trace(go.Scatterpolar(
            r=values2,
            theta=categories + [categories[0]],
            fill='toself',
            name=label2,
            line_color='#3b82f6',
            fillcolor='rgba(59, 130, 246, 0.2)'
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 5], showticklabels=False),
            bgcolor='#1f2937'
        ),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#9ca3af'),
        margin=dict(l=60, r=60, t=40, b=60),
        height=350
    )
    
    return fig

def render_zscore_chart(data):
    """Crée un graphique de Z-Score"""
    if not data:
        return None
    
    df = pd.DataFrame(data)
    df = df.dropna(subset=['zscore'])
    
    if df.empty:
        return None
    
    settings = st.session_state.settings
    
    fig = go.Figure()
    
    # Zone de fond
    fig.add_hrect(y0=settings['zscore_alert'], y1=-3, fillcolor="rgba(239, 68, 68, 0.1)", line_width=0)
    fig.add_hrect(y0=settings['zscore_warning'], y1=settings['zscore_alert'], fillcolor="rgba(245, 158, 11, 0.1)", line_width=0)
    
    # Lignes de référence
    fig.add_hline(y=0, line_dash="dash", line_color="#6b7280", line_width=1)
    fig.add_hline(y=settings['zscore_warning'], line_dash="dash", line_color="#f59e0b", line_width=1)
    fig.add_hline(y=settings['zscore_alert'], line_dash="dash", line_color="#ef4444", line_width=1)
    
    # Courbe
    fig.add_trace(go.Scatter(
        x=df['date_formatted'],
        y=df['zscore'],
        mode='lines+markers',
        line=dict(color='#3b82f6', width=2),
        marker=dict(size=6),
        fill='tozeroy',
        fillcolor='rgba(59, 130, 246, 0.1)',
        name='Z-Score'
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='#1f2937',
        font=dict(color='#9ca3af'),
        margin=dict(l=40, r=40, t=20, b=40),
        height=250,
        xaxis=dict(showgrid=False, tickfont=dict(size=10)),
        yaxis=dict(showgrid=True, gridcolor='#374151', range=[-3, 3], tickfont=dict(size=10)),
        showlegend=False
    )
    
    return fig


# Import des pages
from pages import (
    page_dashboard, page_import, page_effectif, 
    page_infirmerie, page_gestion, page_parametres
)

# ==================== NAVIGATION ====================

def main():
    """Application principale"""
    
    with st.sidebar:
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
            <div style="width: 40px; height: 40px; background: linear-gradient(135deg, #10b981, #059669); 
                        border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px;">
                ⚡
            </div>
            <div>
                <div style="font-weight: bold; color: white;">Wellness</div>
                <div style="font-size: 11px; color: #9ca3af;">Rugby Tracker</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        dates = sorted(st.session_state.wellness_data.keys(), reverse=True)
        alert_count = len(get_alerts_for_date(dates[0])) if dates else 0
        
        page = st.radio(
            "Navigation",
            ["📊 Dashboard", "📥 Import/Export", "👥 Effectif", "🏥 Infirmerie", "👤 Joueurs", "⚙️ Paramètres"],
            label_visibility="collapsed"
        )
        
        if alert_count > 0:
            st.error(f"🚨 {alert_count} alertes")
        
        st.divider()
        st.caption(f"📊 {len(dates)} jours de données")
        st.caption(f"👥 {len(st.session_state.players)} joueurs")
        st.caption("💾 Auto-save activé")
    
    if page == "📊 Dashboard":
        page_dashboard(get_team_averages, get_group_averages, get_alerts_for_date, 
                      calculate_zscore_series, render_metric_card, render_radar_chart, render_zscore_chart)
    elif page == "📥 Import/Export":
        page_import(import_from_google_sheets, import_from_excel)
    elif page == "👥 Effectif":
        page_effectif(get_group_averages)
    elif page == "🏥 Infirmerie":
        page_infirmerie()
    elif page == "👤 Joueurs":
        page_gestion()
    elif page == "⚙️ Paramètres":
        page_parametres()


if __name__ == "__main__":
    main()
