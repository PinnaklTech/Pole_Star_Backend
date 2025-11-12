# Pole Star Backend API

FastAPI backend for Pole Star application.

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- MongoDB (local or remote)
- All dependencies from `requirements.txt`

### Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure environment variables:**
   - Copy `.env.example` to `.env` (if available)
   - Or create `.env` file with required variables

3. **Start the server:**

#### Option 1: Using Python directly (Development)
```bash
python main.py
```

#### Option 2: Using uvicorn command (Development with auto-reload)
```bash
# On Windows (PowerShell):
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# On Linux/Mac:
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### Option 3: Using startup scripts
```bash
# Windows:
.\run_dev.ps1

# Linux/Mac:
chmod +x run_dev.sh
./run_dev.sh
```

#### Option 4: Using uvicorn with custom settings
```bash
uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --log-level info
```

## 📝 Uvicorn Command Options

### Basic Command
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Development Mode (with auto-reload)
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Production Mode (with workers)
```bash
uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --log-level info
```

### Custom Configuration
```bash
uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --log-level debug \
    --access-log \
    --proxy-headers
```

## 🔧 Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Environment
ENVIRONMENT=development
DEBUG=true

# MongoDB
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=pole_wizard_forge

# JWT
JWT_SECRET=your-secret-key-here
JWT_EXPIRES_IN_DAYS=7

# Email (Hostinger SMTP)
EMAIL_HOST=smtp.hostinger.com
EMAIL_PORT=465
EMAIL_USER=noreply.polestar@pinnakltech.com
EMAIL_PASSWORD=your-password
EMAIL_FROM=noreply.polestar@pinnakltech.com

# App URLs
APP_URL=http://localhost:5173
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://localhost:8080

# Server
API_HOST=0.0.0.0
API_PORT=8000
```

## 🌐 Access the API

Once running, you can access:

- **API Root**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc (ReDoc)

## 📚 API Endpoints

### Authentication
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout user
- `GET /api/auth/me` - Get current user
- `POST /api/auth/forgot-password` - Request password reset
- `POST /api/auth/verify-code` - Verify reset code
- `POST /api/auth/reset-password` - Reset password

### Calculations
- `POST /api/calculations/calculate` - Run calculation
- `GET /api/calculations/constants` - Get constants

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find and kill process on port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:8000 | xargs kill -9
```

### MongoDB Connection Error
- Ensure MongoDB is running
- Check `MONGODB_URI` in `.env`
- Verify network access if using remote MongoDB

### Module Not Found
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

## 🚀 Production Deployment

For production deployment, see `PRODUCTION_DEPLOYMENT.md` in the root directory.

Recommended production setup:
```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn + uvicorn workers
gunicorn main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000
```

