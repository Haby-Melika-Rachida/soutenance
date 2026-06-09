# Module de Rapprochement MB / CBS / PI

**LICELI Technologies - Stage Licence ISI 2025-2026**

Stagiaire : YERE Haby Melika Rachida

---

## Description

Ce projet fournit un module de rapprochement automatique des transactions entre :

- la solution Mobile Banking LICELI ;
- le Core Banking System (CBS) de la banque ;
- le système de Paiement Instantané (PI) BCEAO.

L'objectif est de détecter les écarts entre les écritures des différents systèmes, de produire un rapport de rapprochement et de notifier les équipes concernées.

## Périmètre fonctionnel

- Collecte des transactions MB, CBS et PI via des connecteurs API.
- Exécution d'un batch de rapprochement nocturne, avec déclenchement manuel possible.
- Détection des écarts métier :
  - EC-01 : transaction MB absente du CBS ;
  - EC-02 : transaction CBS sans correspondance MB ;
  - EC-03 : doublon côté CBS ;
  - EC-04 : doublon côté MB ;
  - EC-05 : cycle PI irrévocable non débité ;
  - EC-06 : cycle PI irrévocable non crédité.
- Génération de rapports PDF et Excel.
- Notification des écarts critiques.
- Journalisation des actions et conservation des traces d'audit.

## Stack technique

| Couche | Technologie |
|--------|-------------|
| Backend API REST | Python 3.11 + Django 4.2 LTS + DRF 3.15 |
| Frontend | Vue.js 3 |
| Batch / Worker | Celery 5.3 + Celery Beat |
| Message broker | Redis 7 |
| Base de données | PostgreSQL 15 |
| Reverse proxy | Nginx 1.25 |
| Conteneurisation | Docker + Docker Compose 2.27 |
| CI/CD | GitHub Actions vers GHCR |

## Démarrage rapide

### 1. Prérequis

- Docker Desktop installé
- Git installé

### 2. Cloner le projet

```bash
git clone https://github.com/VOTRE_ORG/rapprochement-mb-cbs-pi.git
cd rapprochement-mb-cbs-pi
```

### 3. Configurer les variables d'environnement

```bash
cp .env.example .env
```

Éditer ensuite `.env` avec les valeurs de l'environnement cible.

### 4. Lancer les conteneurs

```bash
docker compose up -d
```

### 5. Initialiser la base de données

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

### 6. Accéder à l'application

- Frontend : http://localhost
- API : http://localhost/api/v1/
- Admin Django : http://localhost/admin/

## Tests et qualité

Depuis le dossier `backend` :

```bash
pytest
flake8
```

Les tests couvrent notamment le chargement du projet, les connecteurs et le moteur de rapprochement.

## Structure du projet

```text
backend/
  apps/
    api/              API REST
    batch/            orchestration des traitements
    connectors/       accès aux systèmes externes
    core/             modèles métier
    matching/         moteur de rapprochement
    notifications/    notifications email
    reports/          génération des rapports
frontend/             interface Vue.js
```

## Stratégie de branches

| Branche | Rôle |
|---------|------|
| `main` | Production stable |
| `develop` | Intégration |
| `feature/*` | Développement d'une fonctionnalité |

## Pipeline CI/CD

```text
push develop/main
  1. test      -> pytest
  2. quality   -> flake8
  3. build     -> image Docker vers GHCR
  4. deploy    -> mise à jour du serveur
```

### Secrets GitHub à configurer

- `DEPLOY_HOST` : IP du serveur LICELI
- `DEPLOY_USER` : utilisateur SSH
- `SSH_KEY` : clé SSH privée
