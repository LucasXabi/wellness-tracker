"""
Pages de l'application Wellness Tracker
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

from config import (
    METRICS, ALL_POSITIONS, ALL_LINES, INJURY_ZONES, 
    CIRCUMSTANCES, STATUSES, DEFAULT_SETTINGS,
    get_player_group, get_player_line, get_player_average,
    format_date, get_color_for_value, get_status_color
)

# ==================== PAGE DASHBOARD ====================

def page_dashboard(get_team_averages, get_group_averages, get_alerts_for_date, 
                   calculate_zscore_series, render_metric_card, render_radar_chart, render_zscore_chart):
    """Page Dashboard"""
    st.title("📊 Dashboard Wellness")
    
    dates = sorted(st.session_state.wellness_data.keys(), reverse=True)
    
    if not dates:
        st.warning("⚠️ Aucune donnée importée. Utilisez la page Import pour charger vos données.")
        return
    
    col1, col2 = st.columns([3, 1])
    with col1:
        selected_date = st.selectbox(
            "📅 Date",
            dates,
            format_func=lambda x: format_date(x, 'full'),
            key="dashboard_date"
        )
    
    date_key = selected_date
    today_data = st.session_state.wellness_data.get(date_key, [])
    team_avg = get_team_averages(date_key)
    
    # Cartes moyennes équipe
    st.subheader("🏉 Moyenne Équipe")
    cols = st.columns(6)
    
    with cols[0]:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); 
                    padding: 1rem; border-radius: 0.75rem; text-align: center;">
            <div style="font-size: 24px;">⚡</div>
            <div style="color: rgba(255,255,255,0.8); font-size: 12px;">Global</div>
            <div style="color: white; font-size: 28px; font-weight: bold;">
                {f"{team_avg['global']:.1f}" if team_avg and team_avg.get('global') else "-"}/5
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    for i, m in enumerate(METRICS):
        with cols[i + 1]:
            val = team_avg.get(m['key']) if team_avg else None
            render_metric_card(m['label'], val, m['icon'])
    
    # Alertes
    alerts = get_alerts_for_date(date_key)
    if alerts:
        st.subheader(f"🚨 Alertes ({len(alerts)})")
        alert_cols = st.columns(min(len(alerts), 4))
        for i, alert in enumerate(alerts[:8]):
            with alert_cols[i % 4]:
                color = "#ef4444" if alert['type'] == 'critical' else "#f59e0b"
                st.markdown(f"""
                <div style="background: {color}15; border: 1px solid {color}; padding: 0.75rem; 
                            border-radius: 0.5rem; margin-bottom: 0.5rem;">
                    <div style="font-weight: 600; color: white;">{alert['player']}</div>
                    <div style="color: {color}; font-size: 13px;">{alert['message']}</div>
                </div>
                """, unsafe_allow_html=True)
    
    # Tableau joueurs
    st.subheader("👥 Joueurs du jour")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_group = st.selectbox("Groupe", ["Tous", "Avants", "Trois-quarts"], key="filter_group")
    with col2:
        filter_line = st.selectbox("Ligne", ["Toutes"] + ALL_LINES, key="filter_line")
    with col3:
        show_issues = st.checkbox("🚨 Problèmes uniquement", key="show_issues")
    
    table_data = []
    for d in today_data:
        player = next((p for p in st.session_state.players if p['name'] == d['name']), None)
        if not player:
            continue
        
        if filter_group != "Tous" and get_player_group(player['position']) != filter_group:
            continue
        if filter_line != "Toutes" and get_player_line(player['position']) != filter_line:
            continue
        
        avg = get_player_average(d)
        has_issue = any(d.get(m['key']) is not None and d.get(m['key']) <= 2 for m in METRICS) or player['status'] == 'Blessé'
        
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
            'Moy': avg,
            '⚖️': d.get('weight'),
            'Remarque': (d.get('remark', '') or '')[:30]
        })
    
    if table_data:
        df_display = pd.DataFrame(table_data)
        
        def color_cell(val):
            if pd.isna(val) or val is None:
                return 'background-color: #374151'
            if isinstance(val, (int, float)) and val <= 5:
                color = get_color_for_value(val)
                return f'background-color: {color}; color: white; font-weight: bold'
            return ''
        
        styled_df = df_display.style.applymap(
            color_cell, 
            subset=['😴', '🧠', '💪', '❤️', '💚']
        ).format({
            'Moy': '{:.1f}',
            '⚖️': '{:.1f}'
        }, na_rep='-')
        
        st.dataframe(styled_df, use_container_width=True, height=400)
    else:
        st.info("Aucun joueur ne correspond aux filtres.")
    
    # Courbe Z-Score
    st.subheader("📈 Courbe Z-Score")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        zscore_metric = st.selectbox(
            "Métrique",
            ['global'] + [m['key'] for m in METRICS],
            format_func=lambda x: "⚡ Global" if x == 'global' else next((f"{m['icon']} {m['label']}" for m in METRICS if m['key'] == x), x),
            key="zscore_metric"
        )
    with col2:
        zscore_group = st.selectbox("Groupe", ["Équipe", "Avants", "Trois-quarts"], key="zscore_group")
    with col3:
        zscore_days = st.selectbox("Période", [7, 14, 30, 60], index=2, key="zscore_days")
    
    group_filter = None if zscore_group == "Équipe" else zscore_group
    zscore_data = calculate_zscore_series(metric=zscore_metric, group=group_filter, days=zscore_days)
    
    fig = render_zscore_chart(zscore_data)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Pas assez de données pour calculer le Z-Score.")
    
    # Radar
    st.subheader("📊 Comparaison Radar")
    col1, col2 = st.columns(2)
    with col1:
        compare1 = st.selectbox("Comparer", ["Équipe", "Avants", "Trois-quarts"], key="compare1")
    with col2:
        compare2 = st.selectbox("Avec", ["Équipe", "Avants", "Trois-quarts"], index=1, key="compare2")
    
    data1 = get_group_averages(date_key, group=None if compare1 == "Équipe" else compare1)
    data2 = get_group_averages(date_key, group=None if compare2 == "Équipe" else compare2)
    
    if data1 or data2:
        fig = render_radar_chart(data1, data2, compare1, compare2)
        st.plotly_chart(fig, use_container_width=True)


# ==================== PAGE IMPORT ====================

def page_import(import_from_google_sheets, import_from_excel):
    """Page Import/Export"""
    st.title("📥 Import / Export")
    
    st.subheader("📊 Importer depuis Google Sheets")
    
    sheet_url = st.text_input(
        "URL du Google Sheet",
        value="https://docs.google.com/spreadsheets/d/1Esm3NnED51jFpTs-oSjIdVybH51BSEcjhWOQhP1P3zI/edit?usp=sharing",
        key="sheet_url"
    )
    
    if st.button("🔄 Importer depuis Google Sheets", type="primary"):
        with st.spinner("Importation en cours..."):
            result, error = import_from_google_sheets(sheet_url)
            if error:
                st.error(f"❌ {error}")
            else:
                st.success(f"✅ Import réussi ! Date: {format_date(result['date'], 'full')} - {result['players_imported']} joueurs - {result['new_players']} nouveaux")
                st.balloons()
    
    st.divider()
    
    st.subheader("📁 Importer un fichier Excel")
    uploaded_file = st.file_uploader("Glissez votre fichier Excel ici", type=['xlsx', 'xls'], key="excel_upload")
    
    if uploaded_file:
        with st.spinner("Traitement du fichier..."):
            result, error = import_from_excel(uploaded_file)
            if error:
                st.error(f"❌ {error}")
            else:
                st.success(f"✅ Import réussi ! {result['players_imported']} joueurs importés")
    
    st.divider()
    
    st.subheader("📅 Données disponibles")
    dates = sorted(st.session_state.wellness_data.keys(), reverse=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📊 Jours de données", len(dates))
    with col2:
        st.metric("👥 Joueurs", len(st.session_state.players))
    
    if dates:
        st.write("**Dates chargées:**")
        date_chips = " ".join([f"`{format_date(d)}`" for d in dates[:20]])
        st.markdown(date_chips)


# ==================== PAGE EFFECTIF ====================

def page_effectif(get_group_averages):
    """Page Effectif"""
    st.title("👥 Effectif & Comparaisons")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Liste", "📊 Comparer", "📈 Période", "👥 Groupes"])
    
    dates = sorted(st.session_state.wellness_data.keys(), reverse=True)
    date_key = dates[0] if dates else None
    today_data = st.session_state.wellness_data.get(date_key, []) if date_key else []
    
    with tab1:
        if not st.session_state.players:
            st.warning("Aucun joueur. Importez des données d'abord.")
            return
        
        search = st.text_input("🔍 Rechercher", key="search_player")
        filtered_players = [p for p in st.session_state.players if search.lower() in p['name'].lower()]
        
        cols = st.columns(3)
        for i, player in enumerate(filtered_players):
            with cols[i % 3]:
                pd_data = next((d for d in today_data if d['name'] == player['name']), {})
                avg = get_player_average(pd_data)
                color = get_status_color(player['status'])
                
                metrics_html = ""
                for m in METRICS:
                    val = pd_data.get(m['key'])
                    cell_color = get_color_for_value(val)
                    metrics_html += f'<span style="display: inline-block; width: 24px; height: 24px; background: {cell_color}; border-radius: 4px; text-align: center; line-height: 24px; font-size: 11px; color: white; margin: 1px;">{int(val) if val else "-"}</span>'
                
                st.markdown(f"""
                <div style="background: #1f2937; padding: 1rem; border-radius: 0.75rem; border: 1px solid #374151; margin-bottom: 0.5rem;">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                        <div>
                            <div style="font-weight: 600; color: white;">{player['name']}</div>
                            <div style="font-size: 11px; color: #9ca3af;">{player['position']}</div>
                        </div>
                        <span style="background: {color}20; color: {color}; padding: 2px 8px; border-radius: 9999px; font-size: 11px;">{player['status']}</span>
                    </div>
                    <div style="margin: 8px 0;">{metrics_html}</div>
                    <div style="display: flex; justify-content: space-between; font-size: 11px; color: #9ca3af;">
                        <span>⚖️ {pd_data.get('weight', '-') or '-'}kg</span>
                        <span style="font-weight: 600;">Moy: {f"{avg:.1f}" if avg else "-"}/5</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    with tab2:
        st.write("**Sélectionnez 2-6 joueurs:**")
        selected = st.multiselect("Joueurs", [p['name'] for p in st.session_state.players], max_selections=6, key="compare_players")
        
        if len(selected) >= 2:
            fig = go.Figure()
            colors = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']
            
            for i, name in enumerate(selected):
                pd_data = next((d for d in today_data if d['name'] == name), {})
                values = [pd_data.get(m['key'], 0) or 0 for m in METRICS]
                values.append(values[0])
                
                fig.add_trace(go.Scatterpolar(
                    r=values, theta=[m['label'] for m in METRICS] + [METRICS[0]['label']],
                    fill='toself', name=name, line_color=colors[i % len(colors)]
                ))
            
            fig.update_layout(polar=dict(radialaxis=dict(range=[0, 5])), paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#9ca3af'), height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        if not dates:
            st.warning("Aucune donnée.")
            return
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Début", value=datetime.strptime(dates[-1], '%Y-%m-%d'))
        with col2:
            end_date = st.date_input("Fin", value=datetime.strptime(dates[0], '%Y-%m-%d'))
        
        selected_players = st.multiselect("Joueurs", [p['name'] for p in st.session_state.players], key="period_players")
        
        if selected_players:
            fig = go.Figure()
            colors = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']
            
            for i, name in enumerate(selected_players):
                history = []
                for date in sorted(dates):
                    d_date = datetime.strptime(date, '%Y-%m-%d').date()
                    if d_date < start_date or d_date > end_date:
                        continue
                    pd_data = next((d for d in st.session_state.wellness_data.get(date, []) if d['name'] == name), None)
                    if pd_data:
                        history.append({'date': date, 'avg': get_player_average(pd_data)})
                
                if history:
                    df = pd.DataFrame(history)
                    fig.add_trace(go.Scatter(x=df['date'], y=df['avg'], mode='lines+markers', name=name, line=dict(color=colors[i % len(colors)], width=2)))
            
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='#1f2937', font=dict(color='#9ca3af'), height=400, yaxis=dict(range=[1, 5]))
            st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        if not date_key:
            return
        
        groups_data = []
        
        team = get_group_averages(date_key)
        if team:
            row = {'Groupe': '🏉 Équipe', 'Eff.': len(st.session_state.players)}
            for m in METRICS:
                row[m['icon']] = team.get(m['key'])
            row['Moy'] = team.get('global')
            groups_data.append(row)
        
        for group in ['Avants', 'Trois-quarts']:
            avg = get_group_averages(date_key, group=group)
            if avg:
                emoji = '💪' if group == 'Avants' else '🏃'
                row = {'Groupe': f'{emoji} {group}', 'Eff.': avg.get('count', 0)}
                for m in METRICS:
                    row[m['icon']] = avg.get(m['key'])
                row['Moy'] = avg.get('global')
                groups_data.append(row)
        
        for line in ALL_LINES:
            avg = get_group_averages(date_key, line=line)
            if avg and avg.get('count', 0) > 0:
                row = {'Groupe': f'  └ {line}', 'Eff.': avg.get('count', 0)}
                for m in METRICS:
                    row[m['icon']] = avg.get(m['key'])
                row['Moy'] = avg.get('global')
                groups_data.append(row)
        
        if groups_data:
            df = pd.DataFrame(groups_data)
            st.dataframe(df.style.format({m['icon']: '{:.1f}' for m in METRICS} | {'Moy': '{:.1f}'}, na_rep='-'), use_container_width=True)


