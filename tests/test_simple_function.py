import pytest
from download_test_data import check_cache, download_test_data

from power_system_simulation.simple_function import add, multiply


@pytest.fixture(scope="session", autouse=True)
def ensure_test_data():
    if not check_cache():
        download_test_data(force=True)


def test_add():
    assert add(1, 1) == 2


def test_multiply():
    assert multiply(2, 2) == 4
