# Guide du Potager Tropical 🌿

Plateforme agronomique et éducative complète dédiée au maraîchage biologique et aux pratiques potagères adaptées au climat tropical et sahélien (Afrique de l'Ouest, Caraïbes, zones tropicales humides et arides).

Le projet comprend une double interface :
1. **Application Web moderne (Django + Tailwind CSS + Vanilla JS)** : Consultation responsive, téléchargement d'ebooks PDF A4, blog avec FAQ, simulateur de calendrier cultural, fiches de diagnostic et paiements sécurisés.
2. **Application Mobile native (Kivy / KivyMD)** : Conçue pour une utilisation au champ et sur parcelle avec mode hors-ligne intégral, schémas techniques en code ASCII/Unicode et navigation optimisée pour smartphones Android.
3. **API RESTful robuste (Django REST Framework + JWT + Swagger)** : Fournissant l'ensemble des données, l'authentification et les webhooks de paiement.

---

## 🚀 Fonctionnalités Détaillées

### 1. Agronomie & Contenus Pédagogiques
- **Manuel Complet & Chapitres Pédagogiques** (`apps/content`) :
  - Découpage hiérarchique en parties et chapitres (préparation du sol vivant, compostage, gestion économe de l'eau, associations végétales, biopesticides).
  - Support simultané **HTML & Markdown** pour l'ensemble des contenus (titres, tableaux, citations, listes ordonnées/à puces, code).
  - Support des schémas d'agronomie en blocs ASCII/Unicode (coupes de buttes, tranchées drainantes, paillage) avec préservation exacte des alignements.
  - Conversion automatique des notations et flèches mathématiques (`$\rightarrow$` $\rightarrow$ `→`).

- **Génération & Téléchargement de PDF Professionnels (A4)** :
  - **Ebook Complet du Guide** : Génération ReportLab de haute qualité avec page de garde stylisée, table des matières, numérotation dynamique (`Page X sur Y`), en-têtes/pieds de page personnalisés et rendu parfait des schémas monospaces.
  - **Articles de Blog en PDF** : Téléchargement individuel au format imprimable A4.

- **Simulateur de Calendrier Cultural Interactif** (`apps/glossary`) :
  - Sélection mensuelle interactive de Janvier à Décembre.
  - Filtrage immédiat par geste cultural (*Semis / Plantation* vs *Récolte*).
  - Conseils agronomiques spécifiques au mois sélectionné.
  - Profils climatiques détaillés : durée de cycle, tolérance à la chaleur, besoins hydriques, exposition solaire.

- **Dictionnaire & Clinique des Plantes** :
  - **Fiches Légumes** : Périodes de semis/récolte, variétés tropicales recommandées, besoins thermiques et conseils de culture.
  - **Familles Botaniques** : Règles de rotation triennale et quadriennale pour casser le cycle des pathogènes du sol.
  - **Maladies Cryptogamiques & Bactériennes** (`apps/pests`) : Diagnostic précoce, symptômes foliaires, mesures préventives et recettes bio tropicales (purins, décoctions de neem, piment, cendre).
  - **Insectes Nuisibles & Biocontrôle** (`apps/pests`) : Identification, dégâts caractéristiques, auxiliaires et barrières agro-écologiques.
  - **Outils Maraîchers de Précision** : Guide ergonomique du matériel respectueux de la vie du sol (grelinette, semoirs de précision, toiles d'ombrage, etc.).

### 2. Module Blog & Foire Aux Questions
- Articles thématiques riches mêlant approches conventionnelles raisonnées et bio-intensives.
- Foire Aux Questions (FAQ) interactive intégrée sous chaque article (accordéon collapsible).
- Espace commentaires interactif pour les membres.
- Système de planification de publication pour les administrateurs (articles brouillons, planifiés, publiés).

### 3. Monétisation & Abonnements Flexibles
- **Abonnements Premium** (`apps/subscriptions`) :
  - Formules administrables depuis le back-office : Mensuel, Saison Potager (3 mois), Annuel.
  - Déblocage automatique des chapitres d'experts, des fiches de maladies/insectes exclusives et des recettes curatives.
- **Achats Numériques à l'Unité (Pay-per-Content)** :
  - Achat du Guide Complet en Ebook PDF téléchargeable à vie.
  - Achat d'articles de blog individuels avec accès permanent et téléchargement PDF.
- **Passerelle de Paiement Chariow** :
  - Paiement sécurisé par **Mobile Money** (Wave, Orange Money, MTN Mobile Money, Moov) et **Carte Bancaire**.
  - Gestion sécurisée des webhooks (`/api/subscriptions/webhook/chariow/`) avec signature cryptographique HMAC-SHA256 et idempotence.

### 4. Authentification & Sécurité
- Authentification basée sur jetons JWT (`rest_framework_simplejwt`) pour le mobile et sessions Django pour le web.
- Protection CSRF et filtrage CORS configuré.
- Paywall progressif vert clair préservant le SEO et invitant à l'abonnement.

---

## 🏗️ Architecture du Projet

```text
Guide du potager/
├── backend/                              # Backend Django & API REST
│   ├── apps/
│   │   ├── accounts/                     # Gestion des utilisateurs & profils JWT
│   │   ├── blog/                         # Articles, catégories, images, FAQ & commentaires
│   │   ├── content/                      # Parties, chapitres, moteur de rendu & générateur PDF
│   │   │   ├── rendering.py              # Moteur de rendu universel Markdown + HTML + LaTeX
│   │   │   └── pdf_service.py            # Générateur ReportLab (Guide complet & articles A4)
│   │   ├── glossary/                     # Légumes, familles botaniques, outils & calendrier
│   │   ├── pests/                        # Maladies, insectes nuisibles & biocontrôle
│   │   ├── subscriptions/                # Formules, paiements Chariow & achats à l'unité
│   │   └── web/                          # Vues et contrôleurs de la plateforme Web
│   ├── config/                           # Paramètres Django (base, dev, prod), URLs, OpenAPI
│   ├── static/                           # Feuilles CSS, JS, favicons et logos
│   ├── templates/                        # Templates HTML Tailwind (web & composants)
│   ├── tests/                            # Suite de tests automatisés
│   ├── manage.py
│   └── requirements.txt
│
├── mobile/                               # Application Client Kivy Mobile (Android / Desktop)
│   ├── app/
│   │   ├── assets/                       # Icônes de l'application & polices TTF (Consolas, DejaVu)
│   │   ├── components/                   # Widgets réutilisables (Cards, DetailPopup, Drawer, etc.)
│   │   ├── screens/                      # Écrans Kivy (Home, Chapter, Blog, Calendar, etc.)
│   │   ├── services/                     # Clients d'API, gestion du cache & authentification
│   │   ├── styles/                       # Thèmes et palette de couleurs naturelles
│   │   └── utils/                        # Parser HTML/Markdown vers Kivy BBCode & Config
│   ├── buildozer.spec                    # Configuration de compilation Android APK/AAB
│   ├── main.py                           # Point d'entrée de l'application Kivy
│   └── requirements.txt
│
├── docker-compose.yml                    # Environnement conteneurisé de développement
├── docker-compose.prod.yml               # Déploiement conteneurisé de production
├── GUIDE_MISE_EN_PRODUCTION.md           # Guide complet de déploiement (Nginx, Gunicorn, PostgreSQL)
└── README.md                             # Documentation principale du projet
```

---

## 🛠️ Installation & Démarrage

### Prérequis
- Python 3.10 ou supérieur
- Git
- Un environnement virtuel dédié pour le backend et le mobile

---

### 1. Démarrage du Backend (Web & API REST)

```bash
# 1. Cloner le dépôt et se positionner dans le dossier backend
cd backend

# 2. Créer et activer un environnement virtuel
python -m venv .venv
# Sur Windows :
.venv\Scripts\activate
# Sur Linux/macOS :
source .venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Appliquer les migrations de base de données
python manage.py makemigrations
python manage.py migrate

# 5. Charger le jeu de données initial (cultures, chapitres, fiches bio)
python manage.py seed_data

# 6. Lancer le serveur de développement
python manage.py runserver
```

#### Points d'accès Backend :
- **Plateforme Web** : [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **API REST** : [http://127.0.0.1:8000/api/](http://127.0.0.1:8000/api/)
- **Documentation OpenAPI / Swagger** : [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)
- **Administration Django** : [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

#### Comptes de démonstration créés par `seed_data` :
- **Membre Standard (Gratuit)** : `demo@potager.fr` / `potager123`
- **Membre Premium (Abonné)** : `premium@potager.fr` / `potager123`
- **Administrateur** : `admin@potager.fr` / `potager123` (ou créé via `createsuperuser`)

---

### 2. Démarrage de l'Application Mobile (Kivy)

```bash
# 1. Se positionner dans le dossier mobile
cd mobile

# 2. Créer et activer un environnement virtuel dédié
python -m venv .env
# Sur Windows :
.env\Scripts\activate
# Sur Linux/macOS :
source .env/bin/activate

# 3. Installer les dépendances Kivy
pip install -r requirements.txt

# 4. Lancer l'application
python main.py
```

#### Configuration Mobile :
L'URL de l'API est configurable dans `mobile/app/utils/config.py` ou via un fichier `.env` :
```env
API_BASE_URL=http://127.0.0.1:8000/api
```
*(Pour tester sur un smartphone physique Android relié au même réseau Wi-Fi, remplacez `127.0.0.1` par l'adresse IP locale de votre machine, ex: `http://192.168.1.50:8000/api`).*

---

### 3. Compilation du Paquet Android (APK / AAB)

La compilation s'effectue sous Linux (ou WSL2 sur Windows) à l'aide de **Buildozer** :

```bash
cd mobile
buildozer android debug
```
L'APK prêt à être installé se trouvera dans le dossier `mobile/bin/`.

---

## 🧪 Tests & Qualité du Code

Exécutez la suite complète de tests unitaires et d'intégration Django :

```bash
cd backend
python manage.py test tests
```

Vérification de l'intégrité du projet Django :
```bash
python manage.py check
```

---

## 💳 Configuration des Paiements Chariow

Pour activer les paiements par Mobile Money et Carte Bancaire :
1. Créez un compte marchand sur [Chariow](https://chariow.com/).
2. Renseignez vos clés API dans `backend/.env` :
   ```env
   CHARIOW_SECRET_KEY=votre_cle_secrete
   CHARIOW_WEBHOOK_SECRET=votre_secret_webhook
   CHARIOW_PUBLIC_KEY=votre_cle_publique
   ```
3. Configurez l'URL de rappel du webhook dans votre tableau de bord Chariow :
   `https://votre-domaine.com/api/subscriptions/webhook/chariow/`

---

## 📄 Licence & Droits

Tous droits réservés © Guide du Potager Tropical. Ce logiciel et ses contenus agronomiques sont protégés par le droit d'auteur.
