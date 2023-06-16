from datetime import datetime

from rest_framework.test import APIClient

import pytest


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def time_tracker():
    tick = datetime.now()
    yield

    tock = datetime.now()
    diff = tock - tick
    print(f'\n runtime: {diff.total_seconds()}')
