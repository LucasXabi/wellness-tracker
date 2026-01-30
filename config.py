"""
Configuration et utilitaires pour l'application Wellness Tracker
"""

import streamlit as st
from supabase import create_client, Client
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import re

# ==================== CONFIGURATION ====================

# Structure des postes rugby
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

METRICS = [
    {'key': 'sleep', 'label': 'Sommeil', 'icon': '😴', 'color': '#3b82f6'},
    {'key': 'mental_load', 'label': 'Charge Mentale', 'icon': '🧠', 'color': '#8b5cf6'},
    {'key': 'motivation', 'label': 'Motivation', 'icon': '💪', 'color': '#f59e0b'},
    {'key': 'hdc', 'label': 'HDC', 'icon': '❤️', 'color': '#ef4444'},
    {'key': 'bdc', 'label': 'BDC', 'icon': '💚', 'color': '#10b981'},
]

INJURY_ZONES = {
    'Ischio-jambiers': {'icon': '🦵', 1: 10, 2: 28, 3: 84},
    'Quadriceps': {'icon': '🦵', 1: 7, 2: 21, 3: 56},
    'Mollet': {'icon': '🦶', 1: 7, 2: 21, 3: 42},
    'Adducteurs': {'icon': '🦵', 1: 7, 2: 21, 3: 42},
    'Genou - LCA': {'icon': '🦿', 1: 180, 2: 270, 3: 365},
    'Genou - Ménisque': {'icon': '🦿', 1: 28, 2: 56, 3: 120},
    'Genou - Entorse': {'icon': '🦿', 1: 14, 2: 42, 3: 84},
    'Cheville': {'icon': '🦶', 1: 7, 2: 21, 3: 56},
    'Épaule - Luxation': {'icon': '💪', 1: 21, 2: 84, 3: 180},
    'Épaule - Autre': {'icon': '💪', 1: 14, 2: 35, 3: 84},
    'Dos': {'icon': '🔙', 1: 7, 2: 21, 3: 56},
    'Cou': {'icon': '🔙', 1: 7, 2: 14, 3: 42},
    'Commotion': {'icon': '🧠', 1: 12, 2: 21, 3: 42},
    'Côtes': {'icon': '🫁', 1: 14, 2: 28, 3: 56},
    'Poignet/Main': {'icon': '✋', 1: 7, 2: 21, 3: 42},
    'Pied': {'icon': '🦶', 1: 7, 2: 21, 3: 42},
    'Autre': {'icon': '🏥', 1: 7, 2: 14, 3: 28},
}

CIRCUMSTANCES = ['Match', 'Entraînement', 'Musculation', 'Hors sport', 'Autre']

STATUSES = ['Apte', 'Blessé', 'Réhabilitation', 'Réathlétisation']

# Mois en français
FRENCH_MONTHS = {
    'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4,
    'mai': 5, 'juin': 6, 'juillet': 7, 'août': 8,
    'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12
}

# ==================== PARAMÈTRES PAR DÉFAUT ====================

DEFAULT_SETTINGS = {
    'low_value_threshold': 2,
    'variation_threshold': 1.5,
    'weight_threshold': 2.0,
    'zscore_days': 14,
    'zscore_alert': -1.5,
    'zscore_warning': -1.0,
}

# ==================== FONCTIONS UTILITAIRES ====================

def get_player_group(position):
    """Retourne le groupe (Avants/Trois-quarts) pour un poste"""
    for group_name, lines in RUGBY_POSITIONS.items():
        for line_positions in lines.values():
            if position in line_positions:
                return group_name
    return 'Avants'

def get_player_line(position):
    """Retourne la ligne pour un poste"""
    for lines in RUGBY_POSITIONS.values():
        for line_name, line_positions in lines.items():
            if position in line_positions:
                return line_name
    return '1ère ligne'

def get_player_average(row):
    """Calcule la moyenne des 5 métriques pour un joueur"""
    values = []
    for m in METRICS:
        val = row.get(m['key'])
        if val is not None and not pd.isna(val):
            values.append(float(val))
    return np.mean(values) if values else None

def calculate_zscore(value, history):
    """Calcule le Z-Score d'une valeur par rapport à un historique"""
    if not history or len(history) < 5:
        return 0
    mean = np.mean(history)
    std = np.std(history)
    if std == 0:
        return 0
    return (value - mean) / std

def parse_french_date(date_str):
    """Parse une date en français (ex: 'mardi 6 janvier 2026')"""
    if not date_str:
        return None
    
    try:
        # Format "mardi 6 janvier 2026"
        match = re.search(r'(\d{1,2})\s+(\w+)\s+(\d{4})', str(date_str).lower())
        if match:
            day = int(match.group(1))
            month_name = match.group(2)
            year = int(match.group(3))
            month = FRENCH_MONTHS.get(month_name)
            if month:
                return datetime(year, month, day).date()
    except:
        pass
    
    return None

def format_date(date_obj, style='short'):
    """Formate une date"""
    if isinstance(date_obj, str):
        date_obj = datetime.strptime(date_obj, '%Y-%m-%d').date()
    
    if style == 'full':
        days = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
        months = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 
                  'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
        return f"{days[date_obj.weekday()]} {date_obj.day} {months[date_obj.month-1]} {date_obj.year}"
    else:
        return date_obj.strftime('%d/%m/%Y')

def get_color_for_value(value):
    """Retourne la couleur CSS pour une valeur 1-5"""
    if value is None or pd.isna(value):
        return '#374151'  # gray
    if value >= 4:
        return '#10b981'  # green
    if value >= 3:
        return '#f59e0b'  # amber
    return '#ef4444'  # red

def get_status_color(status):
    """Retourne la couleur pour un statut"""
    colors = {
        'Apte': '#10b981',
        'Blessé': '#ef4444',
        'Réhabilitation': '#f59e0b',
        'Réathlétisation': '#3b82f6',
    }
    return colors.get(status, '#6b7280')

# ==================== SUPABASE ====================

def init_supabase():
    """Initialise la connexion Supabase"""
    if 'supabase' not in st.session_state:
        try:
            url = st.secrets["SUPABASE_URL"]
            key = st.secrets["SUPABASE_KEY"]
            st.session_state.supabase = create_client(url, key)
        except Exception as e:
            st.session_state.supabase = None
    return st.session_state.supabase

# ==================== SESSION STATE ====================

def init_session_state():
    """Initialise les variables de session"""
    if 'players' not in st.session_state:
        st.session_state.players = []
    if 'wellness_data' not in st.session_state:
        st.session_state.wellness_data = {}
    if 'injuries' not in st.session_state:
        st.session_state.injuries = []
    if 'alerts' not in st.session_state:
        st.session_state.alerts = []
    if 'settings' not in st.session_state:
        st.session_state.settings = DEFAULT_SETTINGS.copy()
    if 'selected_date' not in st.session_state:
        st.session_state.selected_date = datetime.now().date()
    if 'selected_player' not in st.session_state:
        st.session_state.selected_player = None
