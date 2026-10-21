# Security Policy

## Scope

This repository runs the Nabec Networks Connection marketing/lead-generation
website: public pages, a contact form, and a Django admin for managing
content. **It does not process payments or handle card data** — if that
changes, this policy and the site's threat model both need to be revisited
before launch, not after.

## Reporting a vulnerability

If you find a security issue, please email **info@nabecnetworks.co.ke**
(placeholder — update once a real address exists) with details and, if
possible, steps to reproduce. Please do not open a public GitHub issue for
suspected vulnerabilities.

## What's already in place

- CSRF protection, HSTS, secure/HttpOnly/SameSite cookies, and forced HTTPS
  in production (`config/settings/prod.py`)
- A strict Content-Security-Policy and Permissions-Policy on public pages
  (`core/middleware.py`)
- Rate limiting on the contact form and a login-failure throttle on the
  admin login, both IP-based (`core/views.py`, `core/middleware.py`)
- Dependency vulnerability scanning (`pip-audit`) and static security
  analysis (`bandit`) on every push/PR, plus Django's own
  `manage.py check --deploy` checklist (`.github/workflows/ci.yml`)
- Automated dependency update PRs via Dependabot (`.github/dependabot.yml`)
- No third-party JavaScript or CDN scripts — the CSP only needs to trust
  this site's own static files

## What's explicitly NOT covered

No automated scan or checklist makes a site "unhackable," and nobody should
claim otherwise. In particular, this setup has **not** had:

- A professional penetration test or external security audit
- Any payment processing, so no PCI-DSS scope has been considered
- A Web Application Firewall (WAF) or DDoS protection beyond what Render
  provides by default
- Load testing under adversarial conditions

If this site is ever extended to handle payments, memberships, or any
sensitive personal data beyond a contact form, get a real security review
done first — don't treat this document as a substitute for one.
