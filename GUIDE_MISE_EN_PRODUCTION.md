# 🌿 Guide Complet de Mise en Production
## Application « Guide du Potager Tropical » (Backend Django REST & Client Mobile Kivy)

Ce document détaille toutes les étapes, configurations et commandes nécessaires pour déployer l'infrastructure backend en haute disponibilité et distribuer l'application mobile auprès des utilisateurs finaux (Google Play Store et téléchargement direct APK).

---

## 📑 Table des Matières

1. [Architecture Globale de Production](#1-architecture-globale-de-production)
2. [Prérequis Généraux](#2-prérequis-généraux)
3. [Phase 1 : Configuration et Durcissement du Backend Django](#3-phase-1--configuration-et-durcissement-du-backend-django)
   - [3.1 Variables d'environnement (.env.production)](#31-variables-denvironnement-envproduction)
   - [3.2 Gestion des Fichiers Statiques (WhiteNoise)](#32-gestion-des-fichiers-statiques-whitenoise)
   - [3.3 Stockage Persistant des Médias (Cloudinary / S3 / Volume)](#33-stockage-persistant-des-médias-cloudinary--s3--volume)
   - [3.4 Sécurité HTTPS, CORS & Throttling](#34-sécurité-https-cors--throttling)
4. [Phase 2 : Déploiement du Serveur Backend](#4-phase-2--déploiement-du-serveur-backend)
   - [Option A : Déploiement PaaS Managé (Render.com / Railway)](#option-a--déploiement-paas-managé-rendercom--railway)
   - [Option B : Déploiement sur Serveur VPS Dédié (Ubuntu 22.04 / 24.04 avec Docker & Nginx)](#option-b--déploiement-sur-serveur-vps-dédié-ubuntu-2204--2404-avec-docker--nginx)
5. [Phase 3 : Configuration de la Passerelle de Paiement Chariow](#5-phase-3--configuration-de-la-passerelle-de-paiement-chariow)
   - [5.1 Création des Produits Chariow](#51-création-des-produits-chariow)
   - [5.2 Configuration du Webhook en Production](#52-configuration-du-webhook-en-production)
   - [5.3 Test Réel de Bout en Bout](#53-test-réel-de-bout-en-bout)
6. [Phase 4 : Compilation, Signature & Déploiement Mobile](#6-phase-4--compilation-signature--déploiement-mobile)
   - [4.1 Configuration de l'URL de Production](#41-configuration-de-lurl-de-production)
   - [4.2 Vérification du fichier buildozer.spec](#42-vérification-du-fichier-buildozerspec)
   - [4.3 Génération de la Clé de Signature (Keystore)](#43-génération-de-la-clé-de-signature-keystore)
   - [4.4 Compilation de l'Android App Bundle (.aab) & de l'APK](#44-compilation-de-landroid-app-bundle-aab--de-lapk)
   - [4.5 Publication sur Google Play Store](#45-publication-sur-google-play-store)
   - [4.6 Distribution Directe APK (Canal WhatsApp / Site Web)](#46-distribution-directe-apk-canal-whatsapp--site-web)
7. [Phase 5 : Automatisation CI/CD, Monitoring & Sauvegardes](#7-phase-5--automatisation-cicd-monitoring--sauvegardes)
   - [5.1 Sauvegarde Automatisée PostgreSQL (pg_dump)](#51-sauvegarde-automatisée-postgresql-pg_dump)
   - [5.2 Surveillance des Erreurs avec Sentry](#52-surveillance-des-erreurs-avec-sentry)
   - [5.3 Monitoring Uptime & Health Check](#53-monitoring-uptime--health-check)
8. [Checklist Finale Avant Lancement (Go / No-Go)](#8-checklist-finale-avant-lancement-go--no-go)

---

## 1. Architecture Globale de Production

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                       Clients Mobiles (Android)                         │
│               Application Kivy (Mode En Ligne / Hors-Ligne)             │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │  HTTPS (TLS 1.3)
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       Point d'Entrée / Nginx Proxy                      │
│                  - Terminaison SSL Let's Encrypt                        │
│                  - Reverse-Proxy vers port 8000                         │
│                  - Compression Gzip / Rate Limit HTTP                   │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    API Django REST (Conteneur Docker)                   │
│             Gunicorn WSGI (3 workers) + WhiteNoise (Statics)            │
│                     Django 5.0 / Python 3.11-slim                       │
└───────────────────────┬─────────────────────────┬───────────────────────┘
                        │                         │
     SQL (Port 5432)    ▼                         ▼   Téléversements HTTP
┌───────────────────────────────┐     ┌───────────────────────────────────┐
│    PostgreSQL 15/16 Managé    │     │      Stockage Médias Objets       │
│  - Données utilisateurs & JWT │     │   Cloudinary / AWS S3 / MinIO     │
│  - Chapitres & Articles Blog  │     │   - Photos des légumes & outils   │
│  - Abonnements & Paiements    │     │   - Images des maladies/insectes  │
└───────────────────────────────┘     └───────────────────────────────────┘
                ▲
                │ Événement Webhook : successful.sale (HMAC-SHA256)
┌───────────────┴───────────────┐
│    Chariow Payment Gateway    │
│   Orange Money / Wave / MTN   │
└───────────────────────────────┘
```

---

## 2. Prérequis Généraux

Avant de débuter, munissez-vous des éléments suivants :
- Un nom de domaine configuré (ex. `api.guidedupotager.com` ou `potager.mondomaine.org`) avec accès DNS (enregistrement type `A` ou `CNAME`).
- Un serveur hôte :
  - **Option PaaS** : compte sur [Render.com](https://render.com) ou [Railway.app](https://railway.app).
  - **Option VPS** : serveur sous Ubuntu 22.04 LTS ou 24.04 LTS (minimum 2 vCPU, 2 Go de RAM, 20 Go SSD).
- Un compte marchand **Chariow** validé avec accès au tableau de bord de production.
- Un compte développeur **Google Play Console** (si publication sur le Play Store).
- Un environnement Linux pour Buildozer (machine native, WSL2 sous Windows, ou runner CI).

---

## 3. Phase 1 : Configuration et Durcissement du Backend Django

### 3.1 Variables d'environnement (`.env.production`)

Créez le fichier de configuration sécurisé sur votre environnement de production (ne jamais le versionner sur Git) :

```ini
# ==============================================================================
# SÉCURITÉ DJANGO CORE
# ==============================================================================
DEBUG=False
SECRET_KEY=w^q8%9!z_v$2026_super_cle_secrete_aleatoire_a_generer_au_hasard_min_50_chars
DJANGO_SETTINGS_MODULE=config.settings.production
ALLOWED_HOSTS=api.guidedupotager.com,guidedupotager.onrender.com,127.0.0.1,localhost

# ==============================================================================
# BASE DE DONNÉES POSTGRESQL
# ==============================================================================
# Format standard URI
DATABASE_URL=postgres://potager_prod_user:MotDePasseUltraSecurise123!@db_host:5432/potager_prod_db

# ==============================================================================
# SÉCURITÉ HTTPS & SESSIONS
# ==============================================================================
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=False  # Géré par Nginx ou Cloudflare en amont
CORS_ALLOWED_ORIGINS=https://guidedupotager.com,https://api.guidedupotager.com

# ==============================================================================
# PASSERELLE DE PAIEMENT CHARIOW (LIVE)
# ==============================================================================
CHARIOW_API_KEY=chariow_live_sk_xxxxxxxxxxxxxxxxxxxxxxxx
CHARIOW_WEBHOOK_SECRET=chariow_whsec_xxxxxxxxxxxxxxxxxxxxxxxx
CHARIOW_BASE_URL=https://api.chariow.com/v1
CHARIOW_PRODUCT_MONTHLY_ID=prd_monthly_live_id
CHARIOW_PRODUCT_SEASONAL_ID=prd_seasonal_live_id
CHARIOW_PRODUCT_YEARLY_ID=prd_yearly_live_id

# ==============================================================================
# ENVOI D'EMAILS TRANSAC (RÉINITIALISATION DE MOT DE PASSE)
# ==============================================================================
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.votre_cle_api_sendgrid
DEFAULT_FROM_EMAIL=Guide du Potager <support@guidedupotager.com>

# ==============================================================================
# STOCKAGE MÉDIAS (OPTIONNEL SI UTILISATION CLOUDINARY)
# ==============================================================================
CLOUDINARY_CLOUD_NAME=votre_cloud_name
CLOUDINARY_API_KEY=votre_cle_cloudinary
CLOUDINARY_API_SECRET=votre_secret_cloudinary
```

> **Génération d'une SECRET_KEY robuste en ligne de commande :**
> ```bash
> python -c 'import secrets; print(secrets.token_urlsafe(50))'
> ```

---

### 3.2 Gestion des Fichiers Statiques (WhiteNoise)

Le fichier `backend/config/settings/production.py` injecte automatiquement le middleware WhiteNoise. Pour générer les fichiers statiques de l'administration et de Swagger lors du déploiement :

```bash
python manage.py collectstatic --noinput
```

Les fichiers sont compilés dans `backend/staticfiles/` avec empreinte de hachage (`CompressedManifestStaticFilesStorage`) pour une mise en cache navigateur optimale.

---

### 3.3 Stockage Persistant des Médias (Cloudinary / S3 / Volume)

Les images ajoutées via l'administration (photos de légumes, schémas de chapitres, illustrations de maladies) doivent persister au-delà des redémarrages de conteneurs.

#### Solution Recommandée : Cloudinary (Tier gratuit généreux)
1. Ajoutez la dépendance au fichier `backend/requirements.txt` :
   ```text
   django-cloudinary-storage>=0.3.0
   ```
2. Ajoutez dans `backend/config/settings/production.py` :
   ```python
   if os.environ.get('CLOUDINARY_CLOUD_NAME'):
       INSTALLED_APPS = ['cloudinary_storage', 'cloudinary'] + INSTALLED_APPS
       CLOUDINARY_STORAGE = {
           'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
           'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
           'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
       }
       DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
   ```

#### Alternative : Volume Docker Persistant
Si vous déployez sur VPS avec Docker Compose, le dossier `/app/media` est mappé sur un volume Docker persistant (`media_data:/app/media`), servi directement par Nginx.

---

### 3.4 Sécurité HTTPS, CORS & Throttling

Le projet intègre déjà dans DRF un système de limitation de requêtes (`DEFAULT_THROTTLE_RATES`) :
- Anonymes : 120 requêtes / minute.
- Utilisateurs connectés : 300 requêtes / minute.

Pour protéger les points sensibles (connexion `/api/accounts/login/`, webhook Chariow), les en-têtes de sécurité configurés dans `production.py` appliquent :
- `X-Frame-Options: DENY` (anti clickjacking).
- `X-Content-Type-Options: nosniff`.
- `SECURE_BROWSER_XSS_FILTER = True`.
- Cookies de session et CSRF restreints au protocole HTTPS (`SESSION_COOKIE_SECURE=True`).

---

## 4. Phase 2 : Déploiement du Serveur Backend

---

### Option A : Déploiement PaaS Managé (Render.com / Railway)

Cette option est la plus simple et rapide : elle ne requiert pas de gestion manuelle de serveur Linux ou de certificats SSL.

#### 1. Déployer la Base de Données PostgreSQL
1. Connectez-vous sur [Render.com](https://render.com).
2. Cliquez sur **New +** > **PostgreSQL**.
3. Définissez le nom : `potager-db-prod`.
4. Sélectionnez la région (ex. *Frankfurt* ou la plus proche de votre audience cible).
5. Copiez la chaîne de connexion **Internal Database URL** (ex. `postgres://user:pass@dpg-xxxx-a:5432/potager_db`).

#### 2. Déployer le Web Service Backend
1. Cliquez sur **New +** > **Web Service**.
2. Connectez le dépôt GitHub du projet.
3. Paramètres de base :
   - **Name** : `potager-backend-api`
   - **Region** : Même région que votre base PostgreSQL.
   - **Branch** : `main`
   - **Root Directory** : `backend`
   - **Runtime** : `Docker` (Render détecte automatiquement `backend/Dockerfile`)
4. Dans la section **Environment Variables**, renseignez toutes les variables de la section 3.1 :
   - `DATABASE_URL` = *(collez l'URL de la base Render)*
   - `SECRET_KEY` = *(votre clé secrète)*
   - `DJANGO_SETTINGS_MODULE` = `config.settings.production`
   - `ALLOWED_HOSTS` = `potager-backend-api.onrender.com,api.guidedupotager.com`
   - Variables Chariow (`CHARIOW_API_KEY`, etc.)
5. Configurez la commande de pré-déploiement (**Release Command**) :
   ```bash
   python manage.py migrate --noinput && python manage.py collectstatic --noinput
   ```

#### 3. Initialisation des Données
Une fois le service en ligne (*Deploy succeeded*) :
1. Allez dans l'onglet **Shell** du service Render.
2. Créez votre compte administrateur :
   ```bash
   python manage.py createsuperuser
   ```
3. Chargez le catalogue initial (chapitres, fiches légumes, insectes, articles de blog) :
   ```bash
   python manage.py seed_data
   ```
4. Testez l'accès à l'API :
   - `https://potager-backend-api.onrender.com/api/content/parts/`
   - `https://potager-backend-api.onrender.com/api/docs/` (Swagger UI)

---

### Option B : Déploiement sur Serveur VPS Dédié (Ubuntu 22.04 / 24.04 avec Docker & Nginx)

Pour un contrôle total sur les performances, les coûts et les données.

#### 1. Préparation et Sécurisation du VPS
Connectez-vous en SSH à votre serveur :
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl git ufw fail2ban
```

Configurez le pare-feu UFW :
```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

Installez Docker et Docker Compose v2 :
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker
```

#### 2. Cloner le Projet & Configurer l'Environnement
```bash
cd /opt
sudo git clone https://github.com/fredikoko/Guide-du-Potager.git potager
cd /opt/potager
sudo chown -R $USER:$USER /opt/potager
cp .env.example .env  # Remplissez le fichier avec les valeurs de production
```

#### 3. Créer le Fichier `docker-compose.prod.yml`
Créez `/opt/potager/docker-compose.prod.yml` :

```yaml
version: '3.8'

services:
  db:
    image: postgres:16-alpine
    container_name: potager_prod_db
    restart: always
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-guide_potager}
      POSTGRES_USER: ${POSTGRES_USER:-potager_user}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_prod_data:/var/lib/postgresql/data
    networks:
      - potager_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-potager_user}"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: potager_prod_backend
    restart: always
    command: >
      sh -c "python manage.py collectstatic --noinput &&
             python manage.py migrate --noinput &&
             gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120 --access-logfile - --error-logfile -"
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - media_prod_data:/app/media
      - static_prod_data:/app/staticfiles
    ports:
      - "127.0.0.1:8000:8000"
    networks:
      - potager_network

volumes:
  postgres_prod_data:
  media_prod_data:
  static_prod_data:

networks:
  potager_network:
    driver: bridge
```

#### 4. Démarrage des Conteneurs
```bash
docker compose -f docker-compose.prod.yml up -d --build
```

Vérifiez le statut :
```bash
docker compose -f docker-compose.prod.yml ps
docker logs -f potager_prod_backend
```

Exécutez le seed et créez le superutilisateur :
```bash
docker exec -it potager_prod_backend python manage.py seed_data
docker exec -it potager_prod_backend python manage.py createsuperuser
```

#### 5. Configuration de Nginx & Certificat SSL Let's Encrypt
Installez Nginx et Certbot :
```bash
sudo apt install -y nginx certbot python3-certbot-nginx
```

Créez le bloc serveur `/etc/nginx/sites-available/potager.conf` :

```nginx
server {
    server_name api.guidedupotager.com;

    client_max_body_size 25M;

    # Compression Gzip
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 90;
    }

    # Médias servis directement si volume local partagé
    location /media/ {
        alias /var/lib/docker/volumes/potager_media_prod_data/_data/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }
}
```

Activez le site et générez le certificat SSL :
```bash
sudo ln -s /etc/nginx/sites-available/potager.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Obtention du certificat HTTPS automatique
sudo certbot --nginx -d api.guidedupotager.com --non-interactive --agree-tos --email admin@guidedupotager.com
```

---

## 5. Phase 3 : Configuration de la Passerelle de Paiement Chariow

Le module d'abonnement (`apps/subscriptions`) est préconfiguré pour la passerelle Chariow (Mobile Money Afrique de l'Ouest : Wave, Orange Money, MTN MoMo, Moov et Carte bancaire).

### 5.1 Création des Produits Chariow
Dans votre console marchande Chariow :
1. Créez 3 produits correspondant aux formules définies dans l'application :
   - **Pass 1 Mois** : Prix `2 500 XOF` (identifiant produit ex. `prd_monthly_live_xxx`)
   - **Pass Saison (3 Mois)** : Prix `5 000 XOF` (identifiant produit ex. `prd_seasonal_live_xxx`)
   - **Pass Annuel** : Prix `15 000 XOF` (identifiant produit ex. `prd_yearly_live_xxx`)
2. Renseignez ces identifiants dans vos variables d'environnement (`CHARIOW_PRODUCT_MONTHLY_ID`, etc.) ou directement dans l'interface Django Admin (`/admin/subscriptions/subscriptionplan/`).

### 5.2 Configuration du Webhook en Production
1. Dans le tableau de bord Chariow, accédez à **Développeurs > Webhooks**.
2. Créez un nouvel endpoint de webhook :
   - **URL de destination** :
     ```text
     https://api.guidedupotager.com/api/subscriptions/chariow/webhook/
     ```
   - **Événement écouté** : `successful.sale`
3. Chariow vous fournit une **Clé secrète de signature de webhook** (commençant par `whsec_`).
4. Définissez cette clé dans votre variable d'environnement :
   ```ini
   CHARIOW_WEBHOOK_SECRET=whsec_votre_cle_secrete_chariow
   ```

### 5.3 Test Réel de Bout en Bout
1. Créez un compte utilisateur réel sur l'application mobile ou via Swagger.
2. Initiez un paiement réel (ex. 2 500 XOF via Wave ou Orange Money).
3. À la validation du paiement, Chariow envoie la requête signée avec le header `x-chariow-signature`.
4. Inspectez les logs backend pour confirmer la réception :
   ```text
   INFO: Webhook Chariow validé (delivery_id: deliv_xxxx) pour l'utilisateur user@example.com
   INFO: Abonnement 'seasonal' activé jusqu'au 2026-12-20
   ```
5. Confirmez que le profil de l'utilisateur a basculé en `is_premium = True` et `subscription_active = True`.

---

## 6. Phase 4 : Compilation, Signature & Déploiement Mobile

---

### 4.1 Configuration de l'URL de Production

Modifiez le fichier `mobile/app/utils/config.py` ou passez l'URL de production :

```python
import os

class Config:
    API_BASE_URL = os.environ.get('API_BASE_URL', 'https://api.guidedupotager.com/api')
    TIMEOUT = 12.0
```

> **Attention** : Ne laissez jamais `http://127.0.0.1:8000` ou une IP locale en version finale, car un téléphone physique ne pourrait pas joindre l'API. L'URL doit obligatoirement être en `https://`.

---

### 4.2 Vérification du fichier `buildozer.spec`

Assurez-vous que les paramètres clés sont correctement définis dans `mobile/buildozer.spec` :

```ini
[app]
title = Guide du Potager Tropical
package.name = guidedupotagertropical
package.domain = org.guidedupotagertropical
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0.0

requirements = python3,kivy==2.3.0,httpx,requests,urllib3,certifi,openssl,pillow

orientation = portrait
fullscreen = 0
android.permissions = INTERNET,ACCESS_NETWORK_STATE

# Cibles Google Play 2024+ (Android 14)
android.api = 34
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a

# Désactiver le mode debug
android.release_artifact = aab
```

---

### 4.3 Génération de la Clé de Signature (Keystore)

Pour publier sur Google Play ou distribuer un APK sécurisé, vous devez générer une clé cryptographique privée :

```bash
cd mobile

keytool -genkey -v -keystore potager-release.keystore \
        -alias potager_key \
        -keyalg RSA -keysize 2048 -validity 10000 \
        -storepass MotDePasseKeystore123! \
        -keypass MotDePasseKeystore123! \
        -dname "CN=Guide du Potager, OU=Production, O=Potager, L=Dakar, ST=DK, C=SN"
```

> ⚠️ **Sauvegardez ce fichier `potager-release.keystore` dans un coffre-fort sécurisé.** Si vous le perdez, vous ne pourrez plus jamais mettre à jour votre application sur le Google Play Store.

---

### 4.4 Compilation de l'Android App Bundle (.aab) & de l'APK

#### A. Compilation sous Linux / WSL2
Exécutez dans le dossier `mobile` :

```bash
cd mobile

# Nettoyer les caches antérieurs
buildozer android clean

# Compiler le paquet de publication (AAB pour le Play Store)
buildozer android release
```

Le fichier non signé sera généré dans `mobile/bin/` :
`potager-1.0.0-arm64-v8a_armeabi-v7a-release-unsigned.aab`

#### B. Signature du Bundle
```bash
jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 \
          -keystore potager-release.keystore \
          -storepass MotDePasseKeystore123! \
          bin/potager-1.0.0-arm64-v8a_armeabi-v7a-release-unsigned.aab \
          potager_key
```

Renommez le fichier final :
```bash
mv bin/potager-1.0.0-arm64-v8a_armeabi-v7a-release-unsigned.aab bin/GuideDuPotager-v1.0.0.aab
```

#### C. Génération de l'APK autonome (pour test direct ou téléchargement web)
Pour générer un fichier `.apk` directement installable :
```bash
# Dans buildozer.spec, ajustez temporairement :
# android.release_artifact = apk
buildozer android release

# Signature de l'APK :
zipalign -v 4 bin/potager-1.0.0-arm64-v8a_armeabi-v7a-release-unsigned.apk bin/GuideDuPotager-v1.0.0-aligned.apk

apksigner sign --ks potager-release.keystore \
               --ks-key-alias potager_key \
               --ks-pass pass:MotDePasseKeystore123! \
               --out bin/GuideDuPotager-v1.0.0.apk \
               bin/GuideDuPotager-v1.0.0-aligned.apk
```

---

### 4.5 Publication sur Google Play Store

1. Connectez-vous sur la [Google Play Console](https://play.google.com/console).
2. Cliquez sur **Créer une application** :
   - Nom : *Guide du Potager Tropical*
   - Langue par défaut : *Français*
   - Type : *Application* / *Gratuite* (les abonnements sont gérés via Chariow)
3. Remplissez les exigences obligatoires :
   - **Politique de confidentialité** (ex. `https://guidedupotager.com/privacy.html`).
   - **Accès aux applications** : Créez un compte de test pour l'équipe de modération Google (`google-review@potager.fr` / `MotDePasseTest123`).
   - **Classification du contenu** (Questionnaire PEGI / IARC : classification standard tous publics).
   - **Fiche du magasin** :
     - Icône HD (512x512 px)
     - Graphisme de fonctionnalité (1024x500 px)
     - Captures d'écran de l'application (téléphone 16:9 et portrait).
4. Déployez le bundle `.aab` dans le canal **Production** ou **Test Ouvert**.
5. Envoyez pour examen (délai habituel de validation Google : 24 à 72 heures).

---

### 4.6 Distribution Directe APK (Canal WhatsApp / Site Web)

Pour une adoption rapide en Afrique subsaharienne :
1. Hébergez le fichier `GuideDuPotager-v1.0.0.apk` sur votre serveur web ou un CDN (`https://guidedupotager.com/download/app.apk`).
2. Indiquez aux utilisateurs d'autoriser l'installation depuis des sources inconnues sur Android (*Paramètres > Sécurité > Sources inconnues*).
3. L'application vérifie sa connexion au démarrage et bascule en mode cache SQLite si l'utilisateur est hors-ligne.

---

## 7. Phase 5 : Automatisation CI/CD, Monitoring & Sauvegardes

---

### 5.1 Sauvegarde Automatisée PostgreSQL (`pg_dump`)

Sur VPS, configurez une tâche cron pour sauvegarder la base de données toutes les nuits à 02h00 :

```bash
sudo mkdir -p /var/backups/potager
sudo nano /usr/local/bin/backup_potager_db.sh
```

Contenu du script :
```bash
#!/bin/bash
BACKUP_DIR="/var/backups/potager"
DATE=$(date +"%Y%m%d_%H%M%S")
FILENAME="$BACKUP_DIR/potager_backup_$DATE.sql.gz"

# Exécution du dump dans le conteneur
docker exec potager_prod_db pg_dump -U potager_user guide_potager | gzip > "$FILENAME"

# Conserver uniquement les 14 derniers jours
find "$BACKUP_DIR" -type f -name "*.sql.gz" -mtime +14 -delete

echo "Sauvegarde terminée : $FILENAME"
```

Rendez le script exécutable et planifiez-le :
```bash
sudo chmod +x /usr/local/bin/backup_potager_db.sh
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/backup_potager_db.sh") | crontab -
```

---

### 5.2 Surveillance des Erreurs avec Sentry

Pour recevoir une alerte instantanée si une requête API ou un webhook Chariow échoue :

1. Installez le SDK Sentry :
   ```bash
   pip install sentry-sdk
   ```
2. Ajoutez dans `backend/config/settings/production.py` :
   ```python
   import sentry_sdk
   from sentry_sdk.integrations.django import DjangoIntegration

   SENTRY_DSN = os.environ.get('SENTRY_DSN')
   if SENTRY_DSN:
       sentry_sdk.init(
           dsn=SENTRY_DSN,
           integrations=[DjangoIntegration()],
           traces_sample_rate=0.2,
           send_default_pii=False,
       )
   ```

---

### 5.3 Monitoring Uptime & Health Check

1. L'API expose un endpoint de test immédiat : `GET https://api.guidedupotager.com/api/content/parts/` qui renvoie HTTP 200.
2. Configurez un service gratuit de monitoring comme [Uptime Kuma](https://github.com/louislam/uptime-kuma), [BetterStack](https://betterstack.com) ou [UptimeRobot](https://uptimerobot.com) avec un contrôle toutes les 60 secondes.
3. Définissez une alerte vers votre canal Discord, Telegram ou par SMS en cas de panne.

---

## 8. Checklist Finale Avant Lancement (Go / No-Go)

Cochez chaque case avant d'ouvrir l'application au public :

### Backend & Infrastructure
- [ ] `DEBUG = False` vérifié sur l'environnement de production.
- [ ] `SECRET_KEY` unique, cryptographique et non présente sur Git.
- [ ] Base de données PostgreSQL opérationnelle avec sauvegardes planifiées.
- [ ] Migrations Django appliquées sans erreur (`python manage.py migrate`).
- [ ] Compte super-administrateur créé et mot de passe complexe défini.
- [ ] Fichiers statiques collectés (`collectstatic`) et accessibles via `/static/admin/`.
- [ ] Certificat SSL actif (A+ sur SSL Labs, renouvellement automatique certbot).
- [ ] En-têtes HTTPS et cookies sécurisés activés (`SESSION_COOKIE_SECURE = True`).

### Paiements & Chariow
- [ ] Clés Chariow réelles configurées (`CHARIOW_API_KEY`, `CHARIOW_WEBHOOK_SECRET`).
- [ ] Produits Chariow configurés (1 Mois, Saison 3 Mois, Annuel) avec prix conformes.
- [ ] URL de webhook HTTPS active et testée avec succès sur événement réel.
- [ ] Test d'un flux d'achat complet avec un numéro Wave/Orange Money de test.

### Application Mobile
- [ ] `API_BASE_URL` configurée avec le domaine de production en `https://`.
- [ ] Test de toutes les rubriques sur un appareil Android réel :
  - Inscription / Connexion JWT.
  - Consultation hors-ligne (mise en cache validée).
  - Simulateur du calendrier de semis.
  - Fiches légumes, maladies et outils.
  - Déclenchement de la modale d'abonnement et redirection paiement.
- [ ] Paquet `.aab` compilé, signé avec le Keystore de production et aligné.
- [ ] Fiche Google Play complétée (icônes, captures d'écran, politique de confidentialité).
