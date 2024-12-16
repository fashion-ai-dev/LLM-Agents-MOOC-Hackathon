# Fullstack Application - Dockerized Setup

This repository contains two projects: a **backend** (FastAPI) and a **frontend** (React with Vite). Both are configured to run together using Docker Compose.

## Prerequisites

Before starting, ensure you have the following installed on your system:

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Getting Started

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### Step 2: Build and Run the Containers

Run the following command to build and start the backend and frontend services:

```bash
docker-compose up --build
```

### Step 3: Access the Application

- **Frontend**: [http://localhost:5173](http://localhost:5173)
- **Backend**: [http://localhost:3001](http://localhost:3001)

The ports can be adjusted in the `docker-compose.yml` file if needed.

## Project Structure

```plaintext
project-root/
│
├── backend/           # Backend application (FastAPI)
│   ├── Dockerfile     # Dockerfile for the backend
│   ├── main.py        # Main application entry point
│   └── ...
│
├── frontend/          # Frontend application (React + Vite)
│   ├── Dockerfile     # Dockerfile for the frontend
│   ├── src/           # React source files
│   └── ...
│
└── docker-compose.yml # Compose configuration for both services
```

## Environment Variables

### Backend
Environment variables for the backend are defined in the `backend/.env` file. If you don't have it, you can manually create it or use Docker Compose to define variables.

### Frontend
The frontend uses a `.env.example` file that is automatically copied to `.env` during the Docker build process. Update `frontend/.env.example` as needed.

#### Example of `frontend/.env.example`:
```env
VITE_SOCKET_URL=http://localhost:3001
```

## Stopping the Application

To stop the running containers, use:

```bash
docker-compose down
```

## Troubleshooting

1. **Port Conflicts**:
   - Ensure that ports `3001` (backend) and `5173` (frontend) are not being used by other services.
   - You can modify the `ports` section in the `docker-compose.yml` file to use different ports.

2. **Frontend Environment Issues**:
   - Ensure the `.env` file is correctly generated during the Docker build process. Verify its existence in the container:
     ```bash
     docker exec -it <frontend-container-name> cat /app/.env
     ```

3. **Rebuilding Containers**:
   - If changes are made to the source code or environment variables, rebuild the containers:
     ```bash
     docker-compose up --build
     ```

## License

This project is licensed under the [MIT License](LICENSE).
