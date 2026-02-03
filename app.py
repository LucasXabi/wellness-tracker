"""
🏉 Rugby Wellness Tracker - Version Ultra Premium
Application Streamlit avec design moderne et fonctionnalités complètes
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
st.set_page_config(
    page_title="Rugby Wellness Tracker",
    page_icon="🏉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CSS PREMIUM ====================
st.markdown("""
<style>
    /* Reset et base */
    .main .block-container {
        padding: 1rem 2rem;
        max-width: 1400px;
    }
    
    /* Cards premium */
    .premium-card {
        background: linear-gradient(145deg, #1e293b, #0f172a);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    .glass-card {
        background: rgba(30, 41, 59, 0.8);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(148, 163, 184, 0.1);
        border-radius: 12px;
        padding: 1rem;
    }
    
    /* Team average card */
    .team-avg-card {
        background: linear-gradient(135deg, #059669 0%, #0d9488 50%, #0891b2 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 40px rgba(5, 150, 105, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .team-avg-card::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
    }
    
    /* Metric badges */
    .metric-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 36px;
        height: 36px;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 700;
        color: white;
        margin: 2px;
        transition: transform 0.2s;
    }
    
    .metric-badge:hover {
        transform: scale(1.1);
    }
    
    /* Alert cards */
    .alert-card {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(239, 68, 68, 0.05));
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-left: 4px solid #ef4444;
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 8px;
        transition: all 0.2s;
    }
    
    .alert-card:hover {
        transform: translateX(4px);
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.2);
    }
    
    .alert-card.warning {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(245, 158, 11, 0.05));
        border-color: rgba(245, 158, 11, 0.3);
        border-left-color: #f59e0b;
    }
    
    /* Player row */
    .player-row {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(71, 85, 105, 0.3);
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 8px;
        transition: all 0.2s;
        cursor: pointer;
    }
    
    .player-row:hover {
        background: rgba(51, 65, 85, 0.7);
        border-color: rgba(99, 102, 241, 0.5);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .status-apte { background: rgba(16, 185, 129, 0.2); color: #34d399; }
    .status-blesse { background: rgba(239, 68, 68, 0.2); color: #f87171; }
    .status-rehab { background: rgba(245, 158, 11, 0.2); color: #fbbf24; }
    .status-reath { background: rgba(59, 130, 246, 0.2); color: #60a5fa; }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    }
    
    [data-testid="stSidebar"] .stRadio > label {
        background: transparent;
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 4px;
        transition: all 0.2s;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
    }
    
    /* Data display */
    .big-number {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #fff, #94a3b8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1;
    }
    
    /* Calendar */
    .calendar-day {
        width: 100%;
        aspect-ratio: 1;
        border-radius: 8px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        transition: transform 0.2s;
    }
    
    .calendar-day:hover {
        transform: scale(1.05);
    }
    
    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Animations */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .pulse {
        animation: pulse 2s infinite;
    }
    
    /* Table styling */
    .dataframe {
        border-radius: 12px !important;
        overflow: hidden;
    }
    
    /* Progress bars */
    .stProgress > div > div {
        background: linear-gradient(90deg, #10b981, #059669);
        border-radius: 10px;
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

# Mapping flexible pour les colonnes
COLUMN_MAPPINGS = {
    'name': ['joueur', 'nom', 'name', 'player', 'prenom', 'prénom'],
    'weight': ['poids', 'weight', 'kg', 'masse'],
    'sleep': ['sommeil', 'sleep', 'dormir', 'nuit'],
    'mentalLoad': ['charge mentale', 'mental', 'charge', 'stress', 'mentalload'],
    'motivation': ['motivation', 'motiv', 'envie'],
    'hdcState': ['hdc', 'haut du corps', 'hautducorps', 'upper'],
    'bdcState': ['bdc', 'bas du corps', 'basducorps', 'lower'],
    'remark': ['remarque', 'commentaire', 'note', 'comment', 'remark', 'observation']
}

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

def format_date(date_str, fmt='short'):
    if not date_str:
        return '-'
    try:
        d = datetime.strptime(date_str, '%Y-%m-%d')
        if fmt == 'short':
            return d.strftime('%d %b').replace('Jan', 'janv').replace('Feb', 'fév').replace('Mar', 'mars').replace('Apr', 'avr').replace('May', 'mai').replace('Jun', 'juin').replace('Jul', 'juil').replace('Aug', 'août').replace('Sep', 'sept').replace('Oct', 'oct').replace('Nov', 'nov').replace('Dec', 'déc')
        elif fmt == 'full':
            days = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
            months = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
            return f"{days[d.weekday()]} {d.day} {months[d.month-1]} {d.year}"
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

def get_alerts(date_key):
    data = st.session_state.data.get(date_key, [])
    settings = st.session_state.settings
    alerts = []
    
    for d in data:
        p = next((p for p in st.session_state.players if p['name'] == d['name']), None)
        if not p:
            continue
        
        for m in METRICS:
            val = d.get(m['key'])
            if val is not None and val <= settings['lowValueThreshold']:
                alerts.append({
                    'player': d['name'],
                    'player_id': p['id'],
                    'type': 'critical',
                    'metric': m,
                    'value': val,
                    'message': f"{m['label']} à {val}/5"
                })
        
        if d.get('weight') and p.get('targetWeight'):
            diff = abs(d['weight'] - p['targetWeight'])
            if diff > settings['weightThreshold']:
                alerts.append({
                    'player': d['name'],
                    'player_id': p['id'],
                    'type': 'weight',
                    'diff': round(d['weight'] - p['targetWeight'], 1),
                    'message': f"Poids {d['weight']:.1f}kg (forme: {p['targetWeight']}kg)"
                })
    
    return alerts

def get_availability_data():
    counts = {}
    for p in st.session_state.players:
        status = p.get('status', 'Apte')
        counts[status] = counts.get(status, 0) + 1
    
    colors = {'Apte': '#10b981', 'Blessé': '#ef4444', 'Réhabilitation': '#f59e0b', 'Réathlétisation': '#3b82f6'}
    return [{'name': k, 'value': v, 'color': colors.get(k, '#6b7280')} for k, v in counts.items() if v > 0]

def get_player_history(player_name, days=30):
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
    return (value - mean) / std if std > 0 else 0

def get_color_for_value(val):
    if val is None:
        return '#475569'
    if val <= 2:
        return '#ef4444'
    if val <= 3:
        return '#f59e0b'
    return '#10b981'

# ==================== IMPORT INTELLIGENT ====================
def find_column_match(header, mappings):
    """Trouve la correspondance de colonne de manière intelligente"""
    header_clean = str(header).lower().strip()
    header_clean = re.sub(r'[^a-zàâäéèêëïîôùûüç0-9]', '', header_clean)
    
    for key, patterns in mappings.items():
        for pattern in patterns:
            pattern_clean = re.sub(r'[^a-zàâäéèêëïîôùûüç0-9]', '', pattern.lower())
            if pattern_clean in header_clean or header_clean in pattern_clean:
                return key
    return None

def parse_date_french(text):
    """Parse une date en français de manière flexible"""
    text = str(text).lower().strip()
    
    # Format: "6 janvier 2025" ou "06 janvier 2025"
    match = re.search(r'(\d{1,2})\s*(janvier|février|fevrier|mars|avril|mai|juin|juillet|août|aout|septembre|octobre|novembre|décembre|decembre)\s*(\d{4})', text)
    if match:
        day = int(match.group(1))
        month = FRENCH_MONTHS.get(match.group(2), 1)
        year = int(match.group(3))
        return f"{year}-{month:02d}-{day:02d}"
    
    # Format: "06/01/2025" ou "6/1/2025"
    match = re.search(r'(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})', text)
    if match:
        day = int(match.group(1))
        month = int(match.group(2))
        year = int(match.group(3))
        return f"{year}-{month:02d}-{day:02d}"
    
    # Format: "2025-01-06"
    match = re.search(r'(\d{4})[/\-.](\d{1,2})[/\-.](\d{1,2})', text)
    if match:
        year = int(match.group(1))
        month = int(match.group(2))
        day = int(match.group(3))
        return f"{year}-{month:02d}-{day:02d}"
    
    return None

def process_imported_data(df):
    """Traite les données importées avec détection intelligente"""
    try:
        # Debug: afficher les premières lignes
        st.write("**🔍 Analyse du fichier...**")
        
        # Chercher la date dans toutes les cellules
        date_found = None
        header_row = None
        
        for i in range(min(15, len(df))):
            row = df.iloc[i]
            row_str = ' '.join([str(x) for x in row if pd.notna(x)])
            
            # Chercher une date
            if not date_found:
                parsed = parse_date_french(row_str)
                if parsed:
                    date_found = parsed
                    st.success(f"📅 Date trouvée: {format_date(date_found, 'full')}")
            
            # Chercher la ligne d'en-tête - plus flexible
            row_values = [str(x).lower().strip() for x in row if pd.notna(x)]
            
            # Vérifier si c'est une ligne d'en-tête
            has_name_col = any(any(p in v for p in ['joueur', 'nom', 'name']) for v in row_values)
            has_metric_col = any(any(p in v for p in ['poids', 'sommeil', 'motivation', 'hdc', 'bdc', 'charge']) for v in row_values)
            
            if has_name_col and has_metric_col:
                header_row = i
                st.success(f"📋 En-tête trouvé à la ligne {i + 1}")
                break
        
        if not date_found:
            date_found = datetime.now().strftime('%Y-%m-%d')
            st.warning(f"⚠️ Date non trouvée, utilisation de: {format_date(date_found, 'full')}")
        
        if header_row is None:
            # Tentative de détection alternative
            st.warning("⚠️ En-tête standard non trouvé, tentative de détection alternative...")
            
            # Chercher la première ligne avec plusieurs textes non vides
            for i in range(min(15, len(df))):
                row = df.iloc[i]
                non_empty = [str(x).strip() for x in row if pd.notna(x) and str(x).strip()]
                if len(non_empty) >= 3:
                    # Vérifier si ça ressemble à des en-têtes
                    all_text = all(not str(x).replace('.', '').replace(',', '').isdigit() for x in non_empty[:5])
                    if all_text:
                        header_row = i
                        st.info(f"📋 En-tête potentiel détecté à la ligne {i + 1}")
                        break
        
        if header_row is None:
            return {'success': False, 'error': "Impossible de trouver la ligne d'en-tête. Vérifiez que votre fichier contient des colonnes comme 'Joueur', 'Poids', 'Sommeil', etc."}
        
        # Mapper les colonnes
        headers = df.iloc[header_row]
        col_map = {}
        
        st.write("**📊 Colonnes détectées:**")
        for idx, h in enumerate(headers):
            if pd.isna(h):
                continue
            matched_key = find_column_match(str(h), COLUMN_MAPPINGS)
            if matched_key:
                col_map[matched_key] = idx
                st.write(f"  ✓ `{h}` → {matched_key}")
        
        if 'name' not in col_map:
            return {'success': False, 'error': "Colonne 'Joueur' ou 'Nom' non trouvée dans les en-têtes détectés."}
        
        # Extraire les données
        data_rows = df.iloc[header_row + 1:]
        entries = []
        players_created = 0
        
        for _, row in data_rows.iterrows():
            name_idx = col_map.get('name')
            if name_idx is None:
                continue
            
            name = row.iloc[name_idx] if name_idx < len(row) else None
            if pd.isna(name) or not str(name).strip():
                continue
            
            name = str(name).strip()
            
            # Ignorer les lignes qui ressemblent à des en-têtes ou totaux
            if any(x in name.lower() for x in ['total', 'moyenne', 'joueur', 'nom', 'average']):
                continue
            
            # Créer joueur si n'existe pas
            if not any(p['name'] == name for p in st.session_state.players):
                st.session_state.players.append({
                    'id': f"p_{len(st.session_state.players) + 1}_{datetime.now().timestamp():.0f}",
                    'name': name,
                    'position': 'Pilier gauche',
                    'status': 'Apte',
                    'targetWeight': 95
                })
                players_created += 1
            
            entry = {'name': name}
            
            # Extraire valeurs
            for key, idx in col_map.items():
                if key == 'name' or idx is None or idx >= len(row):
                    continue
                
                val = row.iloc[idx]
                
                if key == 'remark':
                    entry[key] = str(val).strip() if pd.notna(val) and str(val).strip() not in ['nan', 'None', ''] else ''
                else:
                    if pd.notna(val):
                        try:
                            # Nettoyer et convertir
                            val_str = str(val).replace(',', '.').replace(' ', '')
                            num = float(val_str)
                            if 0 <= num <= 200:  # Validation basique
                                entry[key] = num
                        except:
                            pass
            
            entries.append(entry)
        
        # Sauvegarder
        if entries:
            st.session_state.data[date_found] = entries
            return {
                'success': True,
                'date': date_found,
                'players': len(st.session_state.players),
                'entries': len(entries),
                'new_players': players_created
            }
        else:
            return {'success': False, 'error': "Aucune donnée valide trouvée dans le fichier."}
        
    except Exception as e:
        return {'success': False, 'error': str(e)}


# ==================== GRAPHIQUES ====================
def create_radar_chart(data1, data2, label1, label2):
    categories = [m['label'] for m in METRICS]
    
    fig = go.Figure()
    
    if data1:
        vals1 = [data1.get(m['key'], 0) or 0 for m in METRICS]
        vals1.append(vals1[0])
        fig.add_trace(go.Scatterpolar(
            r=vals1, 
            theta=categories + [categories[0]], 
            fill='toself', 
            name=label1, 
            line=dict(color='#10b981', width=2),
            fillcolor='rgba(16,185,129,0.3)'
        ))
    
    if data2:
        vals2 = [data2.get(m['key'], 0) or 0 for m in METRICS]
        vals2.append(vals2[0])
        fig.add_trace(go.Scatterpolar(
            r=vals2, 
            theta=categories + [categories[0]], 
            fill='toself', 
            name=label2, 
            line=dict(color='#3b82f6', width=2),
            fillcolor='rgba(59,130,246,0.2)'
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 5], showticklabels=False, gridcolor='#334155'),
            angularaxis=dict(gridcolor='#334155'),
            bgcolor='rgba(15,23,42,0.8)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#94a3b8', size=11),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5, font=dict(size=10)),
        margin=dict(l=60, r=60, t=30, b=50),
        height=300
    )
    return fig

def create_availability_chart():
    avail_data = get_availability_data()
    if not avail_data:
        return None
    
    fig = go.Figure(data=[go.Pie(
        labels=[d['name'] for d in avail_data],
        values=[d['value'] for d in avail_data],
        hole=0.6,
        marker=dict(colors=[d['color'] for d in avail_data], line=dict(color='#0f172a', width=2)),
        textinfo='none',
        hovertemplate='%{label}: %{value}<extra></extra>'
    )])
    
    # Ajouter texte au centre
    total = sum(d['value'] for d in avail_data)
    fig.add_annotation(
        text=f"<b>{total}</b><br><span style='font-size:10px'>joueurs</span>",
        x=0.5, y=0.5, font=dict(size=20, color='white'),
        showarrow=False
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#94a3b8'),
        showlegend=False,
        margin=dict(l=10, r=10, t=10, b=10),
        height=180
    )
    return fig

def create_zscore_chart(data):
    if not data or len(data) < 5:
        return None
    
    df = pd.DataFrame(data)
    df['fmt'] = df['date'].apply(lambda x: format_date(x, 'short'))
    
    settings = st.session_state.settings
    colors = ['#ef4444' if z < settings['zscoreAlert'] else '#f59e0b' if z < settings['zscoreWarning'] else '#10b981' for z in df['zscore']]
    
    fig = go.Figure()
    
    # Zones de référence
    fig.add_hrect(y0=-3, y1=settings['zscoreAlert'], fillcolor="rgba(239,68,68,0.1)", line_width=0)
    fig.add_hrect(y0=settings['zscoreAlert'], y1=settings['zscoreWarning'], fillcolor="rgba(245,158,11,0.1)", line_width=0)
    fig.add_hrect(y0=settings['zscoreWarning'], y1=3, fillcolor="rgba(16,185,129,0.05)", line_width=0)
    
    fig.add_trace(go.Bar(
        x=df['fmt'], 
        y=df['zscore'], 
        marker_color=colors,
        marker_line_width=0,
        hovertemplate='%{x}<br>Z-Score: %{y:.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(15,23,42,0.8)',
        font=dict(color='#94a3b8', size=10),
        margin=dict(l=40, r=20, t=20, b=40),
        height=250,
        xaxis=dict(showgrid=False, tickangle=-45),
        yaxis=dict(showgrid=True, gridcolor='#1e293b', range=[-3, 3], zeroline=True, zerolinecolor='#475569'),
        showlegend=False,
        bargap=0.3
    )
    return fig

def create_weight_chart(player_name, days=30):
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
            chart_data.append({'date': format_date(date), 'weight': pd_data['weight']})
    
    if not chart_data:
        return None
    
    df = pd.DataFrame(chart_data)
    
    fig = go.Figure()
    
    # Zone cible
    fig.add_hrect(y0=target-2, y1=target+2, fillcolor="rgba(16,185,129,0.1)", line_width=0)
    fig.add_hline(y=target, line_dash="dash", line_color="#6b7280", annotation_text="Cible")
    
    fig.add_trace(go.Scatter(
        x=df['date'], 
        y=df['weight'], 
        mode='lines+markers',
        line=dict(color='#10b981', width=3),
        marker=dict(size=8, color='#10b981', line=dict(color='white', width=2)),
        hovertemplate='%{x}<br>Poids: %{y:.1f}kg<extra></extra>'
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(15,23,42,0.8)',
        font=dict(color='#94a3b8', size=10),
        margin=dict(l=40, r=20, t=20, b=40),
        height=220,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#1e293b'),
        showlegend=False
    )
    return fig

def zscore_series(metric='global', group=None, days=30):
    dates = sorted(st.session_state.data.keys())[-days:]
    if len(dates) < 5:
        return []
    
    result = []
    for date in dates:
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
            
            val = get_player_average(d) if metric == 'global' else d.get(metric)
            if val is not None:
                day_values.append(val)
        
        if day_values:
            day_avg = sum(day_values) / len(day_values)
            prev_avgs = [r['value'] for r in result[-14:]]
            zscore = calculate_zscore(day_avg, prev_avgs) if len(prev_avgs) >= 3 else 0
            result.append({'date': date, 'value': day_avg, 'zscore': round(zscore, 2)})
    
    return result


# ==================== FICHE JOUEUR ====================
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
    
    # Header avec sélecteur de date
    col1, col2 = st.columns([3, 1])
    with col1:
        status_class = {'Apte': 'status-apte', 'Blessé': 'status-blesse', 'Réhabilitation': 'status-rehab', 'Réathlétisation': 'status-reath'}.get(player['status'], '')
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:16px;">
            <div style="width:64px;height:64px;border-radius:16px;background:linear-gradient(135deg,#10b981,#0d9488);display:flex;align-items:center;justify-content:center;font-size:28px;font-weight:bold;color:white;box-shadow:0 4px 12px rgba(16,185,129,0.3);">{player['name'][0]}</div>
            <div>
                <div style="font-size:24px;font-weight:bold;color:white;">{player['name']}</div>
                <div style="font-size:13px;color:#94a3b8;margin-bottom:4px;">{player['position']} • {get_player_group(player['position'])} • {get_player_line(player['position'])}</div>
                <span class="status-badge {status_class}">{player['status']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        sel_date = st.selectbox("📅 Date", dates[:30], format_func=lambda x: format_date(x, 'short'), key="modal_date", label_visibility="collapsed")
    
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    
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
        diff_str = f"({'+' if diff_vs_team >= 0 else ''}{diff_vs_team:.2f})" if diff_vs_team else ""
        diff_color = "#10b981" if diff_vs_team and diff_vs_team >= 0 else "#ef4444"
        st.markdown(f"""
        <div class="glass-card">
            <div style="font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:1px;">Moyenne joueur</div>
            <div style="display:flex;align-items:baseline;gap:8px;">
                <span style="font-size:36px;font-weight:bold;color:white;">{avg_str}</span>
                <span style="font-size:20px;color:#64748b;">/5</span>
                <span style="font-size:14px;font-weight:600;color:{diff_color};">{diff_str}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with c2:
        team_str = f"{team_avg['global']:.2f}" if team_avg and team_avg.get('global') else "-"
        st.markdown(f"""
        <div class="glass-card" style="text-align:right;">
            <div style="font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:1px;">Moyenne équipe</div>
            <div style="display:flex;align-items:baseline;gap:8px;justify-content:flex-end;">
                <span style="font-size:36px;font-weight:bold;color:#10b981;">{team_str}</span>
                <span style="font-size:20px;color:#64748b;">/5</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    
    # Métriques du jour
    cols = st.columns(7)
    
    with cols[0]:
        weight_val = pd.get('weight')
        st.markdown(f"""
        <div class="glass-card" style="text-align:center;">
            <div style="font-size:20px;">⚖️</div>
            <div style="font-size:18px;font-weight:bold;color:white;">{f"{weight_val:.1f}" if weight_val else "-"}</div>
            <div style="font-size:9px;color:#64748b;">kg</div>
        </div>
        """, unsafe_allow_html=True)
    
    for i, m in enumerate(METRICS):
        val = pd.get(m['key'])
        color = get_color_for_value(val)
        with cols[i + 1]:
            st.markdown(f"""
            <div class="glass-card" style="text-align:center;">
                <div style="font-size:20px;">{m['icon']}</div>
                <div style="font-size:18px;font-weight:bold;color:{color};">{int(val) if val else "-"}</div>
                <div style="font-size:9px;color:#64748b;">/5</div>
            </div>
            """, unsafe_allow_html=True)
    
    with cols[6]:
        st.markdown(f"""
        <div class="glass-card" style="text-align:center;background:rgba(16,185,129,0.15);border-color:rgba(16,185,129,0.3);">
            <div style="font-size:20px;">⚡</div>
            <div style="font-size:18px;font-weight:bold;color:#10b981;">{f"{avg:.1f}" if avg else "-"}</div>
            <div style="font-size:9px;color:#6ee7b7;">Moy</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### 📊 Radar comparatif")
        compare_type = st.selectbox("Comparer avec", ["Équipe", "Avants", "Trois-quarts"], key="modal_compare", label_visibility="collapsed")
        
        compare_avg = get_team_avg(sel_date, group=None if compare_type == "Équipe" else compare_type)
        player_data = {m['key']: pd.get(m['key'], 0) for m in METRICS}
        fig = create_radar_chart(player_data, compare_avg, player['name'], compare_type)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("##### ⚖️ Évolution poids")
        weight_fig = create_weight_chart(player['name'])
        if weight_fig:
            st.plotly_chart(weight_fig, use_container_width=True)
        else:
            st.info("Pas de données de poids")
    
    # Remarque
    if pd.get('remark'):
        st.markdown(f"""
        <div class="glass-card" style="margin-top:16px;">
            <div style="font-size:12px;color:#64748b;margin-bottom:4px;">💬 Remarque du jour</div>
            <div style="color:white;">{pd['remark']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    
    # Modifier statut
    st.markdown("##### 🔄 Modifier le statut")
    new_status = st.radio("", STATUSES, index=STATUSES.index(player['status']), horizontal=True, key="modal_status", label_visibility="collapsed")
    
    if new_status != player['status']:
        if st.button("💾 Sauvegarder", type="primary", use_container_width=True):
            for p in st.session_state.players:
                if p['id'] == player_id:
                    p['status'] = new_status
            st.success(f"✅ Statut mis à jour: {new_status}")
            st.rerun()


# ==================== PAGES ====================
def page_dashboard():
    st.markdown("# 📊 Dashboard Wellness")
    
    dates = sorted(st.session_state.data.keys(), reverse=True)
    if not dates:
        st.markdown("""
        <div class="premium-card" style="text-align:center;padding:3rem;">
            <div style="font-size:60px;margin-bottom:1rem;">📥</div>
            <h2 style="color:white;margin-bottom:0.5rem;">Bienvenue dans Wellness Tracker !</h2>
            <p style="color:#94a3b8;margin-bottom:1.5rem;">Importez vos données depuis Google Sheets pour commencer le suivi de vos joueurs.</p>
            <p style="color:#64748b;font-size:14px;">👈 Allez dans <b>Import</b> dans le menu latéral</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Sélecteur de date stylisé
    col1, col2 = st.columns([3, 1])
    with col2:
        date_key = st.selectbox("", dates, format_func=lambda x: format_date(x, 'full'), key="dash_date", label_visibility="collapsed")
    
    today_data = st.session_state.data.get(date_key, [])
    team = get_team_avg(date_key)
    
    # Moyenne équipe - Card premium
    if team:
        metrics_html = ''.join([
            f'''<div style="text-align:center;min-width:70px;">
                <div style="font-size:28px;">{m["icon"]}</div>
                <div style="font-size:22px;font-weight:bold;color:white;">{team.get(m["key"], 0):.1f if team.get(m["key"]) else "-"}</div>
                <div style="font-size:10px;color:rgba(255,255,255,0.7);">{m["label"]}</div>
            </div>'''
            for m in METRICS
        ])
        
        global_val = team.get('global')
        global_str = f"{global_val:.2f}" if global_val else "-"
        
        st.markdown(f"""
        <div class="team-avg-card">
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:2rem;position:relative;z-index:1;">
                <div>
                    <div style="color:rgba(255,255,255,0.8);font-size:13px;font-weight:600;text-transform:uppercase;letter-spacing:2px;">⚡ Moyenne Équipe</div>
                    <div style="font-size:4rem;font-weight:800;color:white;line-height:1;">{global_str}<span style="font-size:1.5rem;color:rgba(255,255,255,0.6);">/5</span></div>
                    <div style="color:rgba(255,255,255,0.7);font-size:14px;margin-top:4px;">{team.get('count', 0)} joueurs aujourd'hui</div>
                </div>
                <div style="display:flex;gap:24px;flex-wrap:wrap;">{metrics_html}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Alertes + Disponibilité
    col_alerts, col_avail = st.columns([2, 1])
    
    with col_alerts:
        alerts = get_alerts(date_key)
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">
            <h3 style="margin:0;color:white;">⚠️ Alertes du jour</h3>
            {f'<span style="background:#ef4444;color:white;padding:4px 12px;border-radius:20px;font-size:12px;font-weight:600;">{len(alerts)}</span>' if alerts else ''}
        </div>
        """, unsafe_allow_html=True)
        
        if alerts:
            by_player = {}
            for a in alerts:
                by_player.setdefault(a['player'], []).append(a)
            
            for player_name, player_alerts in list(by_player.items())[:5]:
                msgs = " • ".join([a['message'] for a in player_alerts])
                has_critical = any(a['type'] == 'critical' for a in player_alerts)
                card_class = "alert-card" if has_critical else "alert-card warning"
                badge = "Critique" if has_critical else "Attention"
                
                st.markdown(f"""
                <div class="{card_class}">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span style="font-weight:600;color:white;font-size:14px;">{player_name}</span>
                        <span style="font-size:10px;font-weight:600;text-transform:uppercase;">{badge}</span>
                    </div>
                    <div style="font-size:12px;margin-top:4px;opacity:0.9;">{msgs}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="glass-card" style="text-align:center;padding:2rem;">
                <div style="font-size:40px;margin-bottom:8px;">✅</div>
                <div style="color:#10b981;font-weight:600;">Aucune alerte</div>
                <div style="color:#64748b;font-size:12px;">Tous les joueurs sont en forme !</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col_avail:
        st.markdown("<h3 style='color:white;margin-bottom:16px;'>👥 Disponibilité</h3>", unsafe_allow_html=True)
        
        avail_data = get_availability_data()
        if avail_data:
            fig = create_availability_chart()
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            
            legend_html = " ".join([
                f'<span style="display:inline-flex;align-items:center;margin-right:12px;"><span style="width:10px;height:10px;border-radius:50%;background:{d["color"]};margin-right:6px;"></span><span style="color:#94a3b8;font-size:11px;">{d["name"]}: <b style="color:white">{d["value"]}</b></span></span>'
                for d in avail_data
            ])
            st.markdown(f'<div style="text-align:center;">{legend_html}</div>', unsafe_allow_html=True)
    
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    
    # Filtres
    st.markdown("<h3 style='color:white;'>📋 Vue équipe</h3>", unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns([1.5, 1.5, 1.5, 1])
    with c1:
        sort_by = st.selectbox("Trier", ["Nom A→Z", "🚨 Alertes", "📉 Moyenne ↑", "👥 Groupe"], key="sort", label_visibility="collapsed")
    with c2:
        filter_group = st.selectbox("Groupe", ["Tous", "Avants", "Trois-quarts"], key="fg", label_visibility="collapsed")
    with c3:
        filter_line = st.selectbox("Ligne", ["Toutes"] + ALL_LINES, key="fl", label_visibility="collapsed")
    with c4:
        show_issues = st.checkbox("⚠️ Problèmes", key="si")
    
    # Tableau des joueurs
    rows = []
    player_ids = {}
    
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
        
        rows.append({
            'name': d['name'],
            'position': p['position'],
            'group': get_player_group(p['position']),
            'status': p['status'],
            'weight': d.get('weight'),
            'metrics': {m['key']: d.get(m['key']) for m in METRICS},
            'avg': avg,
            'diff': diff_vs_team,
            'remark': d.get('remark', ''),
            'has_issue': has_issue
        })
    
    # Tri
    if sort_by == "🚨 Alertes":
        rows.sort(key=lambda x: (not x['has_issue'], x['name']))
    elif sort_by == "📉 Moyenne ↑":
        rows.sort(key=lambda x: x['avg'] or 5)
    elif sort_by == "👥 Groupe":
        rows.sort(key=lambda x: (x['group'], x['name']))
    else:
        rows.sort(key=lambda x: x['name'])
    
    # Affichage des joueurs
    if rows:
        st.markdown(f"<div style='color:#64748b;font-size:12px;margin-bottom:12px;'>{len(rows)} joueurs</div>", unsafe_allow_html=True)
        
        for row in rows:
            # Métriques HTML
            metrics_badges = ""
            for m in METRICS:
                val = row['metrics'].get(m['key'])
                color = get_color_for_value(val)
                metrics_badges += f'<span class="metric-badge" style="background:{color};">{int(val) if val else "-"}</span>'
            
            # Moyenne
            avg_color = get_color_for_value(row['avg'])
            avg_str = f"{row['avg']:.1f}" if row['avg'] else "-"
            
            # Diff vs équipe
            diff_str = ""
            if row['diff'] is not None:
                diff_color = "#10b981" if row['diff'] >= 0 else "#ef4444"
                diff_str = f'<span style="color:{diff_color};font-size:11px;font-weight:600;">{("+" if row["diff"] >= 0 else "")}{row["diff"]:.1f}</span>'
            
            # Status
            status_class = {'Apte': 'status-apte', 'Blessé': 'status-blesse', 'Réhabilitation': 'status-rehab', 'Réathlétisation': 'status-reath'}.get(row['status'], '')
            group_abbr = "Av" if row['group'] == "Avants" else "3/4"
            
            col1, col2 = st.columns([5, 1])
            
            with col1:
                st.markdown(f"""
                <div class="player-row">
                    <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
                        <div style="display:flex;align-items:center;gap:12px;min-width:200px;">
                            <div style="width:40px;height:40px;border-radius:10px;background:linear-gradient(135deg,#3b82f6,#1d4ed8);display:flex;align-items:center;justify-content:center;font-weight:bold;color:white;">{row['name'][0]}</div>
                            <div>
                                <div style="font-weight:600;color:white;">{row['name']}</div>
                                <div style="font-size:11px;color:#64748b;">{row['position']} ({group_abbr})</div>
                            </div>
                        </div>
                        <span class="status-badge {status_class}">{row['status']}</span>
                        <div style="display:flex;align-items:center;gap:4px;">
                            <span style="color:#64748b;font-size:12px;min-width:45px;">{f"{row['weight']:.1f}" if row['weight'] else "-"} kg</span>
                            {metrics_badges}
                            <span class="metric-badge" style="background:{avg_color};margin-left:8px;">{avg_str}</span>
                            <span style="min-width:40px;text-align:center;">{diff_str}</span>
                        </div>
                        <div style="color:#64748b;font-size:11px;max-width:150px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{row['remark'][:30] if row['remark'] else ''}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button("👁️", key=f"btn_{row['name']}", use_container_width=True):
                    show_player_modal(player_ids[row['name']])
    else:
        st.info("Aucun joueur ne correspond aux filtres.")
    
    st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Tendance Z-Score")
        mc1, mc2, mc3 = st.columns(3)
        with mc1:
            zmetric = st.selectbox("Métrique", ['global'] + [m['key'] for m in METRICS],
                format_func=lambda x: "⚡ Global" if x == 'global' else next((f"{m['icon']} {m['label']}" for m in METRICS if m['key'] == x), x), key="zm")
        with mc2:
            zgroup = st.selectbox("Groupe", ["Équipe", "Avants", "Trois-quarts"], key="zg")
        with mc3:
            zdays = st.selectbox("Période", [7, 14, 30, 60], index=2, key="zd")
        
        zdata = zscore_series(metric=zmetric, group=None if zgroup == "Équipe" else zgroup, days=zdays)
        fig = create_zscore_chart(zdata)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
            st.caption("🟢 Normal | 🟡 Attention (< -1) | 🔴 Alerte (< -1.5)")
        else:
            st.info("Pas assez de données (min 5 jours)")
    
    with col2:
        st.markdown("### 📊 Comparaison Radar")
        rc1, rc2 = st.columns(2)
        with rc1:
            cmp1 = st.selectbox("", ["Équipe", "Avants", "Trois-quarts"], key="r1", label_visibility="collapsed")
        with rc2:
            cmp2 = st.selectbox("", ["Équipe", "Avants", "Trois-quarts"], index=1, key="r2", label_visibility="collapsed")
        
        d1 = get_team_avg(date_key, group=None if cmp1 == "Équipe" else cmp1)
        d2 = get_team_avg(date_key, group=None if cmp2 == "Équipe" else cmp2)
        
        if d1 or d2:
            st.plotly_chart(create_radar_chart(d1, d2, cmp1, cmp2), use_container_width=True)


def page_import():
    st.markdown("# 📥 Import / Export")
    
    # Google Sheets
    st.markdown("""
    <div class="premium-card">
        <h3 style="color:white;margin-bottom:16px;">📊 Importer depuis Google Sheets</h3>
    """, unsafe_allow_html=True)
    
    url = st.text_input(
        "URL du Google Sheet",
        value="https://docs.google.com/spreadsheets/d/1Esm3NnED51jFpTs-oSjIdVybH51BSEcjhWOQhP1P3zI/edit?usp=sharing",
        help="Collez l'URL complète de votre Google Sheet (doit être partagé en lecture)"
    )
    
    sheet_name = st.text_input("Nom de l'onglet", value="Bien-être", help="Nom exact de l'onglet contenant les données")
    
    if st.button("📥 Importer depuis Google Sheets", type="primary", use_container_width=True):
        try:
            match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
            if not match:
                st.error("❌ URL invalide")
                return
            
            doc_id = match.group(1)
            encoded_sheet = urllib.parse.quote(sheet_name)
            csv_url = f"https://docs.google.com/spreadsheets/d/{doc_id}/gviz/tq?tqx=out:csv&sheet={encoded_sheet}"
            
            with st.spinner("📡 Téléchargement..."):
                df = pd.read_csv(csv_url, header=None)
            
            st.success(f"✅ {len(df)} lignes téléchargées")
            
            with st.spinner("🔄 Traitement des données..."):
                result = process_imported_data(df)
            
            if result['success']:
                st.balloons()
                st.success(f"""
                ✅ **Import réussi !**
                - 📅 Date: {format_date(result['date'], 'full')}
                - 👥 {result['players']} joueurs ({result['new_players']} nouveaux)
                - 📊 {result['entries']} entrées
                """)
            else:
                st.error(f"❌ {result['error']}")
                
        except Exception as e:
            st.error(f"❌ Erreur: {str(e)}")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    
    # Excel
    st.markdown("""
    <div class="premium-card">
        <h3 style="color:white;margin-bottom:16px;">📄 Importer un fichier Excel</h3>
    """, unsafe_allow_html=True)
    
    uploaded = st.file_uploader("", type=['xlsx', 'xls', 'csv'], label_visibility="collapsed")
    if uploaded:
        try:
            if uploaded.name.endswith('.csv'):
                df = pd.read_csv(uploaded, header=None)
            else:
                df = pd.read_excel(uploaded, header=None)
            
            st.info(f"📊 {len(df)} lignes trouvées")
            
            if st.button("📥 Traiter le fichier", use_container_width=True):
                with st.spinner("Traitement..."):
                    result = process_imported_data(df)
                
                if result['success']:
                    st.balloons()
                    st.success(f"✅ Import réussi ! {result['entries']} entrées ajoutées.")
                else:
                    st.error(f"❌ {result['error']}")
        except Exception as e:
            st.error(f"❌ Erreur: {e}")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    
    # Export
    if st.session_state.data:
        st.markdown("""
        <div class="premium-card">
            <h3 style="color:white;margin-bottom:16px;">📤 Exporter les données</h3>
        """, unsafe_allow_html=True)
        
        export_rows = []
        for date, entries in st.session_state.data.items():
            for e in entries:
                export_rows.append({
                    'Date': date,
                    'Joueur': e.get('name'),
                    'Poids': e.get('weight'),
                    **{m['label']: e.get(m['key']) for m in METRICS},
                    'Remarque': e.get('remark')
                })
        
        if export_rows:
            export_df = pd.DataFrame(export_rows)
            csv = export_df.to_csv(index=False).encode('utf-8')
            
            col1, col2 = st.columns(2)
            with col1:
                st.download_button("📥 Télécharger CSV", csv, "wellness_export.csv", "text/csv", use_container_width=True)
            with col2:
                st.metric("Total", f"{len(export_rows)} entrées")
        
        st.markdown("</div>", unsafe_allow_html=True)


def page_effectif():
    st.markdown("# 👥 Effectif & Comparaisons")
    
    if not st.session_state.players:
        st.warning("Aucun joueur. Importez des données d'abord.")
        return
    
    tabs = st.tabs(["📋 Liste", "📊 Comparer", "📈 Évolution", "👥 Groupes"])
    
    with tabs[0]:
        search = st.text_input("🔍 Rechercher un joueur", key="search_eff")
        
        players = st.session_state.players
        if search:
            players = [p for p in players if search.lower() in p['name'].lower()]
        
        dates = sorted(st.session_state.data.keys(), reverse=True)
        latest_date = dates[0] if dates else None
        
        for p in sorted(players, key=lambda x: x['name']):
            pd_data = {}
            if latest_date:
                today_data = st.session_state.data.get(latest_date, [])
                pd_data = next((d for d in today_data if d['name'] == p['name']), {})
            
            avg = get_player_average(pd_data)
            status_class = {'Apte': 'status-apte', 'Blessé': 'status-blesse', 'Réhabilitation': 'status-rehab', 'Réathlétisation': 'status-reath'}.get(p['status'], '')
            
            metrics_badges = ""
            for m in METRICS:
                val = pd_data.get(m['key'])
                color = get_color_for_value(val)
                metrics_badges += f'<span class="metric-badge" style="background:{color};">{int(val) if val else "-"}</span>'
            
            col1, col2 = st.columns([5, 1])
            
            with col1:
                st.markdown(f"""
                <div class="player-row">
                    <div style="display:flex;align-items:center;justify-content:space-between;gap:16px;">
                        <div style="display:flex;align-items:center;gap:12px;">
                            <div style="width:44px;height:44px;border-radius:12px;background:linear-gradient(135deg,#10b981,#059669);display:flex;align-items:center;justify-content:center;font-weight:bold;color:white;font-size:18px;">{p['name'][0]}</div>
                            <div>
                                <div style="font-weight:600;color:white;font-size:15px;">{p['name']}</div>
                                <div style="font-size:12px;color:#64748b;">{p['position']} • {get_player_group(p['position'])}</div>
                            </div>
                        </div>
                        <span class="status-badge {status_class}">{p['status']}</span>
                        <div style="display:flex;gap:4px;">{metrics_badges}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button("👁️", key=f"view_eff_{p['id']}", use_container_width=True):
                    show_player_modal(p['id'])
    
    with tabs[1]:
        st.markdown("### 📊 Comparer des joueurs")
        
        player_names = [p['name'] for p in st.session_state.players]
        
        col1, col2 = st.columns(2)
        with col1:
            sel1 = st.multiselect("Sélectionner 2-4 joueurs", player_names, max_selections=4, key="cmp_players")
        with col2:
            dates = sorted(st.session_state.data.keys(), reverse=True)
            cmp_date = st.selectbox("Date", dates[:30] if dates else [], format_func=lambda x: format_date(x, 'short'), key="cmp_date") if dates else None
        
        if len(sel1) >= 2 and cmp_date:
            today_data = st.session_state.data.get(cmp_date, [])
            
            fig = go.Figure()
            colors = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444']
            categories = [m['label'] for m in METRICS]
            
            for i, name in enumerate(sel1):
                pd_data = next((d for d in today_data if d['name'] == name), {})
                vals = [pd_data.get(m['key'], 0) or 0 for m in METRICS]
                vals.append(vals[0])
                
                fig.add_trace(go.Scatterpolar(
                    r=vals,
                    theta=categories + [categories[0]],
                    fill='toself',
                    name=name,
                    line=dict(color=colors[i % len(colors)], width=2),
                    fillcolor=f'rgba{tuple(int(colors[i % len(colors)].lstrip("#")[j:j+2], 16) for j in (0, 2, 4)) + (0.2,)}'
                ))
            
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 5]), bgcolor='rgba(15,23,42,0.8)'),
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#94a3b8'),
                height=450
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with tabs[2]:
        st.markdown("### 📈 Évolution sur période")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            sel_player = st.selectbox("Joueur", [p['name'] for p in st.session_state.players], key="evol_player")
        with col2:
            period = st.selectbox("Période", [7, 14, 30, 60], index=2, key="evol_days")
        with col3:
            sel_metric = st.selectbox("Métrique", ['global'] + [m['key'] for m in METRICS],
                format_func=lambda x: "⚡ Global" if x == 'global' else next((f"{m['icon']} {m['label']}" for m in METRICS if m['key'] == x), x), key="evol_metric")
        
        if sel_player:
            history = get_player_history(sel_player, period)
            if history:
                chart_data = [{'date': format_date(h['date']), 'value': h['avg'] if sel_metric == 'global' else h.get(sel_metric)}
                              for h in history if (h['avg'] if sel_metric == 'global' else h.get(sel_metric)) is not None]
                
                if chart_data:
                    df = pd.DataFrame(chart_data)
                    fig = px.line(df, x='date', y='value', markers=True)
                    fig.update_traces(line_color='#10b981', line_width=3, marker=dict(size=8))
                    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(15,23,42,0.8)',
                                      font=dict(color='#94a3b8'), height=350,
                                      xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#1e293b'))
                    st.plotly_chart(fig, use_container_width=True)
    
    with tabs[3]:
        st.markdown("### 👥 Vue par groupes")
        
        dates = sorted(st.session_state.data.keys(), reverse=True)
        if dates:
            grp_date = st.selectbox("Date", dates[:30], format_func=lambda x: format_date(x, 'short'), key="grp_date")
            
            for group_name in ['Avants', 'Trois-quarts']:
                grp_avg = get_team_avg(grp_date, group=group_name)
                if grp_avg:
                    global_str = f"{grp_avg.get('global'):.2f}" if grp_avg.get('global') else "-"
                    st.markdown(f"#### {group_name} - Moyenne: **{global_str}/5**")
                    
                    for line_name in RUGBY_POSITIONS[group_name].keys():
                        line_avg = get_team_avg(grp_date, line=line_name)
                        if line_avg:
                            line_str = f"{line_avg.get('global'):.2f}" if line_avg.get('global') else "-"
                            st.markdown(f"• **{line_name}**: {line_str}/5 ({line_avg.get('count', 0)} joueurs)")


def page_infirmerie():
    st.markdown("# 🏥 Infirmerie")
    
    # Stats de disponibilité
    status_counts = {}
    for p in st.session_state.players:
        s = p.get('status', 'Apte')
        status_counts[s] = status_counts.get(s, 0) + 1
    
    cols = st.columns(4)
    status_colors = {'Apte': '#10b981', 'Blessé': '#ef4444', 'Réhabilitation': '#f59e0b', 'Réathlétisation': '#3b82f6'}
    
    for i, status in enumerate(STATUSES):
        count = status_counts.get(status, 0)
        with cols[i]:
            color = status_colors.get(status, '#64748b')
            selected = st.session_state.status_filter == status
            if st.button(f"{status}\n**{count}**", key=f"filter_{status}", use_container_width=True,
                        type="primary" if selected else "secondary"):
                st.session_state.status_filter = status if not selected else None
                st.rerun()
    
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    
    current_filter = st.session_state.status_filter
    filtered_players = [p for p in st.session_state.players if not current_filter or p.get('status') == current_filter]
    
    if current_filter:
        st.info(f"Filtré par: **{current_filter}** ({len(filtered_players)} joueurs)")
    
    for p in filtered_players:
        col1, col2, col3 = st.columns([3, 2, 2])
        
        with col1:
            st.markdown(f"**{p['name']}** - {p['position']}")
        
        with col2:
            new_status = st.selectbox("", STATUSES, index=STATUSES.index(p.get('status', 'Apte')),
                                      key=f"status_{p['id']}", label_visibility="collapsed")
            if new_status != p.get('status'):
                for player in st.session_state.players:
                    if player['id'] == p['id']:
                        player['status'] = new_status
                st.rerun()
        
        with col3:
            if p.get('status') != 'Apte':
                if st.button("➕ Blessure", key=f"inj_{p['id']}"):
                    st.session_state[f'show_injury_{p["id"]}'] = True
        
        if st.session_state.get(f'show_injury_{p["id"]}'):
            with st.form(f'injury_form_{p["id"]}'):
                ic1, ic2 = st.columns(2)
                with ic1:
                    zone = st.selectbox("Zone", list(INJURY_ZONES.keys()))
                with ic2:
                    grade = st.selectbox("Grade", [1, 2, 3])
                
                circ = st.selectbox("Circonstance", CIRCUMSTANCES)
                duration = INJURY_ZONES[zone].get(grade, 14)
                st.info(f"⏱️ Durée estimée: {duration} jours")
                
                if st.form_submit_button("💾 Enregistrer"):
                    st.session_state.injuries.append({
                        'id': f"i_{len(st.session_state.injuries)}",
                        'playerId': p['id'],
                        'playerName': p['name'],
                        'zone': zone,
                        'grade': grade,
                        'circumstance': circ,
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'returnDate': (datetime.now() + timedelta(days=duration)).strftime('%Y-%m-%d'),
                        'status': 'Active'
                    })
                    st.session_state[f'show_injury_{p["id"]}'] = False
                    st.rerun()
        
        st.markdown("---")
    
    # Blessures actives
    st.markdown("### 🩹 Blessures actives")
    active_injuries = [i for i in st.session_state.injuries if i.get('status') == 'Active']
    
    if active_injuries:
        for inj in active_injuries:
            days_remaining = (datetime.strptime(inj['returnDate'], '%Y-%m-%d') - datetime.now()).days
            days_total = INJURY_ZONES[inj['zone']].get(inj['grade'], 14)
            progress = max(0, min(100, ((days_total - max(0, days_remaining)) / days_total) * 100))
            
            col1, col2, col3 = st.columns([3, 4, 2])
            with col1:
                st.markdown(f"**{inj['playerName']}**<br>{INJURY_ZONES[inj['zone']]['icon']} {inj['zone']} (Grade {inj['grade']})", unsafe_allow_html=True)
            with col2:
                st.progress(progress / 100)
                st.caption(f"{max(0, days_remaining)} jours restants")
            with col3:
                if st.button("✅ Guéri", key=f"heal_{inj['id']}"):
                    for injury in st.session_state.injuries:
                        if injury['id'] == inj['id']:
                            injury['status'] = 'Healed'
                    st.rerun()
    else:
        st.success("✅ Aucune blessure active")


def page_joueurs():
    st.markdown("# 👤 Gestion des joueurs")
    
    # Ajouter
    with st.expander("➕ Ajouter un joueur", expanded=False):
        with st.form("add_player"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Nom")
                position = st.selectbox("Poste", ALL_POSITIONS)
            with col2:
                weight = st.number_input("Poids forme (kg)", value=90.0, step=0.5)
                status = st.selectbox("Statut", STATUSES)
            
            if st.form_submit_button("➕ Ajouter", use_container_width=True):
                if name:
                    st.session_state.players.append({
                        'id': f"p_{len(st.session_state.players)}_{datetime.now().timestamp():.0f}",
                        'name': name, 'position': position, 'targetWeight': weight, 'status': status
                    })
                    st.success(f"✅ {name} ajouté !")
                    st.rerun()
    
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    
    # Liste
    for p in sorted(st.session_state.players, key=lambda x: x['name']):
        col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 0.5])
        
        with col1:
            st.write(f"**{p['name']}**")
        with col2:
            new_pos = st.selectbox("", ALL_POSITIONS,
                index=ALL_POSITIONS.index(p['position']) if p['position'] in ALL_POSITIONS else 0,
                key=f"pos_{p['id']}", label_visibility="collapsed")
            if new_pos != p['position']:
                for player in st.session_state.players:
                    if player['id'] == p['id']:
                        player['position'] = new_pos
        with col3:
            new_weight = st.number_input("", value=float(p.get('targetWeight', 90)), step=0.5,
                key=f"weight_{p['id']}", label_visibility="collapsed")
            if new_weight != p.get('targetWeight'):
                for player in st.session_state.players:
                    if player['id'] == p['id']:
                        player['targetWeight'] = new_weight
        with col4:
            new_status = st.selectbox("", STATUSES, index=STATUSES.index(p.get('status', 'Apte')),
                key=f"st_{p['id']}", label_visibility="collapsed")
            if new_status != p.get('status'):
                for player in st.session_state.players:
                    if player['id'] == p['id']:
                        player['status'] = new_status
        with col5:
            if st.button("🗑️", key=f"del_{p['id']}"):
                st.session_state.players = [x for x in st.session_state.players if x['id'] != p['id']]
                st.rerun()


def page_parametres():
    st.markdown("# ⚙️ Paramètres")
    
    st.markdown("### 🚨 Seuils d'alerte")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.session_state.settings['lowValueThreshold'] = st.number_input(
            "Valeur basse", value=float(st.session_state.settings['lowValueThreshold']),
            min_value=1.0, max_value=5.0, step=0.5, help="Alerte si métrique ≤ ce seuil")
    with col2:
        st.session_state.settings['variationThreshold'] = st.number_input(
            "Variation", value=float(st.session_state.settings['variationThreshold']),
            min_value=0.5, max_value=3.0, step=0.5)
    with col3:
        st.session_state.settings['weightThreshold'] = st.number_input(
            "Poids (kg)", value=float(st.session_state.settings['weightThreshold']),
            min_value=1.0, max_value=5.0, step=0.5)
    
    st.markdown("### 📈 Z-Score")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.session_state.settings['zscoreDays'] = st.number_input(
            "Jours calcul", value=int(st.session_state.settings['zscoreDays']),
            min_value=7, max_value=60)
    with col2:
        st.session_state.settings['zscoreWarning'] = st.number_input(
            "Seuil attention", value=float(st.session_state.settings['zscoreWarning']),
            min_value=-3.0, max_value=0.0, step=0.5)
    with col3:
        st.session_state.settings['zscoreAlert'] = st.number_input(
            "Seuil alerte", value=float(st.session_state.settings['zscoreAlert']),
            min_value=-3.0, max_value=0.0, step=0.5)
    
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Réinitialiser", use_container_width=True):
            st.session_state.settings = DEFAULT_SETTINGS.copy()
            st.success("✅ Paramètres réinitialisés")
    with col2:
        if st.button("🗑️ Effacer données", type="primary", use_container_width=True):
            st.session_state.data = {}
            st.session_state.players = []
            st.session_state.injuries = []
            st.success("✅ Données effacées")
            st.rerun()


# ==================== MAIN ====================
def main():
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;padding:1rem 0;">
            <div style="font-size:40px;margin-bottom:8px;">🏉</div>
            <div style="font-size:18px;font-weight:bold;color:white;">Wellness Tracker</div>
            <div style="font-size:11px;color:#64748b;">Rugby Performance</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        
        page = st.radio("", ["📊 Dashboard", "📥 Import", "👥 Effectif", "🏥 Infirmerie", "👤 Joueurs", "⚙️ Paramètres"],
                       label_visibility="collapsed")
        
        st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
        
        dates = sorted(st.session_state.data.keys(), reverse=True)
        if dates:
            alerts = get_alerts(dates[0])
            if alerts:
                st.markdown(f"""
                <div style="background:rgba(239,68,68,0.15);border:1px solid rgba(239,68,68,0.3);border-radius:8px;padding:12px;text-align:center;">
                    <div style="font-size:24px;">🚨</div>
                    <div style="color:#f87171;font-weight:600;">{len(alerts)} alertes</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="color:#64748b;font-size:11px;">
            <div>📊 {len(dates)} jours de données</div>
            <div>👥 {len(st.session_state.players)} joueurs</div>
            <div>🏥 {len([i for i in st.session_state.injuries if i.get('status') == 'Active'])} blessures actives</div>
        </div>
        """, unsafe_allow_html=True)
    
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
