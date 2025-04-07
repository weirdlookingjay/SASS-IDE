# Online IDE Platform

A cloud-based IDE platform that allows developers to code in their browser, similar to Codeanywhere.

## Tech Stack

### Backend
- Python 3.11+
- Django 5.0+
- Django Rest Framework
- PostgreSQL
- Docker/Kubernetes for container orchestration
- JWT Authentication

### Frontend
- NextJS (TypeScript)
- TailwindCSS
- Shadcn UI Components

## Authentication Flow

### JWT Authentication

The application uses JWT (JSON Web Tokens) for secure authentication. Here's how it works:

1. **Login Process**:
   - User submits username/password to `/api/jwt/login/`
   - Server validates credentials and returns:
     - `access_token`: Short-lived JWT for API requests
     - `refresh_token`: Long-lived token for getting new access tokens

2. **Protected Routes**:
   - Frontend adds `Authorization: Bearer <access_token>` header
   - Backend validates token using `DebugJWTAuthentication`
   - Invalid/expired tokens return 401 Unauthorized

3. **Token Refresh**:
   - When access token expires, frontend uses refresh token
   - Call to `/api/jwt/token/refresh/` gets new access token
   - Failed refresh redirects to login

4. **User Data**:
   - Current user data: `GET /api/jwt/me/`
   - User details: `GET /api/jwt/users/<username>/`
   - Both require valid access token

### Security Features

- CORS enabled with proper origin checks
- Tokens stored in localStorage (consider secure cookie in production)
- Automatic token refresh handling
- Protected routes redirect to login if unauthorized

## Core Features

### 1. Workspace Management
- Create and manage development workspaces
- Git repository template selection
- VS Code browser integration
- Configurable resource allocation

### 2. Resource Classes
- Customizable compute resources
- Options include:
  - CPU cores
  - RAM allocation
  - Disk space
  - GPU resources (future)

### 3. Authentication & Authorization
- JWT-based authentication
- User management system
- Role-based access control

## Project Structure

### Backend Components

#### Core Models
```python
Workspace:
   - user (ForeignKey)
   - name
   - git_template
   - resource_class
   - created_at
   - status

ResourceClass:
   - name
   - cpu_count
   - ram_gb
   - disk_space_gb
   - gpu_count
   - price_per_hour

GitTemplate:
   - name
   - repository_url
   - description
   - language
   - is_active
```

#### API Endpoints
- `/api/auth/` - Authentication endpoints
- `/api/workspaces/` - CRUD operations for workspaces
- `/api/templates/` - Git template management
- `/api/resource-classes/` - Available resource configurations
- `/api/containers/` - Container management

## Development Environment Requirements

### System Requirements
- Windows 11 with WSL2 enabled
- Ubuntu on WSL2
- Docker Desktop with WSL2 backend
- VS Code with Remote WSL extension

### Container Technologies
- Docker Engine
- Docker Compose
- VS Code Server (for workspace containers)
- Future scaling: Kubernetes (optional)

### Container Architecture
- Language-specific base images for different programming templates
- Isolated VS Code Server containers per workspace
- Resource-constrained containers (CPU, RAM, Disk)
- Secure networking for web-IDE access

## Development Setup

### 1. WSL2 Setup
```bash
# Check WSL version and distributions
wsl --list --verbose

# If needed, set WSL2 as default
wsl --set-default-version 2
```

### 2. Docker Setup
1. Install Docker Desktop for Windows
2. Enable WSL2 backend in Docker Desktop settings
3. Verify installation:
```bash
docker --version
docker-compose --version
```

### 3. Project Setup
[Coming soon]

## Getting Started

[Coming soon]

## Deployment

[Coming soon]

## Contributing

[Coming soon]

## License

[Coming soon]
