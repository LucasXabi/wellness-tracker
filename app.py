"""
🏉 Rugby Wellness Tracker - Version Complète
Application Streamlit avec toutes les fonctionnalités
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import re
import urllib.parse

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

def get_player_average(d):
    if not d:
        return None
    vals = [d.get(m['key']) for m in METRICS if d.get(m['key']) is not None]
    return np.mean(vals) if vals else None

def get_color(value):
    if value is None:
        return '#374151'
    try:
        v = float(value)
        if v >= 4: return '#10b981'
        if v >= 3: return '#f59e0b'
        return '#ef4444'
    except:
        return '#374151'

def get_status_color(status):
    return {'Apte': '#10b981', 'Blessé': '#ef4444', 'Réhabilitation': '#f59e0b', 'Réathlétisation': '#3b82f6'}.get(status, '#6b7280')

def parse_french_date(date_str):
    if not date_str:
        return None
    try:
        s = str(date_str).lower().strip()
        match = re.search(r'(\d{1,2})\s+(\w+)\s+(\d{4})', s)
        if match:
            day, month_name, year = int(match.group(1)), match.group(2), int(match.group(3))
            month = FRENCH_MONTHS.get(month_name)
            if month:
                return datetime(year, month, day).date()
    except:
        pass
    return None

def format_date(d, style='short'):
    if isinstance(d, str):
        try:
            d = datetime.strptime(d, '%Y-%m-%d').date()
        except:
            return str(d)
    if not d:
        return '-'
    if style == 'full':
        days = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
        months = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
        return f"{days[d.weekday()]} {d.day} {months[d.month-1]} {d.year}"
    return d.strftime('%d/%m/%Y')

def metric_badge(value):
    color = get_color(value)
    text = str(int(value)) if value is not None else "-"
    return f'<span class="metric-badge" style="background:{color}">{text}</span>'

# ==================== IMPORT ====================
def import_from_google_sheets(url):
    try:
        match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
        if not match:
            return None, "URL invalide"
        
        sheet_id = match.group(1)
        sheet_name = urllib.parse.quote("Bien-être")
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
        
        df = pd.read_csv(csv_url, header=None)
        return process_imported_data(df)
    except Exception as e:
        return None, f"Erreur: {str(e)}"

def import_from_excel(file):
    try:
        xl = pd.ExcelFile(file)
        sheet = next((n for n in xl.sheet_names if 'bien' in n.lower() or 'être' in n.lower()), xl.sheet_names[0])
        df = pd.read_excel(file, sheet_name=sheet, header=None)
        return process_imported_data(df)
    except Exception as e:
        return None, f"Erreur: {str(e)}"

def process_imported_data(df):
    """Traite les données importées - format identique au React"""
    try:
        # Chercher la date dans les premières lignes
        date_found = None
        for i in range(min(10, len(df))):
            for val in df.iloc[i]:
                if pd.notna(val):
                    parsed = parse_french_date(str(val))
                    if parsed:
                        date_found = parsed
                        break
            if date_found:
                break
        
        if not date_found:
            date_found = datetime.now().date()
        
        # Trouver la ligne d'en-tête
        header_row = -1
        data_start = -1
        
        for i in range(min(10, len(df))):
            row = df.iloc[i]
            row_str = ' '.join([str(v).lower() for v in row if pd.notna(v)])
            if 'joueur' in row_str or ('poids' in row_str and 'sommeil' in row_str):
                header_row = i
                data_start = i + 1
                break
        
        # Valeurs par défaut si pas trouvé (basé sur le format du Google Sheet)
        if header_row == -1:
            header_row = 2
            data_start = 4  # Après la ligne EQUIPE
        
        # Identifier les colonnes dynamiquement ou utiliser les défauts
        col_map = {
            'name': 1,        # B
            'weight': 2,      # C
            'sleep': 3,       # D
            'mentalLoad': 4,  # E
            'motivation': 5,  # F
            'hdcState': 6,    # G
            'bdcState': 7,    # H
            'remark': 9       # J (après Moyenne en I)
        }
        
        # Essayer d'identifier les colonnes depuis les en-têtes
        if header_row < len(df):
            headers = df.iloc[header_row]
            for idx, h in enumerate(headers):
                if pd.notna(h):
                    hl = str(h).lower().strip()
                    if 'joueur' in hl or hl == 'nom':
                        col_map['name'] = idx
                    elif 'poids' in hl:
                        col_map['weight'] = idx
                    elif 'sommeil' in hl:
                        col_map['sleep'] = idx
                    elif 'charge' in hl or 'mentale' in hl:
                        col_map['mentalLoad'] = idx
                    elif 'motivation' in hl:
                        col_map['motivation'] = idx
                    elif 'hdc' in hl or ('état' in hl and 'haut' in hl):
                        col_map['hdcState'] = idx
                    elif 'bdc' in hl or ('état' in hl and 'bas' in hl):
                        col_map['bdcState'] = idx
                    elif 'remarque' in hl or 'note' in hl or 'commentaire' in hl:
                        col_map['remark'] = idx
        
        # Traiter les données
        data_rows = []
        new_players = []
        existing_names = {p['name'] for p in st.session_state.players}
        
        for i in range(data_start, len(df)):
            row = df.iloc[i]
            
            # Nom du joueur
            name_idx = col_map['name']
            if name_idx >= len(row):
                continue
            name_val = row.iloc[name_idx]
            if pd.isna(name_val):
                continue
            
            name = str(name_val).strip().upper()
            if name in ['', 'EQUIPE', 'NAN', 'NONE', 'ÉQUIPE']:
                continue
            
            def get_num(key):
                idx = col_map.get(key)
                if idx is None or idx >= len(row):
                    return None
                val = row.iloc[idx]
                if pd.isna(val):
                    return None
                s = str(val).strip().replace(',', '.')
                if s in ['', '#DIV/0!', 'nan', 'None', '-']:
                    return None
                try:
                    return float(s)
                except:
                    return None
            
            def get_txt(key):
                idx = col_map.get(key)
                if idx is None or idx >= len(row):
                    return ''
                val = row.iloc[idx]
                if pd.isna(val):
                    return ''
                s = str(val).strip()
                return '' if s.lower() in ['nan', 'none'] else s
            
            entry = {
                'name': name,
                'weight': get_num('weight'),
                'sleep': get_num('sleep'),
                'mentalLoad': get_num('mentalLoad'),
                'motivation': get_num('motivation'),
                'hdcState': get_num('hdcState'),
                'bdcState': get_num('bdcState'),
                'remark': get_txt('remark')
            }
            
            # Vérifier qu'on a au moins une donnée
            has_data = any(entry.get(m['key']) is not None for m in METRICS) or entry.get('weight') is not None
            if not has_data:
                continue
            
            data_rows.append(entry)
            
            # Créer le joueur si nouveau
            if name not in existing_names:
                existing_names.add(name)
                new_players.append({
                    'id': f"{datetime.now().timestamp()}_{name[:3]}",
                    'name': name,
                    'position': 'Pilier gauche',
                    'status': 'Apte',
                    'targetWeight': entry['weight'] or 90
                })
        
        # Ajouter les nouveaux joueurs
        st.session_state.players.extend(new_players)
        
        # Ajouter les données
        date_key = date_found.isoformat()
        if date_key in st.session_state.data:
            existing = {d['name']: d for d in st.session_state.data[date_key]}
            for row in data_rows:
                existing[row['name']] = row
            st.session_state.data[date_key] = list(existing.values())
        else:
            st.session_state.data[date_key] = data_rows
        
        return {'date': date_found, 'count': len(data_rows), 'new': len(new_players)}, None
    
    except Exception as e:
        import traceback
        return None, f"Erreur: {str(e)}\n{traceback.format_exc()}"

# ==================== CALCULS ====================
def get_team_avg(date_key):
    data = st.session_state.data.get(date_key, [])
    if not data:
        return None
    result = {'count': len(data)}
    for m in METRICS:
        vals = [d[m['key']] for d in data if d.get(m['key']) is not None]
        result[m['key']] = np.mean(vals) if vals else None
    avgs = [get_player_average(d) for d in data]
    avgs = [a for a in avgs if a is not None]
    result['global'] = np.mean(avgs) if avgs else None
    return result

def get_group_avg(date_key, group=None, line=None):
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
        result[m['key']] = np.mean(vals) if vals else None
    avgs = [get_player_average(d) for d in filtered]
    avgs = [a for a in avgs if a is not None]
    result['global'] = np.mean(avgs) if avgs else None
    return result

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
                    'type': 'critical',
                    'player': d['name'],
                    'player_obj': p,
                    'metric': m,
                    'value': val,
                    'message': f"{m['icon']} {m['label']} = {int(val)}/5"
                })
        
        # Poids
        if d.get('weight') and p.get('targetWeight'):
            diff = d['weight'] - p['targetWeight']
            if abs(diff) > settings['weightThreshold']:
                alerts.append({
                    'type': 'weight',
                    'player': d['name'],
                    'player_obj': p,
                    'value': d['weight'],
                    'target': p['targetWeight'],
                    'diff': diff,
                    'message': f"⚖️ {d['weight']:.1f}kg ({'+' if diff > 0 else ''}{diff:.1f}kg vs forme)"
                })
    
    return alerts

def calc_zscore(value, history, min_days=5):
    if not history or len(history) < min_days or value is None:
        return None
    mean, std = np.mean(history), np.std(history)
    return 0 if std == 0 else (value - mean) / std

def zscore_series(metric='global', group=None, player_name=None, days=30):
    dates = sorted(st.session_state.data.keys())
    if not dates:
        return []
    
    settings = st.session_state.settings
    zscore_days = settings.get('zscoreDays', 14)
    result = []
    
    for date in dates[-days:]:
        data = st.session_state.data.get(date, [])
        
        filtered = []
        for d in data:
            p = next((p for p in st.session_state.players if p['name'] == d['name']), None)
            if not p:
                continue
            if group and get_player_group(p['position']) != group:
                continue
            if player_name and p['name'] != player_name:
                continue
            filtered.append(d)
        
        if not filtered:
            result.append({'date': date, 'fmt': format_date(date), 'value': None, 'zscore': None})
            continue
        
        # Valeur du jour
        if metric == 'global':
            vals = [get_player_average(d) for d in filtered]
            vals = [v for v in vals if v is not None]
            day_val = np.mean(vals) if vals else None
        else:
            vals = [d.get(metric) for d in filtered if d.get(metric) is not None]
            day_val = np.mean(vals) if vals else None
        
        # Historique pour Z-Score
        idx = dates.index(date)
        hist_dates = dates[max(0, idx - zscore_days):idx]
        hist_vals = []
        
        for hd in hist_dates:
            hdata = st.session_state.data.get(hd, [])
            hfiltered = []
            for d in hdata:
                p = next((p for p in st.session_state.players if p['name'] == d['name']), None)
                if not p:
                    continue
                if group and get_player_group(p['position']) != group:
                    continue
                if player_name and p['name'] != player_name:
                    continue
                hfiltered.append(d)
            
            if hfiltered:
                if metric == 'global':
                    vs = [get_player_average(d) for d in hfiltered]
                    vs = [v for v in vs if v is not None]
                    if vs:
                        hist_vals.append(np.mean(vs))
                else:
                    vs = [d.get(metric) for d in hfiltered if d.get(metric) is not None]
                    if vs:
                        hist_vals.append(np.mean(vs))
        
        zscore = calc_zscore(day_val, hist_vals)
        result.append({
            'date': date,
            'fmt': format_date(date),
            'value': round(day_val, 2) if day_val else None,
            'zscore': round(zscore, 2) if zscore is not None else None
        })
    
    return result

# ==================== GRAPHIQUES ====================
def radar_chart(data1, data2=None, label1="", label2=""):
    cats = [m['label'] for m in METRICS]
    fig = go.Figure()
    
    if data1:
        vals = [data1.get(m['key'], 0) or 0 for m in METRICS] + [data1.get(METRICS[0]['key'], 0) or 0]
        fig.add_trace(go.Scatterpolar(
            r=vals, theta=cats + [cats[0]], fill='toself', name=label1,
            line_color='#10b981', fillcolor='rgba(16,185,129,0.3)'
        ))
    
    if data2:
        vals = [data2.get(m['key'], 0) or 0 for m in METRICS] + [data2.get(METRICS[0]['key'], 0) or 0]
        fig.add_trace(go.Scatterpolar(
            r=vals, theta=cats + [cats[0]], fill='toself', name=label2,
            line_color='#3b82f6', fillcolor='rgba(59,130,246,0.3)'
        ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 5], showticklabels=False), bgcolor='rgba(0,0,0,0)'),
        showlegend=True, legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
        paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#9ca3af'),
        margin=dict(l=60, r=60, t=40, b=60), height=350
    )
    return fig

def zscore_chart(data):
    if not data:
        return None
    df = pd.DataFrame(data).dropna(subset=['zscore'])
    if df.empty:
        return None
    
    settings = st.session_state.settings
    colors = ['#ef4444' if z < settings['zscoreAlert'] else '#f59e0b' if z < settings['zscoreWarning'] else '#10b981' for z in df['zscore']]
    
    fig = go.Figure()
    fig.add_hrect(y0=-3, y1=settings['zscoreAlert'], fillcolor="rgba(239,68,68,0.1)", line_width=0)
    fig.add_hrect(y0=settings['zscoreAlert'], y1=settings['zscoreWarning'], fillcolor="rgba(245,158,11,0.1)", line_width=0)
    fig.add_hline(y=0, line_dash="dash", line_color="#6b7280", line_width=1)
    fig.add_hline(y=settings['zscoreWarning'], line_dash="dash", line_color="#f59e0b", line_width=1)
    fig.add_hline(y=settings['zscoreAlert'], line_dash="dash", line_color="#ef4444", line_width=1)
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
    
    # ===== ALERTES =====
    alerts = get_alerts(date_key)
    if alerts:
        st.subheader(f"🚨 Alertes du jour ({len(alerts)})")
        
        # Grouper par joueur
        by_player = {}
        for a in alerts:
            by_player.setdefault(a['player'], []).append(a)
        
        cols = st.columns(min(len(by_player), 4))
        for i, (player_name, player_alerts) in enumerate(list(by_player.items())[:8]):
            with cols[i % 4]:
                msgs = " • ".join([a['message'] for a in player_alerts])
                has_critical = any(a['type'] == 'critical' for a in player_alerts)
                color = "#ef4444" if has_critical else "#f59e0b"
                badge = "🔴 Critique" if has_critical else "🟠 Attention"
                
                st.markdown(f"""
                <div style="background:{color}15;border:1px solid {color};padding:12px;border-radius:8px;margin-bottom:8px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span style="font-weight:600;color:white;">{player_name}</span>
                        <span style="font-size:10px;background:{color}30;color:{color};padding:2px 6px;border-radius:10px;">{badge}</span>
                    </div>
                    <div style="color:{color};font-size:13px;margin-top:4px;">{msgs}</div>
                </div>
                """, unsafe_allow_html=True)
    
    # ===== FILTRES ET TABLEAU =====
    st.subheader("👥 Vue équipe")
    
    c1, c2, c3, c4 = st.columns([1.5, 1.5, 1.5, 1])
    with c1:
        sort_by = st.selectbox("Trier par", ["Nom A→Z", "🚨 Alertes", "📉 Moyenne ↑", "👥 Groupe"], key="sort")
    with c2:
        filter_group = st.selectbox("Groupe", ["Tous", "Avants", "Trois-quarts"], key="fg")
    with c3:
        filter_line = st.selectbox("Ligne", ["Toutes"] + ALL_LINES, key="fl")
    with c4:
        show_issues = st.checkbox("⚠️ Problèmes", key="si")
    
    # Construire les données du tableau
    rows = []
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
        
        rows.append({
            'Joueur': d['name'],
            'Poste': p['position'],
            'Groupe': get_player_group(p['position']),
            'Statut': p['status'],
            '😴': d.get('sleep'),
            '🧠': d.get('mentalLoad'),
            '💪': d.get('motivation'),
            '❤️': d.get('hdcState'),
            '💚': d.get('bdcState'),
            'Moy': round(avg, 2) if avg else None,
            'vs Éq.': f"{'+' if diff_vs_team and diff_vs_team > 0 else ''}{diff_vs_team:.2f}" if diff_vs_team else '-',
            '⚖️': round(d.get('weight'), 1) if d.get('weight') else None,
            'Note': (d.get('remark', '') or '')[:30],
            '_has_issue': has_issue,
            '_avg': avg or 5
        })
    
    # Trier
    if sort_by == "🚨 Alertes":
        rows.sort(key=lambda x: (not x['_has_issue'], x['Joueur']))
    elif sort_by == "📉 Moyenne ↑":
        rows.sort(key=lambda x: x['_avg'])
    elif sort_by == "👥 Groupe":
        rows.sort(key=lambda x: (x['Groupe'], x['Joueur']))
    else:
        rows.sort(key=lambda x: x['Joueur'])
    
    # Afficher le tableau
    if rows:
        df = pd.DataFrame(rows)
        df = df.drop(columns=['_has_issue', '_avg'])
        
        def color_val(val):
            if pd.isna(val) or val is None:
                return ''
            try:
                v = float(val)
                if v <= 2: return 'background-color:#ef4444;color:white'
                if v <= 3: return 'background-color:#f59e0b;color:white'
                if v <= 5: return 'background-color:#10b981;color:white'
            except:
                pass
            return ''
        
        metric_cols = ['😴', '🧠', '💪', '❤️', '💚']
        styled = df.style.applymap(color_val, subset=metric_cols)
        st.dataframe(styled, use_container_width=True, height=400)
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
                st.caption(f"🟢 {cmp1}: {d1['global']:.2f}/5 | 🔵 {cmp2}: {d2['global']:.2f}/5")


def page_import():
    st.title("📥 Import / Export")
    
    # ===== GOOGLE SHEETS =====
    st.subheader("📊 Importer depuis Google Sheets")
    
    url = st.text_input(
        "URL du Google Sheet",
        value="https://docs.google.com/spreadsheets/d/1Esm3NnED51jFpTs-oSjIdVybH51BSEcjhWOQhP1P3zI/edit?usp=sharing",
        help="Collez l'URL complète de votre Google Sheet"
    )
    
    st.info("💡 **Important**: Le Google Sheet doit être partagé en '**Accessible à tous ceux qui ont le lien**'")
    
    if st.button("🔄 Importer depuis Google Sheets", type="primary"):
        with st.spinner("Import en cours..."):
            res, err = import_from_google_sheets(url)
            if err:
                st.error(f"❌ {err}")
            else:
                st.success(f"""
                ✅ **Import réussi !**
                - 📅 Date: **{format_date(res['date'], 'full')}**
                - 👥 Joueurs importés: **{res['count']}**
                - 🆕 Nouveaux joueurs créés: **{res['new']}**
                """)
                st.balloons()
    
    st.divider()
    
    # ===== EXCEL =====
    st.subheader("📁 Importer un fichier Excel")
    
    file = st.file_uploader("Glissez votre fichier Excel ici", type=['xlsx', 'xls'])
    
    if file:
        with st.spinner("Traitement..."):
            res, err = import_from_excel(file)
            if err:
                st.error(f"❌ {err}")
            else:
                st.success(f"✅ **{res['count']}** joueurs importés pour le **{format_date(res['date'], 'full')}**")
    
    st.divider()
    
    # ===== DONNÉES =====
    st.subheader("📅 Données disponibles")
    
    dates = sorted(st.session_state.data.keys(), reverse=True)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("📊 Jours de données", len(dates))
    c2.metric("👥 Joueurs", len(st.session_state.players))
    c3.metric("📝 Entrées totales", sum(len(v) for v in st.session_state.data.values()))
    
    if dates:
        st.write("**Dates chargées:**")
        st.write(" ".join([f"`{format_date(d)}`" for d in dates[:20]]))
        if len(dates) > 20:
            st.caption(f"... et {len(dates) - 20} autres dates")


def page_effectif():
    st.title("👥 Effectif & Comparaisons")
    
    dates = sorted(st.session_state.data.keys(), reverse=True)
    date_key = dates[0] if dates else None
    today_data = st.session_state.data.get(date_key, []) if date_key else []
    
    if not st.session_state.players:
        st.warning("⚠️ Aucun joueur. Importez des données d'abord.")
        return
    
    tab1, tab2, tab3 = st.tabs(["📋 Liste", "📊 Comparer joueurs", "👥 Stats par groupe"])
    
    # ===== LISTE =====
    with tab1:
        search = st.text_input("🔍 Rechercher un joueur", key="search_eff")
        filtered = [p for p in st.session_state.players if search.lower() in p['name'].lower()]
        
        cols = st.columns(3)
        for i, p in enumerate(filtered):
            with cols[i % 3]:
                pd_data = next((d for d in today_data if d['name'] == p['name']), {})
                avg = get_player_average(pd_data)
                color = get_status_color(p['status'])
                
                metrics_html = ''.join([metric_badge(pd_data.get(m['key'])) for m in METRICS])
                
                st.markdown(f"""
                <div class="player-card">
                    <div style="display:flex;justify-content:space-between;margin-bottom:8px;">
                        <div>
                            <div style="font-weight:600;color:white;">{p['name']}</div>
                            <div style="font-size:11px;color:#9ca3af;">{p['position']} • {get_player_group(p['position'])}</div>
                        </div>
                        <span style="background:{color}30;color:{color};padding:2px 8px;border-radius:20px;font-size:11px;height:fit-content;">{p['status']}</span>
                    </div>
                    <div style="margin:8px 0;">{metrics_html}</div>
                    <div style="display:flex;justify-content:space-between;font-size:11px;color:#9ca3af;">
                        <span>⚖️ {pd_data.get('weight') or '-'}kg</span>
                        <span style="font-weight:600;">Moy: {f"{avg:.1f}" if avg else "-"}/5</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # ===== COMPARER =====
    with tab2:
        st.write("**Sélectionnez 2 à 6 joueurs à comparer:**")
        selected = st.multiselect("Joueurs", [p['name'] for p in st.session_state.players], max_selections=6, key="cmp_players")
        
        if len(selected) >= 2:
            fig = go.Figure()
            colors = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']
            
            for i, name in enumerate(selected):
                pd_data = next((d for d in today_data if d['name'] == name), {})
                vals = [pd_data.get(m['key'], 0) or 0 for m in METRICS] + [pd_data.get(METRICS[0]['key'], 0) or 0]
                fig.add_trace(go.Scatterpolar(
                    r=vals,
                    theta=[m['label'] for m in METRICS] + [METRICS[0]['label']],
                    fill='toself',
                    name=name,
                    line_color=colors[i % len(colors)]
                ))
            
            fig.update_layout(
                polar=dict(radialaxis=dict(range=[0, 5])),
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#9ca3af'),
                height=450
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # ===== GROUPES =====
    with tab3:
        if not date_key:
            st.warning("Aucune donnée")
            return
        
        rows = []
        
        # Équipe
        team = get_group_avg(date_key)
        if team:
            row = {'Groupe': '🏉 Équipe', 'Effectif': team['count']}
            for m in METRICS:
                row[m['icon']] = round(team.get(m['key'], 0) or 0, 1)
            row['Moyenne'] = round(team.get('global', 0) or 0, 2)
            rows.append(row)
        
        # Avants / Trois-quarts
        for g in ['Avants', 'Trois-quarts']:
            avg = get_group_avg(date_key, group=g)
            if avg:
                emoji = '💪' if g == 'Avants' else '🏃'
                row = {'Groupe': f'{emoji} {g}', 'Effectif': avg['count']}
                for m in METRICS:
                    row[m['icon']] = round(avg.get(m['key'], 0) or 0, 1)
                row['Moyenne'] = round(avg.get('global', 0) or 0, 2)
                rows.append(row)
        
        # Lignes
        for line in ALL_LINES:
            avg = get_group_avg(date_key, line=line)
            if avg and avg['count'] > 0:
                row = {'Groupe': f'  └ {line}', 'Effectif': avg['count']}
                for m in METRICS:
                    row[m['icon']] = round(avg.get(m['key'], 0) or 0, 1)
                row['Moyenne'] = round(avg.get('global', 0) or 0, 2)
                rows.append(row)
        
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def page_infirmerie():
    st.title("🏥 Infirmerie")
    
    # ===== COMPTEURS PAR STATUT =====
    counts = {s: len([p for p in st.session_state.players if p['status'] == s]) for s in STATUSES}
    
    cols = st.columns(4)
    status_config = [
        ('Apte', '✅', '#10b981'),
        ('Blessé', '🤕', '#ef4444'),
        ('Réhabilitation', '🏥', '#f59e0b'),
        ('Réathlétisation', '🏃', '#3b82f6')
    ]
    
    for i, (status, emoji, color) in enumerate(status_config):
        with cols[i]:
            if st.button(f"{emoji} {counts[status]} {status}", key=f"btn_{status}", use_container_width=True):
                st.session_state.status_filter = status if st.session_state.status_filter != status else None
                st.rerun()
    
    # Afficher joueurs filtrés
    if st.session_state.status_filter:
        status = st.session_state.status_filter
        filtered = [p for p in st.session_state.players if p['status'] == status]
        
        st.subheader(f"Joueurs {status}s ({len(filtered)})")
        
        for p in filtered:
            c1, c2, c3 = st.columns([2, 2, 1])
            with c1:
                st.write(f"**{p['name']}**")
            with c2:
                st.caption(p['position'])
            with c3:
                new_s = st.selectbox("", STATUSES, index=STATUSES.index(p['status']), key=f"sf_{p['id']}", label_visibility="collapsed")
                if new_s != p['status']:
                    p['status'] = new_s
                    st.rerun()
        
        if st.button("← Fermer"):
            st.session_state.status_filter = None
            st.rerun()
    
    st.divider()
    
    # ===== NOUVELLE BLESSURE =====
    with st.expander("➕ Déclarer une nouvelle blessure", expanded=False):
        if not st.session_state.players:
            st.warning("Aucun joueur")
        else:
            c1, c2 = st.columns(2)
            
            with c1:
                inj_player = st.selectbox("Joueur", [p['name'] for p in st.session_state.players], key="inj_player")
                inj_zone = st.selectbox("Zone blessée", list(INJURY_ZONES.keys()),
                                         format_func=lambda x: f"{INJURY_ZONES[x]['icon']} {x}", key="inj_zone")
                inj_grade = st.selectbox("Grade (1=léger → 3=grave)", [1, 2, 3], key="inj_grade")
            
            with c2:
                inj_date = st.date_input("Date de la blessure", key="inj_date")
                inj_circ = st.selectbox("Circonstance", CIRCUMSTANCES, key="inj_circ")
                est_days = INJURY_ZONES[inj_zone][inj_grade]
                est_return = inj_date + timedelta(days=est_days)
                st.info(f"⏱️ **Estimation**: {est_days} jours\n\n📅 **Retour prévu**: {format_date(est_return)}")
            
            inj_notes = st.text_input("Notes", key="inj_notes")
            
            if st.button("💾 Enregistrer la blessure", type="primary"):
                p = next((p for p in st.session_state.players if p['name'] == inj_player), None)
                if p:
                    st.session_state.injuries.append({
                        'id': str(datetime.now().timestamp()),
                        'player_id': p['id'],
                        'player_name': p['name'],
                        'zone': inj_zone,
                        'grade': inj_grade,
                        'date': inj_date.isoformat(),
                        'circumstance': inj_circ,
                        'notes': inj_notes,
                        'estimated_days': est_days,
                        'estimated_return': est_return.isoformat()
                    })
                    p['status'] = 'Blessé'
                    st.success(f"✅ Blessure enregistrée pour {p['name']}")
                    st.rerun()
    
    # ===== LISTE DES BLESSURES =====
    st.subheader("📋 Blessures enregistrées")
    
    if not st.session_state.injuries:
        st.info("Aucune blessure enregistrée")
    else:
        for inj in st.session_state.injuries:
            start = datetime.strptime(inj['date'], '%Y-%m-%d')
            end = datetime.strptime(inj['estimated_return'], '%Y-%m-%d')
            elapsed = (datetime.now() - start).days
            total = (end - start).days
            progress = min(100, max(0, elapsed / total * 100 if total > 0 else 100))
            
            c1, c2, c3 = st.columns([3, 2, 0.5])
            
            with c1:
                st.markdown(f"**{inj['player_name']}** - {INJURY_ZONES[inj['zone']]['icon']} {inj['zone']} (Grade {inj['grade']})")
                st.caption(f"📅 {format_date(inj['date'])} → {format_date(inj['estimated_return'])} ({inj['estimated_days']} jours)")
                st.progress(progress / 100)
                if inj.get('notes'):
                    st.caption(f"💬 {inj['notes']}")
            
            with c2:
                p = next((p for p in st.session_state.players if p['id'] == inj['player_id']), None)
                if p:
                    new_s = st.selectbox("Statut", STATUSES, index=STATUSES.index(p['status']), key=f"inj_s_{inj['id']}")
                    if new_s != p['status']:
                        p['status'] = new_s
                        st.rerun()
            
            with c3:
                if st.button("🗑️", key=f"del_inj_{inj['id']}"):
                    st.session_state.injuries.remove(inj)
                    st.rerun()
            
            st.divider()


def page_joueurs():
    st.title("👤 Gestion des joueurs")
    
    # ===== AJOUTER =====
    with st.expander("➕ Ajouter un joueur", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            new_name = st.text_input("Nom du joueur", key="new_name")
            new_pos = st.selectbox("Poste", ALL_POSITIONS, key="new_pos")
        with c2:
            new_weight = st.number_input("Poids forme (kg)", value=90.0, key="new_weight")
            new_status = st.selectbox("Statut", STATUSES, key="new_status")
        
        if st.button("💾 Ajouter le joueur", type="primary") and new_name:
            st.session_state.players.append({
                'id': str(datetime.now().timestamp()),
                'name': new_name.upper().strip(),
                'position': new_pos,
                'targetWeight': new_weight,
                'status': new_status
            })
            st.success(f"✅ {new_name.upper()} ajouté !")
            st.rerun()
    
    st.divider()
    
    # ===== LISTE =====
    st.subheader(f"📋 Liste des joueurs ({len(st.session_state.players)})")
    
    if not st.session_state.players:
        st.info("Aucun joueur. Importez des données ou ajoutez des joueurs manuellement.")
    else:
        for p in st.session_state.players:
            c1, c2, c3, c4, c5 = st.columns([2, 2, 1.5, 1.5, 0.5])
            
            with c1:
                st.text_input("", value=p['name'], key=f"pn_{p['id']}", disabled=True, label_visibility="collapsed")
            with c2:
                idx = ALL_POSITIONS.index(p['position']) if p['position'] in ALL_POSITIONS else 0
                new_pos = st.selectbox("", ALL_POSITIONS, index=idx, key=f"pp_{p['id']}", label_visibility="collapsed")
                if new_pos != p['position']:
                    p['position'] = new_pos
            with c3:
                new_w = st.number_input("", value=float(p.get('targetWeight', 90)), key=f"pw_{p['id']}", label_visibility="collapsed")
                if new_w != p.get('targetWeight'):
                    p['targetWeight'] = new_w
            with c4:
                new_s = st.selectbox("", STATUSES, index=STATUSES.index(p['status']), key=f"ps_{p['id']}", label_visibility="collapsed")
                if new_s != p['status']:
                    p['status'] = new_s
            with c5:
                if st.button("🗑️", key=f"pd_{p['id']}"):
                    st.session_state.players = [x for x in st.session_state.players if x['id'] != p['id']]
                    st.rerun()


def page_parametres():
    st.title("⚙️ Paramètres")
    
    s = st.session_state.settings
    
    # ===== ALERTES =====
    st.subheader("🚨 Seuils d'alertes")
    c1, c2, c3 = st.columns(3)
    with c1:
        s['lowValueThreshold'] = st.number_input("Valeur basse (≤ X = alerte)", 1, 5, int(s['lowValueThreshold']),
                                                  help="Alerte si une métrique ≤ cette valeur")
    with c2:
        s['variationThreshold'] = st.number_input("Variation jour/jour", 0.5, 4.0, float(s['variationThreshold']), 0.5,
                                                   help="Alerte si baisse > X pts vs veille")
    with c3:
        s['weightThreshold'] = st.number_input("Écart poids (kg)", 0.5, 10.0, float(s['weightThreshold']), 0.5,
                                                help="Alerte si écart > ±X kg vs poids forme")
    
    st.divider()
    
    # ===== Z-SCORE =====
    st.subheader("📈 Calcul Z-Score")
    c1, c2, c3 = st.columns(3)
    with c1:
        s['zscoreDays'] = st.number_input("Période de calcul (jours)", 7, 60, int(s['zscoreDays']),
                                           help="Historique pour moyenne et écart-type")
    with c2:
        s['zscoreWarning'] = st.number_input("Seuil attention (jaune)", -3.0, 0.0, float(s['zscoreWarning']), 0.1,
                                              help="Zone attention si Z < cette valeur")
    with c3:
        s['zscoreAlert'] = st.number_input("Seuil alerte (rouge)", -3.0, 0.0, float(s['zscoreAlert']), 0.1,
                                            help="Zone alerte si Z < cette valeur")
    
    st.divider()
    
    # ===== ACTIONS =====
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔄 Réinitialiser les paramètres"):
            st.session_state.settings = DEFAULT_SETTINGS.copy()
            st.success("✅ Paramètres réinitialisés")
            st.rerun()
    with c2:
        if st.button("🗑️ Effacer toutes les données", type="secondary"):
            st.session_state.players = []
            st.session_state.data = {}
            st.session_state.injuries = []
            st.warning("⚠️ Toutes les données ont été effacées")
            st.rerun()
    
    # ===== AIDE =====
    st.divider()
    st.subheader("💡 Aide")
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
