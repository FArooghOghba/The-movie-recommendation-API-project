"""
Django command to wait for database to be available.
"""

import time
from typing import Any

from django.db.utils import OperationalError
from django.core.management.base import BaseCommand

from psycopg2 import OperationalError as Psycopg2Error


class Command(BaseCommand):
    """Django command to wait for database."""

    def handle(self, *args: Any, **options: Any) -> None:
        """Entrypoint for command."""

        self.stdout.write('Waiting for database...')
        db_available = False

        while db_available is False:
            try:
                self.check(databases=['default'])
                db_available = True
            except (OperationalError, Psycopg2Error):
                self.stdout.write('Database unavailable, waiting 1 second...')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Database available!'))