# ==================== PAGE INFIRMERIE ====================

def page_infirmerie():
    """Page Infirmerie"""
    st.title("🏥 Infirmerie")
    
    # Compteurs
    counts = {s: len([p for p in st.session_state.players if p['status'] == s]) for s in STATUSES}
    
    cols = st.columns(4)
    for i, (status, emoji, color) in enumerate([('Apte', '✅', 'green'), ('Blessé', '🤕', 'red'), ('Réhabilitation', '🏥', 'orange'), ('Réathlétisation', '🏃', 'blue')]):
        with cols[i]:
            if st.button(f"{emoji} {counts[status]}", key=f"status_{status}", use_container_width=True):
                st.session_state.selected_status = status if st.session_state.get('selected_status') != status else None
                st.rerun()
            st.caption(status)
    
    # Joueurs filtrés
    if st.session_state.get('selected_status'):
        status = st.session_state.selected_status
        filtered = [p for p in st.session_state.players if p['status'] == status]
        
        st.subheader(f"Joueurs {status}s ({len(filtered)})")
        cols = st.columns(3)
        for i, player in enumerate(filtered):
            with cols[i % 3]:
                st.markdown(f"**{player['name']}** - {player['position']}")
                new_status = st.selectbox("Statut", STATUSES, index=STATUSES.index(player['status']), key=f"cs_{player['id']}")
                if new_status != player['status']:
                    player['status'] = new_status
                    st.rerun()
    
    st.divider()
    
    # Nouvelle blessure
    with st.expander("➕ Nouvelle blessure", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            injury_player = st.selectbox("Joueur", [p['name'] for p in st.session_state.players], key="inj_player")
            injury_zone = st.selectbox("Zone", list(INJURY_ZONES.keys()), format_func=lambda x: f"{INJURY_ZONES[x]['icon']} {x}", key="inj_zone")
            injury_grade = st.selectbox("Grade", [1, 2, 3], key="inj_grade")
        with col2:
            injury_date = st.date_input("Date", key="inj_date")
            injury_circumstance = st.selectbox("Circonstance", CIRCUMSTANCES, key="inj_circ")
            estimated_days = INJURY_ZONES[injury_zone][injury_grade]
            st.info(f"⏱️ Estimation: {estimated_days} jours")
        
        injury_notes = st.text_input("Notes", key="inj_notes")
        
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
            player = next((p for p in st.session_state.players if p['id'] == inj['player_id']), None)
            start = datetime.strptime(inj['date'], '%Y-%m-%d')
            end = datetime.strptime(inj['estimated_return'], '%Y-%m-%d')
            progress = min(100, max(0, (datetime.now() - start).days / max(1, (end - start).days) * 100))
            
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{inj['player_name']}** - {INJURY_ZONES[inj['zone']]['icon']} {inj['zone']} Grade {inj['grade']}")
                st.caption(f"📅 {format_date(inj['date'])} → {format_date(inj['estimated_return'])}")
                st.progress(progress / 100)
            with col2:
                if st.button("🗑️", key=f"del_inj_{inj['id']}"):
                    st.session_state.injuries.remove(inj)
                    st.rerun()
            st.divider()


# ==================== PAGE GESTION ====================

def page_gestion():
    """Page Gestion"""
    st.title("👤 Gestion des joueurs")
    
    with st.expander("➕ Ajouter un joueur"):
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("Nom", key="new_name")
            new_position = st.selectbox("Poste", ALL_POSITIONS, key="new_pos")
        with col2:
            new_weight = st.number_input("Poids forme", value=90.0, key="new_weight")
            new_status = st.selectbox("Statut", STATUSES, key="new_status")
        
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
        col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 1])
        
        with col1:
            player['name'] = st.text_input("", value=player['name'], key=f"n_{player['id']}", label_visibility="collapsed")
        with col2:
            idx = ALL_POSITIONS.index(player['position']) if player['position'] in ALL_POSITIONS else 0
            player['position'] = st.selectbox("", ALL_POSITIONS, index=idx, key=f"p_{player['id']}", label_visibility="collapsed")
        with col3:
            player['target_weight'] = st.number_input("", value=float(player.get('target_weight', 90)), key=f"w_{player['id']}", label_visibility="collapsed")
        with col4:
            player['status'] = st.selectbox("", STATUSES, index=STATUSES.index(player['status']), key=f"s_{player['id']}", label_visibility="collapsed")
        with col5:
            if st.button("🗑️", key=f"del_{player['id']}"):
                st.session_state.delete_confirm = player['id']
        
        if st.session_state.get('delete_confirm') == player['id']:
            st.warning(f"⚠️ Supprimer {player['name']} ?")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ Oui", key=f"y_{player['id']}"):
                    st.session_state.players = [p for p in st.session_state.players if p['id'] != player['id']]
                    st.session_state.delete_confirm = None
                    st.rerun()
            with c2:
                if st.button("❌ Non", key=f"no_{player['id']}"):
                    st.session_state.delete_confirm = None
                    st.rerun()


