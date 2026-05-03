# Comparateur de Cotes Sportives

Application moderne de comparaison de cotes sportives en temps réel avec design professionnel type SaaS.

## Stack Technique

### Backend
- **Framework**: FastAPI (Python 3.12)
- **ORM**: SQLAlchemy
- **Base de données**: MySQL 8.0
- **Authentification**: JWT (access + refresh tokens)
- **Serveur**: Uvicorn

### Frontend
- **Framework**: Vue 3 (Composition API)
- **Build**: Vite
- **Routing**: Vue Router
- **State Management**: Pinia
- **Styling**: TailwindCSS
- **HTTP Client**: Axios

## Structure du Projet

```
.
├── backend/
│   ├── app/
│   │   ├── routers/          # Endpoints API
│   │   │   ├── auth.py       # Authentification
│   │   │   ├── sports.py     # Sports
│   │   │   ├── leagues.py    # Ligues
│   │   │   ├── matches.py    # Matchs
│   │   │   └── odds.py       # Cotes
│   │   ├── models.py         # Modèles SQLAlchemy
│   │   ├── schemas.py        # Schémas Pydantic
│   │   ├── auth.py           # Utilitaires JWT
│   │   ├── database.py       # Configuration DB
│   │   ├── config.py         # Configuration
│   │   └── main.py           # Application FastAPI
│   ├── tests/                # Tests unitaires
│   ├── requirements.txt
│   └── Dockerfile
├── src/
│   ├── api/                  # Client API et services
│   ├── stores/               # Stores Pinia
│   ├── views/                # Pages Vue
│   ├── layouts/              # Layouts
│   ├── router/               # Configuration routing
│   └── types/                # Types TypeScript
├── docker-compose.yml
└── README.md
```

## Installation et Lancement

### Prérequis

Votre base de données MySQL doit déjà exister avec les tables de sports, bookmakers, matchs et cotes remplies.

### 1. Configuration de la base de données

Créez la table utilisateur :

```bash
mysql -u admin -p bet < backend/migrations/create_user_table.sql
```

### 2. Configuration des variables d'environnement

Copiez et éditez le fichier `.env` :

```bash
cp .env.example .env
```

Modifiez les valeurs dans `.env` :

```env
VITE_API_URL=http://localhost:8000

DB_HOST_BETTING=localhost
DB_USER_BETTING=admin
DB_PASS_BETTING=votre-mot-de-passe-mysql
DB_NAME_BETTING=bet
DB_PORT_BETTING=3306

JWT_SECRET=changez-cette-cle-en-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 3. Lancement avec Docker (Recommandé)

```bash
docker-compose up -d
```

Les services seront disponibles sur:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Documentation API**: http://localhost:8000/docs

### 4. Lancement en Local

#### Backend

1. **Installer Python 3.12+** et créer un environnement virtuel:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

2. **Installer les dépendances**:
```bash
pip install -r requirements.txt
```

3. **Configurer l'environnement**:
```bash
cp .env.example .env
# Éditer .env avec vos paramètres MySQL
```

4. **Créer les tables**:
```bash
python -c "from app.models import Base; from app.database import engine; Base.metadata.create_all(bind=engine)"
```

5. **Lancer le serveur**:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

1. **Installer Node.js 18+** et les dépendances:
```bash
npm install
```

2. **Configurer l'environnement**:
```bash
cp .env.example .env
# Éditer .env si nécessaire
```

3. **Lancer le serveur de développement**:
```bash
npm run dev
```

## API Endpoints

### Authentification
- `POST /auth/register` - Créer un compte
- `POST /auth/login` - Se connecter
- `POST /auth/refresh` - Rafraîchir le token
- `GET /auth/me` - Profil utilisateur

### Données (Authentification requise)
- `GET /sports` - Liste des sports
- `GET /sports/{sport_id}/leagues` - Ligues par sport
- `GET /leagues/{league_id}/matches` - Matchs par ligue (avec filtres date)
- `GET /matches/{match_id}/odds` - Cotes d'un match

## Tests

### Backend
```bash
cd backend
pytest
```

## Modèle de Données

### Entités Principales
- **User**: Utilisateurs de l'application
- **Sport**: Types de sport (Football, Basketball, etc.)
- **League**: Compétitions/Championnats
- **Team**: Équipes
- **Match**: Événements sportifs
- **Bookmaker**: Bookmakers (Betclic, Winamax, etc.)
- **Market**: Types de marchés (1X2, Over/Under, etc.)
- **Outcome**: Issues des marchés (home, draw, away, etc.)
- **BookmakerOdd**: Cotes par bookmaker avec edge calculé

### Relations
- Un match appartient à une ligue et un sport
- Un match a deux équipes (home/away)
- Un match a plusieurs marchés
- Chaque marché a plusieurs issues
- Chaque issue a des cotes de différents bookmakers

## Fonctionnalités

### Design Moderne SaaS
- **Page de Login** - Design split-screen avec fond animé
- **Page d'inscription** - Interface moderne et intuitive
- **Sélection de sports** - Cartes avec icônes et recherche
- **Layout professionnel** - Header avec logo et navigation fluide
- **Palette de couleurs** - Bleus foncés / Gris / Verts pour les best odds
- **Responsive** - Optimisé mobile et desktop

### Fonctionnalités Utilisateur
- Inscription et connexion sécurisée
- Navigation intuitive : Sport → League → Match → Cotes
- Filtrage par date des matchs
- Recherche rapide de sports
- Gestion automatique des tokens JWT

### Comparateur de Cotes
- Affichage de toutes les cotes par bookmaker
- **Mise en avant de la meilleure cote** (fond vert + badge BEST)
- Calcul et affichage de l'edge en % avec code couleur:
  - Vert si positif (value bet)
  - Rouge si négatif
- Affichage de la fair odd de référence
- Dernière mise à jour des cotes
- Support de tous les types de marchés (ML, Over/Under, Handicap, etc.)

### Backend
- Authentification JWT sécurisée (access + refresh tokens)
- Endpoints protégés par authentification
- Validation des données avec Pydantic
- CORS configuré
- Documentation automatique (Swagger)
- Gestion d'erreurs complète

## Variables d'Environnement

### Backend (.env)
```
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/odds_db
JWT_SECRET=your-secret-key-change-this
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
```

## Sécurité

- Mots de passe hashés avec bcrypt
- Tokens JWT avec expiration
- Refresh tokens pour renouvellement automatique
- Validation des entrées avec Pydantic
- Protection CSRF via tokens
- Endpoints protégés par authentification

## Production

Pour déployer en production:

1. Modifier `JWT_SECRET` avec une clé forte
2. Configurer une vraie base de données MySQL
3. Utiliser un reverse proxy (nginx)
4. Activer HTTPS
5. Configurer les CORS strictement
6. Utiliser des variables d'environnement sécurisées

## Support

Pour toute question ou problème, consultez la documentation de l'API: http://localhost:8000/docs
