# BEKA Ltd — Website

Django site for **BEKA Ltd**, a Nairobi-based cloud and multi-cloud consulting
firm and a Thales Accelerate Partner (Value-Added Reseller, Managed Service
Provider and Advisory tracks) for Thales Data Protection on Demand (DPoD) and
CipherTrust.

## Pages

- **Home** — overview of services and the Thales partnership
- **About** — company background and mission
- **Services** — cloud/multi-cloud consulting, Thales data protection, managed security, advisory
- **Thales Partnership** — the three engagement models (VAR, MSP, Advisory), why DPoD fits SMEs, and the Multi-Cloud Key Protection Package
- **Packages & Pricing** — packaged SME offerings
- **Contact** — a working contact form (saved to the database + optional email notification, with spam honeypot protection)
- **Privacy Policy**

All of Services, the Thales engagement models, and Packages are editable
through the Django admin (`/admin/`) — no code changes needed to update copy
or pricing.

## Local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env      # then edit SECRET_KEY etc.

python manage.py migrate
python manage.py loaddata initial_content   # seeds services/packages/engagement models
python manage.py createsuperuser
python manage.py runserver
```

Visit http://127.0.0.1:8000/.

## Running tests

```bash
python manage.py test
```

## Settings

Settings are split under `config/settings/`:

- `base.py` — shared settings
- `dev.py` — local development (`DEBUG=True`, SQLite)
- `prod.py` — production hardening (HSTS, secure cookies, forced HTTPS,
  Postgres via `DATABASE_URL`)

Set `DJANGO_SETTINGS_MODULE=config.settings.prod` in production, along with
`SECRET_KEY`, `ALLOWED_HOSTS`, `DATABASE_URL`, and SMTP credentials for
contact-form email notifications (see `.env.example`).

## Deployment

- **Docker**: `docker build -t beka-website . && docker run -p 8000:8000 --env-file .env beka-website`
- **Procfile-based platforms** (Render, Railway, Heroku-style): the included
  `Procfile` runs migrations, collects static files, and starts Gunicorn.
- Static files are served via [WhiteNoise](https://whitenoise.readthedocs.io/),
  so no separate static file host is required.

## Content model

- `core.Service` — service line cards (Services page + homepage)
- `core.EngagementModel` — the VAR / MSP / Advisory rows on the Thales Partnership page
- `core.Package` — packaged pricing tiers on the Packages page
- `core.ContactMessage` — contact form submissions, visible and manageable in `/admin/`
