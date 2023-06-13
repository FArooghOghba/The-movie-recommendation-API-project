"""
Test custom Django management commands.
"""

from unittest.mock import patch, MagicMock

from django.core.management import call_command
from django.db.utils import OperationalError

from psycopg2 import OperationalError as Psycopg2Error


@patch(
    'movie_recommendation_api.common.management.commands.wait_for_db.Command.check'
)
class TestWaitForDBCommand:
    """Test commands."""

    def test_wait_for_db_command_is_ready(
            self, patched_check: MagicMock, time_tracker
    ) -> None:
        """Test waiting for database if database is ready."""

        patched_check.return_value = True
        call_command('wait_for_db')

        patched_check.assert_called_once_with(databases=['default'])

    @patch('time.sleep')
    def test_wait_for_db_command_has_delay(
            self, patched_sleep, patched_check: MagicMock, time_tracker
    ) -> None:
        """
        Test waiting for database is ready after 6 called with OperationalError.
        :param patched_sleep: mocking time sleep
        :param patched_check: mocking check
        :return: None
        """

        patched_check.side_effect = [Psycopg2Error] * 2 + \
                                    [OperationalError] * 3 + \
                                    [True]

        call_command('wait_for_db')

        assert patched_check.call_count == 6
        patched_check.assert_called_with(databases=['default'])
