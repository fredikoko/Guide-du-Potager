# 🌿 Guide Complet de Mise en Production
## Application « Guide du Potager Tropical » (Backend Django REST & Plateforme Web, Client Mobile Kivy)

Ce document détaille toutes les étapes, configurations, scripts et commandes nécessaires pour déployer l'infrastructure backend en haute disponibilité, sécuriser les transactions de paiement Mobile Money, garantir la délivrabilité des emails transactionnels (codes OTP à 6 chiffres) et compiler/distribuer l'application mobile Android (Google Play Store & téléchargement direct APK).

---

## 📑 Table des Matières

1. [Architecture Globale de Production](#1-architecture-globale-de-production)
2. [Prérequis Généraux](#2-prérequis-généraux)
3. [Phase 1 : Configuration et Durcissement du Backend Django](#3-phase-1--configuration-et-durcissement-du-backend-django)
   - [3.1 Variables d'environnement (.env.production)](#31-variables-denvironnement-envproduction)
   - [3.2 Système d'E-mails & Codes de Vérification OTP à 6 Chiffres (Critique)](#32-système-d-e-mails--codes-de-vérification-otp-à-6-chiffres-critique)
   - [3.3 Gestion des Fichiers Statiques (WhiteNoise)](#33-gestion-des-fichiers-statiques-whitenoise)
   - [3.4 Stockage Persistant des Médias (Photos, Légumes, Blog)](#34-stockage-persistant-des-médias-photos-légumes-blog)
   - [3.5 Sécurité HTTPS, Headers & Throttling Anti-Abus](#35-sécurité-https-headers--throttling-anti-abus)
4. [Phase 2 : Déploiement du Serveur Backend](#4-phase-2--déploiement-du-serveur-backend)
   - [Option A : Déploiement PaaS Managé (Render.com / Railway)](#option-a--déploiement-paas-managé-rendercom--railway)
   - [Option B : Déploiement sur Serveur VPS Dédié (Ubuntu 22.04 / 24.04 avec Docker & Nginx)](#option-b--déploiement-sur-serveur-vps-dédié-ubuntu-2204--2404-avec-docker--nginx)
   - [Script de Redéploiement Continu sans Interruption (deploy.sh)](#script-de-redéploiement-continu-sans-interruption-deploysh)
5. [Phase 3 : Passerelle Chariow & Abonnements Dynamiques](#5-phase-3--passerelle-chariow--abonnements-dynamiques)
   - [5.1 Gestion Dynamique des Formules (SubscriptionPlan)](#51-gestion-dynamique-des-formules-subscriptionplan)
   - [5.2 Configuration des Produits Chariow](#52-configuration-des-produits-chariow)
   - [5.3 Configuration Sécurisée du Webhook HMAC-SHA256](#53-configuration-sécurisée-du-webhook-hmac-sha256)
   - [5.4 Test Réel de Bout en Bout (Wave / Orange Money)](#54-test-réel-de-bout-en-bout-wave--orange-money)
6. [Phase 4 : Gestion du Module Blog & Contenus Éducatifs](#6-phase-4--gestion-du-module-blog--contenus-éducatifs)
   - [6.1 Architecture du Blog (Web & Mobile)](#61-architecture-du-blog-web--mobile)
   - [6.2 Modération des Commentaires & Articles Premium](#62-modération-des-commentaires--articles-premium)
   - [6.3 Initialisation Automatique du Catalogue (seed_data)](#63-initialisation-automatique-du-catalogue-seed_data)
7. [Phase 5 : Compilation, Signature & Déploiement Mobile](#7-phase-5--compilation-signature--déploiement-mobile)
   - [7.1 Configuration de l'URL d'API de Production](#71-configuration-de-lurl-dapi-de-production)
   - [7.2 Vérification du fichier buildozer.spec (Android 14 / API 34)](#72-vérification-du-fichier-buildozerspec-android-14--api-34)
   - [7.3 Génération du Keystore Privé de Production](#73-génération-du-keystore-privé-de-production)
   - [7.4 Compilation de l'App Bundle (.aab) & de l'APK](#74-compilation-de-lapp-bundle-aab--de-lapk)
   - [7.5 Publication sur Google Play Console](#75-publication-sur-google-play-console)
   - [7.6 Distribution Directe APK (WhatsApp / Site Web)](#76-distribution-directe-apk-whatsapp--site-web)
8. [Phase 6 : Monitoring, Sauvegardes & Maintenance](#8-phase-6--monitoring-sauvegardes--maintenance)
   - [8.1 Sauvegardes Quotidiennes PostgreSQL (pg_dump)](#81-sauvegardes-quotidiennes-postgresql-pg_dump)
   - [8.2 Procédure de Restauration d'Urgence](#82-procédure-de-restauration-durgence)
   - [8.3 Surveillance Sentry & Health Check Uptime](#83-surveillance-sentry--health-check-uptime)
9. [Guide de Dépannage Fréquent (Troubleshooting)](#9-guide-de-dépannage-fréquent-troubleshooting)
10. [Checklist Finale Avant Lancement (Go / No-Go)](#10-checklist-finale-avant-lancement-go--no-go)

---

## 1. Architecture Globale de Production

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                    Clients Mobiles Android (Kivy)                            │
│           - Cache local SQLite pour consultation 100% hors-ligne             │
│           - Synchronisation JWT & Écran d'abonnement responsive              │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       │ HTTPS (TLS 1.3)
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                   Reverse-Proxy Nginx / Ingress PaaS                         │
│           - Terminaison SSL Let's Encrypt (A+ SSL Labs)                      │
│           - Compression Gzip / Brotli & Rate Limiting HTTP                   │
│           - Routage Web & API vers le port 8000                              │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       │ Proxy HTTP
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                     Serveur Backend Django 5.1 (WSGI)                        │
│               Gunicorn (3-4 workers) + WhiteNoise (Fichiers Statiques)       │
│  ├── /api/...         : API RESTful (Auth JWT, Calendrier, Fiches, Blog)     │
│  ├── /                : Portail Web vitrine & Landing page responsive        │
│  ├── /blog/...        : Articles agro-écologiques et actualités maraîchères  │
│  ├── /subscribe/...   : Présentation des formules & checkout Chariow         │
│  └── /admin/...       : Back-office d'administration & modération            │
└───────────────────────┬──────────────────────────────┬───────────────────────┘
                        │                              │
     Port 5432 (SQL)    ▼                              ▼  Médias & Uploads
┌────────────────────────────────────┐    ┌────────────────────────────────────┐
│      PostgreSQL 16 Managé          │    │      Stockage Médias Objets        │
│  - Utilisateurs & Profils agro     │    │   Volume Persistant / Cloudinary   │
│  - Codes OTP à 6 chiffres          │    │   - Couvertures articles blog      │
│  - Fiches légumes & calendrier     │    │   - Photos maladies & ravageurs    │
│  - Abonnements & Plans dynamiques  │    │   - Avatars des profils jardiniers │
└────────────────────────────────────┘    └────────────────────────────────────┘
                  ▲                                      ▲
                  │ Webhook (HMAC-SHA256)                │ SMTP TLS (Port 587)
┌─────────────────┴──────────────────┐    ┌──────────────┴─────────────────────┐
│      Passerelle Chariow Live       │    │   Service d'Emails Transactionnels │
│  Wave / Orange Money / MTN / Carte │    │   Brevo / SendGrid / Resend / SES  │
└────────────────────────────────────┘    └────────────────────────────────────┘
```

---

## 2. Prérequis Généraux

Avant de lancer le déploiement, rassemblez les éléments suivants :

| Composant | Description | Recommandation |
|---|---|---|
| **Nom de domaine** | Domaine DNS pointant vers le serveur | ex. `guidedupotager.com` et `api.guidedupotager.com` |
| **Serveur d'hébergement** | PaaS géré ou VPS Linux | VPS Ubuntu 22.04/24.04 (2 vCPU, 2-4 Go RAM) ou Render.com |
| **Base de données** | Instance PostgreSQL 15 ou 16 | Render Managed PostgreSQL ou conteneur Docker avec volume SSD |
| **Fournisseur SMTP** | Envoi d'emails transactionnels (OTP) | Brevo (300/j gratuits), SendGrid, Resend ou Amazon SES |
| **Compte Chariow** | Passerelle de paiement Mobile Money | Compte marchand validé en mode **Live** |
| **Compte Google Play** | Console développeur Google | Accès administrateur pour soumission du `.aab` |
| **Machine de build Android** | Environnement Linux/WSL2 | Pour compiler avec Python 3, Buildozer et Android NDK/SDK |

---

## 3. Phase 1 : Configuration et Durcissement du Backend Django

### 3.1 Variables d'environnement (`.env.production`)

Créez le fichier de configuration de production (droits `chmod 600 .env` sur le serveur, ne jamais le commiter sur Git) :

```ini
# ==============================================================================
# 1. SÉCURITÉ DJANGO CORE
# ==============================================================================
DEBUG=False
SECRET_KEY=cle_ultra_longue_et_aleatoire_de_minimum_50_caracteres_generee_aleatoirement!
DJANGO_SETTINGS_MODULE=config.settings.production
ALLOWED_HOSTS=guidedupotager.com,api.guidedupotager.com,guidedupotager.onrender.com,127.0.0.1,localhost

# ==============================================================================
# 2. BASE DE DONNÉES POSTGRESQL (PRODUCTION)
# ==============================================================================
# Format : postgres://UTILISATEUR:MOT_DE_PASSE@HOTE:PORT/NOM_BASE
DATABASE_URL=postgres://potager_prod_user:MotDePasseUltraSecurise2026!@127.0.0.1:5432/potager_prod_db

# ==============================================================================
# 3. SERVICE SMTP & CODES OTP À 6 CHIFFRES (INDISPENSABLE)
# ==============================================================================
# En production, ce paramètre DOIT impérativement être 'smtp.EmailBackend'
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp-relay.brevo.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre_identifiant_smtp
EMAIL_HOST_PASSWORD=votre_cle_smtp_ou_mot_de_passe
DEFAULT_FROM_EMAIL=Guide du Potager Tropical <support@guidedupotager.com>

# ==============================================================================
# 4. SÉCURITÉ HTTPS & SESSIONS
# ==============================================================================
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=False  # Géré en amont par Nginx ou Cloudflare
CORS_ALLOWED_ORIGINS=https://guidedupotager.com,https://api.guidedupotager.com

# ==============================================================================
# 5. PASSERELLE DE PAIEMENT CHARIOW (LIVE)
# ==============================================================================
CHARIOW_API_KEY=chariow_live_sk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
CHARIOW_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
CHARIOW_BASE_URL=https://api.chariow.com/v1

# Identifiants des produits Live créés sur le dashboard Chariow
CHARIOW_PRODUCT_MONTHLY_ID=prd_monthly_live_id
CHARIOW_PRODUCT_SEASONAL_ID=prd_seasonal_live_id
CHARIOW_PRODUCT_YEARLY_ID=prd_yearly_live_id

# ==============================================================================
# 6. STOCKAGE MÉDIAS (OPTIONNEL SI UTILISATION CLOUDINARY)
# ==============================================================================
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=

# ==============================================================================
# 7. MONITORING D'ERREURS (SENTRY)
# ==============================================================================
SENTRY_DSN=https://xxxxxxxx@o000000.ingest.sentry.io/0000000
```

> **Génération d'une `SECRET_KEY` cryptographique :**
> ```bash
> python -c 'import secrets; print(secrets.token_urlsafe(60))'
> ```

---

### 3.2 Système d'E-mails & Codes de Vérification OTP à 6 Chiffres (Critique)

L'application intègre un modèle de sécurité `EmailVerificationCode` pour :
1. La validation de l'adresse e-mail lors de la création d'un compte (`purpose='registration'`).
2. La modification sécurisée de l'adresse e-mail (`purpose='email_change'`).
3. La réinitialisation de mot de passe oublié (`purpose='password_reset'`).

> ⚠️ **ATTENTION VIVEMENT RECOMMANDÉE :**  
> Si les identifiants SMTP ne sont pas renseignés ou invalides en production, le backend ne pourra pas délivrer le code à 6 chiffres aux utilisateurs. L'inscription sera alors bloquée.

#### Vérification de la délivrabilité SMTP depuis le serveur :
Connectez-vous au serveur et lancez le shell Django pour tester l'envoi d'un e-mail réel :

```bash
# Dans le conteneur ou l'environnement virtuel :
python manage.py shell -c "
from django.core.mail import send_mail
res = send_mail(
    'Test Production Guide du Potager',
    'Votre code de vérification test est : 123456',
    None,
    ['votre-email-personnel@domaine.com'],
    fail_silently=False
)
print('Statut envoi (1 = succès) :', res)
"
```
Si la commande retourne `1`, votre relais SMTP fonctionne parfaitement.

---

### 3.3 Gestion des Fichiers Statiques (WhiteNoise)

En production (`config/settings/production.py`), **WhiteNoise** est configuré avec `CompressedManifestStaticFilesStorage`. Il assure :
- La compression Gzip/Brotli automatique des CSS, JS et images de l'administration et du site web.
- L'ajout d'un hash unique sur les noms de fichiers pour un cache navigateur infini sans risque de conserver une ancienne version.

Exécutez toujours lors de chaque déploiement :
```bash
python manage.py collectstatic --noinput
```

---

### 3.4 Stockage Persistant des Médias (Photos, Légumes, Blog)

L'application manipule plusieurs répertoires médias sous `/app/media/` :
- `blog/` et `blog/images/` : Couvertures et images d'illustration des articles de blog.
- `vegetables/` : Fiches illustrées des légumes et aromates.
- `insects/` et `diseases/` : Fiches de diagnostic phytosanitaire.
- `avatars/` : Photos de profil des utilisateurs.

#### Sur VPS Dédié (Docker) :
Assurez-vous que le volume Docker nommé `media_prod_data` est bien déclaré et possède les droits d'écriture :
```bash
# Vérifier l'emplacement du volume Docker sur l'hôte :
docker volume inspect potager_media_prod_data
```

#### Sur PaaS Éphémère (Render / Railway sans disque persistant) :
Utilisez le stockage d'objets Cloudinary ou AWS S3 en renseignant les clés `CLOUDINARY_*` pour éviter la perte des images au redémarrage des conteneurs.

---

### 3.5 Sécurité HTTPS, Headers & Throttling Anti-Abus

Le fichier `backend/config/settings/production.py` et la configuration REST Framework appliquent :
- `X-Frame-Options: DENY` (protection contre le clickjacking).
- `SECURE_CONTENT_TYPE_NOSNIFF = True` (protection contre le MIME sniffing).
- `SESSION_COOKIE_SECURE = True` et `CSRF_COOKIE_SECURE = True` (cookies strictement réservés au HTTPS).
- **Throttling anti-bruteforce REST Framework** :
  - Utilisateurs anonymes : limitation à **120 requêtes/minute**.
  - Utilisateurs connectés : limitation à **300 requêtes/minute**.
  - Protection renforcée sur `/api/accounts/login/` et la validation du code OTP (limite de 5 tentatives infructueuses avant invalidation du code).

---

## 4. Phase 2 : Déploiement du Serveur Backend

### Option A : Déploiement PaaS Managé (Render.com / Railway)

Cette option est recommandée si vous ne souhaitez pas administrer de serveur Linux.

1. **Créer la base de données PostgreSQL** :
   - Sur [Render.com](https://render.com), cliquez sur **New +** > **PostgreSQL**.
   - Nom : `potager-prod-db`, Plan : Starter ou Standard.
   - Notez l'**Internal Database URL**.

2. **Créer le Web Service** :
   - **New +** > **Web Service**, sélectionnez le dépôt GitHub `Guide-du-Potager`.
   - **Root Directory** : `backend`
   - **Runtime** : `Docker`
   - **Environment Variables** : Copiez toutes les variables de la section 3.1.
   - **Release Command** (exécutée automatiquement avant chaque mise en ligne) :
     ```bash
     python manage.py migrate --noinput && python manage.py collectstatic --noinput
     ```

3. **Initialisation des Données** :
   Depuis l'onglet **Shell** de Render :
   ```bash
   python manage.py createsuperuser
   python manage.py seed_data
   ```

---

### Option B : Déploiement sur Serveur VPS Dédié (Ubuntu 22.04 / 24.04 avec Docker & Nginx)

Pour une maîtrise complète des coûts et des performances.

#### 1. Préparation du VPS & Pare-feu
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl git ufw fail2ban certbot python3-certbot-nginx

# Configuration du pare-feu
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

#### 2. Installation de Docker & Docker Compose
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker
```

#### 3. Déploiement du Projet
```bash
cd /opt
sudo git clone https://github.com/fredikoko/Guide-du-Potager.git potager
cd /opt/potager
sudo chown -R $USER:$USER /opt/potager

# Création du fichier d'environnement
cp .env.production.example .env  # Éditez avec nano .env
```

#### 4. Fichier `docker-compose.prod.yml`
Vérifiez le contenu de `/opt/potager/docker-compose.prod.yml` :

```yaml
version: '3.8'

services:
  db:
    image: postgres:16-alpine
    container_name: potager_prod_db
    restart: always
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-potager_prod_db}
      POSTGRES_USER: ${POSTGRES_USER:-potager_prod_user}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_prod_data:/var/lib/postgresql/data
    networks:
      - potager_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-potager_prod_user} -d ${POSTGRES_DB:-potager_prod_db}"]
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

#### 5. Lancement & Initialisation
```bash
docker compose -f docker-compose.prod.yml up -d --build

# Initialisation du catalogue complet et du superutilisateur
docker exec -it potager_prod_backend python manage.py seed_data
docker exec -it potager_prod_backend python manage.py createsuperuser
```

#### 6. Configuration Nginx & Certificat SSL Let's Encrypt
Créez `/etc/nginx/sites-available/potager.conf` :

```nginx
server {
    listen 80;
    server_name guidedupotager.com api.guidedupotager.com;
    client_max_body_size 25M;

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

    # Fichiers médias servis avec cache
    location /media/ {
        alias /var/lib/docker/volumes/potager_media_prod_data/_data/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }
}
```

Activez le site et obtenez le certificat HTTPS :
```bash
sudo ln -s /etc/nginx/sites-available/potager.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
sudo certbot --nginx -d guidedupotager.com -d api.guidedupotager.com --non-interactive --agree-tos --email admin@guidedupotager.com
```

---

### Script de Redéploiement Continu sans Interruption (`deploy.sh`)

Créez le script `/opt/potager/deploy.sh` pour déployer facilement les futures versions :

```bash
#!/bin/bash
set -e

echo "🚀 [1/4] Récupération des dernières modifications Git..."
git pull origin main

echo "📦 [2/4] Reconstruction de l'image Docker du backend..."
docker compose -f docker-compose.prod.yml build backend

echo "🔄 [3/4] Application des migrations et relance des conteneurs..."
docker compose -f docker-compose.prod.yml up -d --no-deps backend

echo "🧹 [4/4] Nettoyage des anciennes images inutilisées..."
docker image prune -f

echo "✅ Déploiement en production terminé avec succès !"
```

Rendez-le exécutable : `chmod +x /opt/potager/deploy.sh`. Chaque mise à jour se fait désormais par un simple `./deploy.sh`.

---

## 5. Phase 3 : Passerelle Chariow & Abonnements Dynamiques

### 5.1 Gestion Dynamique des Formules (`SubscriptionPlan`)

Les abonnements ne sont pas figés dans le code : ils sont administrables dynamiquement via l'interface `/admin/subscriptions/subscriptionplan/`.

Les 3 formules par défaut configurées par `seed_data` sont :
1. **Pass 1 Mois** (`plan_type='monthly'`) : `2 500 XOF` (~4€) — Découverte sans engagement (30 jours).
2. **Pass Saison (3 Mois)** (`plan_type='seasonal'`) : `5 000 XOF` (~8€) — Badge `⭐ Recommandé`, 1 cycle de culture complet (90 jours).
3. **Pass Annuel** (`plan_type='yearly'`) : `15 000 XOF` (~23€) — Badge `-50%`, accès illimité 365 jours.

Chaque formule gère dynamiquement son prix, sa devise (`XOF`), son texte promotionnel et son activation (`is_active=True`).

### 5.2 Configuration des Produits Chariow
1. Dans votre espace marchand [Chariow](https://chariow.com) (Mode Live) :
   - Créez les 3 produits avec les montants exacts : 2 500 XOF, 5 000 XOF, 15 000 XOF.
   - Notez leurs IDs respectifs (`prd_xxxx`).
2. Renseignez ces IDs dans votre `.env` :
   ```ini
   CHARIOW_PRODUCT_MONTHLY_ID=prd_monthly_live_id
   CHARIOW_PRODUCT_SEASONAL_ID=prd_seasonal_live_id
   CHARIOW_PRODUCT_YEARLY_ID=prd_yearly_live_id
   ```

### 5.3 Configuration Sécurisée du Webhook HMAC-SHA256
1. Sur le tableau de bord Chariow > **Développeurs** > **Webhooks** :
   - **URL cible** : `https://api.guidedupotager.com/api/subscriptions/chariow/webhook/`
   - **Événement souscrit** : `successful.sale`
2. Récupérez la clé secrète de signature (`whsec_...`) et ajoutez-la à votre configuration :
   ```ini
   CHARIOW_WEBHOOK_SECRET=whsec_votre_cle_fournie_par_chariow
   ```
3. Le backend vérifie l'en-tête `x-chariow-signature` à l'aide d'un hash HMAC-SHA256 pour interdire toute injection frauduleuse.

### 5.4 Test Réel de Bout en Bout (Wave / Orange Money)
1. Créez un compte test sur l'application mobile ou sur le site web.
2. Cliquez sur l'une des formules d'abonnement.
3. Finalisez un achat réel de 2 500 XOF via Wave ou Orange Money.
4. Surveillez les logs du backend pour valider le déclenchement :
   ```bash
   docker logs -f potager_prod_backend | grep -i chariow
   ```
5. Confirmez que le profil de l'utilisateur bascule immédiatement en `is_premium = True` et que sa date d'expiration est automatiquement calculée.

---

## 6. Phase 4 : Gestion du Module Blog & Contenus Éducatifs

### 6.1 Architecture du Blog (Web & Mobile)
Le module blog (`apps/blog`) est synchronisé entre la vitrine web et l'application mobile :
- **Web** : `/blog/` (liste paginée et filtrable par catégorie) et `/blog/<slug>/` (lecture détaillée et commentaires).
- **Mobile** : Écran dédié `blog_screen.py` synchronisé via l'API REST `/api/blog/posts/`.

### 6.2 Modération des Commentaires & Articles Premium
- **Articles Premium (`is_premium=True`)** : Réservés aux détenteurs d'un abonnement actif. Sur l'application, un utilisateur gratuit voit l'extrait et un bouton d'abonnement débloquant l'accès.
- **Commentaires (`apps.blog.models.Comment`)** : Les commentaires postés peuvent être modérés directement dans l'interface Django Admin (`/admin/blog/comment/`).

### 6.3 Initialisation Automatique du Catalogue (`seed_data`)
La commande suivante préremplit la base avec un catalogue complet :
```bash
python manage.py seed_data
```
Elle initialise :
- Les formules d'abonnement (Pass 1 mois, 3 mois, Annuel).
- Les parties et chapitres de formation maraîchère.
- Les familles botaniques tropicales et fiches légumes complètes.
- Les fiches de maladies (flétrissement bactérien, virose TYLCV) et de ravageurs (mouche blanche, chenille).
- Les premières catégories et articles de blog éducatifs.

---

## 7. Phase 5 : Compilation, Signature & Déploiement Mobile

### 7.1 Configuration de l'URL d'API de Production
Vérifiez `mobile/app/utils/config.py` :
```python
import os

class Config:
    API_BASE_URL = os.environ.get('API_BASE_URL', 'https://api.guidedupotager.com/api')
    TIMEOUT = 12.0
```
> L'URL doit obligatoirement être en `https://` avec un certificat SSL valide. Android bloque par défaut tout trafic HTTP non chiffré en clair.

### 7.2 Vérification du fichier `buildozer.spec` (Android 14 / API 34)
Assurez-vous que le fichier `mobile/buildozer.spec` cible les exigences actuelles de Google Play :
```ini
[app]
title = Guide du Potager Tropical
package.name = guidedupotagertropical
package.domain = org.guidedupotagertropical
source.dir = .
version = 1.0.0

requirements = python3,kivy==2.3.0,httpx,requests,urllib3,certifi,openssl,pillow

orientation = portrait
android.permissions = INTERNET,ACCESS_NETWORK_STATE

# Cibles Google Play Store (Android 14)
android.api = 34
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a

android.release_artifact = aab
```

### 7.3 Génération du Keystore Privé de Production
```bash
cd mobile
keytool -genkey -v -keystore potager-release.keystore \
        -alias potager_key \
        -keyalg RSA -keysize 2048 -validity 10000 \
        -storepass MotDePasseKeystoreRobuste2026! \
        -keypass MotDePasseKeystoreRobuste2026! \
        -dname "CN=Guide du Potager, OU=Production, O=GuidePotager, L=Dakar, ST=DK, C=SN"
```
> 🔒 **Conservez précieusement ce fichier `potager-release.keystore` et ses mots de passe.** Sa perte rendrait impossible toute publication de mise à jour sur le Play Store.

### 7.4 Compilation de l'App Bundle (.aab) & de l'APK

#### Pour publication sur Google Play Store (Bundle .aab) :
```bash
cd mobile
buildozer android clean
buildozer android release

# Signature du bundle généré
jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 \
          -keystore potager-release.keystore \
          -storepass MotDePasseKeystoreRobuste2026! \
          bin/potager-1.0.0-arm64-v8a_armeabi-v7a-release-unsigned.aab \
          potager_key

mv bin/potager-1.0.0-arm64-v8a_armeabi-v7a-release-unsigned.aab bin/GuideDuPotager-v1.0.0.aab
```

#### Pour distribution directe de l'APK (WhatsApp / Site Web) :
Modifiez temporairement `android.release_artifact = apk` dans `buildozer.spec` :
```bash
buildozer android release

zipalign -v 4 bin/potager-1.0.0-arm64-v8a_armeabi-v7a-release-unsigned.apk bin/GuideDuPotager-v1.0.0-aligned.apk

apksigner sign --ks potager-release.keystore \
               --ks-key-alias potager_key \
               --ks-pass pass:MotDePasseKeystoreRobuste2026! \
               --out bin/GuideDuPotager-v1.0.0.apk \
               bin/GuideDuPotager-v1.0.0-aligned.apk
```

### 7.5 Publication sur Google Play Console
1. Connectez-vous sur [Google Play Console](https://play.google.com/console).
2. Créez votre application : **Guide du Potager Tropical**, langue : *Français*, type : *Gratuite*.
3. Complétez la fiche du magasin :
   - Icône HD (512x512 px)
   - Graphisme de fonctionnalité (1024x500 px)
   - Captures d'écran montrant les fiches légumes, le calendrier de semis, le blog et l'espace hors-ligne.
   - Lien vers la politique de confidentialité (`https://guidedupotager.com/privacy/`).
4. Téléversez le fichier `GuideDuPotager-v1.0.0.aab` dans le canal de **Production**.
5. Validez et envoyez pour examen Google (délai de 24 à 72h).

### 7.6 Distribution Directe APK (WhatsApp / Site Web)
Déposez le fichier `GuideDuPotager-v1.0.0.apk` sur votre serveur pour téléchargement immédiat :
```bash
# Exemple de lien de téléchargement direct :
https://guidedupotager.com/download/GuideDuPotager-v1.0.0.apk
```

---

## 8. Phase 6 : Monitoring, Sauvegardes & Maintenance

### 8.1 Sauvegardes Quotidiennes PostgreSQL (`pg_dump`)
Sur le serveur VPS, mettez en place un script de sauvegarde automatique dans `/usr/local/bin/backup_potager_db.sh` :

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/potager"
mkdir -p "$BACKUP_DIR"
DATE=$(date +"%Y%m%d_%H%M%S")
FILENAME="$BACKUP_DIR/potager_backup_$DATE.sql.gz"

# Exécution du dump dans le conteneur Docker
docker exec potager_prod_db pg_dump -U potager_prod_user potager_prod_db | gzip > "$FILENAME"

# Purge des sauvegardes vieilles de plus de 30 jours
find "$BACKUP_DIR" -type f -name "*.sql.gz" -mtime +30 -delete

echo "✅ Sauvegarde réussie : $FILENAME"
```

Rendez exécutable et planifiez via crontab toutes les nuits à 03h00 :
```bash
sudo chmod +x /usr/local/bin/backup_potager_db.sh
(crontab -l 2>/dev/null; echo "0 3 * * * /usr/local/bin/backup_potager_db.sh") | crontab -
```

### 8.2 Procédure de Restauration d'Urgence
En cas de corruption ou de panne matérielle :
```bash
# 1. Décompresser la sauvegarde choisie
gunzip -c /var/backups/potager/potager_backup_YYYYMMDD_HHMMSS.sql.gz > restore.sql

# 2. Restaurer dans PostgreSQL
cat restore.sql | docker exec -i potager_prod_db psql -U potager_prod_user -d potager_prod_db

# 3. Supprimer le fichier décompressé
rm restore.sql
```

### 8.3 Surveillance Sentry & Health Check Uptime
- **Sentry** : Capture en temps réel de toute exception 500 sur l'API et sur les webhooks Chariow.
- **Uptime Monitoring** : Configurez un ping HTTP toutes les minutes sur `https://api.guidedupotager.com/api/content/parts/` via [BetterStack](https://betterstack.com) ou [UptimeRobot](https://uptimerobot.com) avec alerte par SMS ou Telegram.

---

## 9. Guide de Dépannage Fréquent (Troubleshooting)

### Problème 1 : Les utilisateurs ne reçoivent pas leur code OTP à 6 chiffres
- **Cause** : Configuration SMTP manquante ou bloquée en mode console (`console.EmailBackend`).
- **Solution** : Vérifiez que `EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend` est bien actif dans `.env`. Testez l'envoi d'un mail avec le script de la section 3.2. Vérifiez que le port sortant `587` n'est pas bloqué par votre hébergeur VPS (certains hébergeurs comme OVH ou Hetzner bloquent le port SMTP par défaut, demandez l'ouverture au support).

### Problème 2 : L'abonnement ne s'active pas après un paiement Chariow
- **Cause** : Mauvaise clé secrète de webhook ou rejet de signature HMAC.
- **Solution** : Vérifiez que la variable `CHARIOW_WEBHOOK_SECRET` correspond exactement à la clé commençant par `whsec_` sur le dashboard Chariow. Inspectez les logs backend :
  ```bash
  docker logs potager_prod_backend --tail 100 | grep -i chariow
  ```

### Problème 3 : L'application mobile affiche « Erreur de connexion au serveur »
- **Cause** : URL non sécurisée en HTTP ou certificat SSL invalide.
- **Solution** : Vérifiez que le nom de domaine de l'API s'ouvre dans un navigateur sans avertissement de sécurité SSL. Confirmez que `API_BASE_URL` dans l'application utilise bien le protocole `https://`.

### Problème 4 : Les images de couverture du blog ne s'affichent pas
- **Cause** : Mauvaise configuration de l'alias Nginx ou permissions Docker sur le volume des médias.
- **Solution** : Vérifiez les droits du dossier média sur le serveur :
  ```bash
  sudo chmod -R 755 /var/lib/docker/volumes/potager_media_prod_data/_data/
  ```

---

## 10. Checklist Finale Avant Lancement (Go / No-Go)

Cochez méticuleusement chaque point avant l'ouverture officielle :

### 🛡️ Backend & Infrastructure
- [ ] `DEBUG = False` strictement vérifié sur l'environnement de production.
- [ ] `SECRET_KEY` unique, cryptographique et générée aléatoirement.
- [ ] Base PostgreSQL 16 opérationnelle avec script de sauvegarde cron quotidien (`0 3 * * *`).
- [ ] Toutes les migrations appliquées sans conflit (`python manage.py migrate`).
- [ ] Catalogue initial complet injecté avec succès (`python manage.py seed_data`).
- [ ] Superutilisateur administrateur créé avec mot de passe fort.
- [ ] Fichiers statiques collectés avec succès (`collectstatic`).
- [ ] Certificat SSL Let's Encrypt actif et note A+ sur SSL Labs.

### ✉️ Authentification & E-mails
- [ ] Relais SMTP en production configuré et validé par un test d'envoi réel.
- [ ] Réception effective du code OTP à 6 chiffres lors d'une nouvelle inscription.
- [ ] Limitation des tentatives de validation du code OTP vérifiée (protection anti-bruteforce).
- [ ] Réinitialisation de mot de passe par e-mail opérationnelle.

### 💳 Passerelle Chariow & Abonnements
- [ ] Clés Chariow réelles (`CHARIOW_API_KEY`, `CHARIOW_WEBHOOK_SECRET`) configurées.
- [ ] Les 3 formules d'abonnement dynamiques (`SubscriptionPlan`) créées et actives dans l'admin.
- [ ] Endpoint webhook HTTPS configuré dans Chariow avec écoute de `successful.sale`.
- [ ] Paiement réel de test (Wave / Orange Money) effectué avec activation immédiate du profil Premium.

### 📱 Application Mobile
- [ ] `API_BASE_URL` configurée vers l'URL HTTPS de production.
- [ ] Test sur appareil physique Android :
  - Inscription avec code OTP à 6 chiffres reçu par e-mail.
  - Consultation hors-ligne des chapitres et fiches légumes en cache SQLite.
  - Affichage responsive de l'écran d'abonnement sur plusieurs tailles d'écran.
  - Consultation du module Blog et lecture des articles.
  - Déclenchement de la redirection vers le paiement Chariow.
- [ ] Fichier `.aab` compilé, signé avec le Keystore de production et validé sur le Google Play Console.
- [ ] Fichier `.apk` signé disponible pour téléchargement direct.
