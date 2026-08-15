# Guide du Potager 🌿

Application mobile éducative et interactive sur le jardinage potager (Kivy) communiquant avec un Backend REST API Django (Django REST Framework + JWT).

---

## 🚀 Fonctionnalités Principales

- **Authentification Sécurisée JWT** : Inscription, connexion, réinitialisation de mot de passe, suppression de compte.
- **Parties & Chapitres Éducatifs** : Organisation hiérarchique avec affichage du contenu riche HTML/Kivy Markup, temps de lecture et images.
- **Dictionnaire Visuel Maraîcher** :
  - **Outils Maraîchers** (Grelinette, Transplantoir, Serouette, etc.)
  - **Familles Botaniques** (Solanacées, Cucurbitacées, Fabacées, Brassicacées)
  - **Fiches Légumes** avec périodes de semis, récolte et conseils de soins.
- **Fiches Maladies & Insectes** : Symptômes, dégâts, traitements bio et prévention.
- **Système d'Abonnement Premium** :
  - Accès gratuit aux chapitres de base.
  - Accès Premium débloquant les chapitres avancés, fiches maladies/insectes et outils de précision.
  - **Paiements** : Intégration simulée et prêt pour **Orange Money**, **Wave**, **MTN Mobile Money** (Afrique de l'Ouest) et **Stripe**.
- **Mode Hors-ligne / Cache** : Mise en cache locale des chapitres consultés.

---

## 🛠️ Installation & Démarrage

### 1. Backend Django REST API

```bash
cd backend
python -m pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py seed_data  # Alimente la base avec du contenu éducatif de démonstration
python manage.py runserver
```

L'API sera accessible sur `http://127.0.0.1:8000/api/`.

### Comptes de démonstration pré-créés par `seed_data` :
- **Utilisateur Gratuit** : `demo@potager.fr` / `potager123`
- **Utilisateur Premium** : `premium@potager.fr` / `potager123`

### 2. Application Mobile Kivy

```bash
cd mobile
python -m pip install -r requirements.txt
python main.py
```

### Build Android avec Buildozer :

```bash
cd mobile
buildozer android debug
```

---

## 🧪 Tests Unitaires Backend

```bash
python backend/manage.py test tests
```

---

## 📁 Structure du Projet

```text
guide-potager/
├── backend/                  # API REST Django
│   ├── apps/
│   │   ├── accounts/         # Utilisateurs & Authentification JWT
│   │   ├── content/          # Parties & Chapitres
│   │   ├── glossary/         # Outils, Familles & Légumes
│   │   ├── pests/            # Maladies & Insectes
│   │   └── subscriptions/    # Abonnements & Paiements (Mobile & Stripe)
│   ├── config/               # Settings (base, dev, prod) & URLs
│   ├── manage.py
│   └── requirements.txt
├── mobile/                   # Application Client Kivy
│   ├── app/
│   │   ├── screens/          # Login, Register, Home, Chapter, Tools, Families, Vegetables, Diseases, Insects, Profile, Subscription
│   │   ├── services/         # APIClient, AuthService, ContentService, GlossaryService, PestService, SubscriptionService, CacheService
│   │   ├── components/       # Drawer, Cards, SearchBar
│   │   ├── styles/           # Palette de thèmes naturels
│   │   └── utils/            # Config, Storage JSON, HTML Parser
│   ├── main.py
│   ├── buildozer.spec
│   └── requirements.txt
├── docker-compose.yml
└── README.md
```
