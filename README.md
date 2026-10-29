# Nabec Networks Connection — Website

Django site for **Nabec Networks Connection**, a Nairobi-based cloud and
multi-cloud consulting business (registered business name, owner Catherine
Chemtai Naibei; Business No. BN-79S6KEBZ). The site also documents vendor
partnerships Nabec Networks Connection is working to establish (currently
Thales and eMudhra) — **none of these partnerships are formalized yet**; the
site labels them explicitly as planned/not-yet-formalized and this must stay
accurate as the business develops. Only flip a `Partner`'s `status` to
`active` in the admin once there is an actual signed, certified or contracted
relationship with that vendor.

## Pages

- **Home** — overview of services and planned partnerships
- **About** — company background and mission
- **Services** — cloud/multi-cloud consulting, data protection, managed security, advisory
- **Partnerships** — a hub listing each vendor Nabec Networks Connection is pursuing a partnership with, plus a detail page per vendor (engagement models, benefits, packages) that clearly flags "not yet formalized" status until it's real
- **Packages & Pricing** — packaged SME offerings across all vendors
- **Contact** — a working contact form (saved to the database + optional email notification, with spam honeypot protection)
- **Privacy Policy**

Services, Partners (with their benefits, engagement models) and Packages are
all editable through the Django admin (`/admin/`) — no code changes needed to
update copy, pricing, or a partner's status once a relationship becomes real.

## Local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env      # then edit SECRET_KEY etc.

python manage.py migrate        # also inserts the starter content (services, partners, packages)
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
contact-form email notifications (see `.env.example`). Optionally set
`ADMIN_URL` to something other than `admin` to cut down on automated bot
traffic against the login page.

## Security

See [SECURITY.md](./SECURITY.md) for the full picture, including what this
setup explicitly does **not** cover. Short version: this is a single
Django application (not microservices — a well-secured monolith is the
right call at this scale), currently scoped to a public marketing site and
a contact form, with no payment processing. It follows standard Django/OWASP
hardening (CSRF, HSTS, secure/HttpOnly/SameSite cookies, a strict
Content-Security-Policy, admin login throttling, contact-form rate
limiting) and is scanned on every push with `bandit` (static analysis),
`pip-audit` (dependency CVEs) and Django's own `manage.py check --deploy`.
None of that adds up to "unhackable" — if this site ever takes on payments
or other sensitive functionality, get a real security review first.

## Deployment

Static files are served via [WhiteNoise](https://whitenoise.readthedocs.io/),
so no separate static file host is required in any of the options below.

### Free hosting: Render (web app) + Neon (database)

This is the recommended free path — no credit card, and the database doesn't
expire like Render's own free Postgres does (30 days). You do need to create
both accounts yourself; nobody else can do that step for you.

1. **Create a free Postgres database on [Neon](https://neon.tech)** (sign up
   with GitHub/Google, no card needed). Create a project, then copy its
   connection string (starts with `postgres://...`) — you'll need it in step 3.
2. **Create a free account on [Render](https://render.com)** and connect your
   GitHub account so it can see the `cskimaru/KimTech` repo.
3. In Render, choose **New → Blueprint**, point it at this repo — it will read
   `render.yaml` and set up the web service automatically. When prompted for
   the env vars marked "set during deploy", fill in:
   - `ALLOWED_HOSTS` — your Render URL once assigned, e.g. `nabec-networks-connection.onrender.com` (comma-separate if you add a custom domain later)
   - `CSRF_TRUSTED_ORIGINS` — `https://nabec-networks-connection.onrender.com` (same, with `https://`)
   - `DATABASE_URL` — the Neon connection string from step 1
   - `CONTACT_NOTIFY_EMAIL`, and the `EMAIL_*` vars if you want contact-form
     email notifications (leave blank to skip email; submissions are always
     saved to the database and visible in `/admin/` either way)
   `SECRET_KEY` is generated for you automatically.
4. Render builds and deploys automatically on every push to `main`. The free plan
   has no Shell, so the admin account is created on start-up instead: in the service's
   **Environment**, add `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_EMAIL` and
   `DJANGO_SUPERUSER_PASSWORD`, save (it redeploys), sign in at `/admin/`, then delete
   `DJANGO_SUPERUSER_PASSWORD`. `manage.py ensure_admin` only acts when no admin exists,
   so it never changes an existing account.
5. **Known limitation of the free tier**: the site "sleeps" after 15 minutes
   with no traffic, so the first visitor after a quiet spell waits ~30–60
   seconds for it to wake up. That's a Render free-tier trade-off, not a bug.

### Docker (any host that runs containers)

```bash
docker build -t nabec-networks-website .
docker run -p 8000:8000 --env-file .env nabec-networks-website
```

### Any other Procfile-based platform

The included `Procfile` runs migrations, collects static files, and starts
Gunicorn — works on Railway, Heroku-style platforms, etc.

## Content model

The starter content lives in `core/fixtures/initial_content.json`. Migration
`0003_seed_starter_content` inserts any of it that's missing on `migrate`, so a fresh
deploy shows a complete site; it never changes rows that already exist or were edited
in the admin.

Services and packages have a **category**: *Get online* (domains, business email,
websites, memorial websites, cloud backup, email & SMS campaigns) or *Cloud & data
protection*. The home, Services and Packages pages show each group separately. The
WhatsApp chat button uses `COMPANY_WHATSAPP` (international format without "+",
default `254702857036`).

- `core.Service` — service line cards (Services page + homepage)
- `core.Partner` — a vendor (e.g. Thales, eMudhra), with a `status` of
  `planned` (not yet formalized — the default, and the honest state until a
  real agreement exists) or `active` (certified/contracted)
- `core.PartnerBenefit` — "why this fits our clients" bullets per partner
- `core.EngagementModel` — the VAR / MSP / Advisory rows on a partner's page
- `core.Package` — packaged pricing tiers on the Packages page, optionally tied to a partner
- `core.ContactMessage` — contact form submissions, visible and manageable in `/admin/`
