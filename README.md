# 🏉 Rugby Wellness Tracker

Application de suivi du bien-être des joueurs de rugby, développée avec Streamlit.

## ✨ Fonctionnalités

- 📊 **Dashboard** : Vue globale avec moyennes équipe, alertes, tableau joueurs, courbe Z-Score
- 📥 **Import** : Import direct depuis Google Sheets ou fichier Excel
- 👥 **Effectif** : Liste des joueurs, comparaisons radar, analyse par période, groupes
- 🏥 **Infirmerie** : Gestion des blessures avec estimation automatique de retour
- ⚙️ **Paramètres** : Configuration des seuils d'alertes et Z-Score

## 🚀 Déploiement sur Streamlit Cloud (GRATUIT)

### Étape 1 : Créer un compte GitHub (si pas déjà fait)
1. Aller sur [github.com](https://github.com)
2. S'inscrire gratuitement

### Étape 2 : Créer un repository GitHub
1. Cliquer sur "New repository"
2. Nommer le repo "wellness-tracker"
3. Laisser public
4. Créer

### Étape 3 : Uploader les fichiers
Uploader ces fichiers dans le repo :
- `app.py`
- `config.py`
- `pages.py`
- `requirements.txt`
- `.streamlit/config.toml`

### Étape 4 : Déployer sur Streamlit Cloud
1. Aller sur [share.streamlit.io](https://share.streamlit.io)
2. Se connecter avec GitHub
3. Cliquer "New app"
4. Sélectionner votre repo "wellness-tracker"
5. Branch: `main`
6. Main file path: `app.py`
7. Cliquer "Deploy!"

### Étape 5 : C'est prêt ! 🎉
Votre app sera accessible à : `https://votre-nom-wellness-tracker.streamlit.app`

## 📊 Format Google Sheets attendu

L'app reconnaît automatiquement ce format :

```
Ligne 1: (vide ou titre)
Ligne 2: Date en français (ex: "mardi 6 janvier 2026")
Ligne 3: En-têtes (Joueur, Poids, Sommeil, Charge mentale, Motivation, HDC, BDC, Moyenne, Remarque)
Ligne 4: EQUIPE (ignorée)
Ligne 5+: Données des joueurs
```

**Important** : Le Google Sheet doit être partagé en "Accessible à tous ceux qui ont le lien".

## 🔧 Structure des fichiers

```
wellness-tracker/
├── app.py              # Application principale
├── config.py           # Configuration et utilitaires
├── pages.py            # Pages de l'application
├── requirements.txt    # Dépendances Python
├── .streamlit/
│   └── config.toml     # Configuration Streamlit (thème)
└── README.md
```

## 📱 Utilisation

1. **Importer les données** : Aller sur "Import/Export" et cliquer "Importer depuis Google Sheets"
2. **Consulter le Dashboard** : Voir les moyennes, alertes, et graphiques
3. **Gérer les blessures** : Page "Infirmerie"
4. **Configurer** : Page "Paramètres" pour ajuster les seuils

## 🛠️ Développement local

```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer l'app
streamlit run app.py
```

## 📝 Notes

- Les données sont stockées en session (perdues si on ferme l'onglet)
- Pour une persistance permanente, connecter à Supabase (voir documentation avancée)
- Le Google Sheet reste la source de vérité pour la saisie

---

Développé avec ❤️ pour le rugby 🏉
