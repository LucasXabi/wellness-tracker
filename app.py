"""
🏉 Rugby Wellness Tracker - Version Ultra Premium FIXED
Application Streamlit complète avec parsing amélioré pour Google Sheets
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
import json
import os
import requests

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
    
    /* Cards premium avec glassmorphism */
    .premium-card {
        background: linear-gradient(145deg, #1e293b, #0f172a);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    
    .premium-card:hover {
        border-color: rgba(99, 102, 241, 0.4);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
    }
    
    .glass-card {
        background: rgba(30, 41, 59, 0.8);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(148, 163, 184, 0.1);
        border-radius: 12px;
        padding: 1rem;
        transition: all 0.2s ease;
    }
    
    .glass-card:hover {
        background: rgba(30, 41, 59, 0.95);
        border-color: rgba(148, 163, 184, 0.2);
    }
    
    /* Team average card - Hero section */
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
        pointer-events: none;
    }
    
    .team-avg-card::after {
        content: '';
        position: absolute;
        bottom: -30%;
        left: -30%;
        width: 60%;
        height: 60%;
        background: radial-gradient(circle, rgba(255,255,255,0.05) 0%, transparent 70%);
        pointer-events: none;
    }
    
    /* Metric badges améliorés */
    .metric-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 38px;
        height: 38px;
        border-radius: 10px;
        font-size: 14px;
        font-weight: 700;
        color: white;
        margin: 2px;
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }
    
    .metric-badge:hover {
        transform: scale(1.15) translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    
    /* Alert cards avec animations */
    .alert-card {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(239, 68, 68, 0.05));
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-left: 4px solid #ef4444;
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 8px;
        transition: all 0.2s ease;
    }
    
    .alert-card:hover {
        transform: translateX(4px);
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.2);
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(239, 68, 68, 0.1));
    }
    
    .alert-card.warning {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(245, 158, 11, 0.05));
        border-color: rgba(245, 158, 11, 0.3);
        border-left-color: #f59e0b;
    }
    
    .alert-card.warning:hover {
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.2);
    }
    
    /* Player row avec effets */
    .player-row {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(71, 85, 105, 0.3);
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 8px;
        transition: all 0.25s ease;
        cursor: pointer;
    }
    
    .player-row:hover {
        background: rgba(51, 65, 85, 0.8);
        border-color: rgba(99, 102, 241, 0.5);
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.25);
    }
    
    .player-row.has-alert {
        border-left: 3px solid #ef4444;
    }
    
    /* Status badges premium */
    .status-badge {
        display: inline-block;
        padding: 5px 14px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        transition: all 0.2s ease;
    }
    
    .status-badge:hover {
        transform: scale(1.05);
    }
    
    .status-apte { 
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.3), rgba(16, 185, 129, 0.1)); 
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .status-blesse { 
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.3), rgba(239, 68, 68, 0.1)); 
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    .status-rehab { 
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.3), rgba(245, 158, 11, 0.1)); 
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    .status-reath { 
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.3), rgba(59, 130, 246, 0.1)); 
        color: #60a5fa;
        border: 1px solid rgba(59, 130, 246, 0.3);
    }
    
    /* Sidebar améliorée */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    }
    
    [data-testid="stSidebar"] .stRadio > label {
        background: transparent;
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 4px;
        transition: all 0.2s ease;
    }
    
    [data-testid="stSidebar"] .stRadio > label:hover {
        background: rgba(99, 102, 241, 0.1);
    }
    
    /* Buttons premium */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.2s ease;
        border: none;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6366f1, #4f46e5);
    }
    
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #818cf8, #6366f1);
    }
    
    /* Big numbers */
    .big-number {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #fff, #94a3b8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1;
    }
    
    /* Calendar days */
    .calendar-day {
        width: 100%;
        aspect-ratio: 1;
        border-radius: 8px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        font-size: 11px;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    
    .calendar-day:hover {
        transform: scale(1.1);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    }
    
    /* Avatar avec gradient */
    .player-avatar {
        width: 44px;
        height: 44px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        color: white;
        font-size: 18px;
        transition: all 0.2s ease;
    }
    
    .player-avatar:hover {
        transform: scale(1.1);
    }
    
    .avatar-gradient-1 { background: linear-gradient(135deg, #10b981, #059669); }
    .avatar-gradient-2 { background: linear-gradient(135deg, #3b82f6, #1d4ed8); }
    .avatar-gradient-3 { background: linear-gradient(135deg, #8b5cf6, #6d28d9); }
    .avatar-gradient-4 { background: linear-gradient(135deg, #f59e0b, #d97706); }
    .avatar-gradient-5 { background: linear-gradient(135deg, #ef4444, #dc2626); }
    
    /* Progress bar custom */
    .custom-progress {
        height: 8px;
        background: rgba(71, 85, 105, 0.3);
        border-radius: 4px;
        overflow: hidden;
    }
    
    .custom-progress-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 0.5s ease;
    }
    
    /* Stat card */
    .stat-card {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(71, 85, 105, 0.2);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        transition: all 0.2s ease;
    }
    
    .stat-card:hover {
        background: rgba(30, 41, 59, 0.9);
        transform: translateY(-2px);
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 16px;
    }
    
    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Animations */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .pulse { animation: pulse 2s infinite; }
    .slide-in { animation: slideIn 0.3s ease; }
    
    /* Scrollbar custom */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(15, 23, 42, 0.5);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(99, 102, 241, 0.5);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(99, 102, 241, 0.7);
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

FRENCH_DAYS = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']

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


# ==================== SAUVEGARDE / CHARGEMENT DONNÉES ====================
DATA_FILE = "wellness_data.json"

def save_data_to_file():
    """Sauvegarde les données dans un fichier JSON"""
    try:
        data_to_save = {
            'players': st.session_state.players,
            'data': st.session_state.data,
            'injuries': st.session_state.injuries,
            'settings': {k: v for k, v in st.session_state.settings.items() if not k.startswith('cloud_')},
            'saved_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)
        st.session_state.last_save_time = datetime.now()
        
        # Auto-save to cloud
        save_to_cloud()
        
        return True, f"Données sauvegardées ({len(st.session_state.players)} joueurs, {len(st.session_state.data)} jours)"
    except Exception as e:
        return False, f"Erreur: {str(e)}"

def load_data_from_file():
    """Charge les données depuis un fichier JSON"""
    try:
        if not os.path.exists(DATA_FILE):
            return False, "Aucune sauvegarde trouvée"
        
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            loaded = json.load(f)
        
        st.session_state.players = loaded.get('players', [])
        st.session_state.data = loaded.get('data', {})
        st.session_state.injuries = loaded.get('injuries', [])
        if 'settings' in loaded:
            st.session_state.settings.update(loaded['settings'])
        
        saved_at = loaded.get('saved_at', 'inconnue')
        return True, f"Données chargées ({len(st.session_state.players)} joueurs, {len(st.session_state.data)} jours) - Sauvegarde du {saved_at}"
    except Exception as e:
        return False, f"Erreur: {str(e)}"

def export_data_to_json():
    """Exporte les données en JSON pour téléchargement"""
    data_to_export = {
        'players': st.session_state.players,
        'data': st.session_state.data,
        'injuries': st.session_state.injuries,
        'settings': {k: v for k, v in st.session_state.settings.items() if not k.startswith('cloud_')},
        'exported_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    return json.dumps(data_to_export, ensure_ascii=False, indent=2)

def import_data_from_json(json_content):
    """Importe les données depuis un fichier JSON uploadé"""
    try:
        loaded = json.loads(json_content)
        st.session_state.players = loaded.get('players', [])
        st.session_state.data = loaded.get('data', {})
        st.session_state.injuries = loaded.get('injuries', [])
        if 'settings' in loaded:
            for k, v in loaded['settings'].items():
                if not k.startswith('cloud_'):
                    st.session_state.settings[k] = v
        # Sauvegarder immédiatement après import
        save_data_to_file()
        return True, f"Import réussi: {len(st.session_state.players)} joueurs, {len(st.session_state.data)} jours"
    except Exception as e:
        return False, f"Erreur: {str(e)}"

# ==================== CLOUD STORAGE AUTOMATIQUE ====================
# Utilise JSONBlob - gratuit, pas d'inscription, jamais de pause !
# L'ID est stocké dans Streamlit Secrets pour survivre aux redémarrages
CLOUD_ID_FILE = "cloud_id.txt"

def get_cloud_id():
    """Récupère l'ID cloud (priorité: Secrets > Session > Fichier)"""
    # 1. Priorité maximale : Streamlit Secrets (survit aux redémarrages)
    try:
        if hasattr(st, 'secrets') and 'CLOUD_BLOB_ID' in st.secrets:
            blob_id = st.secrets['CLOUD_BLOB_ID']
            if blob_id:
                st.session_state.settings['cloud_blob_id'] = blob_id
                return blob_id
    except:
        pass
    
    # 2. Session state
    if 'cloud_blob_id' in st.session_state.settings and st.session_state.settings['cloud_blob_id']:
        return st.session_state.settings['cloud_blob_id']
    
    # 3. Fichier local (peut être perdu au redémarrage)
    if os.path.exists(CLOUD_ID_FILE):
        try:
            with open(CLOUD_ID_FILE, 'r') as f:
                blob_id = f.read().strip()
                if blob_id:
                    st.session_state.settings['cloud_blob_id'] = blob_id
                    return blob_id
        except:
            pass
    
    return None

def save_cloud_id(blob_id):
    """Sauvegarde l'ID cloud"""
    st.session_state.settings['cloud_blob_id'] = blob_id
    try:
        with open(CLOUD_ID_FILE, 'w') as f:
            f.write(blob_id)
    except:
        pass

def is_cloud_id_in_secrets():
    """Vérifie si l'ID est configuré dans les Secrets Streamlit"""
    try:
        return hasattr(st, 'secrets') and 'CLOUD_BLOB_ID' in st.secrets and st.secrets['CLOUD_BLOB_ID']
    except:
        return False

def save_to_cloud():
    """Sauvegarde automatique dans le cloud"""
    try:
        data_to_save = {
            'players': st.session_state.players,
            'data': st.session_state.data,
            'injuries': st.session_state.injuries,
            'settings': {k: v for k, v in st.session_state.settings.items() if not k.startswith('cloud_')},
            'saved_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'app_version': 'v16'
        }
        
        json_data = json.dumps(data_to_save, ensure_ascii=False)
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        
        blob_id = get_cloud_id()
        
        if blob_id:
            # Mettre à jour le blob existant
            url = f"https://jsonblob.com/api/jsonBlob/{blob_id}"
            response = requests.put(url, data=json_data.encode('utf-8'), headers=headers, timeout=30)
            
            if response.status_code == 200:
                st.session_state.last_cloud_save = datetime.now()
                return True, "☁️ Synchronisé"
            elif response.status_code == 404:
                # Blob supprimé, en créer un nouveau
                st.session_state.settings['cloud_blob_id'] = None
                return save_to_cloud()
            else:
                return False, f"Erreur: {response.status_code}"
        else:
            # Créer un nouveau blob
            url = "https://jsonblob.com/api/jsonBlob"
            response = requests.post(url, data=json_data.encode('utf-8'), headers=headers, timeout=30)
            
            if response.status_code == 201:
                location = response.headers.get('Location', '')
                if location:
                    new_blob_id = location.split('/')[-1]
                    save_cloud_id(new_blob_id)
                    st.session_state.last_cloud_save = datetime.now()
                    st.session_state.new_cloud_id_created = new_blob_id  # Flag pour afficher les instructions
                    return True, "☁️ Cloud créé"
            return False, f"Erreur création: {response.status_code}"
        
    except requests.exceptions.Timeout:
        return False, "Timeout"
    except Exception as e:
        return False, f"Erreur: {str(e)}"

