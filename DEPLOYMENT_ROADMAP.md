# 🚀 Feuille de Route Complète de Mise en Production
## Projet : Guide du Potager (Backend Django & Application Mobile Kivy)

---

## 📋 Table des Matières
1. [Vue d'Ensemble & Architecture](#1-vue-densemble--architecture)
2. [Étape 1 : Préparation & Configuration du Backend Django](#2-étape-1--préparation--configuration-du-backend-django)
3. [Étape 2 : Déploiement du Backend & Base de Données (PaaS / VPS)](#3-étape-2--déploiement-du-backend--base-de-données)
4. [Étape 3 : Stockage des Fichiers Médias (Images & Photos)](#4-étape-3--stockage-des-fichiers-médias)
5. [Étape 4 : Configuration & Validation Chariow en Production](#5-étape-4--configuration--validation-chariow-en-production)
6. [Étape 5 : Compilation & Déploiement Mobile (Android APK/AAB)](#6-étape-5--compilation--déploiement-mobile)
7. [Étape 6 : Monitoring, Sécurité & Sauvegardes](#7-étape-6--monitoring-sécurité--sauvegardes)
8. [Checklist Finale Avant Lancement](#8-checklist-finale-avant-lancement)

---

## 1. Vue d'Ensemble & Architecture

```text
       ┌───────────────────────────────────────────────────────────┐
       │             Application Mobile (Android / iOS)            │
       │                   Kivy + Python 3.11/3.13                 │
       │                  Cache SQLite Hors-ligne                  │
       └─────────────────────────────┬─────────────────────────────┘
                                     │  Requêtes HTTPS REST
                                     ▼
       ┌───────────────────────────────────────────────────────────┐
       │               Serveur API & Administration                │
       │                  Django + Gunicorn (WSGI)                 │
       │                     WhiteNoise (Statics)                  │
       └──────────────┬─────────────────────────────┬──────────────┘
                      │                             │
                      ▼                             ▼
       ┌──────────────────────────┐   ┌───────────────────────────┐
       │   PostgreSQL (Managé)    │   │  Stockage Médias (Images) │
       │  Données, Abonnements,   │   │   Cloudinary / AWS S3 /   │
       │   Légumes, Calendrier    │   │      Supabase Storage     │
       └──────────────────────────┘   └───────────────────────────┘
                      ▲
                      │  Webhooks Pulses (HMAC-SHA256)
       ┌──────────────┴───────────┐
       │  Passerelle Chariow Live │
       │ Wave / Orange / MTN MoMo │
       └──────────────────────────┘
```

---

## 2. Étape 1 : Préparation & Configuration du Backend Django

### 1.1 Variables d'environnement de production
Créez un fichier `.env` sur votre serveur de production (ou renseignez ces variables dans le panneau de votre hébergeur) :

```bash
# Sécurité & Environnement
DEBUG=False
SECRET_KEY=cle_ultra_secrete_aleatoire_de_minimum_50_caracteres
DJANGO_SETTINGS_MODULE=config.settings.production
ALLOWED_HOSTS=api.guidedupotager.com,guidedupotager.onrender.com,127.0.0.1

# Base de Données PostgreSQL
DATABASE_URL=postgres://potager_user:MotDePasseFort@postgres_host:5432/potager_prod_db

# Configuration Chariow Live (Mobile Money & Carte)
CHARIOW_API_KEY=chariow_live_sk_xxxxxxxxxxxxxxxxxxxx
CHARIOW_WEBHOOK_SECRET=chariow_whsec_xxxxxxxxxxxxxxxxxxxx
CHARIOW_BASE_URL=https://api.chariow.com/v1

# IDs des Produits Chariow configurés sur votre tableau de bord
CHARIOW_PRODUCT_MONTHLY_ID=prd_monthly_live_id
CHARIOW_PRODUCT_SEASONAL_ID=prd_seasonal_live_id
CHARIOW_PRODUCT_YEARLY_ID=prd_yearly_live_id

# Sécurité HTTPS / Cookies
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
CORS_ALLOWED_ORIGINS=https://guidedupotager.com,https://api.guidedupotager.com
```

### 1.2 Fichiers Statiques & WhiteNoise
Le fichier `backend/config/settings/production.py` intègre déjà WhiteNoise pour servir les fichiers statiques de l'administration Django de manière compressée et performante sans serveur web externe obligatoire.

---

## 3. Étape 2 : Déploiement du Backend & Base de Données

### Option A : Déploiement Clé en Main sur Render.com (Recommandé)

1. **Créer une base de données PostgreSQL** :
   * Sur le dashboard [Render.com](https://render.com), cliquez sur **New +** > **PostgreSQL**.
   * Nom : `potager-db`.
   * Notez l'URL interne de connexion (`Internal Database URL`).

2. **Créer le service Web Backend** :
   * Cliquez sur **New +** > **Web Service**.
   * Connectez votre dépôt Git (`Guide-du-Potager`).
   * Sélectionnez l'environnement **Docker** (Render détectera automatiquement le `Dockerfile` dans `backend/Dockerfile`).
   * Root Directory : `backend`.

3. **Variables d'environnement dans Render** :
   * Ajoutez les variables de l'Étape 1 (`DATABASE_URL`, `SECRET_KEY`, `CHARIOW_*`, etc.).

4. **Exécuter les migrations & le seed initial** :
   * Dans l'onglet **Shell** de votre service Render :
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py seed_data
   ```

---

### Option B : Déploiement sur Serveur VPS Dédié (Hetzner / OVH / DigitalOcean)

Si vous optez pour un VPS Ubuntu 22.04 / 24.04 :

1. **Installer Docker et Docker Compose** :
   ```bash
   sudo apt update && sudo apt install -y docker.io docker-compose-v2
   ```

2. **Fichier `docker-compose.prod.yml`** :
   ```yaml
   services:
     db:
       image: postgres:16-alpine
       restart: always
       environment:
         POSTGRES_DB: potager_db
         POSTGRES_USER: potager_user
         POSTGRES_PASSWORD: StrongPasswordHere!
       volumes:
         - pgdata:/var/lib/postgresql/data

     web:
       build:
         context: ./backend
         dockerfile: Dockerfile
       restart: always
       env_file: .env
       depends_on:
         - db
       ports:
         - "8000:8000"

   volumes:
     pgdata:
   ```

3. **Nginx Reverse Proxy & Certificat SSL Gratuit (Certbot)** :
   ```bash
   sudo apt install -y nginx certbot python3-certbot-nginx
   sudo certbot --nginx -d api.guidedupotager.com
   ```

---

## 4. Étape 3 : Stockage des Fichiers Médias

Dans un conteneur éphémère (Docker / Render), les images uploadées depuis l'administration Django ne doivent pas être stockées sur le disque local du conteneur.

### Solution Recommandée : Cloudinary (Gratuit & Optimisé)
1. Installez `django-cloudinary-storage` :
   ```bash
   pip install django-cloudinary-storage
   ```
2. Dans `backend/config/settings/production.py` :
   ```python
   CLOUDINARY_STORAGE = {
       'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
       'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
       'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
   }
   DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
   ```

---

## 5. Étape 4 : Configuration & Validation Chariow en Production

1. **Créer les Produits sur le Dashboard Chariow** :
   * Produit 1 : *Pass 1 Mois* (Prix : 2 500 XOF).
   * Produit 2 : *Pass Saison (3 Mois)* (Prix : 5 000 XOF).
   * Produit 3 : *Pass Annuel* (Prix : 15 000 XOF).
   * Copiez les identifiants de produits dans vos variables d'environnement ou directement dans l'admin Django (`SubscriptionPlanAdmin`).

2. **Configurer l'URL Webhook sur Chariow** :
   * Rendez-vous dans **Chariow Dashboard > Developers > Webhooks**.
   * URL de webhook :
     ```text
     https://api.guidedupotager.com/api/subscriptions/chariow/webhook/
     ```
   * Événement à écouter : `successful.sale`.
   * Récupérez la clé secrète de signature et assignez-la à `CHARIOW_WEBHOOK_SECRET`.

3. **Test Réel de Bout en Bout** :
   * Effectuez un premier achat réel avec un compte test via Wave ou Orange Money.
   * Vérifiez que le webhook renvoie un statut HTTP 200 et que l'utilisateur passe automatiquement en statut `Premium`.

---

## 6. Étape 5 : Compilation & Déploiement Mobile (Android APK/AAB)

### 6.1 Mettre à jour l'URL de l'API
Dans `mobile/app/utils/config.py` :
```python
import os

class Config:
    API_BASE_URL = os.environ.get('API_BASE_URL', 'https://api.guidedupotager.com/api')
    TIMEOUT = 12.0
```

### 6.2 Compilation Android avec Buildozer
La compilation Kivy nécessite un environnement Linux (WSL2 sous Windows ou machine virtuelle Ubuntu) :

```bash
cd mobile

# Nettoyage
buildozer android clean

# Compilation de l'APK Release
buildozer android release
```

### 6.3 Signature de l'APK / AAB pour le Google Play Store
Générez votre clé de signature (keystore) :
```bash
keytool -genkey -v -keystore potager-release.keystore -alias potager -keyalg RSA -keysize 2048 -validity 10000
```
Signez le fichier :
```bash
jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 -keystore potager-release.keystore bin/potager-0.1-arm64-v8a_armeabi-v7a-release-unsigned.aab potager
```

### 6.4 Distribution
* **Canal Direct (Rapide)** : Proposez l'APK en téléchargement direct sur votre site web ou via WhatsApp / Telegram pour vos premiers bêta-testeurs.
* **Google Play Store** : Créez une fiche d'application sur la [Google Play Console](https://play.google.com/console) (frais unique de 25 $).

---

## 7. Étape 6 : Monitoring, Sécurité & Sauvegardes

1. **Sauvegardes de la Base de Données** :
   * Si vous utilisez Render/Neon/Supabase : activez les sauvegardes automatiques quotidiennes (snapshots).
   * Sur VPS : planifiez une tâche cron `pg_dump` vers un stockage sécurisé distant.
2. **Suivi des Erreurs (Crash Reporting)** :
   * Installez **Sentry** (`pip install sentry-sdk`) pour recevoir une alerte instantanée par email en cas d'erreur inattendue sur l'API ou sur un webhook.
3. **Journalisation (Logs)** :
   * Consultez les logs de production avec `docker logs -f` ou via la console Render.

---

## 8. Checklist Finale Avant Lancement

- [ ] `DEBUG = False` vérifié sur le backend.
- [ ] Certificat SSL actif (cadenas vert `https://`).
- [ ] Migrations appliquées sur la base PostgreSQL distante (`migrate`).
- [ ] Superutilisateur créé pour l'accès à `/admin/`.
- [ ] Formules d'abonnement vérifiées dans l'admin (Pass 1 Mois, Pass Saison 3 Mois, Pass Annuel).
- [ ] Webhook Chariow configuré et testé en mode réel (Live).
- [ ] Fichiers statiques collectés (`collectstatic`).
- [ ] `API_BASE_URL` configuré vers le domaine de production dans le code mobile.
- [ ] APK / AAB testé sur un appareil Android réel (connexion, affichage hors-ligne, paiement).
