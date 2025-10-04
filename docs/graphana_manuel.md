# Grafana Container Manual

## Purpose
- Explain how to run, configure, and use the Grafana container included in this project.
- Provide actionable steps to provision datasources, load dashboards, set alerts, and operate Grafana in production.

## Prerequisites
- Docker and Docker Compose installed.
- This repository cloned locally.
- Containers built and running using the project’s compose files.

## Service Overview
- Image: `grafana/grafana:latest`
- Port: `3000` (exposed as `http://localhost:3000/`)
- Provisioning via mounted volumes:
  - Datasources: `django-graphql-boilerplate/deploy/monitoring/grafana/datasources/`
  - Dashboards providers: `django-graphql-boilerplate/deploy/monitoring/grafana/dashboards/`
  - Dashboard JSONs: `django-graphql-boilerplate/deploy/monitoring/grafana/json/`
- Persistent data volume: `grafana_data` mounted at `/var/lib/grafana`.

## Start and Access
- Start (from repository root or project folder):
  - `docker compose -f django-graphql-boilerplate/deploy/docker-compose.production.yml up -d --build`
- Check logs:
  - `docker compose -f django-graphql-boilerplate/deploy/docker-compose.production.yml logs -f grafana`
- Access UI:
  - `http://localhost:3000/`
- Default credentials:
  - `admin` / `admin` (you will be prompted to change the password on first login).

## Provisioning Layout
- Datasource config file:
  - `django-graphql-boilerplate/deploy/monitoring/grafana/datasources/datasource.yml`
  - Preconfigures a Prometheus datasource at `http://prometheus:9090`.
- Dashboards provider file:
  - `django-graphql-boilerplate/deploy/monitoring/grafana/dashboards/dashboards.yml`
  - Points Grafana to load dashboards from `/var/lib/grafana/dashboards` (mounted from repo `json` folder).
- Example dashboard JSON:
  - `django-graphql-boilerplate/deploy/monitoring/grafana/json/health.json`

## Prometheus Datasource
- Prometheus runs as a sibling container; configuration file:
  - `django-graphql-boilerplate/deploy/monitoring/prometheus/prometheus.yml`
- Typical scrape targets include `nginx:80` or your app endpoints exporting metrics.
- Verify Prometheus:
  - `http://localhost:9090/`
- Verify Grafana datasource:
  - In Grafana UI → `Configuration` → `Data sources` → `Prometheus` → `Save & test`.

## Adding New Datasources
- Add a new file under `django-graphql-boilerplate/deploy/monitoring/grafana/datasources/` (e.g., `loki.yml`).
- Example Loki datasource:
  - `apiVersion: 1`
  - `datasources:`
  - `  - name: Loki`
  - `    type: loki`
  - `    access: proxy`
  - `    url: http://loki:3100`
- Restart Grafana to apply changes:
  - `docker compose -f django-graphql-boilerplate/deploy/docker-compose.production.yml restart grafana`

## Dashboards: Create, Import, Persist
- Create in UI:
  - `Dashboards` → `New` → `New dashboard` → Add panel → Select `Prometheus` → Write PromQL.
- Import a JSON:
  - `Dashboards` → `Import` → Upload `health.json` or paste JSON.
- Persist custom dashboards:
  - Export from UI → Save JSON into `django-graphql-boilerplate/deploy/monitoring/grafana/json/`.
  - Ensure `dashboards.yml` provider points to `/var/lib/grafana/dashboards`.
- Example `dashboards.yml` content:
  - `apiVersion: 1`
  - `providers:`
  - `  - name: 'App Dashboards'`
  - `    orgId: 1`
  - `    folder: 'Application'`
  - `    type: file`
  - `    disableDeletion: false`
  - `    updateIntervalSeconds: 30`
  - `    options:`
  - `      path: /var/lib/grafana/dashboards`

## Example Panels and PromQL
- Error Rate (5xx responses over 5 minutes):
  - `rate(http_requests_total{status=~"5.."}[5m])`
- Request Rate by method:
  - `sum by (method)(rate(http_requests_total[1m]))`
- Latency (95th percentile if histogram present):
  - `histogram_quantile(0.95, sum by (le)(rate(http_request_duration_seconds_bucket[5m])))`

## Alerting (Grafana Unified Alerting)
- Configure contact points:
  - Grafana UI → `Alerting` → `Contact points` (email, Slack, webhook).
- Create alert rules:
  - Grafana UI → `Alerting` → `Alert rules` → New rule.
- Rule examples:
  - High error rate: `rate(http_requests_total{status=~"5.."}[5m]) > 0`
  - Slow requests: `histogram_quantile(0.95, sum by (le)(rate(http_request_duration_seconds_bucket[5m]))) > 0.8`
- Persistence (optional):
  - Use Grafana provisioning for alerting or store definitions in code via Grafana API.

## Operations and Maintenance
- Restart Grafana:
  - `docker compose -f django-graphql-boilerplate/deploy/docker-compose.production.yml restart grafana`
- Rebuild all services:
  - `docker compose -f django-graphql-boilerplate/deploy/docker-compose.production.yml up -d --build`
- Tail logs:
  - `docker compose -f django-graphql-boilerplate/deploy/docker-compose.production.yml logs -f grafana`

## Backup and Restore
- Backup persistent data volume `grafana_data`:
  - `docker run --rm -v grafana_data:/data -v "$PWD":/backup alpine tar czf /backup/grafana_data.tar.gz /data`
- Restore:
  - `docker run --rm -v grafana_data:/data -v "$PWD":/backup alpine sh -lc 'cd / && tar xzf /backup/grafana_data.tar.gz'`

## Security Hardening
- Change the default admin password immediately.
- Optionally set `GF_SECURITY_ADMIN_PASSWORD` via environment variables in compose.
- Restrict exposure (bind to internal networks, or enforce auth at reverse proxy).
- Enable SSO/OAuth: Configure `GF_AUTH_*` settings (Google, GitHub, Azure AD) as needed.

## Troubleshooting
- Grafana UI shows no dashboards:
  - Verify `dashboards.yml` points to `/var/lib/grafana/dashboards`.
  - Confirm JSON validity; try importing via UI.
- Prometheus datasource fails `Save & test`:
  - Check Prometheus container health; ensure `prometheus:9090` is reachable from Grafana network.
- Prometheus has no metrics:
  - Review `prometheus.yml` scrape configs; ensure targets are correct and metrics exposed.
- Volume permission issues on Windows:
  - Confirm paths in compose exist and are accessible; run PowerShell as admin if needed.

## Advanced: Automating Dashboard Provisioning
- Store canonical dashboards as JSON in `json/` folder and track via version control.
- Use folders in Grafana (e.g., `Application`, `Infrastructure`, `Database`) for organization.
- Add labels or variables (service, environment) to panels for flexible filtering.

## References
- Compose: `django-graphql-boilerplate/deploy/docker-compose.production.yml`
- Datasource: `django-graphql-boilerplate/deploy/monitoring/grafana/datasources/datasource.yml`
- Dashboards provider: `django-graphql-boilerplate/deploy/monitoring/grafana/dashboards/dashboards.yml`
- Dashboard JSONs: `django-graphql-boilerplate/deploy/monitoring/grafana/json/`
- Prometheus: `django-graphql-boilerplate/deploy/monitoring/prometheus/prometheus.yml`

## Quick Checklist
- Start stack and access `http://localhost:3000/`.
- Change admin password.
- Verify Prometheus datasource (`Save & test`).
- Import `health.json`, validate panels.
- Add alert rules for errors and latency.
- Back up `grafana_data` regularly.