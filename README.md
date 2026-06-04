# Module de Rapprochement MB / CBS / PI
**LICELI Technologies — Stage Licence ISI 2025–2026**

Stagiaire : YERE Haby Melika Rachida

---

## Description
Module automatique de rapprochement nocturne des transactions entre la solution **Mobile Banking LICELI**, le **Core Banking System (CBS)** de la banque et le système de **Paiement Instantané (PI) BCEAO**.

---

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
| CI/CD | GitHub Actions → GHCR |

---

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
# Éditer .env avec les vraies valeurs
```

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

---

## Stratégie de branches (GitFlow)
| Branche | Rôle |
|---------|------|
| `main` | Production stable — merge uniquement depuis develop |
| `develop` | Intégration — pipeline CI/CD à chaque push |
| `feature/*` | Développement unitaire — ex: `feature/matching-cbs` |

---

## Pipeline CI/CD (GitHub Actions)
```
push develop/main
    │
    ├── 1. test      → pytest (100% requis)
    ├── 2. quality   → flake8 PEP8 (zéro erreur)
    ├── 3. build     → Docker image → GHCR
    └── 4. deploy    → SSH → docker compose pull && up
```

### Secrets GitHub à configurer
Dans `Settings > Secrets and variables > Actions` :
- `DEPLOY_HOST` : IP du serveur LICELI
- `DEPLOY_USER` : utilisateur SSH
- `SSH_KEY` : clé SSH privée
