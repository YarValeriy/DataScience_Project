# FastAPI PhotoShare Project

This project is a FastAPI application that allows users to share photos and comments on them. It includes user authentication, photo uploading, commenting, and role-based access control.

## Features

- User registration and authentication with JWT tokens
- User roles (admin, user) with different access levels
- Rate limiting to prevent abuse
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

4. Populate database schema:

```bash
alembic upgrade head
```

5. Run the application:

```bash
python main.py
```

6. Access the API documentation at `http://localhost:8000/docs`.

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
- [Yuliia Chorna](https://github.com/YuliiaChorna1)
- [Gennadiy Shpak](https://github.com/gyshpak)
- [Andrii Demenin](https://github.com/demagoit)
- [Olena Polkhova](https://github.com/ElenaPolkhovaS)

## FOR DEVS:

HERE IS FRONTEND REPO: https://github.com/gyshpak/PhotoShare-Python-front

HERE IS FRONTEND RENDER: https://photoshare-python-front.onrender.com/

&#xa0;
