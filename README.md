# Guide du Potager 🌿

Application mobile éducative et interactive sur le jardinage potager et le maraîchage biologique (Kivy), communicant avec un backend Django REST API (Django REST Framework + JWT).

---

## 🚀 Fonctionnalités Principales

- **Authentification Sécurisée JWT** : Inscription, connexion, réinitialisation de mot de passe à jeton, profil et gestion de compte.
- **Parties & Chapitres Éducatifs** : Organisation hiérarchique avec affichage de contenu riche HTML, images intégrées dans le texte, temps de lecture et gestion des accès.
- **Simulateur Interactif de Calendrier de Semis & Récoltes** (`calendar_screen.py`) :
  - Sélection mensuelle interactive (Janvier à Décembre).
  - Filtrage par geste alternatif (*Semis & Plantations* vs *Récoltes*).
  - Génération du plan de culture sur-mesure avec fiches légumes, conseils et périodes.
- **📰 Module Blog & Actualités** (`apps/blog`) :
  - Publication d'articles par catégories (*Conseils de Saison*, *Permaculture*, etc.).
  - Support des images de couverture et des images secondaires intégrées dans le corps du texte.
  - **Gestion d'Accès Gratuit vs Premium** : Articles gratuits pour tous et articles exclusifs réservés aux abonnés Premium.
  - Espace commentaires sous chaque article pour les membres.
- **Dictionnaire Visuel Maraîcher & Pop-up Modale Détaillée** (`DetailPopup`) :
  - **Outils Maraîchers** (Grelinette, Transplantoir, Serouette, Semoir de précision...).
  - **Familles Botaniques** (Solanacées, Cucurbitacées, Fabacées, Brassicacées...).
  - **Fiches Légumes** avec périodes de semis, récoltes et conseils de soin.
  - **Fiches Maladies & Insectes** avec symptômes, dégâts, traitements bio et prévention.
  - Affichage direct des illustrations dans les cartes de liste + bouton **"Voir les détails →"**.
- **Interface Administrateur Django Enrichie** :
  - Téléversement d'images inline (`ChapterImageInline`, `PostImageInline`).
  - Aperçu miniature instantané et **générateur automatique de code HTML** prêt à copier/coller dans le texte des chapitres et articles.
- **Documentation OpenAPI & Swagger UI** :
  - Interface Swagger UI interactive accessible sur `http://127.0.0.1:8000/api/docs/`.
  - Schéma OpenAPI sur `http://127.0.0.1:8000/api/schema/`.
- **Pagination REST Rétrocompatible** (`FlexiblePageNumberPagination`) :
  - Pagination à 15 éléments par page par défaut avec paramètre `page_size=all` pour la réactivité mobile.
- **Système d'Abonnement Premium** :
  - Accès gratuit au contenu de base.
  - Déblocage Premium des chapitres avancés, fiches maladies/insectes, outils spécialisés et articles de blog exclusifs.
  - **Paiements** : Intégration simulée et prête pour **Orange Money**, **Wave**, **MTN Mobile Money** (Afrique de l'Ouest) et **Stripe**.
- **Mode Hors-ligne & Cache** : Mise en cache locale JSON des données consultées.

---

## 🛠️ Installation & Démarrage

### 1. Backend Django REST API

```bash
cd backend
python -m pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py seed_data  # Alimente la base avec du contenu éducatif et des articles de démonstration
python manage.py runserver
```

- **API REST** : `http://127.0.0.1:8000/api/`
- **Documentation Swagger UI** : `http://127.0.0.1:8000/api/docs/`
- **Administration Django** : `http://127.0.0.1:8000/admin/`

### Comptes de démonstration pré-créés par `seed_data` :
- **Utilisateur Gratuit** : `demo@potager.fr` / `potager123`
- **Utilisateur Premium** : `premium@potager.fr` / `potager123`

---

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
Guide du potager/
├── backend/                  # API REST Django
│   ├── apps/
│   │   ├── accounts/         # Utilisateurs & Authentification JWT
│   │   ├── content/          # Parties, Chapitres & Pagination
│   │   ├── blog/             # Articles, Catégories, Images & Commentaires
│   │   ├── glossary/         # Outils, Familles & Légumes
│   │   ├── pests/            # Maladies & Insectes
│   │   └── subscriptions/    # Abonnements & Paiements (Mobile & Stripe)
│   ├── config/               # Settings (base, dev, prod), URLs & Swagger OpenAPI
│   ├── tests/                # Suite de tests unitaires
│   ├── manage.py
│   └── requirements.txt
├── mobile/                   # Application Client Kivy
│   ├── app/
│   │   ├── screens/          # Login, Register, Home, Chapter, Calendar, Blog, PostDetail, Tools, Families, Vegetables, Diseases, Insects, Profile, Subscription
│   │   ├── services/         # APIClient, AuthService, ContentService, BlogService, GlossaryService, PestService, SubscriptionService, CacheService
│   │   ├── components/       # Drawer, Cards, SearchBar, DetailPopup, LoadingSpinner
│   │   ├── styles/           # Palette de thèmes naturels
│   │   └── utils/            # Config, Storage JSON, HTML Parser (Images & Balises)
│   ├── main.py
│   ├── buildozer.spec
│   └── requirements.txt
├── docker-compose.yml
└── README.md
```