def load_from_cloud():
    """Charge les données depuis le cloud"""
    try:
        blob_id = get_cloud_id()
        if not blob_id:
            return False, "Pas de sauvegarde cloud"
        
        url = f"https://jsonblob.com/api/jsonBlob/{blob_id}"
        response = requests.get(url, headers={'Accept': 'application/json'}, timeout=30)
        
        if response.status_code == 200:
            loaded = response.json()
            
            st.session_state.players = loaded.get('players', [])
            st.session_state.data = loaded.get('data', {})
            st.session_state.injuries = loaded.get('injuries', [])
            if 'settings' in loaded:
                for k, v in loaded['settings'].items():
                    if not k.startswith('cloud_'):
                        st.session_state.settings[k] = v
            
            # Sauvegarder localement
            try:
                with open(DATA_FILE, 'w', encoding='utf-8') as f:
                    json.dump({
                        'players': st.session_state.players,
                        'data': st.session_state.data,
                        'injuries': st.session_state.injuries,
                        'settings': st.session_state.settings,
                        'saved_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }, f, ensure_ascii=False, indent=2)
            except:
                pass
            
            return True, f"☁️ Chargé ({len(st.session_state.players)} joueurs, {len(st.session_state.data)} jours)"
        elif response.status_code == 404:
            return False, "Sauvegarde cloud introuvable"
        else:
            return False, f"Erreur: {response.status_code}"
        
    except Exception as e:
        return False, f"Erreur: {str(e)}"

def get_cloud_status():
    """Retourne le statut du cloud"""
    blob_id = get_cloud_id()
    return (True, blob_id) if blob_id else (False, None)

def get_backup_reminder():
    """Vérifie si un rappel de backup est nécessaire"""
    if 'last_save_time' not in st.session_state:
        return True
    time_since_save = datetime.now() - st.session_state.last_save_time
    return time_since_save.total_seconds() > 1800

# ==================== CHARGEMENT AUTOMATIQUE AU DÉMARRAGE ====================
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = True
    st.session_state.last_save_time = datetime.now()
    
    # 1. Charger l'ID cloud depuis les Secrets Streamlit (priorité)
    try:
        if hasattr(st, 'secrets') and 'CLOUD_BLOB_ID' in st.secrets:
            st.session_state.settings['cloud_blob_id'] = st.secrets['CLOUD_BLOB_ID']
    except:
        pass
    
    # 2. Ou depuis le fichier local
    if not st.session_state.settings.get('cloud_blob_id') and os.path.exists(CLOUD_ID_FILE):
        try:
            with open(CLOUD_ID_FILE, 'r') as f:
                blob_id = f.read().strip()
                if blob_id:
                    st.session_state.settings['cloud_blob_id'] = blob_id
        except:
            pass
    
    # 3. Charger les données locales pour comparaison
    local_data_count = 0
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                local_data = json.load(f)
            local_data_count = len(local_data.get('data', {}))
            st.session_state.players = local_data.get('players', [])
            st.session_state.data = local_data.get('data', {})
            st.session_state.injuries = local_data.get('injuries', [])
            if 'settings' in local_data:
                for k, v in local_data['settings'].items():
                    if not k.startswith('cloud_'):
                        st.session_state.settings[k] = v
        except:
            pass
    
    # 4. Si on a un ID cloud, charger depuis le cloud et comparer
    cloud_blob_id = get_cloud_id()
    if cloud_blob_id:
        try:
            url = f"https://jsonblob.com/api/jsonBlob/{cloud_blob_id}"
            response = requests.get(url, headers={'Accept': 'application/json'}, timeout=15)
            if response.status_code == 200:
                cloud_data = response.json()
                cloud_data_count = len(cloud_data.get('data', {}))
                
                # Si le cloud a plus de données OU autant, utiliser le cloud (plus récent)
                if cloud_data_count >= local_data_count:
                    st.session_state.players = cloud_data.get('players', [])
                    st.session_state.data = cloud_data.get('data', {})
                    st.session_state.injuries = cloud_data.get('injuries', [])
                    if 'settings' in cloud_data:
                        for k, v in cloud_data['settings'].items():
                            if not k.startswith('cloud_'):
                                st.session_state.settings[k] = v
                    st.session_state.cloud_loaded = True
        except:
            pass

# ==================== UTILITAIRES ====================
def get_player_group(position):
    """Retourne le groupe (Avants/Trois-quarts) pour une position"""
    for group_name, lines in RUGBY_POSITIONS.items():
        for line_positions in lines.values():
            if position in line_positions:
                return group_name
    return 'Avants'

def get_player_line(position):
    """Retourne la ligne (1ère ligne, Demis, etc.) pour une position"""
    for lines in RUGBY_POSITIONS.values():
        for line_name, line_positions in lines.items():
            if position in line_positions:
                return line_name
    return '1ère ligne'

def format_date(date_str, fmt='short'):
    """Formate une date en français"""
    if not date_str:
        return '-'
    try:
        d = datetime.strptime(date_str, '%Y-%m-%d')
        months = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 
                  'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
        if fmt == 'short':
            return f"{d.day} {months[d.month-1][:3]}"
        elif fmt == 'full':
            return f"{FRENCH_DAYS[d.weekday()]} {d.day} {months[d.month-1]} {d.year}"
        else:
            return d.strftime('%d/%m/%Y')
    except:
        return date_str

def get_player_average(player_data):
    """Calcule la moyenne des métriques d'un joueur"""
    if not player_data:
        return None
    vals = [player_data.get(m['key']) for m in METRICS if player_data.get(m['key']) is not None]
    return sum(vals) / len(vals) if vals else None

def get_team_avg(date_key, group=None, line=None, position=None):
    """Calcule les moyennes de l'équipe avec filtres optionnels"""
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
        if position and p['position'] != position:
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
    """Génère les alertes pour une date donnée"""
    data = st.session_state.data.get(date_key, [])
    settings = st.session_state.settings
    alerts = []
    
    for d in data:
        p = next((p for p in st.session_state.players if p['name'] == d['name']), None)
        if not p:
            continue
        
        # Alertes métriques basses
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
        
        # Alerte poids
        if d.get('weight') and p.get('targetWeight'):
            diff = abs(d['weight'] - p['targetWeight'])
            if diff > settings['weightThreshold']:
                sign = '+' if d['weight'] > p['targetWeight'] else '-'
                alerts.append({
                    'player': d['name'],
                    'player_id': p['id'],
                    'type': 'weight',
                    'diff': round(d['weight'] - p['targetWeight'], 1),
                    'message': f"Poids {sign}{diff:.1f}kg vs forme"
                })
    
    return alerts

def get_availability_data():
    """Retourne les données de disponibilité pour le pie chart"""
    counts = {}
    for p in st.session_state.players:
        status = p.get('status', 'Apte')
        counts[status] = counts.get(status, 0) + 1
    
    colors = {'Apte': '#10b981', 'Blessé': '#ef4444', 'Réhabilitation': '#f59e0b', 'Réathlétisation': '#3b82f6'}
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
    """Calcule le Z-Score d'une valeur par rapport à un historique"""
    if not prev_values or len(prev_values) < 3:
        return 0
    mean = sum(prev_values) / len(prev_values)
    std = (sum((v - mean) ** 2 for v in prev_values) / len(prev_values)) ** 0.5
    return (value - mean) / std if std > 0 else 0

def get_color_for_value(val):
    """Retourne la couleur selon la valeur (1-5)"""
    if val is None:
        return '#475569'
    if val <= 2:
        return '#ef4444'
    if val <= 3:
        return '#f59e0b'
    return '#10b981'

def get_avatar_gradient(name):
    """Retourne une classe de gradient basée sur le nom"""
    idx = sum(ord(c) for c in name) % 5 + 1
    return f"avatar-gradient-{idx}"

def fmt_val(val, decimals=1, suffix=""):
    """Formate une valeur numérique de façon sécurisée"""
    if val is None:
        return "-"
    try:
        if decimals == 0:
            return f"{int(val)}{suffix}"
        elif decimals == 1:
            return f"{val:.1f}{suffix}"
        else:
            return f"{val:.2f}{suffix}"
    except (TypeError, ValueError):
        return "-"

# ==================== IMPORT AMÉLIORÉ ====================
def parse_date_french(text):
    """Parse une date en français - format: 'mardi 6 janvier 2026' ou '6 janvier 2026'"""
    if pd.isna(text):
        return None
    text = str(text).lower().strip()
    
    # Format: "mardi 6 janvier 2026" ou "6 janvier 2026"
    match = re.search(r'(\d{1,2})\s+(janvier|février|fevrier|mars|avril|mai|juin|juillet|août|aout|septembre|octobre|novembre|décembre|decembre)\s+(\d{4})', text)
    if match:
        day = int(match.group(1))
        month = FRENCH_MONTHS.get(match.group(2), 1)
        year = int(match.group(3))
        return f"{year}-{month:02d}-{day:02d}"
    
    # Format: "06/01/2026"
    match = re.search(r'(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})', text)
    if match:
        day = int(match.group(1))
        month = int(match.group(2))
        year = int(match.group(3))
        return f"{year}-{month:02d}-{day:02d}"
    
    return None


def normalize_text(text):
    """Normalise le texte pour la comparaison (supprime accents, lowercase)"""
    if pd.isna(text):
        return ""
    text = str(text).lower().strip()
    # Remplacements des caractères accentués
    replacements = {
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'à': 'a', 'â': 'a', 'ä': 'a',
        'ù': 'u', 'û': 'u', 'ü': 'u',
        'ô': 'o', 'ö': 'o',
        'î': 'i', 'ï': 'i',
        'ç': 'c'
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def find_column_index(row, keywords, debug_info=None):
    """
    Trouve l'index d'une colonne en cherchant des mots-clés.
    keywords: liste de mots-clés possibles (premier trouvé gagne)
    """
    for j, cell in enumerate(row):
        if pd.notna(cell):
            cell_norm = normalize_text(cell)
            for kw in keywords:
                if kw in cell_norm:
                    if debug_info is not None:
                        debug_info.append(f"  → '{kw}' trouvé en colonne {j}: '{cell}'")
                    return j
    return None


def detect_date_blocks(df, debug=False):
    """
    Détecte les blocs de dates dans un fichier "Suivi BE" où les jours sont côte à côte.
    Nouvelle approche: trouver les colonnes "Joueur" pour délimiter les blocs.
    """
    import streamlit as st
    blocks = []
    
    # 1. Trouver la ligne des dates (chercher dans les premières lignes)
    date_row_idx = None
    dates_in_row = {}  # col_idx -> date_str
    
    for row_idx in range(min(6, len(df))):
        row = df.iloc[row_idx]
        found_dates = {}
        for col_idx, cell in enumerate(row):
            if pd.notna(cell):
                parsed = parse_date_french(str(cell))
                if parsed:
                    found_dates[col_idx] = {'date': parsed, 'label': str(cell)}
        
        if len(found_dates) >= 1:  # On a trouvé au moins une date
            date_row_idx = row_idx
            dates_in_row = found_dates
            if debug:
                st.write(f"📅 Dates trouvées ligne {row_idx}: {len(found_dates)} dates")
            break
    
    if not dates_in_row:
        if debug:
            st.warning("⚠️ Aucune date trouvée dans les premières lignes")
        return []
    
    # 2. Trouver la ligne d'en-têtes (contient plusieurs "Joueur")
    header_row_idx = None
    joueur_columns = []  # Liste des colonnes où on trouve "Joueur"
    
    for row_idx in range(date_row_idx + 1, min(date_row_idx + 5, len(df))):
        row = df.iloc[row_idx]
        joueur_cols = []
        for col_idx, cell in enumerate(row):
            if pd.notna(cell):
                cell_norm = normalize_text(cell)
                if cell_norm == 'joueur' or cell_norm == 'nom':
                    joueur_cols.append(col_idx)
        
        if joueur_cols:
            header_row_idx = row_idx
            joueur_columns = joueur_cols
            if debug:
                st.write(f"📋 En-têtes ligne {row_idx}: {len(joueur_cols)} blocs trouvés (colonnes: {joueur_cols})")
            break
    
    if not joueur_columns:
        if debug:
            st.warning("⚠️ Colonnes 'Joueur' non trouvées")
        return []
    
    # 3. Associer chaque colonne "Joueur" avec la date la plus proche à gauche ou au-dessus
    for i, joueur_col in enumerate(joueur_columns):
        # Trouver la fin du bloc (prochaine colonne Joueur ou fin)
        if i + 1 < len(joueur_columns):
            end_col = joueur_columns[i + 1]
        else:
            end_col = len(df.columns)
        
        # Trouver la date associée (la plus proche à gauche ou égale)
        best_date = None
        best_date_col = -1
        for date_col, date_info in dates_in_row.items():
            if date_col <= joueur_col and date_col > best_date_col:
                best_date = date_info
                best_date_col = date_col
        
        if best_date:
            blocks.append({
                'date': best_date['date'],
                'date_str': best_date['label'],
                'start_col': joueur_col,  # Commence à la colonne "Joueur"
                'end_col': end_col,
                'header_row': header_row_idx
            })
    
    if debug:
        st.write(f"✅ {len(blocks)} blocs détectés")
        for b in blocks[:3]:
            st.write(f"  • {b['date_str']}: colonnes {b['start_col']}-{b['end_col']}")
    
    return blocks


def process_suivi_be_data(df, selected_dates=None, debug=False):
    """
    Traite les données du format "Suivi BE" avec les jours côte à côte.
    """
    try:
        import streamlit as st
        
        if debug:
            st.write("### 🔍 Analyse du fichier Suivi BE")
            st.write(f"**Dimensions:** {len(df)} lignes × {len(df.columns)} colonnes")
        
        # 1. Détecter les blocs de dates
        blocks = detect_date_blocks(df, debug)
        
        if not blocks:
            return {'success': False, 'error': "Aucun bloc de données trouvé. Vérifiez que le fichier contient des dates et des colonnes 'Joueur'."}
        
        # Si aucune date sélectionnée, retourner la liste des dates disponibles
        if selected_dates is None:
            return {
                'success': True,
                'mode': 'list_dates',
                'available_dates': [{'date': b['date'], 'label': b['date_str']} for b in blocks]
            }
        
        # 2. Traiter chaque bloc sélectionné
        total_entries = 0
        players_created = 0
        dates_imported = []
        
        for block in blocks:
            if block['date'] not in selected_dates:
                continue
            
            date_key = block['date']
            start_col = block['start_col']
            end_col = block['end_col']
            header_row_idx = block['header_row']
            
            if debug:
                st.write(f"📊 Traitement de **{block['date_str']}** (colonnes {start_col}-{end_col})")
            
            # Mapper les colonnes par POSITION relative depuis "Joueur"
            # Structure: Joueur | Sommeil | Charge | Motivation | HDC | BDC | Moyenne | Remarque | [prochain Joueur]
            header_row_data = df.iloc[header_row_idx]
            col_indices = {'name': start_col}
            
            # Les en-têtes des métriques sont souvent vides (None) dans le CSV exporté
            # On mappe par position relative depuis la colonne Joueur
            col_indices['sleep'] = start_col + 1
            col_indices['mentalLoad'] = start_col + 2
            col_indices['motivation'] = start_col + 3
            col_indices['hdcState'] = start_col + 4
            col_indices['bdcState'] = start_col + 5
            # +6 serait Moyenne (on l'ignore)
            # +7 serait Remarque
            
            # Chercher la colonne Remarque explicitement d'abord
            remark_found = False
            # Chercher dans les colonnes après BDC jusqu'à la fin du bloc
            for offset in range(5, min(15, end_col - start_col)):
                check_col = start_col + offset
                if check_col < len(header_row_data) and check_col < end_col:
                    cell = header_row_data.iloc[check_col]
                    if pd.notna(cell):
                        cell_norm = normalize_text(str(cell))
                        if 'remarque' in cell_norm or 'commentaire' in cell_norm or 'note' in cell_norm or 'comment' in cell_norm:
                            col_indices['remark'] = check_col
                            remark_found = True
                            if debug:
                                st.write(f"  ✅ Remarque trouvée en colonne {check_col} (header: '{cell}')")
                            break
            
            # Si pas trouvé par nom, essayer plusieurs positions par défaut
            if not remark_found:
                # Essayer +7, +8, +6 dans cet ordre
                possible_positions = [start_col + 7, start_col + 8, start_col + 6]
                for remark_col in possible_positions:
                    if remark_col < end_col and remark_col < len(header_row_data):
                        col_indices['remark'] = remark_col
                        if debug:
                            st.write(f"  📝 Remarque assignée par position par défaut à colonne {remark_col}")
                        break
            
            if debug:
                st.write(f"  Colonnes mappées (par position): name={col_indices.get('name')}, sleep={col_indices.get('sleep')}, mentalLoad={col_indices.get('mentalLoad')}, motivation={col_indices.get('motivation')}, hdcState={col_indices.get('hdcState')}, bdcState={col_indices.get('bdcState')}, remark={col_indices.get('remark')}")
            
            # Extraire les données des joueurs
            entries = []
            skipped_players = []
            skipped_reasons = {}
            
            for row_idx in range(header_row_idx + 1, len(df)):
                row = df.iloc[row_idx]
                
                # Récupérer le nom
                name_col = col_indices.get('name')
                if name_col >= len(row):
                    continue
                
                name = row.iloc[name_col]
                if pd.isna(name):
                    continue
                
                name = str(name).strip()
                
                # Ignorer lignes vides ou EQUIPE
                if not name or len(name) < 2:
                    continue
                if name.upper() in ['EQUIPE', 'ÉQUIPE', 'TOTAL', 'MOYENNE']:
                    continue
                if name.lower() in ['joueur', 'nom', 'nan', 'none']:
                    continue
                
                # Ignorer si le "nom" ressemble à une remarque (trop long ou contient des mots-clés)
                name_lower = name.lower()
                
                # Mots-clés de remarque - phrases ou expressions qui indiquent clairement une remarque
                # On utilise des expressions plus longues pour éviter les faux positifs sur les noms
                remark_patterns = [
                    # Expressions de douleur/blessure
                    'douleur', 'courbature', 'fatigue', 'crampe', 'blessure', 
                    'contracture', 'entorse', 'foulure', 'claquage', 'déchir',
                    'inflamm', 'tendinite', 'élongation', 'lésion', 'lesion',
                    # Parties du corps (comme début de remarque)
                    'genou droit', 'genou gauche', 'cheville', 'épaule', 'mollet',
                    'ischio', 'cuisse', 'adducteur', 'quadri', 'dos bloqué',
                    'kyste', 'hernie', 'pubis', 'lombes', 'lombaire',
                    # États
                    'pas en forme', 'fatigué', 'malade', 'grippé', 'épuisé',
                    'mieux', 'soucis', 'souci', 'problème', 'probleme',
                    # Actions/situations
                    'rien à signaler', 'tout va bien', 'en forme', 'récupération',
                    'au repos', 'absent', 'indisponible',
                    # Temporels (indiquent une remarque contextuelle)
                    'ce matin', 'cette nuit', 'hier soir', 'depuis', 'toujours',
                    'encore', 'gêné', 'gene',
                    # Phrases types
                    'mal au', 'mal à la', 'mal aux', 'douleur au', 'gêne au',
                    'sensation de', 'léger problème', 'petit souci'
                ]
                
                # RÈGLE PRINCIPALE: Les noms de joueurs sont en MAJUSCULES
                # Si le texte n'est pas en majuscules, c'est probablement une remarque
                def is_valid_player_name(text):
                    """Vérifie si le texte ressemble à un nom de joueur"""
                    # Doit être principalement en majuscules (au moins 80%)
                    upper_chars = sum(1 for c in text if c.isupper())
                    alpha_chars = sum(1 for c in text if c.isalpha())
                    if alpha_chars == 0:
                        return False
                    uppercase_ratio = upper_chars / alpha_chars
                    
                    # Critères:
                    # 1. Au moins 80% majuscules OU entièrement en majuscules
                    # 2. Pas trop long (max 25 caractères)
                    # 3. Pas trop d'espaces (max 2 pour les noms composés)
                    return (
                        (uppercase_ratio >= 0.8 or text.isupper()) and
                        len(text) <= 25 and
                        text.count(' ') <= 2
                    )
                
                skip_reason = None
                
                # Vérifier si c'est un nom valide (MAJUSCULES)
                if not is_valid_player_name(name):
                    skip_reason = f"pas en majuscules (nom invalide)"
                # Vérifier les patterns de remarque
                elif any(pattern in name_lower for pattern in remark_patterns):
                    matched = [p for p in remark_patterns if p in name_lower]
                    skip_reason = f"pattern remarque: '{matched[0]}'"
                
                if skip_reason:
                    skipped_reasons[name] = skip_reason
                    continue
                
                # Créer le joueur s'il n'existe pas
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
                metrics_found = []
                
                # Métriques (1-5)
                for metric_key in ['sleep', 'mentalLoad', 'motivation', 'hdcState', 'bdcState']:
                    if metric_key in col_indices and col_indices[metric_key] < len(row):
                        val = row.iloc[col_indices[metric_key]]
                        if pd.notna(val):
                            try:
                                val_str = str(val).replace(',', '.').replace(' ', '')
                                if val_str and val_str not in ['#DIV/0!', '#N/A', '#VALUE!', '-', '']:
                                    num = float(val_str)
                                    if 1 <= num <= 5:
                                        entry[metric_key] = num
                                        metrics_found.append(metric_key)
                            except:
                                pass
                
                # Remarque
                if 'remark' in col_indices and col_indices['remark'] < len(row):
                    val = row.iloc[col_indices['remark']]
                    if pd.notna(val):
                        remark = str(val).strip()
                        if remark and remark.lower() not in ['nan', 'none', '', '#n/a']:
                            entry['remark'] = remark
                
                # N'ajouter que si on a au moins une métrique
                has_data = any(entry.get(m['key']) for m in METRICS)
                if has_data:
                    entries.append(entry)
                else:
                    skipped_players.append(name)
            
            if debug:
                entries_with_remarks = sum(1 for e in entries if e.get('remark'))
                st.write(f"  → {len(entries)} joueurs avec données ({entries_with_remarks} avec remarques)")
                if skipped_reasons:
                    with st.expander(f"⚠️ {len(skipped_reasons)} noms filtrés (pas des joueurs)"):
                        for name, reason in list(skipped_reasons.items())[:10]:
                            st.write(f"  • `{name}` - {reason}")
                if skipped_players and len(skipped_players) <= 5:
                    st.write(f"  ⚠️ Joueurs sans métriques valides: {skipped_players}")
                elif skipped_players:
                    st.write(f"  ⚠️ {len(skipped_players)} joueurs sans métriques valides")
            
            if entries:
                # Fusionner avec les données existantes ou créer
                if date_key in st.session_state.data:
                    existing = {e['name']: e for e in st.session_state.data[date_key]}
                    for entry in entries:
                        existing[entry['name']] = entry
                    st.session_state.data[date_key] = list(existing.values())
                else:
                    st.session_state.data[date_key] = entries
                
                total_entries += len(entries)
                dates_imported.append(block['date_str'])
        
        if dates_imported:
            # AUTO-SAVE après import réussi
            save_data_to_file()
            
            return {
                'success': True,
                'mode': 'imported',
                'dates_imported': dates_imported,
                'entries': total_entries,
                'new_players': players_created,
                'players': len(st.session_state.players)
            }
        else:
            return {'success': False, 'error': "Aucune donnée importée. Activez le mode debug pour voir les détails du parsing."}
        
    except Exception as e:
        import traceback
        if debug:
            st.error(f"Erreur: {traceback.format_exc()}")
        return {'success': False, 'error': str(e)}


def process_suivi_poids_data(df, selected_dates=None, debug=False):
    """
    Traite les données du format "Suivi Poids" - met à jour le poids des joueurs existants.
    
    Format attendu :
    - Ligne 0 : vide, puis dates (23/06, 24/06, etc.)
    - Colonne 0 : noms des joueurs
    - Cellules : poids en kg
    """
    try:
        import streamlit as st
        
        if debug:
            st.write("### 🔍 Analyse du fichier Suivi Poids")
            st.write(f"**Dimensions:** {len(df)} lignes × {len(df.columns)} colonnes")
        
        # 1. Extraire les dates depuis la première ligne
        date_row = df.iloc[0]
        dates_info = []
        
        for col_idx in range(1, len(date_row)):
            cell = date_row.iloc[col_idx]
            if pd.notna(cell):
                cell_str = str(cell).strip()
                # Essayer de parser la date (format DD/MM ou DD/MM/YY ou DD/MM/YYYY)
                parsed_date = None
                for fmt in ['%d/%m', '%d/%m/%y', '%d/%m/%Y', '%d-%m', '%d-%m-%y', '%d-%m-%Y']:
                    try:
                        parsed = datetime.strptime(cell_str, fmt)
                        # Si pas d'année, utiliser l'année courante ou 2025/2026
                        if fmt in ['%d/%m', '%d-%m']:
                            # Déterminer l'année selon le mois
                            if parsed.month >= 7:  # Juillet ou après → année de début
                                parsed = parsed.replace(year=2025)
                            else:  # Avant juillet → année de fin
                                parsed = parsed.replace(year=2026)
                        parsed_date = parsed.strftime('%Y-%m-%d')
                        break
                    except:
                        continue
                
                if parsed_date:
                    dates_info.append({
                        'col_idx': col_idx,
                        'date': parsed_date,
                        'date_str': cell_str
                    })
        
        if not dates_info:
            return {'success': False, 'error': "Aucune date trouvée dans la première ligne."}
        
        if debug:
            st.write(f"**Dates trouvées:** {len(dates_info)}")
            st.write(f"Du {dates_info[0]['date_str']} au {dates_info[-1]['date_str']}")
        
        # Si aucune date sélectionnée, retourner la liste des dates disponibles
        if selected_dates is None:
            return {
                'success': True,
                'mode': 'list_dates',
                'available_dates': [{'date': d['date'], 'label': d['date_str']} for d in dates_info]
            }
        
        # 2. Créer un mapping des noms de joueurs existants
        existing_players = {p['name'].upper().strip(): p['name'] for p in st.session_state.players}
        
        if debug:
            st.write(f"**Joueurs existants:** {len(existing_players)}")
        
        # 3. Parcourir les lignes (joueurs) et colonnes (dates) pour mettre à jour le poids
        updates_count = 0
        players_updated = set()
        dates_updated = set()
        
        for row_idx in range(1, len(df)):  # Commencer à la ligne 1 (après les dates)
            row = df.iloc[row_idx]
            player_name_raw = row.iloc[0]
            
            if pd.isna(player_name_raw):
                continue
            
            player_name_raw = str(player_name_raw).strip()
            if not player_name_raw:
                continue
            
            # Chercher le joueur dans les existants
            player_name_upper = player_name_raw.upper()
            matched_name = None
            
            # Correspondance exacte
            if player_name_upper in existing_players:
                matched_name = existing_players[player_name_upper]
            else:
                # Essayer une correspondance partielle
                for key, name in existing_players.items():
                    if player_name_upper in key or key in player_name_upper:
                        matched_name = name
                        break
            
            if not matched_name:
                if debug and row_idx <= 5:
                    st.write(f"  ⚠️ Joueur non trouvé: {player_name_raw}")
                continue
            
            # Parcourir les dates sélectionnées et mettre à jour le poids
            for date_info in dates_info:
                if date_info['date'] not in selected_dates:
                    continue
                
                col_idx = date_info['col_idx']
                date_key = date_info['date']
                
                if col_idx >= len(row):
                    continue
                
                weight_val = row.iloc[col_idx]
                
                if pd.isna(weight_val):
                    continue
                
                # Parser le poids
                try:
                    if isinstance(weight_val, (int, float)):
                        weight = float(weight_val)
                    else:
                        weight_str = str(weight_val).replace(',', '.').strip()
                        weight = float(weight_str)
                    
                    # Valider le poids (entre 50 et 200 kg pour un rugbyman)
                    if weight < 50 or weight > 200:
                        continue
                except:
                    continue
                
                # Mettre à jour le poids dans les données wellness de cette date
                if date_key in st.session_state.data:
                    for entry in st.session_state.data[date_key]:
                        if entry.get('name') == matched_name:
                            entry['weight'] = round(weight, 1)
                            updates_count += 1
                            players_updated.add(matched_name)
                            dates_updated.add(date_key)
                            break
                    else:
                        # Le joueur n'a pas d'entrée pour cette date, en créer une avec juste le poids
                        # (optionnel - seulement si on veut créer des entrées)
                        pass
        
        if updates_count > 0:
            # AUTO-SAVE après import réussi
            save_data_to_file()
            
            return {
                'success': True,
                'mode': 'imported',
                'dates_imported': list(dates_updated),
                'entries': updates_count,
                'players_updated': len(players_updated),
                'message': f"Poids mis à jour pour {len(players_updated)} joueurs sur {len(dates_updated)} dates"
            }
        else:
            return {
                'success': False, 
                'error': "Aucun poids mis à jour. Vérifiez que les joueurs existent et que les dates correspondent."
            }
        
    except Exception as e:
        import traceback
        if debug:
            st.error(f"Erreur: {traceback.format_exc()}")
        return {'success': False, 'error': str(e)}


def process_imported_data(df, debug=False):
    """
    Traite les données importées depuis Google Sheets.
    Version améliorée avec détection flexible des en-têtes.
    
    Structure attendue :
    - Ligne avec la date (ex: "mardi 6 janvier 2026")
    - Ligne d'en-têtes : Joueur, Poids, Sommeil, Charge mentale, Motivation, état général HDC, état général BDC, Moyenne, ..., Remarque
    - Ligne EQUIPE (à ignorer)
    - Données des joueurs
    """
    try:
        debug_info = [] if debug else None
        
        if debug:
            st.write("### 🔍 Analyse détaillée du fichier")
            st.write(f"**Dimensions:** {len(df)} lignes × {len(df.columns)} colonnes")
            st.write("**Aperçu des premières lignes:**")
            st.dataframe(df.head(10))
        
        # 1. Chercher la date dans les premières lignes
        date_found = None
        for i in range(min(10, len(df))):
            for j in range(len(df.columns)):
                cell = df.iloc[i, j]
                if pd.notna(cell):
                    parsed = parse_date_french(str(cell))
                    if parsed:
                        date_found = parsed
                        if debug:
                            st.success(f"📅 Date trouvée ligne {i}, colonne {j}: **{format_date(date_found, 'full')}** (valeur: '{cell}')")
                        break
            if date_found:
                break
        
        if not date_found:
            date_found = datetime.now().strftime('%Y-%m-%d')
            if debug:
                st.warning(f"⚠️ Date non trouvée, utilisation de la date du jour: {date_found}")
        
        # 2. Chercher la ligne d'en-têtes avec plusieurs stratégies
        header_row = None
        col_indices = {}
        
        # Mots-clés pour détecter la ligne d'en-têtes
        header_keywords = ['joueur', 'nom', 'poids', 'sommeil', 'motivation', 'charge']
        
        for i in range(min(20, len(df))):
            row = df.iloc[i]
            row_values = [str(x).lower().strip() for x in row if pd.notna(x)]
            row_text = ' '.join(row_values)
            
            if debug:
                debug_info.append(f"\n**Ligne {i}:** {row_values[:8]}")
            
            # Compter combien de mots-clés d'en-tête sont présents
            keywords_found = sum(1 for kw in header_keywords if kw in row_text)
            
            if debug:
                debug_info.append(f"  Keywords trouvés: {keywords_found}")
            
            # Si on trouve au moins 3 mots-clés, c'est probablement l'en-tête
            if keywords_found >= 3:
                header_row = i
                if debug:
                    st.success(f"📋 En-tête détecté ligne {i} ({keywords_found} mots-clés)")
                
                # Mapper les colonnes avec des recherches flexibles
                col_indices['name'] = find_column_index(row, ['joueur', 'nom'], debug_info)
                col_indices['weight'] = find_column_index(row, ['poids', 'weight'], debug_info)
                col_indices['sleep'] = find_column_index(row, ['sommeil', 'sleep'], debug_info)
                col_indices['mentalLoad'] = find_column_index(row, ['charge mentale', 'charge', 'mental'], debug_info)
                col_indices['motivation'] = find_column_index(row, ['motivation'], debug_info)
                col_indices['hdcState'] = find_column_index(row, ['hdc', 'etat general hdc', 'etat hdc'], debug_info)
                col_indices['bdcState'] = find_column_index(row, ['bdc', 'etat general bdc', 'etat bdc'], debug_info)
                col_indices['remark'] = find_column_index(row, ['remarque', 'commentaire', 'note'], debug_info)
                
                # Filtrer les None
                col_indices = {k: v for k, v in col_indices.items() if v is not None}
                break
        
        if debug and debug_info:
            with st.expander("🔧 Détails du parsing"):
                for line in debug_info:
                    st.write(line)
        
        if header_row is None:
            # Stratégie de fallback: chercher une ligne avec "Joueur" ou "JOUEUR"
            for i in range(min(20, len(df))):
                row = df.iloc[i]
                for j, cell in enumerate(row):
                    if pd.notna(cell) and normalize_text(cell) in ['joueur', 'nom']:
                        header_row = i
                        col_indices['name'] = j
                        if debug:
                            st.warning(f"🔄 Fallback: en-tête trouvé ligne {i} via 'Joueur'")
                        break
                if header_row is not None:
                    break
        
        if header_row is None:
            return {'success': False, 'error': "Ligne d'en-tête non trouvée. Le fichier doit contenir une ligne avec 'Joueur', 'Poids', 'Sommeil', etc."}
        
        if 'name' not in col_indices:
            return {'success': False, 'error': "Colonne 'Joueur' non trouvée. Vérifiez que la colonne des noms est présente."}
        
        if debug:
            st.write(f"**Colonnes mappées:** {col_indices}")
        
        # 3. Si on n'a pas trouvé toutes les colonnes de métriques, essayer de les déduire par position
        if len([k for k in col_indices if k in ['sleep', 'mentalLoad', 'motivation', 'hdcState', 'bdcState']]) < 3:
            if debug:
                st.warning("⚠️ Peu de colonnes métriques trouvées, tentative de mapping par position...")
            
            # Supposer un ordre standard après 'name'
            # Structure: Joueur | Poids | Sommeil | Charge | Motivation | HDC | BDC | Moyenne | Remarque
            #              +0      +1      +2        +3        +4         +5    +6     +7        +8
            name_col = col_indices.get('name', 0)
            
            position_map = {
                'weight': name_col + 1,
                'sleep': name_col + 2,
                'mentalLoad': name_col + 3,
                'motivation': name_col + 4,
                'hdcState': name_col + 5,
                'bdcState': name_col + 6,
                # +7 = Moyenne (on l'ignore)
                'remark': name_col + 8
            }
            
            for metric, pos in position_map.items():
                if metric not in col_indices:
                    col_indices[metric] = pos
                    if debug:
                        st.write(f"  → {metric} assigné à la colonne {pos}")
        
        # Ajouter la remarque par position si pas trouvée
        if 'remark' not in col_indices:
            # La remarque est après BDC + Moyenne, donc +2
            last_metric_col = max([col_indices.get(k, 0) for k in ['sleep', 'mentalLoad', 'motivation', 'hdcState', 'bdcState'] if k in col_indices], default=0)
            if last_metric_col > 0:
                # +1 serait Moyenne, +2 est Remarque
                col_indices['remark'] = last_metric_col + 2
                if debug:
                    st.write(f"  → remark assigné à la colonne {col_indices['remark']} (après Moyenne)")
        
        # 4. Extraire les données (lignes après l'en-tête)
        entries = []
        players_created = 0
        skipped_rows = []
        
        for row_idx in range(header_row + 1, len(df)):
            row = df.iloc[row_idx]
            
            # Récupérer le nom
            name_col = col_indices.get('name')
            if name_col is None or name_col >= len(row):
                continue
            
            name = row.iloc[name_col]
            if pd.isna(name):
                continue
            
            name = str(name).strip()
            
            # Ignorer lignes vides, EQUIPE, ou non-joueurs
            if not name or len(name) < 2:
                continue
            name_upper = name.upper()
            if name_upper in ['EQUIPE', 'ÉQUIPE', 'TOTAL', 'MOYENNE', 'AVERAGE', 'TEAM']:
                if debug:
                    skipped_rows.append(f"Ligne {row_idx}: '{name}' (ligne équipe)")
                continue
            if name.lower() in ['joueur', 'nom', 'nan', 'none', 'player']:
                continue
            
            # Ignorer si le "nom" ressemble à une remarque (trop long ou contient des mots-clés)
            name_lower = name.lower()
            
            # Mots-clés de remarque - phrases ou expressions qui indiquent clairement une remarque
            remark_patterns = [
                'douleur', 'courbature', 'fatigue', 'crampe', 'blessure', 
                'contracture', 'entorse', 'foulure', 'claquage', 'déchir',
                'inflamm', 'tendinite', 'élongation', 'lésion', 'lesion',
                'genou droit', 'genou gauche', 'cheville', 'épaule', 'mollet',
                'ischio', 'cuisse', 'adducteur', 'quadri', 'dos bloqué',
                'kyste', 'hernie', 'pubis', 'lombes', 'lombaire',
                'pas en forme', 'fatigué', 'malade', 'grippé', 'épuisé',
                'mieux', 'soucis', 'souci', 'problème', 'probleme',
                'rien à signaler', 'tout va bien', 'en forme', 'récupération',
                'au repos', 'absent', 'indisponible',
                'ce matin', 'cette nuit', 'hier soir', 'depuis', 'toujours',
                'encore', 'gêné', 'gene',
                'mal au', 'mal à la', 'mal aux', 'douleur au', 'gêne au',
                'sensation de', 'léger problème', 'petit souci'
            ]
            
            # RÈGLE PRINCIPALE: Les noms de joueurs sont en MAJUSCULES
            def is_valid_player_name(text):
                """Vérifie si le texte ressemble à un nom de joueur"""
                upper_chars = sum(1 for c in text if c.isupper())
                alpha_chars = sum(1 for c in text if c.isalpha())
                if alpha_chars == 0:
                    return False
                uppercase_ratio = upper_chars / alpha_chars
                return (
                    (uppercase_ratio >= 0.8 or text.isupper()) and
                    len(text) <= 25 and
                    text.count(' ') <= 2
                )
            
            skip_as_remark = False
            skip_reason = ""
            
            # Vérifier si c'est un nom valide (MAJUSCULES)
            if not is_valid_player_name(name):
                skip_as_remark = True
                skip_reason = "pas en majuscules"
            # Vérifier les patterns de remarque
            elif any(pattern in name_lower for pattern in remark_patterns):
                skip_as_remark = True
                skip_reason = "pattern remarque détecté"
            
            if skip_as_remark:
                if debug:
                    skipped_rows.append(f"Ligne {row_idx}: '{name}' ({skip_reason})")
                continue
            
            # Ignorer les lignes qui semblent être des erreurs Excel (#DIV/0!, etc.)
            row_values = [str(x) for x in row if pd.notna(x)]
            if all('#' in v or 'DIV' in v.upper() for v in row_values[1:] if v):
                if debug:
                    skipped_rows.append(f"Ligne {row_idx}: '{name}' (erreurs Excel)")
                continue
            
            # Créer le joueur s'il n'existe pas
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
            
            # Poids
            if 'weight' in col_indices and col_indices['weight'] < len(row):
                val = row.iloc[col_indices['weight']]
                if pd.notna(val):
                    try:
                        # Gérer les formats avec virgule
                        num = float(str(val).replace(',', '.').replace(' ', ''))
                        if 40 <= num <= 200:
                            entry['weight'] = num
                    except:
                        pass
            
            # Métriques (1-5)
            for metric_key in ['sleep', 'mentalLoad', 'motivation', 'hdcState', 'bdcState']:
                if metric_key in col_indices and col_indices[metric_key] < len(row):
                    val = row.iloc[col_indices[metric_key]]
                    if pd.notna(val):
                        try:
                            # Gérer divers formats
                            val_str = str(val).replace(',', '.').replace(' ', '')
                            if val_str and val_str not in ['#DIV/0!', '#N/A', '#VALUE!', '-', '']:
                                num = float(val_str)
                                if 1 <= num <= 5:
                                    entry[metric_key] = num
                        except:
                            pass
            
            # Remarque
            if 'remark' in col_indices and col_indices['remark'] < len(row):
                val = row.iloc[col_indices['remark']]
                if pd.notna(val):
                    remark = str(val).strip()
                    if remark and remark.lower() not in ['nan', 'none', '', '#n/a']:
                        entry['remark'] = remark
            
            # N'ajouter que si on a au moins le nom et le poids ou une métrique
            has_data = entry.get('weight') or any(entry.get(m['key']) for m in METRICS)
            if has_data:
                entries.append(entry)
            elif debug:
                skipped_rows.append(f"Ligne {row_idx}: '{name}' (pas de données)")
        
        if debug and skipped_rows:
            with st.expander(f"⏭️ {len(skipped_rows)} lignes ignorées"):
                for r in skipped_rows:
                    st.write(r)
        
        if entries:
            st.session_state.data[date_found] = entries
            # AUTO-SAVE après import réussi
            save_data_to_file()
            return {
                'success': True,
                'date': date_found,
                'players': len(st.session_state.players),
                'entries': len(entries),
                'new_players': players_created,
                'columns_found': list(col_indices.keys())
            }
        else:
            return {'success': False, 'error': f"Aucune donnée de joueur valide trouvée. {len(skipped_rows)} lignes ont été ignorées. Activez le mode debug pour plus de détails."}
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        if debug:
            st.error(f"Erreur détaillée:\n{error_detail}")
        return {'success': False, 'error': str(e)}


# ==================== GRAPHIQUES ====================
def create_radar_chart(data1, data2, label1, label2):
    """Crée un graphique radar comparatif"""
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
            angularaxis=dict(gridcolor='#334155', tickfont=dict(size=10)),
            bgcolor='rgba(15,23,42,0.8)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#94a3b8', size=11),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5, font=dict(size=10)),
        margin=dict(l=60, r=60, t=30, b=60),
        height=320
    )
    return fig

