import pytest

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    print("Setting up the test environment")