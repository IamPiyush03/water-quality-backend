# Water Quality Backend Deployment Guide for Render

This guide will help you deploy your Water Quality Backend with PostgreSQL on Render.

## Prerequisites

1. A GitHub account with your code repository
2. A Render account (free tier available)
3. Your backend code pushed to GitHub

## Step 1: Prepare Your Repository

1. **Ensure all files are committed to GitHub:**
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Verify these files exist in your repository:**
   - `requirements.txt`
   - `main.py`
   - `build.sh`
   - `render.yaml`
   - `runtime.txt`
   - `database/config.py`
   - `models/` directory (with your trained model)
   - `data/` directory (with your data files)

## Step 2: Create Render Account and Connect Repository

1. Go to [render.com](https://render.com) and sign up
2. Click "New +" and select "Blueprint"
3. Connect your GitHub account and select your repository
4. Render will automatically detect the `render.yaml` file

## Step 3: Configure Environment Variables

After creating the service, go to the Environment tab and add these variables:

### Required Environment Variables:
- `SECRET_KEY`: A secure random string (Render can generate this)
- `ALGORITHM`: `HS256`
- `ACCESS_TOKEN_EXPIRE_MINUTES`: `30`
- `DEBUG`: `false`
- `ALLOWED_ORIGINS`: Your frontend URL (e.g., `https://your-frontend.onrender.com`)

### Database Variables (Auto-configured by Render):
- `DATABASE_URL`: Automatically set by Render when you create a PostgreSQL database

## Step 4: Deploy the Application

1. **Using Blueprint (Recommended):**
   - Render will automatically create both the web service and PostgreSQL database
   - Click "Apply" to start the deployment

2. **Manual Deployment:**
   - Create a PostgreSQL database first
   - Create a web service
   - Link the database to the web service

## Step 5: Configure Build and Start Commands

### Build Command:
```bash
chmod +x build.sh && ./build.sh
```

### Start Command:
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

## Step 6: Health Check Configuration

- **Health Check Path:** `/health`
- **Health Check Timeout:** 180 seconds

## Step 7: Database Setup

The `build.sh` script will:
1. Install Python dependencies
2. Create necessary directories
3. Train the model if not present
4. Initialize the database
5. Seed initial data

## Step 8: Verify Deployment

1. **Check the deployment logs** in Render dashboard
2. **Test the health endpoint:** `https://your-app.onrender.com/health`
3. **Test the API endpoints** using your frontend or tools like Postman

## Step 9: Update Frontend Configuration

Update your frontend's API configuration to point to your new Render backend URL:

```typescript
// In your frontend API configuration
const API_BASE_URL = 'https://your-backend.onrender.com';
```

## Troubleshooting

### Common Issues:

1. **Build Failures:**
   - Check the build logs in Render dashboard
   - Ensure all dependencies are in `requirements.txt`
   - Verify Python version compatibility

2. **Database Connection Issues:**
   - Ensure `DATABASE_URL` is properly set
   - Check if the database is created and accessible
   - Verify the database initialization script runs successfully

3. **Model Loading Issues:**
   - Ensure model files are in the `models/` directory
   - Check if training data is available in `data/` directory
   - Verify the model training script works

4. **CORS Issues:**
   - Update `ALLOWED_ORIGINS` with your frontend URL
   - Check the CORS configuration in `main.py`

### Useful Commands:

```bash
# Check application logs
# Use Render dashboard or CLI

# Test database connection locally
python -c "from database.config import engine; print('Database connected')"

# Test model loading
python -c "import joblib; model = joblib.load('models/water_quality_model.joblib')"
```

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:port/db` |
| `SECRET_KEY` | JWT secret key | `your-secret-key-here` |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | `30` |
| `DEBUG` | Debug mode | `false` |
| `ALLOWED_ORIGINS` | CORS allowed origins | `https://your-frontend.onrender.com` |

## Cost Considerations

- **Free Tier:** 750 hours/month for web services, 90 days for PostgreSQL
- **Paid Plans:** Start at $7/month for web services, $7/month for PostgreSQL
- **Auto-sleep:** Free tier services sleep after 15 minutes of inactivity

## Security Best Practices

1. **Never commit sensitive data** to your repository
2. **Use environment variables** for all secrets
3. **Enable HTTPS** (automatic on Render)
4. **Regularly update dependencies**
5. **Monitor application logs** for security issues

## Support

- Render Documentation: [docs.render.com](https://docs.render.com)
- Render Community: [community.render.com](https://community.render.com)
- FastAPI Documentation: [fastapi.tiangolo.com](https://fastapi.tiangolo.com) 