def create_availability_chart():
    """Crée un pie chart de disponibilité"""
    avail_data = get_availability_data()
    if not avail_data:
        return None
    
    fig = go.Figure(data=[go.Pie(
        labels=[d['name'] for d in avail_data],
        values=[d['value'] for d in avail_data],
        hole=0.65,
        marker=dict(colors=[d['color'] for d in avail_data], line=dict(color='#0f172a', width=3)),
        textinfo='none',
        hovertemplate='%{label}: %{value}<extra></extra>'
    )])
    
    total = sum(d['value'] for d in avail_data)
    aptes = next((d['value'] for d in avail_data if d['name'] == 'Apte'), 0)
    
    fig.add_annotation(
        text=f"<b style='font-size:28px'>{aptes}</b><br><span style='font-size:11px;color:#94a3b8'>/{total} aptes</span>",
        x=0.5, y=0.5, font=dict(size=16, color='white'),
        showarrow=False
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#94a3b8'),
        showlegend=False,
        margin=dict(l=10, r=10, t=10, b=10),
        height=200
    )
    return fig

def create_zscore_chart(data):
    """Crée un graphique de Z-Score"""
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
        margin=dict(l=40, r=20, t=20, b=50),
        height=280,
        xaxis=dict(showgrid=False, tickangle=-45),
        yaxis=dict(showgrid=True, gridcolor='#1e293b', range=[-3, 3], zeroline=True, zerolinecolor='#475569'),
        showlegend=False,
        bargap=0.3
    )
    return fig

