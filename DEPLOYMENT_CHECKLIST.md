# Deployment Checklist for Render

## Pre-Deployment Checklist

- [ ] All code is committed to GitHub
- [ ] `requirements.txt` is up to date
- [ ] `build.sh` is executable (`chmod +x build.sh`)
- [ ] `render.yaml` is configured
- [ ] `runtime.txt` specifies Python version
- [ ] Database configuration uses `DATABASE_URL`
- [ ] CORS configuration uses environment variables
- [ ] Model files are in `models/` directory
- [ ] Data files are in `data/` directory

## Render Setup Checklist

- [ ] Create Render account
- [ ] Connect GitHub repository
- [ ] Create PostgreSQL database
- [ ] Create web service
- [ ] Link database to web service
- [ ] Set environment variables:
  - [ ] `SECRET_KEY`
  - [ ] `ALGORITHM` = `HS256`
  - [ ] `ACCESS_TOKEN_EXPIRE_MINUTES` = `30`
  - [ ] `DEBUG` = `false`
  - [ ] `ALLOWED_ORIGINS` = your frontend URL
- [ ] Configure build command: `chmod +x build.sh && ./build.sh`
- [ ] Configure start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- [ ] Set health check path: `/health`

## Post-Deployment Verification

- [ ] Check deployment logs for errors
- [ ] Test health endpoint: `https://your-app.onrender.com/health`
- [ ] Test API endpoints
- [ ] Verify database connection
- [ ] Test model predictions
- [ ] Update frontend API URL
- [ ] Test complete user flow

## Environment Variables Summary

```bash
# Required for deployment
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=false
ALLOWED_ORIGINS=https://your-frontend.onrender.com

# Auto-configured by Render
DATABASE_URL=postgresql://user:pass@host:port/db
```

## Quick Commands

```bash
# Make build script executable
chmod +x build.sh

# Test locally
uvicorn main:app --reload

# Test database connection
python -c "from database.config import engine; print('Connected')"

# Test model loading
python -c "import joblib; model = joblib.load('models/water_quality_model.joblib')"
``` 