"""
🏉 Rugby Wellness Tracker
Application de suivi du bien-être des joueurs de rugby
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import re

# ==================== CONFIGURATION PAGE ====================

st.set_page_config(
    page_title="Rugby Wellness Tracker",
    page_icon="🏉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CONSTANTES ====================

METRICS = [
    {'key': 'sleep', 'label': 'Sommeil', 'icon': '😴', 'color': '#3b82f6'},
    {'key': 'mental_load', 'label': 'Charge Mentale', 'icon': '🧠', 'color': '#8b5cf6'},
    {'key': 'motivation', 'label': 'Motivation', 'icon': '💪', 'color': '#f59e0b'},
    {'key': 'hdc', 'label': 'HDC', 'icon': '❤️', 'color': '#ef4444'},
    {'key': 'bdc', 'label': 'BDC', 'icon': '💚', 'color': '#10b981'},
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
    'Ischio-jambiers': {'icon': '🦵', 1: 10, 2: 28, 3: 84},
    'Quadriceps': {'icon': '🦵', 1: 7, 2: 21, 3: 56},
    'Mollet': {'icon': '🦶', 1: 7, 2: 21, 3: 42},
    'Genou': {'icon': '🦿', 1: 14, 2: 42, 3: 120},
    'Cheville': {'icon': '🦶', 1: 7, 2: 21, 3: 56},
    'Épaule': {'icon': '💪', 1: 14, 2: 35, 3: 84},
    'Dos': {'icon': '🔙', 1: 7, 2: 21, 3: 56},
    'Commotion': {'icon': '🧠', 1: 12, 2: 21, 3: 42},
    'Autre': {'icon': '🏥', 1: 7, 2: 14, 3: 28},
}

CIRCUMSTANCES = ['Match', 'Entraînement', 'Musculation', 'Hors sport', 'Autre']
STATUSES = ['Apte', 'Blessé', 'Réhabilitation', 'Réathlétisation']

FRENCH_MONTHS = {
    'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4,
    'mai': 5, 'juin': 6, 'juillet': 7, 'août': 8,
    'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12
}

DEFAULT_SETTINGS = {
    'low_value_threshold': 2,
    'variation_threshold': 1.5,
    'weight_threshold': 2.0,
    'zscore_days': 14,
    'zscore_alert': -1.5,
    'zscore_warning': -1.0,
}

# ==================== INITIALISATION SESSION ====================

if 'players' not in st.session_state:
    st.session_state.players = []
if 'wellness_data' not in st.session_state:
    st.session_state.wellness_data = {}
if 'injuries' not in st.session_state:
    st.session_state.injuries = []
if 'settings' not in st.session_state:
    st.session_state.settings = DEFAULT_SETTINGS.copy()

# ==================== FONCTIONS UTILITAIRES ====================

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

def get_player_average(row):
    values = []
    for m in METRICS:
        val = row.get(m['key'])
        if val is not None and not pd.isna(val):
            values.append(float(val))
    return np.mean(values) if values else None

def get_color_for_value(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return '#374151'
    if value >= 4:
        return '#10b981'
    if value >= 3:
        return '#f59e0b'
    return '#ef4444'

def get_status_color(status):
    colors = {
        'Apte': '#10b981',
        'Blessé': '#ef4444',
        'Réhabilitation': '#f59e0b',
        'Réathlétisation': '#3b82f6',
    }
    return colors.get(status, '#6b7280')

def parse_french_date(date_str):
    if not date_str:
        return None
    try:
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
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.strptime(date_obj, '%Y-%m-%d').date()
        except:
            return date_obj
    
    if style == 'full':
        days = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
        months = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 
                  'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
        return f"{days[date_obj.weekday()]} {date_obj.day} {months[date_obj.month-1]} {date_obj.year}"
    else:
        return date_obj.strftime('%d/%m/%Y')

# ==================== FONCTIONS D'IMPORT ====================

def import_from_google_sheets(sheet_url):
    try:
        match = re.search(r'/d/([a-zA-Z0-9-_]+)', sheet_url)
        if not match:
            return None, "URL invalide"
        
        sheet_id = match.group(1)
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Bien-être"
        
        df_raw = pd.read_csv(csv_url, header=None)
        return process_imported_data(df_raw)
    
    except Exception as e:
        return None, f"Erreur: {str(e)}"

def import_from_excel(uploaded_file):
    try:
        xl = pd.ExcelFile(uploaded_file)
        sheet_name = None
        for name in xl.sheet_names:
            if 'bien' in name.lower():
                sheet_name = name
                break
        if not sheet_name:
            sheet_name = xl.sheet_names[0]
        
        df_raw = pd.read_excel(uploaded_file, sheet_name=sheet_name, header=None)
        return process_imported_data(df_raw)
    
    except Exception as e:
        return None, f"Erreur: {str(e)}"

def process_imported_data(df_raw):
    try:
        # Chercher la date
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
        
        # Colonnes par défaut
        col_indices = {
            'name': 1, 'weight': 2, 'sleep': 3, 'mental_load': 4,
            'motivation': 5, 'hdc': 6, 'bdc': 7, 'remark': 9
        }
        
        # Trouver la ligne d'en-tête
        header_row = 2
        for i in range(min(10, len(df_raw))):
            row_str = ' '.join([str(v).lower() for v in df_raw.iloc[i] if pd.notna(v)])
            if 'joueur' in row_str or ('poids' in row_str and 'sommeil' in row_str):
                header_row = i
                break
        
        # Traiter les données
        data_rows = []
        new_players = []
        existing_names = {p['name'] for p in st.session_state.players}
        
        for i in range(header_row + 2, len(df_raw)):
            row = df_raw.iloc[i]
            
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
            
            if name not in existing_names:
                existing_names.add(name)
                new_players.append({
                    'id': f"{datetime.now().timestamp()}_{len(new_players)}",
                    'name': name,
                    'position': 'Pilier gauche',
                    'status': 'Apte',
                    'target_weight': data_row['weight'] or 90
                })
        
        st.session_state.players.extend(new_players)
        
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
    data = st.session_state.wellness_data.get(date_key, [])
    if not data:
        return None
    
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
    data = st.session_state.wellness_data.get(date_key, [])
    settings = st.session_state.settings
    alerts = []
    
    for d in data:
        player = next((p for p in st.session_state.players if p['name'] == d['name']), None)
        if not player:
            continue
        
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

# ==================== PAGES ====================

def page_dashboard():
    st.title("📊 Dashboard Wellness")
    
    dates = sorted(st.session_state.wellness_data.keys(), reverse=True)
    
    if not dates:
        st.warning("⚠️ Aucune donnée importée. Utilisez la page Import pour charger vos données.")
        return
    
    selected_date = st.selectbox(
        "📅 Date",
        dates,
        format_func=lambda x: format_date(x, 'full')
    )
    
    date_key = selected_date
    today_data = st.session_state.wellness_data.get(date_key, [])
    team_avg = get_team_averages(date_key)
    
    # Moyennes équipe
    st.subheader("🏉 Moyenne Équipe")
    cols = st.columns(6)
    
    with cols[0]:
        global_val = team_avg['global'] if team_avg and team_avg.get('global') else None
        st.metric("⚡ Global", f"{global_val:.1f}/5" if global_val else "-")
    
    for i, m in enumerate(METRICS):
        with cols[i + 1]:
            val = team_avg.get(m['key']) if team_avg else None
            st.metric(f"{m['icon']} {m['label']}", f"{val:.1f}/5" if val else "-")
    
    # Alertes
    alerts = get_alerts_for_date(date_key)
    if alerts:
        st.subheader(f"🚨 Alertes ({len(alerts)})")
        for alert in alerts[:8]:
            st.error(f"**{alert['player']}** - {alert['message']}")
    
    # Tableau joueurs
    st.subheader("👥 Joueurs du jour")
    
    col1, col2 = st.columns(2)
    with col1:
        filter_group = st.selectbox("Groupe", ["Tous", "Avants", "Trois-quarts"])
    with col2:
        show_issues = st.checkbox("🚨 Problèmes uniquement")
    
    table_data = []
    for d in today_data:
        player = next((p for p in st.session_state.players if p['name'] == d['name']), None)
        if not player:
            continue
        
        if filter_group != "Tous" and get_player_group(player['position']) != filter_group:
            continue
        
        avg = get_player_average(d)
        has_issue = any(d.get(m['key']) is not None and d.get(m['key']) <= 2 for m in METRICS)
        
        if show_issues and not has_issue:
            continue
        
        table_data.append({
            'Joueur': d['name'],
            'Poste': player['position'],
            'Statut': player['status'],
            '😴': d.get('sleep'),
            '🧠': d.get('mental_load'),
            '💪': d.get('motivation'),
            '❤️': d.get('hdc'),
            '💚': d.get('bdc'),
            'Moy': round(avg, 1) if avg else None,
            '⚖️': d.get('weight'),
            'Remarque': (d.get('remark', '') or '')[:30]
        })
    
    if table_data:
        df_display = pd.DataFrame(table_data)
        st.dataframe(df_display, use_container_width=True, height=400)
    else:
        st.info("Aucun joueur ne correspond aux filtres.")


def page_import():
    st.title("📥 Import / Export")
    
    st.subheader("📊 Importer depuis Google Sheets")
    
    sheet_url = st.text_input(
        "URL du Google Sheet",
        value="https://docs.google.com/spreadsheets/d/1Esm3NnED51jFpTs-oSjIdVybH51BSEcjhWOQhP1P3zI/edit?usp=sharing"
    )
    
    if st.button("🔄 Importer depuis Google Sheets", type="primary"):
        with st.spinner("Importation en cours..."):
            result, error = import_from_google_sheets(sheet_url)
            if error:
                st.error(f"❌ {error}")
            else:
                st.success(f"✅ Import réussi ! Date: {format_date(result['date'], 'full')} - {result['players_imported']} joueurs")
                st.balloons()
    
    st.divider()
    
    st.subheader("📁 Importer un fichier Excel")
    uploaded_file = st.file_uploader("Glissez votre fichier Excel ici", type=['xlsx', 'xls'])
    
    if uploaded_file:
        with st.spinner("Traitement..."):
            result, error = import_from_excel(uploaded_file)
            if error:
                st.error(f"❌ {error}")
            else:
                st.success(f"✅ {result['players_imported']} joueurs importés")
    
    st.divider()
    
    st.subheader("📅 Données disponibles")
    dates = sorted(st.session_state.wellness_data.keys(), reverse=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📊 Jours de données", len(dates))
    with col2:
        st.metric("👥 Joueurs", len(st.session_state.players))


def page_effectif():
    st.title("👥 Effectif")
    
    dates = sorted(st.session_state.wellness_data.keys(), reverse=True)
    date_key = dates[0] if dates else None
    today_data = st.session_state.wellness_data.get(date_key, []) if date_key else []
    
    if not st.session_state.players:
        st.warning("Aucun joueur. Importez des données d'abord.")
        return
    
    search = st.text_input("🔍 Rechercher")
    filtered_players = [p for p in st.session_state.players if search.lower() in p['name'].lower()]
    
    cols = st.columns(3)
    for i, player in enumerate(filtered_players):
        with cols[i % 3]:
            pd_data = next((d for d in today_data if d['name'] == player['name']), {})
            avg = get_player_average(pd_data)
            
            metrics_str = " | ".join([
                f"{m['icon']} {int(pd_data.get(m['key'])) if pd_data.get(m['key']) else '-'}"
                for m in METRICS
            ])
            
            st.markdown(f"""
            **{player['name']}** ({player['status']})  
            {player['position']}  
            {metrics_str}  
            Moy: {f"{avg:.1f}" if avg else "-"}/5
            """)
            st.divider()


def page_infirmerie():
    st.title("🏥 Infirmerie")
    
    # Compteurs
    counts = {s: len([p for p in st.session_state.players if p['status'] == s]) for s in STATUSES}
    
    cols = st.columns(4)
    cols[0].metric("✅ Aptes", counts['Apte'])
    cols[1].metric("🤕 Blessés", counts['Blessé'])
    cols[2].metric("🏥 Réhab", counts['Réhabilitation'])
    cols[3].metric("🏃 Réath", counts['Réathlétisation'])
    
    st.divider()
    
    # Nouvelle blessure
    with st.expander("➕ Nouvelle blessure"):
        col1, col2 = st.columns(2)
        with col1:
            injury_player = st.selectbox("Joueur", [p['name'] for p in st.session_state.players])
            injury_zone = st.selectbox("Zone", list(INJURY_ZONES.keys()))
            injury_grade = st.selectbox("Grade", [1, 2, 3])
        with col2:
            injury_date = st.date_input("Date")
            injury_circumstance = st.selectbox("Circonstance", CIRCUMSTANCES)
            estimated_days = INJURY_ZONES[injury_zone][injury_grade]
            st.info(f"⏱️ Estimation: {estimated_days} jours")
        
        injury_notes = st.text_input("Notes")
        
        if st.button("💾 Enregistrer", type="primary"):
            player = next((p for p in st.session_state.players if p['name'] == injury_player), None)
            if player:
                st.session_state.injuries.append({
                    'id': str(datetime.now().timestamp()),
                    'player_id': player['id'],
                    'player_name': player['name'],
                    'zone': injury_zone,
                    'grade': injury_grade,
                    'date': injury_date.isoformat(),
                    'circumstance': injury_circumstance,
                    'notes': injury_notes,
                    'estimated_days': estimated_days,
                    'estimated_return': (injury_date + timedelta(days=estimated_days)).isoformat()
                })
                player['status'] = 'Blessé'
                st.success("✅ Enregistré")
                st.rerun()
    
    # Liste blessures
    st.subheader("📋 Blessures")
    
    if not st.session_state.injuries:
        st.info("Aucune blessure")
    else:
        for inj in st.session_state.injuries:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{inj['player_name']}** - {INJURY_ZONES[inj['zone']]['icon']} {inj['zone']} Grade {inj['grade']}")
                st.caption(f"📅 {format_date(inj['date'])} → {format_date(inj['estimated_return'])}")
            with col2:
                if st.button("🗑️", key=f"del_{inj['id']}"):
                    st.session_state.injuries.remove(inj)
                    st.rerun()


def page_gestion():
    st.title("👤 Gestion des joueurs")
    
    with st.expander("➕ Ajouter un joueur"):
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("Nom")
            new_position = st.selectbox("Poste", ALL_POSITIONS)
        with col2:
            new_weight = st.number_input("Poids forme", value=90.0)
            new_status = st.selectbox("Statut", STATUSES)
        
        if st.button("💾 Ajouter", type="primary") and new_name:
            st.session_state.players.append({
                'id': str(datetime.now().timestamp()),
                'name': new_name.upper(),
                'position': new_position,
                'target_weight': new_weight,
                'status': new_status
            })
            st.rerun()
    
    st.divider()
    
    for player in st.session_state.players:
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            st.write(f"**{player['name']}** - {player['position']}")
        with col2:
            new_status = st.selectbox("", STATUSES, index=STATUSES.index(player['status']), key=f"s_{player['id']}", label_visibility="collapsed")
            if new_status != player['status']:
                player['status'] = new_status
        with col3:
            if st.button("🗑️", key=f"d_{player['id']}"):
                st.session_state.players = [p for p in st.session_state.players if p['id'] != player['id']]
                st.rerun()


def page_parametres():
    st.title("⚙️ Paramètres")
    
    settings = st.session_state.settings
    
    st.subheader("🚨 Seuils d'alertes")
    col1, col2, col3 = st.columns(3)
    with col1:
        settings['low_value_threshold'] = st.number_input("Valeur basse", 1, 5, settings['low_value_threshold'])
    with col2:
        settings['variation_threshold'] = st.number_input("Variation", 0.5, 4.0, settings['variation_threshold'], 0.5)
    with col3:
        settings['weight_threshold'] = st.number_input("Écart poids", 0.5, 10.0, settings['weight_threshold'], 0.5)
    
    if st.button("🔄 Réinitialiser"):
        st.session_state.settings = DEFAULT_SETTINGS.copy()
        st.rerun()


# ==================== MAIN ====================

def main():
    with st.sidebar:
        st.markdown("## ⚡ Wellness Tracker")
        st.caption("Rugby Performance")
        
        page = st.radio(
            "Navigation",
            ["📊 Dashboard", "📥 Import", "👥 Effectif", "🏥 Infirmerie", "👤 Joueurs", "⚙️ Paramètres"],
            label_visibility="collapsed"
        )
        
        dates = sorted(st.session_state.wellness_data.keys(), reverse=True)
        if dates:
            alerts = get_alerts_for_date(dates[0])
            if alerts:
                st.error(f"🚨 {len(alerts)} alertes")
        
        st.divider()
        st.caption(f"📊 {len(dates)} jours")
        st.caption(f"👥 {len(st.session_state.players)} joueurs")
    
    if page == "📊 Dashboard":
        page_dashboard()
    elif page == "📥 Import":
        page_import()
    elif page == "👥 Effectif":
        page_effectif()
    elif page == "🏥 Infirmerie":
        page_infirmerie()
    elif page == "👤 Joueurs":
        page_gestion()
    elif page == "⚙️ Paramètres":
        page_parametres()


if __name__ == "__main__":
    main()