def create_weight_chart(player_name, days=30):
    """Crée un graphique d'évolution du poids"""
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
    
    # Zone cible ±2kg
    fig.add_hrect(y0=target-2, y1=target+2, fillcolor="rgba(16,185,129,0.15)", line_width=0)
    fig.add_hline(y=target, line_dash="dash", line_color="#6b7280", annotation_text=f"Cible: {target}kg")
    
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
        height=240,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#1e293b'),
        showlegend=False
    )
    return fig

def create_metrics_evolution_chart(player_name, metric='global', days=30):
    """Crée un graphique d'évolution d'une métrique"""
    history = get_player_history(player_name, days)
    if not history:
        return None
    
    chart_data = []
    for h in history:
        if metric == 'global':
            val = h.get('avg')
        else:
            val = h.get(metric)
        
        if val is not None:
            chart_data.append({'date': format_date(h['date']), 'value': val})
    
    if not chart_data:
        return None
    
    df = pd.DataFrame(chart_data)
    
    fig = go.Figure()
    
    # Zones de couleur
    fig.add_hrect(y0=0, y1=2, fillcolor="rgba(239,68,68,0.1)", line_width=0)
    fig.add_hrect(y0=2, y1=3, fillcolor="rgba(245,158,11,0.1)", line_width=0)
    fig.add_hrect(y0=3, y1=5, fillcolor="rgba(16,185,129,0.1)", line_width=0)
    
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['value'],
        mode='lines+markers',
        line=dict(color='#6366f1', width=3),
        marker=dict(size=8, color='#6366f1', line=dict(color='white', width=2)),
        fill='tozeroy',
        fillcolor='rgba(99,102,241,0.1)'
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(15,23,42,0.8)',
        font=dict(color='#94a3b8'),
        margin=dict(l=40, r=20, t=20, b=40),
        height=240,
        yaxis=dict(range=[0, 5], showgrid=True, gridcolor='#1e293b'),
        xaxis=dict(showgrid=False),
        showlegend=False
    )
    return fig

def zscore_series(metric='global', group=None, days=30):
    """Calcule la série de Z-Scores pour une métrique/groupe"""
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


def get_absolute_values_series(metric='global', group=None, days=30):
    """Calcule la série de valeurs absolues moyennes pour une métrique/groupe"""
    dates = sorted(st.session_state.data.keys())[-days:]
    if len(dates) < 1:
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
            result.append({'date': date, 'value': round(day_avg, 2)})
    
    return result


def create_absolute_values_chart(data):
    """Crée un graphique des valeurs absolues (0-5)"""
    if not data or len(data) < 1:
        return None
    
    df = pd.DataFrame(data)
    df['formatted_date'] = df['date'].apply(lambda x: format_date(x, 'short'))
    
    # Couleurs selon la valeur
    colors = []
    for val in df['value']:
        if val >= 4:
            colors.append('#10b981')  # Vert
        elif val >= 3:
            colors.append('#f59e0b')  # Orange
        else:
            colors.append('#ef4444')  # Rouge
    
    fig = go.Figure()
    
    # Barres
    fig.add_trace(go.Bar(
        x=df['formatted_date'],
        y=df['value'],
        marker_color=colors,
        hovertemplate='%{x}<br>Valeur: %{y:.2f}/5<extra></extra>'
    ))
    
    # Lignes de référence
    fig.add_hline(y=4, line_dash="dash", line_color="#10b981", opacity=0.5, annotation_text="Excellent")
    fig.add_hline(y=3, line_dash="dash", line_color="#f59e0b", opacity=0.5, annotation_text="Correct")
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#94a3b8'),
        margin=dict(l=40, r=20, t=20, b=60),
        xaxis=dict(
            showgrid=False,
            tickangle=-45,
            tickfont=dict(size=10)
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(71,85,105,0.3)',
            range=[0, 5.5],
            tickvals=[0, 1, 2, 3, 4, 5],
            title="Moyenne /5"
        ),
        height=350,
        bargap=0.3
    )
    
    return fig

def player_zscore_series(player_name, days=30):
    """Calcule la série de Z-Scores pour un joueur"""
    dates = sorted(st.session_state.data.keys())[-days:]
    if len(dates) < 5:
        return []
    
    result = []
    for date in dates:
        data = st.session_state.data.get(date, [])
        pd_data = next((d for d in data if d['name'] == player_name), None)
        if not pd_data:
            continue
        
        avg = get_player_average(pd_data)
        if avg is not None:
            prev_avgs = [r['value'] for r in result[-14:]]
            zscore = calculate_zscore(avg, prev_avgs) if len(prev_avgs) >= 3 else 0
            result.append({'date': date, 'value': avg, 'zscore': round(zscore, 2)})
    
    return result


# ==================== CALENDRIER WELLNESS ====================
def create_wellness_calendar(player_name, year=None, month=None):
    """Crée un calendrier wellness pour un joueur"""
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().month
    
    # Récupérer les données du mois
    month_data = {}
    for date_str, data in st.session_state.data.items():
        try:
            d = datetime.strptime(date_str, '%Y-%m-%d')
            if d.year == year and d.month == month:
                pd_data = next((x for x in data if x['name'] == player_name), None)
                if pd_data:
                    avg = get_player_average(pd_data)
                    month_data[d.day] = avg
        except:
            pass
    
    # Créer le calendrier
    cal = calendar.Calendar(firstweekday=0)  # Lundi = 0
    month_days = list(cal.itermonthdays(year, month))
    
    # En-têtes
    days_header = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
    
    html = '<div style="display:grid;grid-template-columns:repeat(7,1fr);gap:6px;text-align:center;max-width:400px;">'
    
    # En-têtes des jours
    for day_name in days_header:
        html += f'<div style="font-size:11px;color:#64748b;padding:4px;font-weight:600;">{day_name}</div>'
    
    # Jours du mois
    for day in month_days:
        if day == 0:
            html += '<div></div>'
        else:
            avg = month_data.get(day)
            if avg is not None:
                if avg >= 4:
                    bg = '#10b981'
                elif avg >= 3:
                    bg = '#f59e0b'
                else:
                    bg = '#ef4444'
                html += f'<div style="background:{bg};color:white;border-radius:8px;padding:8px 4px;"><span style="font-weight:bold;font-size:14px;">{day}</span><br><span style="font-size:10px;">{avg:.1f}</span></div>'
            else:
                html += f'<div style="background:rgba(71,85,105,0.3);color:#64748b;border-radius:8px;padding:8px 4px;"><span style="font-size:14px;">{day}</span></div>'
    
    html += '</div>'
    return html


