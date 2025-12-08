# Vercel Deployment Guide for InstaForms

## Quick Setup

### 1. Install Vercel CLI (Optional)
```bash
npm i -g vercel
```

### 2. Environment Variables

Add these environment variables in your Vercel project settings:

**Required:**
- `SECRET_KEY` - Your Django secret key
- `DEBUG` - Set to `False` for production
- `ALLOWED_HOSTS` - Your Vercel domain (e.g., `your-project.vercel.app`)

**Example:**
```
SECRET_KEY=your-super-secret-key-here-change-this
DEBUG=False
ALLOWED_HOSTS=.vercel.app
```

### 3. Database Configuration

**Option A: SQLite (Development/Small Projects)**
- SQLite works on Vercel but data will be lost on each deployment
- Good for testing, not recommended for production

**Option B: External PostgreSQL (Recommended)**

Popular options:
- **Neon** (https://neon.tech) - Free tier available
- **Supabase** (https://supabase.com) - Free tier available
- **Railway** (https://railway.app) - $5/month
- **AWS RDS** - Production grade

Add these environment variables for PostgreSQL:
```
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

### 4. Settings Update

Update `instaforms/settings.py` for Vercel:

```python
import os
from decouple import config
import dj_database_url  # pip install dj-database-url

# SECURITY
SECRET_KEY = config('SECRET_KEY', default='django-insecure-dev-key')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='.vercel.app').split(',')

# Database
if config('DATABASE_URL', default=None):
    DATABASES = {
        'default': dj_database_url.config(
            default=config('DATABASE_URL'),
            conn_max_age=600
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': '/tmp/db.sqlite3',  # Use /tmp for Vercel
        }
    }

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### 5. Deploy

**Option A: Via GitHub (Recommended)**
1. Push your code to GitHub
2. Import project in Vercel dashboard
3. Add environment variables
4. Deploy

**Option B: Via CLI**
```bash
vercel
```

### 6. Run Migrations

After first deployment, run migrations:

**If using external database:**
```bash
# Locally with DATABASE_URL pointing to production DB
python manage.py migrate
python manage.py createsuperuser
```

**Note:** Vercel doesn't support running migrations automatically. Use one of:
- Run migrations locally against production database
- Use a management command in your Django admin
- Use a separate deployment hook service

## Important Notes

### Limitations on Vercel

1. **No persistent filesystem** - Files uploaded will be lost on next deployment
2. **No background tasks** - Celery/Redis won't work (use external services)
3. **Cold starts** - First request after inactivity may be slow
4. **10-second timeout** - Requests must complete within 10 seconds
5. **Size limits** - Lambda function size limited to 50MB

### What Was Removed

The following packages were removed from requirements.txt for Vercel compatibility:

- `pillow` - Requires system libraries (use external image processing service)
- `celery` - Requires persistent workers (use external job queue)
- `redis` - Requires persistent server (use external Redis service)
- `psycopg2-binary` - Only needed if using PostgreSQL

### Recommended Alternatives

For removed functionality:

1. **Image Processing (pillow):**
   - Cloudinary (https://cloudinary.com)
   - Imgix (https://imgix.com)
   - AWS S3 + Lambda

2. **Background Tasks (celery):**
   - Vercel Cron Jobs
   - AWS Lambda
   - Google Cloud Functions
   - Inngest (https://inngest.com)

3. **Caching (redis):**
   - Upstash Redis (https://upstash.com)
   - Redis Labs
   - Vercel KV (https://vercel.com/docs/storage/vercel-kv)

## Testing Locally

Before deploying:

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Test the server
python manage.py runserver
```

## Troubleshooting

### Build Fails
- Check Python version matches (3.12)
- Verify all dependencies are in requirements.txt
- Check Vercel build logs for specific errors

### Database Connection Issues
- Verify DATABASE_URL is correct
- Check database allows external connections
- Ensure IP whitelist includes Vercel IPs (or allow all)

### Static Files Not Loading
- Run `python manage.py collectstatic`
- Verify STATIC_ROOT and STATICFILES_STORAGE settings
- Check Whitenoise is installed

### API Endpoints Return 404
- Check `vercel.json` routes configuration
- Verify WSGI application path
- Check ALLOWED_HOSTS includes your Vercel domain

## Production Checklist

- [ ] Set DEBUG=False
- [ ] Use strong SECRET_KEY
- [ ] Configure external database
- [ ] Set up CORS origins
- [ ] Configure ALLOWED_HOSTS
- [ ] Enable HTTPS only
- [ ] Set up error monitoring (Sentry)
- [ ] Configure external file storage (if needed)
- [ ] Set up proper backup strategy
- [ ] Configure rate limiting
- [ ] Review security settings

## Alternative Deployment Options

If Vercel limitations are too restrictive, consider:

1. **Railway** - Better for traditional Django apps
2. **Render** - Good Django support, free tier
3. **DigitalOcean App Platform** - Full Django support
4. **Heroku** - Classic platform (paid only now)
5. **AWS Elastic Beanstalk** - Full control
6. **Google Cloud Run** - Container-based

## Support

For deployment issues:
- Vercel Docs: https://vercel.com/docs
- Django Deployment: https://docs.djangoproject.com/en/4.2/howto/deployment/

