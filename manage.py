#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path


def main():
    """Run administrative tasks."""
    # Prioritize local rail-django-graphql package if present
    # try:
    #     project_root = Path(__file__).resolve().parent
    #     repo_root = project_root.parent
    #     local_pkg_path = repo_root / "rail-django-graphql"
    #     if local_pkg_path.exists():
    #         sys.path.insert(0, str(local_pkg_path))
    # except Exception:
    #     # Non-fatal: continue even if path setup fails
    #     pass
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()