# ==================== FICHE JOUEUR (MODAL) ====================
@st.dialog("📋 Fiche Joueur", width="large")
def show_player_modal(player_id):
    """Affiche la fiche complète d'un joueur dans une modale"""
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
        avatar_class = get_avatar_gradient(player['name'])
        
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:16px;">
            <div class="player-avatar {avatar_class}" style="width:70px;height:70px;font-size:28px;">{player['name'][0]}</div>
            <div>
                <div style="font-size:26px;font-weight:bold;color:white;">{player['name']}</div>
                <div style="font-size:13px;color:#94a3b8;margin-bottom:6px;">
                    {player['position']} • {get_player_group(player['position'])} • {get_player_line(player['position'])}
                </div>
                <span class="status-badge {status_class}">{player['status']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        sel_date = st.selectbox("📅", dates[:30], format_func=lambda x: format_date(x, 'short'), key="modal_date", label_visibility="collapsed")
    
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    
    # Données du jour
    today_data = st.session_state.data.get(sel_date, [])
    pd = next((d for d in today_data if d['name'] == player['name']), {})
    avg = get_player_average(pd)
    team_avg = get_team_avg(sel_date)
    diff_vs_team = (avg - team_avg['global']) if avg and team_avg and team_avg.get('global') else None
    
    # Cards Moyenne joueur vs équipe
    c1, c2 = st.columns(2)
    with c1:
        avg_str = f"{avg:.2f}" if avg else "-"
        diff_str = ""
        diff_color = "#64748b"
        if diff_vs_team is not None:
            diff_color = "#10b981" if diff_vs_team >= 0 else "#ef4444"
            diff_str = f"({'+' if diff_vs_team >= 0 else ''}{diff_vs_team:.2f})"
        
        st.markdown(f"""
        <div class="glass-card">
            <div style="font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;">Moyenne joueur</div>
            <div style="display:flex;align-items:baseline;gap:8px;">
                <span style="font-size:40px;font-weight:bold;color:white;">{avg_str}</span>
                <span style="font-size:18px;color:#64748b;">/5</span>
                <span style="font-size:16px;font-weight:600;color:{diff_color};">{diff_str}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with c2:
        team_str = f"{team_avg['global']:.2f}" if team_avg and team_avg.get('global') else "-"
        st.markdown(f"""
        <div class="glass-card" style="text-align:right;">
            <div style="font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;">Moyenne équipe</div>
            <div style="display:flex;align-items:baseline;gap:8px;justify-content:flex-end;">
                <span style="font-size:40px;font-weight:bold;color:#10b981;">{team_str}</span>
                <span style="font-size:18px;color:#64748b;">/5</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    
    # Métriques du jour (7 colonnes)
    cols = st.columns(7)
    
    # Poids
    with cols[0]:
        weight_val = pd.get('weight')
        target = player.get('targetWeight', 90)
        weight_diff = ""
        if weight_val and target:
            diff = weight_val - target
            weight_diff = f"<span style='font-size:10px;color:{'#10b981' if abs(diff) <= 2 else '#ef4444'}'>{'+' if diff > 0 else ''}{diff:.1f}</span>"
        
        st.markdown(f"""
        <div class="glass-card" style="text-align:center;padding:12px;">
            <div style="font-size:22px;">⚖️</div>
            <div style="font-size:20px;font-weight:bold;color:white;">{f"{weight_val:.1f}" if weight_val else "-"}</div>
            <div style="font-size:10px;color:#64748b;">kg {weight_diff}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # 5 métriques
    for i, m in enumerate(METRICS):
        val = pd.get(m['key'])
        color = get_color_for_value(val)
        with cols[i + 1]:
            st.markdown(f"""
            <div class="glass-card" style="text-align:center;padding:12px;">
                <div style="font-size:22px;">{m['icon']}</div>
                <div style="font-size:20px;font-weight:bold;color:{color};">{int(val) if val else "-"}</div>
                <div style="font-size:10px;color:#64748b;">/5</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Moyenne
    with cols[6]:
        avg_color = get_color_for_value(avg)
        st.markdown(f"""
        <div class="glass-card" style="text-align:center;padding:12px;background:linear-gradient(135deg, rgba(16,185,129,0.2), rgba(16,185,129,0.05));border-color:rgba(16,185,129,0.3);">
            <div style="font-size:22px;">⚡</div>
            <div style="font-size:20px;font-weight:bold;color:{avg_color};">{f"{avg:.1f}" if avg else "-"}</div>
            <div style="font-size:10px;color:#6ee7b7;">Moyenne</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    
    # Graphiques
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Radar", "⚖️ Poids", "📈 Évolution", "📅 Calendrier"])
    
    with tab1:
        compare_type = st.selectbox("Comparer avec", ["Équipe", "Avants", "Trois-quarts", get_player_line(player['position']), player['position']], key="modal_compare")
        
        if compare_type == "Équipe":
            compare_avg = get_team_avg(sel_date)
        elif compare_type in ["Avants", "Trois-quarts"]:
            compare_avg = get_team_avg(sel_date, group=compare_type)
        elif compare_type == player['position']:
            compare_avg = get_team_avg(sel_date, position=compare_type)
        else:
            compare_avg = get_team_avg(sel_date, line=compare_type)
        
        player_data = {m['key']: pd.get(m['key'], 0) for m in METRICS}
        fig = create_radar_chart(player_data, compare_avg, player['name'], compare_type)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        weight_fig = create_weight_chart(player['name'])
        if weight_fig:
            st.plotly_chart(weight_fig, use_container_width=True)
        else:
            st.info("Pas de données de poids disponibles")
    
    with tab3:
        metric_sel = st.selectbox("Métrique", ['global'] + [m['key'] for m in METRICS],
            format_func=lambda x: "⚡ Global" if x == 'global' else next((f"{m['icon']} {m['label']}" for m in METRICS if m['key'] == x), x),
            key="modal_evol_metric")
        
        evol_fig = create_metrics_evolution_chart(player['name'], metric_sel)
        if evol_fig:
            st.plotly_chart(evol_fig, use_container_width=True)
        else:
            st.info("Pas assez de données")
    
    with tab4:
        now = datetime.now()
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            cal_month = st.selectbox("Mois", range(1, 13), index=now.month - 1, 
                format_func=lambda x: ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'][x-1],
                key="cal_month")
        with col_m2:
            cal_year = st.selectbox("Année", [now.year - 1, now.year, now.year + 1], index=1, key="cal_year")
        
        calendar_html = create_wellness_calendar(player['name'], cal_year, cal_month)
        st.markdown(calendar_html, unsafe_allow_html=True)
        st.caption("🟢 ≥4 | 🟡 3-4 | 🔴 <3 | ⬜ Pas de données")
    
    # Remarque
    if pd.get('remark'):
        st.markdown(f"""
        <div class="glass-card" style="margin-top:20px;">
            <div style="font-size:12px;color:#64748b;margin-bottom:6px;">💬 Remarque du jour</div>
            <div style="color:white;font-size:14px;">{pd['remark']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    
    # Modifier statut
    st.markdown("#### 🔄 Modifier le statut")
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
    """Page principale - Dashboard"""
    st.markdown("# 📊 Dashboard Wellness")
    
    dates = sorted(st.session_state.data.keys(), reverse=True)
    if not dates:
        st.markdown("""
        <div class="premium-card" style="text-align:center;padding:4rem;">
            <div style="font-size:80px;margin-bottom:1rem;">🏉</div>
            <h2 style="color:white;margin-bottom:1rem;">Bienvenue dans Wellness Tracker !</h2>
            <p style="color:#94a3b8;font-size:16px;margin-bottom:2rem;">
                Commencez par importer vos données depuis Google Sheets pour suivre le bien-être de vos joueurs.
            </p>
            <p style="color:#64748b;font-size:14px;">
                👈 Allez dans <b>📥 Import</b> dans le menu latéral
            </p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Sélecteur de date
    col1, col2 = st.columns([3, 1])
    with col2:
        date_key = st.selectbox("", dates, format_func=lambda x: format_date(x, 'full'), key="dash_date", label_visibility="collapsed")
    
    today_data = st.session_state.data.get(date_key, [])
    team = get_team_avg(date_key)
    
    # === MOYENNE ÉQUIPE - Hero Card ===
    if team:
        metrics_html = ''.join([
            f'''<div style="text-align:center;min-width:80px;">
                <div style="font-size:30px;margin-bottom:4px;">{m["icon"]}</div>
                <div style="font-size:24px;font-weight:bold;color:white;">{fmt_val(team.get(m["key"]))}</div>
                <div style="font-size:11px;color:rgba(255,255,255,0.7);">{m["label"]}</div>
            </div>'''
            for m in METRICS
        ])
        
        global_val = team.get('global')
        global_str = f"{global_val:.2f}" if global_val else "-"
        
        st.markdown(f"""
        <div class="team-avg-card">
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:2rem;position:relative;z-index:1;">
                <div>
                    <div style="color:rgba(255,255,255,0.8);font-size:13px;font-weight:600;text-transform:uppercase;letter-spacing:2px;margin-bottom:8px;">⚡ Moyenne Équipe</div>
                    <div style="font-size:4.5rem;font-weight:800;color:white;line-height:1;">{global_str}<span style="font-size:1.8rem;color:rgba(255,255,255,0.6);">/5</span></div>
                    <div style="color:rgba(255,255,255,0.7);font-size:15px;margin-top:8px;">📊 {team.get('count', 0)} joueurs aujourd'hui</div>
                </div>
                <div style="display:flex;gap:28px;flex-wrap:wrap;">{metrics_html}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # === ALERTES + DISPONIBILITÉ ===
    col_alerts, col_avail = st.columns([2, 1])
    
    with col_alerts:
        alerts = get_alerts(date_key)
        alert_count = len(alerts)
        
        # Compter les joueurs uniques avec alertes
        unique_players_with_alerts = len(set(a['player'] for a in alerts)) if alerts else 0
        
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">
            <h3 style="margin:0;color:white;">⚠️ Alertes du jour</h3>
            {f'<span style="background:linear-gradient(135deg,#ef4444,#dc2626);color:white;padding:5px 14px;border-radius:20px;font-size:13px;font-weight:600;box-shadow:0 2px 8px rgba(239,68,68,0.3);">{unique_players_with_alerts} joueurs</span>' if alert_count else ''}
        </div>
        """, unsafe_allow_html=True)
        
        if alerts:
            by_player = {}
            for a in alerts:
                by_player.setdefault(a['player'], []).append(a)
            
            # Conteneur scrollable
            st.markdown('<div style="max-height:350px;overflow-y:auto;padding-right:8px;">', unsafe_allow_html=True)
            
            for player_name, player_alerts in by_player.items():
                msgs = " • ".join([a['message'] for a in player_alerts])
                has_critical = any(a['type'] == 'critical' for a in player_alerts)
                
                if has_critical:
                    bg = 'linear-gradient(135deg, rgba(239,68,68,0.15), rgba(220,38,38,0.1))'
                    border_color = 'rgba(239,68,68,0.4)'
                    badge = '🔴 CRITIQUE'
                else:
                    bg = 'linear-gradient(135deg, rgba(245,158,11,0.15), rgba(217,119,6,0.1))'
                    border_color = 'rgba(245,158,11,0.4)'
                    badge = '🟡 Attention'
                
                st.markdown(f"""
                <div style="background:{bg};border:1px solid {border_color};border-radius:12px;padding:12px 16px;margin-bottom:10px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                        <span style="font-weight:600;color:white;font-size:14px;">{player_name}</span>
                        <span style="font-size:10px;font-weight:600;text-transform:uppercase;opacity:0.8;color:white;">{badge}</span>
                    </div>
                    <div style="font-size:12px;color:rgba(255,255,255,0.85);">{msgs}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="glass-card" style="text-align:center;padding:2.5rem;">
                <div style="font-size:50px;margin-bottom:12px;">✅</div>
                <div style="color:#10b981;font-weight:600;font-size:16px;">Aucune alerte</div>
                <div style="color:#64748b;font-size:13px;margin-top:4px;">Tous les joueurs sont en forme !</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col_avail:
        st.markdown("<h3 style='color:white;margin-bottom:16px;'>👥 Disponibilité</h3>", unsafe_allow_html=True)
        
        avail_data = get_availability_data()
        if avail_data:
            fig = create_availability_chart()
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            
            legend_html = "".join([
                f'<div style="display:flex;align-items:center;gap:6px;margin-bottom:6px;"><span style="width:12px;height:12px;border-radius:3px;background:{d["color"]};"></span><span style="color:#94a3b8;font-size:12px;">{d["name"]}: <b style="color:white">{d["value"]}</b></span></div>'
                for d in avail_data
            ])
            st.markdown(f'<div style="padding:0 10px;">{legend_html}</div>', unsafe_allow_html=True)
    
    st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)
    
    # === FILTRES ===
    st.markdown("<h3 style='color:white;margin-bottom:16px;'>📋 Vue équipe</h3>", unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns([1.5, 1.5, 1.5, 1])
    with c1:
        sort_by = st.selectbox("Trier par", ["Nom A→Z", "🚨 Alertes d'abord", "📉 Moyenne (↑)", "👥 Par groupe"], key="sort", label_visibility="collapsed")
    with c2:
        filter_group = st.selectbox("Groupe", ["Tous les groupes", "Avants", "Trois-quarts"], key="fg", label_visibility="collapsed")
    with c3:
        filter_line = st.selectbox("Ligne", ["Toutes les lignes"] + ALL_LINES, key="fl", label_visibility="collapsed")
    with c4:
        show_issues = st.checkbox("⚠️ Problèmes", key="si")
    
    # === TABLEAU DES JOUEURS ===
    rows = []
    player_ids = {}
    
    for d in today_data:
        p = next((p for p in st.session_state.players if p['name'] == d['name']), None)
        if not p:
            continue
        if filter_group not in ["Tous les groupes", "Tous"] and get_player_group(p['position']) != filter_group:
            continue
        if filter_line not in ["Toutes les lignes", "Toutes"] and get_player_line(p['position']) != filter_line:
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
    if sort_by == "🚨 Alertes d'abord":
        rows.sort(key=lambda x: (not x['has_issue'], x['avg'] or 5))
    elif sort_by == "📉 Moyenne (↑)":
        rows.sort(key=lambda x: x['avg'] or 5)
    elif sort_by == "👥 Par groupe":
        rows.sort(key=lambda x: (x['group'], x['name']))
    else:
        rows.sort(key=lambda x: x['name'])
    
    # Affichage
    if rows:
        st.markdown(f"<div style='color:#64748b;font-size:13px;margin-bottom:12px;'>{len(rows)} joueurs affichés</div>", unsafe_allow_html=True)
        
        # En-têtes des colonnes
        st.markdown("""
        <div style="display:grid;grid-template-columns:190px 65px 55px repeat(5, 38px) 45px 42px 1fr;gap:6px;align-items:center;padding:8px 16px;margin-bottom:4px;color:#64748b;font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;">
            <span>Joueur</span>
            <span style="text-align:center;">Statut</span>
            <span style="text-align:center;">Poids</span>
            <span style="text-align:center;">😴</span>
            <span style="text-align:center;">🧠</span>
            <span style="text-align:center;">💪</span>
            <span style="text-align:center;">❤️</span>
            <span style="text-align:center;">💚</span>
            <span style="text-align:center;">Moy.</span>
            <span style="text-align:center;">Δ</span>
            <span>💬 Remarque</span>
        </div>
        """, unsafe_allow_html=True)
        
        for idx, row in enumerate(rows):
            # Métriques badges
            metrics_html = ""
            for m in METRICS:
                val = row['metrics'].get(m['key'])
                color = get_color_for_value(val)
                metrics_html += f'<span style="display:inline-flex;align-items:center;justify-content:center;width:36px;height:36px;border-radius:8px;background:{color};color:white;font-weight:600;font-size:14px;">{int(val) if val else "-"}</span>'
            
            # Moyenne + diff
            avg_color = get_color_for_value(row['avg'])
            avg_str = f"{row['avg']:.1f}" if row['avg'] else "-"
            
            diff_str = ""
            if row['diff'] is not None:
                diff_color = "#10b981" if row['diff'] >= 0 else "#ef4444"
                diff_str = f'<span style="color:{diff_color};font-size:12px;font-weight:600;">{("+" if row["diff"] >= 0 else "")}{row["diff"]:.1f}</span>'
            
            # Status badge
            status_colors = {'Apte': '#10b981', 'Blessé': '#ef4444', 'Réhabilitation': '#f59e0b', 'Réathlétisation': '#3b82f6'}
            status_color = status_colors.get(row['status'], '#64748b')
            group_abbr = "Av" if row['group'] == "Avants" else "3/4"
            avatar_class = get_avatar_gradient(row['name'])
            
            # Poids
            weight_str = f"{row['weight']:.1f}" if row['weight'] else "-"
            
            # Remarque
            remark_full = row['remark'] if row['remark'] else ""
            remark_truncated = remark_full[:30] + "…" if len(remark_full) > 30 else remark_full
            has_remark = bool(remark_full)
            remark_bg = "background:rgba(99,102,241,0.12);padding:3px 8px;border-radius:5px;" if has_remark else ""
            
            # Layout uniforme pour tous
            col_main, col_btns = st.columns([5.8, 1.2])
            
            with col_main:
                st.markdown(f"""
                <div class="player-row {'has-alert' if row['has_issue'] else ''}" style="padding:10px 16px;">
                    <div style="display:grid;grid-template-columns:190px 65px 55px repeat(5, 38px) 45px 42px 1fr;gap:6px;align-items:center;">
                        <div style="display:flex;align-items:center;gap:10px;">
                            <div class="player-avatar {avatar_class}" style="width:36px;height:36px;font-size:15px;">{row['name'][0]}</div>
                            <div>
                                <div style="font-weight:600;color:white;font-size:13px;">{row['name']}</div>
                                <div style="font-size:10px;color:#64748b;">{row['position']} ({group_abbr})</div>
                            </div>
                        </div>
                        <span style="display:inline-block;padding:3px 8px;border-radius:20px;font-size:9px;font-weight:600;background:{status_color};color:white;text-align:center;">{row['status']}</span>
                        <span style="color:#94a3b8;font-size:12px;text-align:center;">{weight_str}</span>
                        {metrics_html}
                        <span style="display:inline-flex;align-items:center;justify-content:center;width:38px;height:34px;border-radius:8px;background:{avg_color};color:white;font-weight:600;font-size:12px;">{avg_str}</span>
                        <span style="text-align:center;min-width:40px;">{diff_str}</span>
                        <div style="{remark_bg}color:#cbd5e1;font-size:10px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;" title="{remark_full}">{remark_truncated if has_remark else '—'}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_btns:
                # Deux petits boutons côte à côte, toujours présents
                b1, b2 = st.columns(2)
                with b1:
                    if st.button("👁️", key=f"fiche_{idx}", help=f"Fiche {row['name']}"):
                        show_player_modal(player_ids[row['name']])
                with b2:
                    if has_remark:
                        with st.popover("💬", help="Voir remarque"):
                            st.markdown(f"""
                            <div style="min-width:280px;max-width:400px;">
                                <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">
                                    <div class="player-avatar {avatar_class}" style="width:32px;height:32px;font-size:14px;">{row['name'][0]}</div>
                                    <span style="font-weight:600;color:white;font-size:14px;">{row['name']}</span>
                                </div>
                                <div style="background:rgba(99,102,241,0.15);padding:14px;border-radius:10px;color:#e2e8f0;font-size:13px;line-height:1.6;">{remark_full}</div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        # Placeholder invisible pour garder l'alignement
                        st.write("")
    else:
        st.info("Aucun joueur ne correspond aux filtres sélectionnés.")
    
    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
    
    # === GRAPHIQUES ===
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Tendance Wellness")
        
        # Option pour choisir le type de graphique
        chart_type = st.radio("Type d'affichage", ["📊 Z-Score (vs moyenne)", "📈 Valeurs absolues (0-5)"], horizontal=True, key="chart_type")
        
        mc1, mc2, mc3 = st.columns(3)
        with mc1:
            zmetric = st.selectbox("Métrique", ['global'] + [m['key'] for m in METRICS],
                format_func=lambda x: "⚡ Global" if x == 'global' else next((f"{m['icon']} {m['label']}" for m in METRICS if m['key'] == x), x), key="zm")
        with mc2:
            zgroup = st.selectbox("Groupe", ["Équipe", "Avants", "Trois-quarts"], key="zg")
        with mc3:
            zdays = st.selectbox("Période", [7, 14, 30, 60], index=2, format_func=lambda x: f"{x} jours", key="zd")
        
        if chart_type == "📊 Z-Score (vs moyenne)":
            zdata = zscore_series(metric=zmetric, group=None if zgroup == "Équipe" else zgroup, days=zdays)
            fig = create_zscore_chart(zdata)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
                st.caption("🟢 Normal (≥ -1) | 🟡 Attention (-1.5 à -1) | 🔴 Alerte (< -1.5)")
            else:
                st.info("Pas assez de données (minimum 5 jours)")
        else:
            # Graphique valeurs absolues
            abs_data = get_absolute_values_series(metric=zmetric, group=None if zgroup == "Équipe" else zgroup, days=zdays)
            fig = create_absolute_values_chart(abs_data)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
                st.caption("🟢 Excellent (≥4) | 🟡 Correct (3-4) | 🔴 Faible (<3)")
            else:
                st.info("Pas assez de données")
    
    with col2:
        st.markdown("### 📊 Comparaison Radar")
        rc1, rc2 = st.columns(2)
        with rc1:
            cmp1 = st.selectbox("Groupe 1", ["Équipe", "Avants", "Trois-quarts"], key="r1")
        with rc2:
            cmp2 = st.selectbox("Groupe 2", ["Équipe", "Avants", "Trois-quarts"], index=1, key="r2")
        
        d1 = get_team_avg(date_key, group=None if cmp1 == "Équipe" else cmp1)
        d2 = get_team_avg(date_key, group=None if cmp2 == "Équipe" else cmp2)
        
        if d1 or d2:
            st.plotly_chart(create_radar_chart(d1, d2, cmp1, cmp2), use_container_width=True)
        else:
            st.info("Pas de données pour la comparaison")


def page_import():
    """Page d'import/export"""
    st.markdown("# 📥 Import / Export")
    
    # === GOOGLE SHEETS ===
    st.markdown("""
    <div class="premium-card">
        <h3 style="color:white;margin-bottom:20px;">📊 Importer depuis Google Sheets</h3>
    """, unsafe_allow_html=True)
    
    url = st.text_input(
        "URL du Google Sheet",
        value="https://docs.google.com/spreadsheets/d/1Esm3NnED51jFpTs-oSjIdVybH51BSEcjhWOQhP1P3zI/edit?usp=sharing",
        help="Collez l'URL complète de votre Google Sheet (doit être partagé en lecture publique)"
    )
    
    # Choix du mode d'import
    import_mode = st.radio(
        "Mode d'import",
        ["📅 Dernier jour (Bien-être)", "📆 Historique (Suivi BE)", "⚖️ Suivi Poids"],
        horizontal=True,
        help="Choisissez le type de données à importer"
    )
    
    # Nom de l'onglet selon le mode
    if import_mode == "📅 Dernier jour (Bien-être)":
        sheet_name = st.text_input("Nom de l'onglet", value="Bien-être", key="sheet_bienetre")
    elif import_mode == "📆 Historique (Suivi BE)":
        sheet_name = st.text_input("Nom de l'onglet", value="Suivi BE", key="sheet_suivi")
    else:  # Suivi Poids
        sheet_name = st.text_input("Nom de l'onglet", value="Suivi Poids", key="sheet_poids")
    
    debug_mode = st.checkbox("🔧 Mode debug (affiche les détails du parsing)", value=False)
    
    # === MODE BIEN-ÊTRE (dernier jour) ===
    if import_mode == "📅 Dernier jour (Bien-être)":
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("👁️ Voir le contenu brut", use_container_width=True, key="view_bienetre"):
                try:
                    match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
                    if match:
                        doc_id = match.group(1)
                        encoded_sheet = urllib.parse.quote(sheet_name)
                        csv_url = f"https://docs.google.com/spreadsheets/d/{doc_id}/gviz/tq?tqx=out:csv&sheet={encoded_sheet}"
                        
                        df = pd.read_csv(csv_url, header=None)
                        st.success(f"✅ {len(df)} lignes × {len(df.columns)} colonnes")
                        
                        st.markdown("**Premières lignes (avec index de colonnes):**")
                        for i in range(min(10, len(df))):
                            row_vals = []
                            for j in range(min(12, len(df.columns))):
                                val = df.iloc[i, j]
                                if pd.notna(val):
                                    row_vals.append(f"[{j}]`{val}`")
                            st.write(f"**L{i}:** {' | '.join(row_vals)}")
                        
                        st.dataframe(df.head(15))
                except Exception as e:
                    st.error(f"Erreur: {e}")
        
        with col2:
            if st.button("📥 Importer les données", type="primary", use_container_width=True, key="import_bienetre"):
                try:
                    match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
                    if not match:
                        st.error("❌ URL invalide")
                    else:
                        doc_id = match.group(1)
                        encoded_sheet = urllib.parse.quote(sheet_name)
                        csv_url = f"https://docs.google.com/spreadsheets/d/{doc_id}/gviz/tq?tqx=out:csv&sheet={encoded_sheet}"
                        
                        with st.spinner("📡 Téléchargement..."):
                            df = pd.read_csv(csv_url, header=None)
                        
                        st.success(f"✅ {len(df)} lignes téléchargées")
                        
                        with st.spinner("🔄 Traitement..."):
                            result = process_imported_data(df, debug=debug_mode)
                        
                        if result['success']:
                            st.balloons()
                            cols_found = result.get('columns_found', [])
                            st.success(f"""
                            ✅ **Import réussi !**
                            - 📅 Date: **{format_date(result['date'], 'full')}**
                            - 👥 {result['players']} joueurs ({result['new_players']} nouveaux)
                            - 📊 {result['entries']} entrées
                            - 🔍 Colonnes détectées: {', '.join(cols_found)}
                            """)
                        else:
                            st.error(f"❌ Erreur: {result['error']}")
                            
                except Exception as e:
                    st.error(f"❌ Erreur: {str(e)}")
    
    # === MODE SUIVI BE (historique) ===
    elif import_mode == "📆 Historique (Suivi BE)":
        st.markdown("""
        <div style="background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.3);border-radius:8px;padding:12px;margin-bottom:16px;">
            <div style="color:#60a5fa;font-weight:600;">📆 Import historique</div>
            <div style="color:#94a3b8;font-size:13px;">Les données de l'onglet "Suivi BE" contiennent plusieurs jours côte à côte. Sélectionnez les dates à importer.</div>
        </div>
        """, unsafe_allow_html=True)
        
        col_scan1, col_scan2 = st.columns(2)
        
        with col_scan1:
            # Bouton pour voir le contenu brut
            if st.button("👁️ Voir le contenu brut", use_container_width=True, key="view_suivi"):
                try:
                    match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
                    if match:
                        doc_id = match.group(1)
                        encoded_sheet = urllib.parse.quote(sheet_name)
                        csv_url = f"https://docs.google.com/spreadsheets/d/{doc_id}/gviz/tq?tqx=out:csv&sheet={encoded_sheet}"
                        
                        df = pd.read_csv(csv_url, header=None)
                        st.success(f"✅ {len(df)} lignes × {len(df.columns)} colonnes")
                        
                        st.markdown("**Premières lignes (avec index de colonnes):**")
                        for i in range(min(8, len(df))):
                            row_vals = []
                            for j in range(min(20, len(df.columns))):
                                val = df.iloc[i, j]
                                if pd.notna(val):
                                    val_str = str(val)[:15]
                                    row_vals.append(f"[{j}]`{val_str}`")
                            st.write(f"**L{i}:** {' | '.join(row_vals)}")
                        
                        st.dataframe(df.iloc[:10, :15])
                except Exception as e:
                    st.error(f"Erreur: {e}")
        
        with col_scan2:
            # Étape 1: Scanner les dates disponibles
            if st.button("🔍 Scanner les dates disponibles", use_container_width=True, key="scan_dates"):
                try:
                    match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
                    if not match:
                        st.error("❌ URL invalide")
                    else:
                        doc_id = match.group(1)
                        encoded_sheet = urllib.parse.quote(sheet_name)
                        csv_url = f"https://docs.google.com/spreadsheets/d/{doc_id}/gviz/tq?tqx=out:csv&sheet={encoded_sheet}"
                        
                        with st.spinner("📡 Téléchargement..."):
                            df = pd.read_csv(csv_url, header=None)
                        
                        st.success(f"✅ {len(df)} lignes × {len(df.columns)} colonnes")
                        
                        with st.spinner("🔍 Analyse des dates..."):
                            result = process_suivi_be_data(df, selected_dates=None, debug=debug_mode)
                        
                        if result['success'] and result.get('mode') == 'list_dates':
                            st.session_state['suivi_be_dates'] = result['available_dates']
                            st.session_state['suivi_be_df'] = df
                            st.success(f"✅ {len(result['available_dates'])} dates trouvées !")
                        else:
                            st.error(f"❌ Erreur: {result.get('error', 'Erreur inconnue')}")
                            
                except Exception as e:
                    st.error(f"❌ Erreur: {str(e)}")
        
        # Étape 2: Afficher les dates et permettre la sélection
        if 'suivi_be_dates' in st.session_state and st.session_state['suivi_be_dates']:
            available_dates = st.session_state['suivi_be_dates']
            
            st.markdown(f"### 📅 {len(available_dates)} dates disponibles")
            
            # Initialiser le compteur pour forcer le refresh du multiselect
            if 'multiselect_key' not in st.session_state:
                st.session_state['multiselect_key'] = 0
            
            # Options de sélection rapide
            col_sel1, col_sel2, col_sel3 = st.columns(3)
            with col_sel1:
                if st.button("✅ Tout sélectionner", use_container_width=True):
                    st.session_state['selected_suivi_dates'] = [d['date'] for d in available_dates]
                    st.session_state['multiselect_key'] += 1  # Force refresh
                    st.rerun()
            with col_sel2:
                if st.button("❌ Tout désélectionner", use_container_width=True):
                    st.session_state['selected_suivi_dates'] = []
                    st.session_state['multiselect_key'] += 1
                    st.rerun()
            with col_sel3:
                if st.button("📅 7 derniers jours", use_container_width=True):
                    st.session_state['selected_suivi_dates'] = [d['date'] for d in available_dates[-7:]]
                    st.session_state['multiselect_key'] += 1
                    st.rerun()
            
            # Multi-select des dates avec clé dynamique
            date_options = {d['date']: d['label'] for d in available_dates}
            default_selection = st.session_state.get('selected_suivi_dates', [])
            
            # Utiliser une clé dynamique pour forcer le refresh
            selected = st.multiselect(
                "Sélectionnez les dates à importer",
                options=list(date_options.keys()),
                default=[d for d in default_selection if d in date_options],
                format_func=lambda x: date_options.get(x, x),
                key=f"date_multiselect_{st.session_state['multiselect_key']}"
            )
            
            # Mettre à jour la sélection
            st.session_state['selected_suivi_dates'] = selected
            
            # Afficher le nombre sélectionné
            st.info(f"📊 **{len(selected)} date(s) sélectionnée(s)**")
            
            # Bouton d'import (toujours visible)
            if st.button(f"📥 Importer les dates sélectionnées", type="primary", use_container_width=True, key="import_suivi", disabled=(len(selected) == 0)):
                if not selected:
                    st.warning("⚠️ Sélectionnez au moins une date")
                else:
                    try:
                        df = st.session_state.get('suivi_be_df')
                        if df is None:
                            st.error("❌ Données non chargées. Veuillez rescanner les dates.")
                        else:
                            with st.spinner(f"🔄 Import de {len(selected)} jours..."):
                                result = process_suivi_be_data(df, selected_dates=selected, debug=debug_mode)
                            
                            if result['success'] and result.get('mode') == 'imported':
                                st.balloons()
                                st.success(f"""
                                ✅ **Import réussi !**
                                - 📅 Jours importés: **{len(result['dates_imported'])}**
                                - 👥 {result['players']} joueurs ({result['new_players']} nouveaux)
                                - 📊 {result['entries']} entrées au total
                                """)
                                
                                # Auto-save après import
                                save_success, save_msg = save_data_to_file()
                                if save_success:
                                    st.info(f"💾 {save_msg}")
                                
                                with st.expander("📋 Détail des dates importées"):
                                    for d in result['dates_imported']:
                                        st.write(f"• {d}")
                                
                                # Nettoyer le cache
                                if 'suivi_be_dates' in st.session_state:
                                    del st.session_state['suivi_be_dates']
                                if 'suivi_be_df' in st.session_state:
                                    del st.session_state['suivi_be_df']
                                if 'selected_suivi_dates' in st.session_state:
                                    del st.session_state['selected_suivi_dates']
                            else:
                                st.error(f"❌ Erreur: {result.get('error', 'Erreur inconnue')}")
                                
                    except Exception as e:
                        st.error(f"❌ Erreur: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())
            
            if not selected:
                st.warning("👆 Sélectionnez au moins une date pour importer")
    
    # === MODE SUIVI POIDS ===
    elif import_mode == "⚖️ Suivi Poids":
        st.markdown("""
        <div style="background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.3);border-radius:8px;padding:12px;margin-bottom:16px;">
            <div style="color:#fbbf24;font-weight:600;">⚖️ Import du suivi de poids</div>
            <div style="color:#94a3b8;font-size:13px;">Met à jour le poids des joueurs <b>existants</b> aux dates correspondantes. Les joueurs doivent déjà avoir des données wellness importées.</div>
        </div>
        """, unsafe_allow_html=True)
        
        col_scan1, col_scan2 = st.columns(2)
        
        with col_scan1:
            if st.button("👁️ Voir le contenu brut", use_container_width=True, key="view_poids"):
                try:
                    match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
                    if match:
                        doc_id = match.group(1)
                        encoded_sheet = urllib.parse.quote(sheet_name)
                        csv_url = f"https://docs.google.com/spreadsheets/d/{doc_id}/gviz/tq?tqx=out:csv&sheet={encoded_sheet}"
                        
                        df = pd.read_csv(csv_url, header=None)
                        st.success(f"✅ {len(df)} lignes × {len(df.columns)} colonnes")
                        
                        st.markdown("**Premières lignes:**")
                        st.dataframe(df.iloc[:15, :15])
                except Exception as e:
                    st.error(f"Erreur: {e}")
        
        with col_scan2:
            if st.button("🔍 Scanner les dates disponibles", use_container_width=True, key="scan_poids"):
                try:
                    match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
                    if not match:
                        st.error("❌ URL invalide")
                    else:
                        doc_id = match.group(1)
                        encoded_sheet = urllib.parse.quote(sheet_name)
                        csv_url = f"https://docs.google.com/spreadsheets/d/{doc_id}/gviz/tq?tqx=out:csv&sheet={encoded_sheet}"
                        
                        with st.spinner("📡 Téléchargement..."):
                            df = pd.read_csv(csv_url, header=None)
                        
                        st.success(f"✅ {len(df)} lignes × {len(df.columns)} colonnes")
                        
                        with st.spinner("🔍 Analyse des dates..."):
                            result = process_suivi_poids_data(df, selected_dates=None, debug=debug_mode)
                        
                        if result['success'] and result.get('mode') == 'list_dates':
                            st.session_state['suivi_poids_dates'] = result['available_dates']
                            st.session_state['suivi_poids_df'] = df
                            st.success(f"✅ {len(result['available_dates'])} dates trouvées !")
                        else:
                            st.error(f"❌ Erreur: {result.get('error', 'Erreur inconnue')}")
                            
                except Exception as e:
                    st.error(f"❌ Erreur: {str(e)}")
        
        # Étape 2: Afficher les dates et permettre la sélection
        if 'suivi_poids_dates' in st.session_state and st.session_state['suivi_poids_dates']:
            available_dates = st.session_state['suivi_poids_dates']
            
            st.markdown(f"### 📅 {len(available_dates)} dates disponibles")
            
            # Vérifier les dates qui ont déjà des données wellness
            dates_with_data = set(st.session_state.data.keys())
            dates_with_match = [d for d in available_dates if d['date'] in dates_with_data]
            dates_without_match = [d for d in available_dates if d['date'] not in dates_with_data]
            
            if dates_without_match:
                st.warning(f"⚠️ {len(dates_without_match)} dates n'ont pas de données wellness correspondantes et seront ignorées")
            
            # Initialiser le compteur
            if 'poids_multiselect_key' not in st.session_state:
                st.session_state['poids_multiselect_key'] = 0
            
            # Options de sélection rapide
            col_sel1, col_sel2, col_sel3 = st.columns(3)
            with col_sel1:
                if st.button("✅ Tout sélectionner", use_container_width=True, key="sel_all_poids"):
                    st.session_state['selected_poids_dates'] = [d['date'] for d in dates_with_match]
                    st.session_state['poids_multiselect_key'] += 1
                    st.rerun()
            with col_sel2:
                if st.button("❌ Tout désélectionner", use_container_width=True, key="desel_all_poids"):
                    st.session_state['selected_poids_dates'] = []
                    st.session_state['poids_multiselect_key'] += 1
                    st.rerun()
            with col_sel3:
                if st.button("📅 7 derniers jours", use_container_width=True, key="sel_7_poids"):
                    st.session_state['selected_poids_dates'] = [d['date'] for d in dates_with_match[-7:]]
                    st.session_state['poids_multiselect_key'] += 1
                    st.rerun()
            
            # Multi-select des dates (seulement celles avec données wellness)
            date_options = {d['date']: f"{d['label']} ✓" for d in dates_with_match}
            default_selection = st.session_state.get('selected_poids_dates', [])
            
            selected = st.multiselect(
                "Sélectionnez les dates à importer (✓ = données wellness existantes)",
                options=list(date_options.keys()),
                default=[d for d in default_selection if d in date_options],
                format_func=lambda x: date_options.get(x, x),
                key=f"poids_multiselect_{st.session_state['poids_multiselect_key']}"
            )
            
            st.session_state['selected_poids_dates'] = selected
            st.info(f"📊 **{len(selected)} date(s) sélectionnée(s)**")
            
            # Bouton d'import
            if st.button(f"⚖️ Importer les poids", type="primary", use_container_width=True, key="import_poids", disabled=(len(selected) == 0)):
                if not selected:
                    st.warning("⚠️ Sélectionnez au moins une date")
                else:
                    try:
                        df = st.session_state.get('suivi_poids_df')
                        if df is None:
                            st.error("❌ Données non chargées. Veuillez rescanner les dates.")
                        else:
                            with st.spinner(f"🔄 Import du poids pour {len(selected)} jours..."):
                                result = process_suivi_poids_data(df, selected_dates=selected, debug=debug_mode)
                            
                            if result['success'] and result.get('mode') == 'imported':
                                st.balloons()
                                st.success(f"""
                                ✅ **Import du poids réussi !**
                                - 📅 Jours mis à jour: **{len(result['dates_imported'])}**
                                - 👥 Joueurs avec poids: **{result['players_updated']}**
                                - ⚖️ {result['entries']} valeurs de poids importées
                                """)
                                
                                # Auto-save
                                save_success, save_msg = save_data_to_file()
                                if save_success:
                                    st.info(f"💾 {save_msg}")
                                
                                # Nettoyer le cache
                                if 'suivi_poids_dates' in st.session_state:
                                    del st.session_state['suivi_poids_dates']
                                if 'suivi_poids_df' in st.session_state:
                                    del st.session_state['suivi_poids_df']
                                if 'selected_poids_dates' in st.session_state:
                                    del st.session_state['selected_poids_dates']
                            else:
                                st.error(f"❌ Erreur: {result.get('error', 'Erreur inconnue')}")
                                
                    except Exception as e:
                        st.error(f"❌ Erreur: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())
            
            if not selected:
                st.warning("👆 Sélectionnez au moins une date pour importer les poids")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Info box sur le format attendu
    with st.expander("ℹ️ Formats attendus"):
        st.markdown("""
        ### 📅 Format "Bien-être" (dernier jour)
        - **Ligne 1-2**: Date (ex: "mardi 6 janvier 2026")
        - **Ligne 3**: En-têtes (Joueur, Poids, Sommeil, Charge mentale, Motivation, HDC, BDC, Remarque)
        - **Ligne 4**: EQUIPE (ignorée)
        - **Lignes 5+**: Données des joueurs
        
        ### 📆 Format "Suivi BE" (historique)
        - Les jours sont **côte à côte horizontalement**
        - Chaque bloc contient: Date → En-têtes → EQUIPE → Joueurs
        - Pas de colonne Poids (seulement les métriques wellness)
        
        ### ⚖️ Format "Suivi Poids"
        - **Ligne 1**: Vide puis dates (23/06, 24/06, etc.)
        - **Colonne A**: Noms des joueurs (doivent correspondre aux joueurs existants)
        - **Cellules**: Poids en kg
        - ⚠️ Les joueurs doivent déjà avoir des données wellness pour les dates concernées
        
        **Colonnes reconnues :** Joueur, Sommeil, Charge mentale, Motivation, HDC, BDC, Remarque
        """)
    
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    
    # === EXCEL ===
    st.markdown("""
    <div class="premium-card">
        <h3 style="color:white;margin-bottom:20px;">📄 Importer un fichier Excel/CSV</h3>
    """, unsafe_allow_html=True)
    
    uploaded = st.file_uploader("Glissez votre fichier ici", type=['xlsx', 'xls', 'csv'], label_visibility="collapsed")
    
    if uploaded:
        try:
            if uploaded.name.endswith('.csv'):
                df = pd.read_csv(uploaded, header=None)
            else:
                df = pd.read_excel(uploaded, header=None)
            
            st.info(f"📊 Fichier chargé: {len(df)} lignes × {len(df.columns)} colonnes")
            
            if st.button("📥 Traiter le fichier", use_container_width=True):
                with st.spinner("Traitement..."):
                    result = process_imported_data(df, debug=debug_mode)
                
                if result['success']:
                    st.balloons()
                    st.success(f"✅ Import réussi ! {result['entries']} joueurs pour le {format_date(result['date'], 'full')}")
                    # Auto-save après import
                    save_success, save_msg = save_data_to_file()
                    if save_success:
                        st.info(f"💾 {save_msg}")
                else:
                    st.error(f"❌ {result['error']}")
        except Exception as e:
            st.error(f"❌ Erreur de lecture: {e}")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    
    # === EXPORT ===
    if st.session_state.data:
        st.markdown("""
        <div class="premium-card">
            <h3 style="color:white;margin-bottom:20px;">📤 Exporter les données</h3>
        """, unsafe_allow_html=True)
        
        export_rows = []
        for date, entries in st.session_state.data.items():
            for e in entries:
                export_rows.append({
                    'Date': date,
                    'Joueur': e.get('name'),
                    'Poids': e.get('weight'),
                    **{m['label']: e.get(m['key']) for m in METRICS},
                    'Remarque': e.get('remark', '')
                })
        
        if export_rows:
            export_df = pd.DataFrame(export_rows)
            csv = export_df.to_csv(index=False).encode('utf-8')
            
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.download_button("📥 Télécharger CSV", csv, "wellness_export.csv", "text/csv", use_container_width=True)
            with col2:
                st.metric("📊 Entrées", len(export_rows))
            with col3:
                st.metric("📅 Jours", len(st.session_state.data))
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    
    # === STOCKAGE CLOUD AUTOMATIQUE ===
    cloud_connected, cloud_id = get_cloud_status()
    
    st.markdown(f"""
    <div class="premium-card" style="border:2px solid rgba(16,185,129,0.3);background:linear-gradient(135deg,rgba(16,185,129,0.05),rgba(0,0,0,0));">
        <h3 style="color:white;margin-bottom:8px;">☁️ Synchronisation Cloud</h3>
        <div style="background:rgba(16,185,129,0.1);border-radius:8px;padding:12px;margin-bottom:16px;">
            <p style="color:#10b981;font-size:13px;margin:0;font-weight:600;">
                {"✅ Cloud actif - Données synchronisées automatiquement !" if cloud_connected else "✅ Prêt - Cliquez sur Synchroniser pour activer le cloud"}
            </p>
            <p style="color:#94a3b8;font-size:12px;margin:8px 0 0 0;">
                Les données sont partagées entre tous les utilisateurs de l'application.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col_sync1, col_sync2 = st.columns(2)
    with col_sync1:
        if st.button("☁️ Synchroniser", type="primary", use_container_width=True):
            with st.spinner("Synchronisation..."):
                success, msg = save_to_cloud()
                if success:
                    st.success(f"✅ {msg}")
                else:
                    st.error(f"❌ {msg}")
    
    with col_sync2:
        if st.button("📥 Recharger depuis le cloud", use_container_width=True, disabled=not cloud_connected):
            with st.spinner("Chargement..."):
                success, msg = load_from_cloud()
                if success:
                    st.success(f"✅ {msg}")
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")
    
    # Info dernière synchro
    if 'last_cloud_save' in st.session_state:
        st.caption(f"⏱️ Dernière synchro : {st.session_state.last_cloud_save.strftime('%d/%m/%Y %H:%M')}")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Backup JSON optionnel (caché par défaut)
    with st.expander("📦 Backup JSON manuel (optionnel)"):
        col_restore, col_save = st.columns(2)
        with col_restore:
            uploaded_json = st.file_uploader("Restaurer depuis JSON", type=['json'], key="json_upload")
            if uploaded_json:
                if st.button("✅ Restaurer", use_container_width=True):
                    content = uploaded_json.read().decode('utf-8')
                    success, msg = import_data_from_json(content)
                    if success:
                        st.success(f"✅ {msg}")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")
        with col_save:
            if st.session_state.data or st.session_state.players:
                json_data = export_data_to_json()
                st.download_button(
                    "📥 Télécharger backup JSON",
                    json_data,
                    f"wellness_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                    "application/json",
                    use_container_width=True
                )
    
    # Info stats actuelles
    if st.session_state.players or st.session_state.data:
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        with col_stat1:
            st.metric("👥 Joueurs", len(st.session_state.players))
        with col_stat2:
            st.metric("📅 Jours de données", len(st.session_state.data))
        with col_stat3:
            total_entries = sum(len(e) for e in st.session_state.data.values())
            st.metric("📊 Entrées totales", total_entries)
        with col_stat4:
            st.metric("🏥 Blessures actives", len([i for i in st.session_state.injuries if i.get('status') == 'Active']))


def page_effectif():
    """Page Effectif & Comparaisons"""
    st.markdown("# 👥 Effectif & Comparaisons")
    
    if not st.session_state.players:
        st.warning("Aucun joueur enregistré. Importez des données d'abord.")
        return
    
    tabs = st.tabs(["📋 Liste", "📊 Comparer", "📈 Évolution", "👥 Par groupe"])
    
    # === TAB LISTE ===
    with tabs[0]:
        search = st.text_input("🔍 Rechercher un joueur", key="search_eff")
        
        players = st.session_state.players
        if search:
            players = [p for p in players if search.lower() in p['name'].lower()]
        
        dates = sorted(st.session_state.data.keys(), reverse=True)
        latest_date = dates[0] if dates else None
        
        st.markdown(f"<div style='color:#64748b;font-size:13px;margin:12px 0;'>{len(players)} joueurs</div>", unsafe_allow_html=True)
        
        # En-têtes
        st.markdown("""
        <div style="display:grid;grid-template-columns:200px 80px repeat(5, 40px) 1fr;gap:8px;align-items:center;padding:8px 16px;color:#64748b;font-size:10px;font-weight:600;text-transform:uppercase;">
            <span>Joueur</span>
            <span style="text-align:center;">Statut</span>
            <span style="text-align:center;">😴</span>
            <span style="text-align:center;">🧠</span>
            <span style="text-align:center;">💪</span>
            <span style="text-align:center;">❤️</span>
            <span style="text-align:center;">💚</span>
            <span>💬 Remarque</span>
        </div>
        """, unsafe_allow_html=True)
        
        for p in sorted(players, key=lambda x: x['name']):
            pd_data = {}
            if latest_date:
                today_data = st.session_state.data.get(latest_date, [])
                pd_data = next((d for d in today_data if d['name'] == p['name']), {})
            
            status_colors = {'Apte': '#10b981', 'Blessé': '#ef4444', 'Réhabilitation': '#f59e0b', 'Réathlétisation': '#3b82f6'}
            status_color = status_colors.get(p['status'], '#64748b')
            avatar_class = get_avatar_gradient(p['name'])
            
            metrics_html = ""
            for m in METRICS:
                val = pd_data.get(m['key'])
                color = get_color_for_value(val)
                metrics_html += f'<span style="display:inline-flex;align-items:center;justify-content:center;width:36px;height:36px;border-radius:8px;background:{color};color:white;font-weight:600;font-size:14px;">{int(val) if val else "-"}</span>'
            
            # Remarque
            remark = pd_data.get('remark', '')
            remark_style = "color:#e2e8f0;background:rgba(99,102,241,0.15);padding:6px 10px;border-radius:6px;font-size:12px;" if remark else "color:#64748b;font-size:12px;"
            
            col1, col2 = st.columns([6, 1])
            
            with col1:
                st.markdown(f"""
                <div class="player-row" style="padding:10px 16px;">
                    <div style="display:grid;grid-template-columns:200px 80px repeat(5, 40px) 1fr;gap:8px;align-items:center;">
                        <div style="display:flex;align-items:center;gap:10px;">
                            <div class="player-avatar {avatar_class}" style="width:38px;height:38px;font-size:16px;">{p['name'][0]}</div>
                            <div>
                                <div style="font-weight:600;color:white;font-size:13px;">{p['name']}</div>
                                <div style="font-size:10px;color:#64748b;">{p['position']}</div>
                            </div>
                        </div>
                        <span style="display:inline-block;padding:4px 10px;border-radius:20px;font-size:10px;font-weight:600;background:{status_color};color:white;text-align:center;">{p['status']}</span>
                        {metrics_html}
                        <div style="{remark_style}" title="{remark}">{remark if remark else '-'}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button("👁️", key=f"view_eff_{p['id']}", use_container_width=True):
                    show_player_modal(p['id'])
    
    # === TAB COMPARER ===
    with tabs[1]:
        st.markdown("### 📊 Comparer des joueurs")
        
        player_names = [p['name'] for p in st.session_state.players]
        
        col1, col2 = st.columns(2)
        with col1:
            sel_players = st.multiselect("Sélectionner 2 à 4 joueurs", player_names, max_selections=4, key="cmp_players")
        with col2:
            dates = sorted(st.session_state.data.keys(), reverse=True)
            cmp_date = st.selectbox("Date", dates[:30] if dates else [], format_func=lambda x: format_date(x, 'short'), key="cmp_date") if dates else None
        
        if len(sel_players) >= 2 and cmp_date:
            today_data = st.session_state.data.get(cmp_date, [])
            
            fig = go.Figure()
            colors = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444']
            categories = [m['label'] for m in METRICS]
            
            for i, name in enumerate(sel_players):
                pd_data = next((d for d in today_data if d['name'] == name), {})
                vals = [pd_data.get(m['key'], 0) or 0 for m in METRICS]
                vals.append(vals[0])
                
                fig.add_trace(go.Scatterpolar(
                    r=vals,
                    theta=categories + [categories[0]],
                    fill='toself',
                    name=name,
                    line=dict(color=colors[i % len(colors)], width=2)
                ))
            
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 5]), bgcolor='rgba(15,23,42,0.8)'),
                paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8'), height=450
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sélectionnez au moins 2 joueurs pour comparer")
    
    # === TAB ÉVOLUTION ===
    with tabs[2]:
        st.markdown("### 📈 Évolution individuelle")
        
        # Filtre par catégorie/poste
        col_filter, col_player, col_period, col_metric = st.columns([1, 2, 1, 1])
        
        with col_filter:
            # Collecter les catégories et postes uniques
            categories = ["Tous", "Avants", "Trois-quarts"]
            positions = sorted(set(p.get('position', 'Non défini') for p in st.session_state.players if p.get('position')))
            filter_options = categories + ["─── Par poste ───"] + positions
            
            selected_filter = st.selectbox(
                "Filtrer", 
                filter_options,
                key="evol_filter",
                format_func=lambda x: x if x != "─── Par poste ───" else "─── Par poste ───"
            )
        
        # Filtrer les joueurs selon la sélection
        all_players = st.session_state.players
        if selected_filter == "Tous" or selected_filter == "─── Par poste ───":
            filtered_players = all_players
        elif selected_filter == "Avants":
            avants_positions = ['Pilier', 'Talonneur', 'Deuxième ligne', '2ème ligne', 'Troisième ligne', '3ème ligne', 'Flanker', 'Numéro 8', 'N°8']
            filtered_players = [p for p in all_players if any(pos.lower() in p.get('position', '').lower() for pos in avants_positions)]
        elif selected_filter == "Trois-quarts":
            trois_quarts_positions = ['Demi de mêlée', 'Demi d\'ouverture', 'Centre', 'Ailier', 'Arrière']
            filtered_players = [p for p in all_players if any(pos.lower() in p.get('position', '').lower() for pos in trois_quarts_positions)]
        else:
            # Filtre par poste spécifique
            filtered_players = [p for p in all_players if p.get('position', '') == selected_filter]
        
        # Si aucun joueur après filtre, revenir à tous
        if not filtered_players:
            filtered_players = all_players
        
        with col_player:
            player_names = sorted([p['name'] for p in filtered_players])
            sel_player = st.selectbox("Joueur", player_names, key="evol_player")
        
        with col_period:
            period = st.selectbox("Période", [7, 14, 30, 60], index=2, format_func=lambda x: f"{x} jours", key="evol_days")
        
        with col_metric:
            sel_metric = st.selectbox("Métrique", ['global'] + [m['key'] for m in METRICS],
                format_func=lambda x: "⚡ Global" if x == 'global' else next((f"{m['icon']} {m['label']}" for m in METRICS if m['key'] == x), x), key="evol_metric")
        
        if sel_player:
            fig = create_metrics_evolution_chart(sel_player, sel_metric, period)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Pas assez de données pour ce joueur")
    
    # === TAB GROUPES ===
    with tabs[3]:
        st.markdown("### 👥 Vue par groupes")
        
        dates = sorted(st.session_state.data.keys(), reverse=True)
        if dates:
            grp_date = st.selectbox("Date", dates[:30], format_func=lambda x: format_date(x, 'short'), key="grp_date")
            
            col1, col2 = st.columns(2)
            
            for i, group_name in enumerate(['Avants', 'Trois-quarts']):
                with [col1, col2][i]:
                    grp_avg = get_team_avg(grp_date, group=group_name)
                    if grp_avg:
                        global_str = f"{grp_avg.get('global'):.2f}" if grp_avg.get('global') else "-"
                        color = "#ef4444" if group_name == "Avants" else "#3b82f6"
                        
                        st.markdown(f"""
                        <div class="glass-card" style="margin-bottom:16px;">
                            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
                                <span style="font-weight:bold;color:white;font-size:18px;">{group_name}</span>
                                <span style="font-size:28px;font-weight:bold;color:{color};">{global_str}/5</span>
                            </div>
                            <div style="color:#64748b;font-size:13px;">{grp_avg.get('count', 0)} joueurs</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        for line_name in RUGBY_POSITIONS[group_name].keys():
                            line_avg = get_team_avg(grp_date, line=line_name)
                            if line_avg and line_avg.get('global'):
                                line_str = f"{line_avg.get('global'):.2f}"
                                st.markdown(f"• **{line_name}**: {line_str}/5 ({line_avg.get('count', 0)} joueurs)")


def page_infirmerie():
    """Page Infirmerie"""
    st.markdown("# 🏥 Infirmerie")
    
    # Stats de disponibilité
    status_counts = {}
    for p in st.session_state.players:
        s = p.get('status', 'Apte')
        status_counts[s] = status_counts.get(s, 0) + 1
    
    cols = st.columns(4)
    status_colors = {'Apte': '#10b981', 'Blessé': '#ef4444', 'Réhabilitation': '#f59e0b', 'Réathlétisation': '#3b82f6'}
    status_icons = {'Apte': '✅', 'Blessé': '🤕', 'Réhabilitation': '🔄', 'Réathlétisation': '💪'}
    
    for i, status in enumerate(STATUSES):
        count = status_counts.get(status, 0)
        with cols[i]:
            color = status_colors.get(status, '#64748b')
            icon = status_icons.get(status, '👤')
            selected = st.session_state.status_filter == status
            
            if st.button(f"{icon} {status}\n**{count}**", key=f"filter_{status}", use_container_width=True,
                        type="primary" if selected else "secondary"):
                st.session_state.status_filter = status if not selected else None
                st.rerun()
    
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    
    current_filter = st.session_state.status_filter
    filtered_players = [p for p in st.session_state.players if not current_filter or p.get('status') == current_filter]
    
    if current_filter:
        st.info(f"🔍 Filtré par: **{current_filter}** ({len(filtered_players)} joueurs)")
    
    for p in sorted(filtered_players, key=lambda x: x['name']):
        col1, col2, col3 = st.columns([3, 2, 2])
        
        with col1:
            avatar_class = get_avatar_gradient(p['name'])
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:12px;">
                <div class="player-avatar {avatar_class}">{p['name'][0]}</div>
                <div>
                    <div style="font-weight:600;color:white;">{p['name']}</div>
                    <div style="font-size:12px;color:#64748b;">{p['position']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
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
                if st.button("➕ Blessure", key=f"inj_{p['id']}", use_container_width=True):
                    st.session_state[f'show_injury_{p["id"]}'] = True
        
        # Formulaire blessure
        if st.session_state.get(f'show_injury_{p["id"]}'):
            with st.form(f'injury_form_{p["id"]}'):
                st.markdown(f"**Nouvelle blessure pour {p['name']}**")
                ic1, ic2 = st.columns(2)
                with ic1:
                    zone = st.selectbox("Zone", list(INJURY_ZONES.keys()), key=f"zone_{p['id']}")
                with ic2:
                    grade = st.selectbox("Grade", [1, 2, 3], key=f"grade_{p['id']}")
                
                circ = st.selectbox("Circonstance", CIRCUMSTANCES, key=f"circ_{p['id']}")
                duration = INJURY_ZONES[zone].get(grade, 14)
                st.info(f"⏱️ Durée estimée: **{duration} jours**")
                
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    if st.form_submit_button("💾 Enregistrer", use_container_width=True):
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
                        st.success("✅ Blessure enregistrée")
                        st.rerun()
                with col_s2:
                    if st.form_submit_button("❌ Annuler", use_container_width=True):
                        st.session_state[f'show_injury_{p["id"]}'] = False
                        st.rerun()
        
        st.markdown("---")
    
    # === BLESSURES ACTIVES ===
    st.markdown("### 🩹 Blessures actives")
    active_injuries = [i for i in st.session_state.injuries if i.get('status') == 'Active']
    
    if active_injuries:
        for inj in active_injuries:
            days_remaining = (datetime.strptime(inj['returnDate'], '%Y-%m-%d') - datetime.now()).days
            days_total = INJURY_ZONES[inj['zone']].get(inj['grade'], 14)
            progress = max(0, min(100, ((days_total - max(0, days_remaining)) / days_total) * 100))
            
            col1, col2, col3 = st.columns([3, 4, 2])
            
            with col1:
                st.markdown(f"""
                <div>
                    <div style="font-weight:bold;color:white;">{inj['playerName']}</div>
                    <div style="font-size:13px;color:#94a3b8;">{INJURY_ZONES[inj['zone']]['icon']} {inj['zone']} (Grade {inj['grade']})</div>
                    <div style="font-size:11px;color:#64748b;">{inj['circumstance']} - {format_date(inj['date'])}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                progress_color = "#10b981" if progress > 75 else "#f59e0b" if progress > 40 else "#ef4444"
                st.markdown(f"""
                <div style="margin-top:10px;">
                    <div class="custom-progress">
                        <div class="custom-progress-fill" style="width:{progress}%;background:{progress_color};"></div>
                    </div>
                    <div style="font-size:12px;color:#94a3b8;margin-top:4px;">
                        {max(0, days_remaining)} jours restants • Retour prévu: {format_date(inj['returnDate'])}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                if st.button("✅ Guéri", key=f"heal_{inj['id']}", use_container_width=True):
                    for injury in st.session_state.injuries:
                        if injury['id'] == inj['id']:
                            injury['status'] = 'Healed'
                    st.success("✅ Joueur marqué comme guéri")
                    st.rerun()
            
            st.markdown("---")
    else:
        st.success("✅ Aucune blessure active - Tous les joueurs sont en forme !")


def page_joueurs():
    """Page Gestion des joueurs"""
    st.markdown("# 👤 Gestion des joueurs")
    
    # === AJOUTER ===
    with st.expander("➕ Ajouter un nouveau joueur", expanded=False):
        with st.form("add_player"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Nom complet")
                position = st.selectbox("Poste", ALL_POSITIONS)
            with col2:
                weight = st.number_input("Poids forme (kg)", value=90.0, min_value=50.0, max_value=200.0, step=0.5)
                status = st.selectbox("Statut initial", STATUSES)
            
            if st.form_submit_button("➕ Ajouter le joueur", use_container_width=True, type="primary"):
                if name and len(name) >= 2:
                    if not any(p['name'].lower() == name.lower() for p in st.session_state.players):
                        st.session_state.players.append({
                            'id': f"p_{len(st.session_state.players)}_{datetime.now().timestamp():.0f}",
                            'name': name, 'position': position, 'targetWeight': weight, 'status': status
                        })
                        st.success(f"✅ {name} ajouté à l'effectif !")
                        st.rerun()
                    else:
                        st.error("❌ Ce joueur existe déjà")
                else:
                    st.error("❌ Entrez un nom valide (minimum 2 caractères)")
    
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    
    # === LISTE ===
    if st.session_state.players:
        st.markdown(f"<div style='color:#64748b;font-size:13px;margin-bottom:12px;'>📋 {len(st.session_state.players)} joueurs dans l'effectif</div>", unsafe_allow_html=True)
        
        for p in sorted(st.session_state.players, key=lambda x: x['name']):
            col1, col2, col3, col4, col5 = st.columns([2.5, 2, 1.5, 1.5, 0.5])
            
            with col1:
                avatar_class = get_avatar_gradient(p['name'])
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:10px;">
                    <div class="player-avatar {avatar_class}" style="width:36px;height:36px;font-size:14px;">{p['name'][0]}</div>
                    <span style="font-weight:600;color:white;">{p['name']}</span>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                new_pos = st.selectbox("", ALL_POSITIONS,
                    index=ALL_POSITIONS.index(p['position']) if p['position'] in ALL_POSITIONS else 0,
                    key=f"pos_{p['id']}", label_visibility="collapsed")
                if new_pos != p['position']:
                    for player in st.session_state.players:
                        if player['id'] == p['id']:
                            player['position'] = new_pos
            
            with col3:
                new_weight = st.number_input("", value=float(p.get('targetWeight', 90)), min_value=50.0, max_value=200.0, step=0.5,
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
                # Confirmation de suppression
                confirm_key = f"confirm_del_{p['id']}"
                if confirm_key not in st.session_state:
                    st.session_state[confirm_key] = False
                
                if st.session_state[confirm_key]:
                    # Mode confirmation - afficher les boutons confirmer/annuler
                    btn_cols = st.columns(2)
                    with btn_cols[0]:
                        if st.button("✅", key=f"confirm_{p['id']}", help="Confirmer"):
                            st.session_state.players = [x for x in st.session_state.players if x['id'] != p['id']]
                            # Nettoyer aussi les données du joueur
                            for date in st.session_state.data:
                                st.session_state.data[date] = [e for e in st.session_state.data[date] if e.get('name') != p['name']]
                            st.session_state[confirm_key] = False
                            # Auto-save après suppression
                            save_data_to_file()
                            st.success(f"✅ {p['name']} supprimé")
                            st.rerun()
                    with btn_cols[1]:
                        if st.button("❌", key=f"cancel_{p['id']}", help="Annuler"):
                            st.session_state[confirm_key] = False
                            st.rerun()
                else:
                    if st.button("🗑️", key=f"del_{p['id']}", help="Supprimer ce joueur"):
                        st.session_state[confirm_key] = True
                        st.rerun()
        
        # Message pour annuler les confirmations en attente
        pending_deletions = [k for k in st.session_state if k.startswith("confirm_del_") and st.session_state[k]]
        if pending_deletions:
            st.warning("⚠️ Cliquez sur ✅ pour confirmer ou ❌ pour annuler la suppression")
        
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        
        # Bouton sauvegarde rapide
        if st.button("💾 Sauvegarder les modifications", type="primary", use_container_width=True):
            success, msg = save_data_to_file()
            if success:
                st.success(f"✅ {msg}")
            else:
                st.error(f"❌ {msg}")
    else:
        st.info("Aucun joueur. Importez des données ou ajoutez des joueurs manuellement.")


def page_parametres():
    """Page Paramètres"""
    st.markdown("# ⚙️ Paramètres")
    
    # === SEUILS D'ALERTE ===
    st.markdown("### 🚨 Seuils d'alerte")
    st.markdown("<div style='color:#64748b;font-size:13px;margin-bottom:12px;'>Configurez quand les alertes sont déclenchées</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.session_state.settings['lowValueThreshold'] = st.number_input(
            "Valeur basse (1-5)", 
            value=float(st.session_state.settings['lowValueThreshold']),
            min_value=1.0, max_value=5.0, step=0.5, 
            help="Alerte si une métrique est ≤ à ce seuil"
        )
    with col2:
        st.session_state.settings['variationThreshold'] = st.number_input(
            "Seuil variation", 
            value=float(st.session_state.settings['variationThreshold']),
            min_value=0.5, max_value=3.0, step=0.5,
            help="Alerte si variation jour/jour ≥ ce seuil"
        )
    with col3:
        st.session_state.settings['weightThreshold'] = st.number_input(
            "Écart poids (kg)", 
            value=float(st.session_state.settings['weightThreshold']),
            min_value=1.0, max_value=5.0, step=0.5,
            help="Alerte si écart avec poids forme ≥ ce seuil"
        )
    
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    
    # === Z-SCORE ===
    st.markdown("### 📈 Paramètres Z-Score")
    st.markdown("<div style='color:#64748b;font-size:13px;margin-bottom:12px;'>Configurez la détection de fatigue par Z-Score</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.session_state.settings['zscoreDays'] = st.number_input(
            "Jours de calcul", 
            value=int(st.session_state.settings['zscoreDays']),
            min_value=7, max_value=60,
            help="Nombre de jours utilisés pour calculer la moyenne et l'écart-type"
        )
    with col2:
        st.session_state.settings['zscoreWarning'] = st.number_input(
            "Seuil attention", 
            value=float(st.session_state.settings['zscoreWarning']),
            min_value=-3.0, max_value=0.0, step=0.5,
            help="Z-Score en dessous duquel une attention est requise (jaune)"
        )
    with col3:
        st.session_state.settings['zscoreAlert'] = st.number_input(
            "Seuil alerte", 
            value=float(st.session_state.settings['zscoreAlert']),
            min_value=-3.0, max_value=0.0, step=0.5,
            help="Z-Score en dessous duquel une alerte est déclenchée (rouge)"
        )
    
    st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)
    
    # === STOCKAGE CLOUD AUTOMATIQUE ===
    st.markdown("### ☁️ Stockage Cloud Automatique")
    
    # Vérifier le statut
    cloud_connected, cloud_id = get_cloud_status()
    is_in_secrets = is_cloud_id_in_secrets()
    
    if cloud_connected and is_in_secrets:
        # Configuration parfaite !
        st.markdown(f"""
        <div style="background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.3);border-radius:12px;padding:16px;margin-bottom:16px;">
            <div style="display:flex;align-items:center;gap:12px;">
                <span style="font-size:28px;">✅</span>
                <div style="flex:1;">
                    <div style="color:#10b981;font-weight:600;font-size:16px;">Cloud configuré parfaitement !</div>
                    <div style="color:#94a3b8;font-size:12px;margin-top:4px;">
                        Vos données survivront à tous les redémarrages, vacances, etc.
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    elif cloud_connected and not is_in_secrets:
        # Cloud actif mais pas dans les Secrets - IMPORTANT !
        st.markdown(f"""
        <div style="background:rgba(245,158,11,0.15);border:2px solid rgba(245,158,11,0.5);border-radius:12px;padding:16px;margin-bottom:16px;">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;">
                <span style="font-size:28px;">⚠️</span>
                <div style="flex:1;">
                    <div style="color:#f59e0b;font-weight:600;font-size:16px;">Action requise pour sécuriser vos données !</div>
                    <div style="color:#94a3b8;font-size:12px;margin-top:4px;">
                        Copiez l'ID ci-dessous dans les Secrets Streamlit pour que les données survivent aux redémarrages.
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Afficher l'ID à copier
        st.markdown("#### 📋 Votre ID Cloud (à copier) :")
        st.code(cloud_id, language=None)
        
        with st.expander("🔧 Instructions de configuration (2 minutes)", expanded=True):
            st.markdown(f"""
            ### Étapes pour sécuriser vos données :
            
            **1.** Allez sur **[share.streamlit.io](https://share.streamlit.io)**
            
            **2.** Trouvez votre app **wellness-tracker-rugby** → cliquez sur **⋮** (3 points) → **Settings**
            
            **3.** Cliquez sur **Secrets** dans le menu à gauche
            
            **4.** Collez ce texte exactement :
            ```toml
            CLOUD_BLOB_ID = "{cloud_id}"
            ```
            
            **5.** Cliquez **Save**
            
            **6.** L'app va redémarrer automatiquement → vos données seront sécurisées ! ✅
            
            ---
            ⚠️ **Sans cette configuration**, si Streamlit redémarre (maintenance, vacances, etc.), 
            l'app ne saura plus où trouver vos données !
            """)
    else:
        # Pas encore de cloud
        st.markdown("""
        <div style="background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.3);border-radius:12px;padding:16px;margin-bottom:16px;">
            <div style="display:flex;align-items:center;gap:12px;">
                <span style="font-size:28px;">☁️</span>
                <div>
                    <div style="color:#3b82f6;font-weight:600;font-size:16px;">Cloud prêt à être activé</div>
                    <div style="color:#94a3b8;font-size:12px;margin-top:4px;">
                        Cliquez sur "Synchroniser" pour créer votre espace cloud.
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Dernière synchro
    if 'last_cloud_save' in st.session_state:
        time_diff = datetime.now() - st.session_state.last_cloud_save
        if time_diff.total_seconds() < 60:
            sync_text = "à l'instant"
        elif time_diff.total_seconds() < 3600:
            sync_text = f"il y a {int(time_diff.total_seconds() / 60)} min"
        else:
            sync_text = st.session_state.last_cloud_save.strftime("%d/%m %H:%M")
        st.caption(f"⏱️ Dernière synchronisation : {sync_text}")
    
    # Boutons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("☁️ Synchroniser maintenant", use_container_width=True, type="primary"):
            with st.spinner("Synchronisation..."):
                success, msg = save_to_cloud()
                if success:
                    st.success(f"✅ {msg}")
                    # Si nouveau cloud créé, forcer le rerun pour afficher les instructions
                    if st.session_state.get('new_cloud_id_created'):
                        st.rerun()
                else:
                    st.error(f"❌ {msg}")
    
    with col2:
        if st.button("📥 Forcer chargement cloud", use_container_width=True, disabled=not cloud_connected):
            with st.spinner("Chargement..."):
                success, msg = load_from_cloud()
                if success:
                    st.success(f"✅ {msg}")
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")
    
    st.markdown("""
    <div style="background:rgba(255,255,255,0.03);border-radius:8px;padding:12px;margin-top:16px;">
        <div style="color:#64748b;font-size:12px;">
            <strong style="color:#94a3b8;">ℹ️ Comment ça marche ?</strong><br>
            • Les données sont sauvegardées dans le cloud quand vous cliquez "Synchroniser"<br>
            • Au démarrage, l'app charge automatiquement depuis le cloud<br>
            • Gratuit, illimité, pas de pause !<br>
            • <strong style="color:#f59e0b;">Important :</strong> Configurez les Secrets Streamlit pour que ça survive aux redémarrages
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)
    
    # === ACTIONS ===
    st.markdown("### 🔧 Actions")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Réinitialiser les paramètres", use_container_width=True):
            st.session_state.settings = DEFAULT_SETTINGS.copy()
            st.success("✅ Paramètres réinitialisés aux valeurs par défaut")
    
    with col2:
        if st.button("🗑️ Effacer toutes les données", type="primary", use_container_width=True):
            st.session_state.confirm_delete = True
    
    if st.session_state.get('confirm_delete'):
        st.warning("⚠️ Cette action est irréversible ! Toutes les données seront supprimées.")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            if st.button("✅ Confirmer la suppression", type="primary", use_container_width=True):
                st.session_state.data = {}
                st.session_state.players = []
                st.session_state.injuries = []
                st.session_state.confirm_delete = False
                st.success("✅ Toutes les données ont été effacées")
                st.rerun()
        with col_c2:
            if st.button("❌ Annuler", use_container_width=True):
                st.session_state.confirm_delete = False
                st.rerun()
    
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    
    # === STATS ===
    st.markdown("### 📊 Statistiques")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div style="font-size:32px;font-weight:bold;color:#10b981;">{len(st.session_state.data)}</div>
            <div style="font-size:12px;color:#64748b;">Jours de données</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div style="font-size:32px;font-weight:bold;color:#3b82f6;">{len(st.session_state.players)}</div>
            <div style="font-size:12px;color:#64748b;">Joueurs</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        total_entries = sum(len(e) for e in st.session_state.data.values())
        st.markdown(f"""
        <div class="stat-card">
            <div style="font-size:32px;font-weight:bold;color:#f59e0b;">{total_entries}</div>
            <div style="font-size:12px;color:#64748b;">Entrées totales</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        active_injuries = len([i for i in st.session_state.injuries if i.get('status') == 'Active'])
        st.markdown(f"""
        <div class="stat-card">
            <div style="font-size:32px;font-weight:bold;color:#ef4444;">{active_injuries}</div>
            <div style="font-size:12px;color:#64748b;">Blessures actives</div>
        </div>
        """, unsafe_allow_html=True)


# ==================== MAIN ====================
def main():
    """Point d'entrée principal"""
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;padding:1.5rem 0;">
            <div style="font-size:50px;margin-bottom:8px;">🏉</div>
            <div style="font-size:20px;font-weight:bold;color:white;">Wellness Tracker</div>
            <div style="font-size:12px;color:#64748b;">Rugby Performance</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        
        page = st.radio(
            "", 
            ["📊 Dashboard", "📥 Import", "👥 Effectif", "🏥 Infirmerie", "👤 Joueurs", "⚙️ Paramètres"],
            label_visibility="collapsed"
        )
        
        st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
        
        # Alertes dans la sidebar
        dates = sorted(st.session_state.data.keys(), reverse=True)
        if dates:
            alerts = get_alerts(dates[0])
            if alerts:
                unique_players = len(set(a['player'] for a in alerts))
                st.markdown(f"""
                <div style="background:linear-gradient(135deg,rgba(239,68,68,0.2),rgba(239,68,68,0.1));border:1px solid rgba(239,68,68,0.3);border-radius:12px;padding:16px;text-align:center;">
                    <div style="font-size:28px;">🚨</div>
                    <div style="color:#f87171;font-weight:600;font-size:16px;">{unique_players} alertes</div>
                    <div style="color:#64748b;font-size:11px;">aujourd'hui</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
        
        # Stats rapides
        st.markdown(f"""
        <div style="color:#64748b;font-size:12px;padding:0 8px;">
            <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                <span>📊 Données</span>
                <span style="color:white;font-weight:600;">{len(dates)} jours</span>
            </div>
            <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                <span>👥 Joueurs</span>
                <span style="color:white;font-weight:600;">{len(st.session_state.players)}</span>
            </div>
            <div style="display:flex;justify-content:space-between;">
                <span>🏥 Blessures</span>
                <span style="color:white;font-weight:600;">{len([i for i in st.session_state.injuries if i.get('status') == 'Active'])}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        
        # Indicateur de statut cloud (automatique)
        cloud_connected, cloud_id = get_cloud_status()
        is_in_secrets = is_cloud_id_in_secrets()
        
        if cloud_connected and is_in_secrets:
            # Parfait !
            if 'last_cloud_save' in st.session_state:
                time_diff = datetime.now() - st.session_state.last_cloud_save
                if time_diff.total_seconds() < 60:
                    sync_text = "à l'instant"
                elif time_diff.total_seconds() < 3600:
                    sync_text = f"il y a {int(time_diff.total_seconds() / 60)} min"
                else:
                    sync_text = st.session_state.last_cloud_save.strftime("%H:%M")
                
                st.markdown(f"""
                <div style="background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.3);border-radius:8px;padding:10px;text-align:center;">
                    <div style="font-size:11px;color:#10b981;">✅ Cloud sécurisé {sync_text}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.3);border-radius:8px;padding:10px;text-align:center;">
                    <div style="font-size:11px;color:#10b981;">✅ Cloud sécurisé</div>
                </div>
                """, unsafe_allow_html=True)
                
        elif cloud_connected and not is_in_secrets:
            # Cloud actif mais pas sécurisé
            st.markdown("""
            <div style="background:rgba(245,158,11,0.15);border:1px solid rgba(245,158,11,0.4);border-radius:8px;padding:10px;text-align:center;">
                <div style="font-size:11px;color:#f59e0b;">⚠️ Config requise</div>
                <div style="font-size:9px;color:#94a3b8;">Voir Paramètres</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Pas encore de cloud
            st.markdown("""
            <div style="background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.3);border-radius:8px;padding:10px;text-align:center;">
                <div style="font-size:11px;color:#3b82f6;">☁️ Cliquez Synchroniser</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Indicateur si chargé depuis le cloud
        if st.session_state.get('cloud_loaded'):
            st.markdown("""
            <div style="font-size:9px;color:#64748b;text-align:center;margin-top:4px;">
                📥 Chargé depuis le cloud
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        
        # Bouton synchro cloud
        if st.button("☁️ Synchroniser", use_container_width=True, help="Sauvegarder dans le cloud"):
            success, msg = save_to_cloud()
            if success:
                st.success("✅ Synchronisé !")
            else:
                st.error(msg)
    
    # Navigation
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