# ==================== PAGE PARAMETRES ====================

def page_parametres():
    """Page Paramètres"""
    st.title("⚙️ Paramètres")
    
    settings = st.session_state.settings
    
    st.subheader("🚨 Seuils d'alertes")
    col1, col2, col3 = st.columns(3)
    with col1:
        settings['low_value_threshold'] = st.number_input("Valeur basse", 1, 5, settings['low_value_threshold'])
    with col2:
        settings['variation_threshold'] = st.number_input("Variation", 0.5, 4.0, settings['variation_threshold'], 0.5)
    with col3:
        settings['weight_threshold'] = st.number_input("Écart poids (kg)", 0.5, 10.0, settings['weight_threshold'], 0.5)
    
    st.subheader("📈 Z-Score")
    col1, col2, col3 = st.columns(3)
    with col1:
        settings['zscore_days'] = st.number_input("Période (jours)", 7, 60, settings['zscore_days'])
    with col2:
        settings['zscore_warning'] = st.number_input("Seuil attention", -3.0, 0.0, settings['zscore_warning'], 0.1)
    with col3:
        settings['zscore_alert'] = st.number_input("Seuil alerte", -3.0, 0.0, settings['zscore_alert'], 0.1)
    
    if st.button("🔄 Réinitialiser"):
        st.session_state.settings = DEFAULT_SETTINGS.copy()
        st.rerun()
