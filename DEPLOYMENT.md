Deployment Guide

This boilerplate includes a production-ready deployment pack under `django-graphql-boilerplate/deploy`.

Prerequisites
- Docker and Docker Compose
- Set `.env.production` with secure values

Services
- `db`: PostgreSQL 15 with tuned configuration and init SQL
- `redis`: Redis 7 with persistence and LRU policy
 - `web`: Django app served by Daphne (ASGI)
- `nginx`: Reverse proxy and static/media hosting
- `prometheus`: Metrics collection
- `grafana`: Dashboards and provisioning
 - `backup`: Cron-based DB and media backups

Quick Start
1. Copy env: `cp django-graphql-boilerplate/deploy/.env.production.example django-graphql-boilerplate/deploy/.env.production` and set `SECRET_KEY`, `POSTGRES_PASSWORD`, `ALLOWED_HOSTS`
2. Compose up: `docker compose -f django-graphql-boilerplate/deploy/docker-compose.production.yml --env-file django-graphql-boilerplate/deploy/.env.production up -d --build`
3. Migrate: `docker compose -f django-graphql-boilerplate/deploy/docker-compose.production.yml exec web python manage.py migrate`
4. Static: `docker compose -f django-graphql-boilerplate/deploy/docker-compose.production.yml exec web python manage.py collectstatic --noinput`
5. Superuser: `docker compose -f django-graphql-boilerplate/deploy/docker-compose.production.yml exec web python manage.py createsuperuser`

Notes
- Static and media are volume-mounted and served by Nginx.
- SSL can be enabled by adding certs and exposing 443; update Nginx site config accordingly.
- Redis cache is configured via `REDIS_URL` and integrated with Django `CACHES`.
 - Postgres extensions and example role are applied by `init-db.sql`; adapt for your environment.

Backups
-------

Environment variables (set in `deploy/.env.production`):
- `DB_BACKUPS_DIR`: Directory for database dumps inside backup container (mapped to a volume).
- `MEDIA_BACKUPS_DIR`: Directory for media backups (local path in the container or host volume).
- `DB_BACKUP_CRON`: Cron schedule for DB backups (default `0 2 * * *`).
- `MEDIA_BACKUP_CRON`: Cron schedule for media backups (default `0 3 * * *`).
- `DB_BACKUP_RETENTION_DAYS`: Days to keep DB backups (default `7`).
- `MEDIA_BACKUP_TARGET`: Destination for media backups; can be a local path or remote `user@host:/path`.

Run backups manually:
- DB: `docker compose -f deploy/docker-compose.production.yml exec backup backup.sh db`
- Media: `docker compose -f deploy/docker-compose.production.yml exec backup backup.sh media`

Restore procedures:
- Restore DB: `docker compose -f deploy/docker-compose.production.yml exec backup restore_db.sh /backups/db/db-YYYYMMDD-HHMMSS.sql.gz`
- Restore media: `docker compose -f deploy/docker-compose.production.yml exec backup restore_media.sh /backups/media`

Retention policy:
- DB backups older than `DB_BACKUP_RETENTION_DAYS` are pruned automatically after each backup.