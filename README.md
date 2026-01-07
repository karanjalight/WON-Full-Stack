# Travil Django Application

## Setup Complete! ✓

Your landing page has been successfully configured with Django. The external assets from the `assets/` folder are now properly integrated.

## What Was Done:

1. **Settings Configuration** (`won/settings.py`):
   - Configured `STATICFILES_DIRS` to point to the external `assets/` folder
   - Set up proper templates directory
   - Configured static and media files handling

2. **Landing Page** (`templates/frontend/index.html`):
   - Created from `index-2.html`
   - All asset references converted to Django `{% static %}` template tags
   - Copied `style.css` to the assets folder

3. **Views** (`core/views.py`):
   - Created `index` view to render the landing page

4. **URLs** (`won/urls.py`):
   - Configured root URL (`/`) to display the landing page
   - Set up static files serving for development
   - Admin panel still accessible at `/admin/`

## How to Run:

### 1. Activate Virtual Environment (if using one):
```bash
cd "/home/dev-karanja/Downloads/themeforest-v9559Uwq-travil-travel-tour-booking-html-template (2)/travil-html"
source venv/bin/activate
```

### 2. Navigate to Django Project:
```bash
cd won-fullstack
```

### 3. Run Development Server:
```bash
python3 manage.py runserver
```

### 4. Access Your Site:
Open your browser and visit: **http://127.0.0.1:8000/**

## Important Notes:

- All CSS, JavaScript, images, and fonts from the `assets/` folder are now accessible
- The landing page uses Django template tags for all static files
- Static files are served automatically in DEBUG mode
- For production, you'll need to run `python3 manage.py collectstatic`

## Project Structure:
```
travil-html/
├── assets/              # External assets (CSS, JS, images, fonts)
│   ├── css/
│   ├── js/
│   ├── img/
│   └── fonts/
└── won-fullstack/       # Django project
    ├── core/            # Main app
    ├── templates/       # HTML templates
    │   └── frontend/
    │       └── index.html  # Landing page
    ├── won/             # Django settings
    └── manage.py
```

## Troubleshooting:

If static files don't load:
1. Ensure the assets folder exists at the correct path
2. Check that DEBUG = True in settings.py
3. Verify STATICFILES_DIRS points to the correct location

Enjoy your Django-powered Travil website! 🚀















