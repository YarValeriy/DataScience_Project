# FastAPI Data-Science Project

This project is a FastAPI application that allows users to download PDF documents and make queries from that document.

## Features

- User registration and authentication with JWT tokens
- User roles (admin, user) with different access levels
- Redis for caching and rate limiting
- PostgreSQL database for data storage
- Email verification and password reset
- Role management

## Getting Started

1. Clone the repository:

```bash
git clone https://github.com/your-username/fastapi-photo-share.git
cd fastapi-photo-share
```

2. Install the dependencies:

```bash
pip install poetry
poetry shell
poetry update
```

3. Please rename `.env.example` file to `.env` and set up the environment variables in it.

4. docker-compose up --build -d

for next steps:

```bash
cd app
```

5. Populate database schema:

```bash
alembic upgrade head
```

6. Run the application:

```bash
python main.py
```

7. Access the API documentation at `http://localhost:8000/docs`.

## API Endpoints

### Authentication

- **POST /api/auth/signup**: Register a new user.
- **POST /api/auth/login**: Log in an existing user.
- **POST /api/auth/refresh_token**: Refresh the access token.
- **POST /api/auth/logout**: Log out the current user.

### Users

- **GET /api/users/me**: Get the current user's profile.
- **PUT /api/users/**: Update the current user's profile.
- **PUT /api/users/avatar**: Update the current user's avatar.

## Developed by:

### PyMagic team:

- [Roman Hnatiak](https://github.com/Hnatiak)
- [Gennadiy Shpak](https://github.com/gyshpak)
- [Olena Polkhova](https://github.com/ElenaPolkhovaS)
- 
- 
- 

## FOR DEVS:

HERE IS FRONTEND REPO: 

HERE IS FRONTEND RENDER: 

&#xa0;
