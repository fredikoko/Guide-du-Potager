# 🌿 Guide du Potager Tropical — Présentation Détaillée de l'Application

> **Une solution numérique tout-en-un dédiée à l'apprentissage, à la pratique et à la réussite du maraîchage biologique et de l'agro-écologie sous climats tropicaux, arides et tempérés.**

---

## 📑 Sommaire

1. [Vision & Raison d'Être](#1-vision--raison-dêtre)
2. [Vue d'Ensemble de l'Écosystème](#2-vue-densemble-de-lécosystème)
3. [Détail Exhaustif des Fonctionnalités par Module](#3-détail-exhaustif-des-fonctionnalités-par-module)
   - [3.1 Authentification Sécurisée & Profil Agro-Climatique](#31-authentification-sécurisée--profil-agro-climatique)
   - [3.2 Parcours Pédagogique & Chapitres de Formation](#32-parcours-pédagogique--chapitres-de-formation)
   - [3.3 Simulateur Interactif de Calendrier de Semis & Récoltes](#33-simulateur-interactif-de-calendrier-de-semis--récoltes)
   - [3.4 Encyclopédie Maraîchère & Dictionnaire Visuel](#34-encyclopédie-maraîchère--dictionnaire-visuel)
   - [3.5 Dispensaire Phytosanitaire & Protection Naturelle](#35-dispensaire-phytosanitaire--protection-naturelle)
   - [3.6 Module Blog, Actualités & Partage d'Expériences](#36-module-blog-actualités--partage-dexpériences)
   - [3.7 Formules d'Abonnement Dynamiques & Paiement Mobile Money](#37-formules-dabonnement-dynamiques--paiement-mobile-money)
   - [3.8 Portail Web Vitrine & Interface Responsive](#38-portail-web-vitrine--interface-responsive)
   - [3.9 Expérience Mobile Kivy & Mode Hors-Ligne Résilient](#39-expérience-mobile-kivy--mode-hors-ligne-résilient)
   - [3.10 Back-Office d'Administration & Gestion de Contenu](#310-back-office-dadministration--gestion-de-contenu)
4. [Matrice des Accès : Gratuit vs Premium](#4-matrice-des-accès--gratuit-vs-premium)
5. [Architecture Technique & Stack Logicielle](#5-architecture-technique--stack-logicielle)
6. [Cas d'Usage Types & Personas](#6-cas-dusage-types--personas)
7. [Impact & Valeur Ajoutée](#7-impact--valeur-ajoutée)

---

## 1. Vision & Raison d'Être

Le maraîchage sous les tropiques et dans les zones sahéliennes présente des défis uniques : fortes chaleurs (> 40°C), pluies torrentielles ou sécheresses prolongées, ravageurs voraces (mouches blanches, chenilles défoliatrices) et pression de maladies bactériennes foudroyantes.

La majorité des ressources de jardinage disponibles en ligne sont conçues pour des climats tempérés occidentaux (France métropolitaine, Europe du Nord) et se révèlent inadaptées, voire contre-productives sous climat chaud.

**Le Guide du Potager Tropical** a été conçu pour combler ce vide en offrant un outil moderne, scientifique et accessible sur le terrain. L'application accompagne chaque étape du cultivateur — du choix de l'emplacement jusqu'à la conservation des graines — avec des solutions **100% agro-écologiques, locales et peu coûteuses**.

---

## 2. Vue d'Ensemble de l'Écosystème

L'application s'articule autour d'un écosystème interconnecté composé de trois piliers complémentaires :

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                       ÉCOSYSTÈME GUIDE DU POTAGER                            │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       │
        ┌──────────────────────────────┼──────────────────────────────┐
        ▼                              ▼                              ▼
┌────────────────────────┐   ┌────────────────────────┐   ┌────────────────────────┐
│  Application Mobile    │   │      Portail Web       │   │    Back-Office Admin   │
│      Android/iOS       │   │       Interactif       │   │     Django Avancé      │
│  - Client Kivy Python  │   │  - Vitrine publique    │   │  - Modération blog     │
│  - Cache 100% offline  │   │  - Découverte cours    │   │  - Gestion des plans   │
│  - Responsive multi-   │   │  - Blog & Actualités   │   │  - Bibliothèque médias │
│    écrans (tél/tablette│   │  - Souscription Web    │   │  - Gestion utilisateurs│
└────────────────────────┘   └────────────────────────┘   └────────────────────────┘
```

---

## 3. Détail Exhaustif des Fonctionnalités par Module

### 3.1 Authentification Sécurisée & Profil Agro-Climatique

L'application intègre un système d'authentification robuste basé sur les standards modernes de sécurité :

* **Authentification par jetons JWT (JSON Web Tokens)** : Connexion sécurisée avec renouvellement automatique des jetons d'accès et de rafraîchissement.
* **Système de Vérification à 6 Chiffres (OTP par E-mail)** :
  * Code sécurisé à usage unique expédié par e-mail lors de la création d'un compte.
  * Validation obligatoire avant activation du compte pour garantir des profils authentiques.
  * Réutilisation sécurisée pour le changement d'e-mail et la réinitialisation de mot de passe.
  * Protection anti-bruteforce (invalidation automatique après 5 tentatives échouées).
* **Profil Personnalisé de Jardinier** :
  * **Zone agro-climatique** : Sahélienne (aride, harmattan), Soudano-sahélienne, Tropicale humide / Côtière, Équatoriale / Forêt, ou Insulaire tropicale.
  * **Type de culture** : Potager de pleine terre, Hors-sol (bacs & tables maraîchères), Micro-jardin urbain, ou Exploitation périurbaine.
  * Suivi de l'état de l'abonnement et historique d'activité.

---

### 3.2 Parcours Pédagogique & Chapitres de Formation

Une véritable école maraîchère structurée de façon modulaire et progressive :

* **Organisation en 3 Grandes Parties** :
  1. *Les Fondamentaux du Potager* (Emplacement, vie du sol, fertilisation de base).
  2. *Calendrier de Semis & Gestes Techniques* (Pépinière tropicale, repiquage, arrosage en saison sèche).
  3. *Permaculture & Techniques Avancées* (Associations bénéfiques, mulching, compostage à chaud).
* **Contenus Pédagogiques Riches** :
  * Rendu HTML mis en forme avec typographie soignée.
  * Intégration d'images techniques légendées au cœur du texte.
  * Estimation du temps de lecture (ex. *« 8 min de lecture »*).
  * Système de chapitres gratuits et de chapitres Premium débloquables.

---

### 3.3 Simulateur Interactif de Calendrier de Semis & Récoltes

L'un des cœurs interactifs de l'application (`calendar_screen.py`) permettant de savoir précisément **quoi faire au potager, quand et comment** :

* **Sélecteur Mensuel Dynamique** : Navigation instantanée entre les 12 mois de l'année (de Janvier à Décembre).
* **Double Filtre de Travaux** :
  * 🌱 **Semis & Plantations** : Affiche les espèces à semer sous ombrière, en pépinière ou en pleine terre pour le mois sélectionné.
  * 🧺 **Périodes de Récolte** : Affiche les cultures prêtes à être cueillies ou récoltées selon le cycle biologique.
* **Fiches Pratiques Contextuelles** :
  * Indication des conseils saisonniers spécifiques (ex. gestion de l'harmattan en décembre-février, ombrage obligatoire en avril-mai, drainage en juillet-août).
  * Accès direct à la fiche technique complète de chaque légume concerné.

---

### 3.4 Encyclopédie Maraîchère & Dictionnaire Visuel

Un répertoire exhaustif illustré pour identifier et cultiver toutes les espèces végétales :

* **Fiches Légumes Complètes** :
  * Nom commun, nom scientifique et nom vernaculaire local.
  * Conseils d'arrosage, d'ensoleillement et de fertilisation organique.
  * Espacement recommandé entre les lignes et entre les plants.
  * Période de pépinière, temps de levée et durée jusqu'à la récolte.
* **Familles Botaniques Tropicales** :
  * Regroupement par grandes familles : *Solanacées* (tomate, piment, aubergine), *Malvacées* (gombo, bissap), *Cucurbitacées* (courge, concombre), *Fabacées* (niébé, arachide), etc.
  * Explication des caractéristiques communes et des règles de rotation.
* **Boîte à Outils Maraîchère** :
  * Présentation des outils manuels ergonomiques : Grelinette, transplantoir, serouette, semoir de précision, arrosoir à pomme fine, couteau à désherber.
  * Conseils d'entretien et d'utilisation pour préserver la structure du sol.
* **Interface Modale Détaillée (`DetailPopup`)** :
  * Fiche popup instantanée avec photo HD, résumé des caractéristiques, boutons d'action et conseils de compagnonnage.
  * Tri alphabétique optimisé et recherche en temps réel par mot-clé.

---

### 3.5 Dispensaire Phytosanitaire & Protection Naturelle

Un outil d'aide au diagnostic pour soigner les plantes **sans aucun intrant chimique de synthèse** :

* **Diagnostic Visuel des Maladies** :
  * Symptômes détaillés (ex. flétrissement bactérien brutal, jaunissement en cuillère TYLCV, nécrose apicale).
  * Conditions météo favorables au développement (saison des pluies, forte hygrométrie).
  * Méthodes de prévention prophylactique et assainissement du sol.
* **Fiches Ravageurs & Insectes Nuisibles** :
  * Identification des insectes (mouche blanche / aleurode, chenille défoliatrice, pucerons, nématodes à galles).
  * Description précise des dégâts causés sur les feuilles et fruits.
* **Formulations de Lutte Biologique Tropicale** :
  * Recettes détaillées prêtes à l'emploi : décoction de graines de neem, macération piment-ail-savon noir, épandage de cendre de bois, purin d'ortie/consoude.
  * Conseils sur les barrières physiques (filets anti-insectes 50 mesh, ombrières, bandes fleuries de tagètes et basilic).

---

### 3.6 Module Blog, Actualités & Partage d'Expériences

Un magazine numérique intégré (`apps/blog`) pour s'informer et se perfectionner en continu :

* **Classement Thématique** :
  * *Calendrier & Saisons Tropicales*, *Agro-écologie Tropicale*, *Fiches Légumes & Récoltes*, *Protection Naturelle*, *Gestion de l'Eau*, *Potager Urbain & Balcon*, etc.
* **Articles Riches & Multimédias** :
  * Couvertures illustrées, galerie d'images secondaires légendées.
  * Mise en forme aérée avec sous-titres, encadrés et listes de contrôle.
  * Compteur de vues et temps estimé de lecture.
* **Espace Communautaire** :
  * Zone de commentaires sous chaque article permettant aux jardiniers d'échanger des retours d'expérience et de poser leurs questions.
* **Modèle Freemium Éditorial** :
  * Articles d'initiation accessibles à tous.
  * Guides avancés et dossiers exclusifs réservés aux membres abonnés Premium.

---

### 3.7 Formules d'Abonnement Dynamiques & Paiement Mobile Money

Un système de monétisation éthique, adapté aux réalités des marchés subsahariens et internationaux :

* **Formules Administrables Dynamiquement (`SubscriptionPlan`)** :
  * 🌿 **Pass 1 Mois (Découverte)** : 2 500 XOF (~4€) — Idéal pour tester sans engagement.
  * ⭐ **Pass Saison 3 Mois (1 Cycle Maraîcher)** : 5 000 XOF (~8€) — Formule recommandée pour accompagner un cycle complet du semis à la récolte.
  * 🏆 **Pass Annuel (Autonomie Complète)** : 15 000 XOF (~23€) — Accès illimité 365 jours avec 50% de réduction.
  * Possibilité pour l'administrateur de créer de nouveaux plans ou de modifier les tarifs et badges promotionnels en un clic.
* **Passerelle de Paiement Chariow Intégrée** :
  * Prise en charge des moyens de paiement les plus populaires : **Wave**, **Orange Money**, **MTN Mobile Money**, **Moov Money** et Cartes bancaires (Visa/Mastercard).
  * Validation instantanée et automatique des abonnements via Webhooks sécurisés par signature cryptographique HMAC-SHA256.
  * Basculement automatique du compte utilisateur en statut `is_premium` sans intervention manuelle.

---

### 3.8 Portail Web Vitrine & Interface Responsive

En plus de l'application mobile, le projet dispose d'une présence web complète :

* **Landing Page Professionnelle** : Présentation du projet, des fonctionnalités, des témoignages et des captures de l'application.
* **Vitrine des Formations & Extraits** : Consultation publique des premiers chapitres pour susciter l'intérêt.
* **Magazine Blog en Ligne** : Indexation SEO de tous les articles pour attirer du trafic organique depuis Google.
* **Page d'Abonnement Web Dédiée** : Grille tarifaire claire avec tunnel de commande relié à la passerelle Chariow.
* **Section « À Propos » & Valeurs** : Explication de la mission agro-écologique et de la protection de la biodiversité locale.

---

### 3.9 Expérience Mobile Kivy & Mode Hors-Ligne Résilient

Développée avec le framework multiplateforme **Kivy**, l'application mobile a été spécifiquement optimisée pour les conditions réelles d'utilisation au jardin :

* **Fonctionnement Hors-Ligne Intégral** :
  * Les chapitres consultés, le calendrier de semis et l'encyclopédie sont mis en cache localement sur l'appareil.
  * Le cultivateur peut consulter ses fiches techniques au fond de son potager, même en zone blanche sans couverture 3G/4G.
* **Design 100% Responsive & Ergonomique** :
  * Interface s'adaptant automatiquement aux smartphones de toute taille (petits écrans 4,5 pouces comme grands smartphones 6,8 pouces) ainsi qu'aux tablettes.
  * Palette de couleurs inspirée de la nature : vert feuillage (`#2d6a4f`), vert tendre (`#52b788`), terre cuite (`#b07d62`) et fond crème doux reposant pour les yeux.
* **Navigation Fluide par Tiroir Latéral (Navigation Drawer)** :
  * Accès en 1 tap à toutes les sections : Accueil, Cours, Calendrier, Légumes, Maladies, Outils, Blog, Mon Profil, Abonnement.

---

### 3.10 Back-Office d'Administration & Gestion de Contenu

Une interface d'administration Django enrichie et sécurisée pour les gestionnaires de la plateforme :

* **Édition WYSIWYG & Générateur HTML d'Images** : Téléversement direct des images d'illustration avec aperçu miniature et génération de tags HTML prêts à insérer dans le texte.
* **Pilotage des Abonnements** : Visualisation des transactions Chariow, des abonnements actifs et de la valeur client.
* **Modération des Commentaires** : Validation, modération ou suppression des commentaires laissés sur le blog.
* **Gestion des Fiches Techniques** : Ajout ou modification des fiches légumes, insectes ravageurs et calendrier de semis sans toucher au code source.

---

## 4. Matrice des Accès : Gratuit vs Premium

| Fonctionnalité | Compte Gratuit (Découverte) | Membre Premium (Abonné) |
|---|:---:|:---:|
| **Partie 1 du Cours (Les Fondamentaux)** | ✅ Accès complet | ✅ Accès complet |
| **Parties 2 & 3 (Semis avancés & Permaculture)** | ❌ Verrouillé | ✅ Accès illimité |
| **Simulateur de Calendrier de Semis & Récoltes** | ✅ 12 mois accessibles | ✅ 12 mois + astuces poussées |
| **Fiches Légumes & Familles Botaniques de base** | ✅ Consultation libre | ✅ Consultation libre |
| **Fiches Maladies & Ravageurs Avancées** | ⚠️ Aperçu limité | ✅ Symptômes + Recettes complètes |
| **Outils Maraîchers Spécialisés** | ⚠️ Outils de base | ✅ Tous les outils professionnels |
| **Articles de Blog** | ✅ Articles publics | ✅ Articles publics + Dossiers Premium |
| **Commentaires & Questions aux Experts** | ❌ Lecture seule | ✅ Droit de publication |
| **Mode Hors-Ligne Local** | ✅ Contenu gratuit en cache | ✅ Intégralité du catalogue hors-ligne |
| **Badge Membre & Support Privilégié** | ❌ Non | ✅ Profil arborant le badge Master |

---

## 5. Architecture Technique & Stack Logicielle

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                               STACK TECHNIQUE                                │
├──────────────────────────┬───────────────────────────────────────────────────┤
│ Backend API & Serveur    │ Python 3.11/3.13, Django 5.1, Django REST FW      │
│ Authentification         │ JWT (djangorestframework-simplejwt) + OTP Email   │
│ Fichiers Statiques       │ WhiteNoise avec compression Gzip/Brotli           │
│ Base de Données          │ PostgreSQL 16 (Production) / SQLite (Développement)│
│ Passerelle de Paiement   │ Chariow API v1 (Wave, Orange Money, MTN, CB)      │
│ Documentation API        │ OpenAPI 3.0 via drf-spectacular & Swagger UI      │
│ Application Mobile       │ Kivy 2.3.0, Requests, Httpx, Pillow, SQLite Local │
│ Packaging Mobile         │ Buildozer, Python-for-Android, Android API 34     │
│ Déploiement & Conteneurs │ Docker, Docker Compose, Nginx, Let's Encrypt SSL  │
└──────────────────────────┴───────────────────────────────────────────────────┘
```

---

## 6. Cas d'Usage Types & Personas

### Persona 1 : Aminata, Débutante en Milieu Urbain (Dakar, Sénégal)
* **Situation** : Dispose d'une petite terrasse et souhaite faire pousser des tomates, du piment et de la menthe dans des bacs.
* **Utilisation de l'application** :
  * Sélectionne son profil *"Micro-jardin urbain / Zone Côtière"*.
  * Consulte la Partie 1 pour préparer un substrat drainant sans terre de mauvaise qualité.
  * Utilise le calendrier interactif pour savoir quelles herbes planter en novembre.
  * Fabrique un répulsif à base d'ail et piment grâce à la recette du dispensaire pour éliminer les aleurodes sur ses piments.

### Persona 2 : Ibrahim, Maraîcher Agro-écologique (Bobo-Dioulasso, Burkina Faso)
* **Situation** : Exploite une parcelle maraîchère périurbaine de 500 m² soumise à des chaleurs intenses et à la sécheresse.
* **Utilisation de l'application** :
  * Souscrit au *Pass Saison (3 Mois)* via Orange Money pour accompagner son cycle de culture.
  * Débloque les chapitres de la Partie 3 sur les associations de cultures (*Maïs + Niébé + Courge*).
  * Consulte hors-ligne au milieu de ses planches les fiches de dosage du purin de neem pour protéger ses gombos contre les chenilles défoliatrices sans dépenser en pesticides chimiques.

### Persona 3 : Marc, Passionné de Permaculture & Autosuffisance (Abidjan, Côte d'Ivoire)
* **Situation** : Souhaite produire une nourriture saine pour sa famille et transmettre ses connaissances.
* **Utilisation de l'application** :
  * S'abonne au *Pass Annuel* pour un accès continu.
  * Lit les articles hebdomadaires du blog sur les techniques de thé de compost aéré et la conservation des semences paysannes.
  * Participe aux discussions dans l'espace commentaires pour partager ses réussites de culture de la patate douce sur buttes.

---

## 7. Impact & Valeur Ajoutée

1. **Souveraineté Alimentaire & Économies** : Permet aux familles et producteurs de produire une alimentation saine, fraîche et abondante à coût réduit.
2. **Santé & Environnement** : Éradique le recours aux pesticides chimiques nocifs grâce à des protocoles de bioprotection éprouvés (neem, cendre, ail, savon noir).
3. **Résilience Climatique** : Enseigne les techniques d'économie d'eau (paillage lourd, ollas, arrosage au goulot) permettant d'économiser jusqu'à **70% d'eau** d'arrosage en période aride.
4. **Accessibilité Totale** : Pensée pour l'Afrique et les zones rurales grâce au **mode hors-ligne**, au faible poids de l'application et au paiement direct en **Mobile Money local**.

---

*Document de référence rédigé pour le projet **Guide du Potager Tropical** — Version 1.0.0 (2026).*
