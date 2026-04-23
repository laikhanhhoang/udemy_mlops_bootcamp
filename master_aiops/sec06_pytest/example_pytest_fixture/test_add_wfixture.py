import pytest
from add import add

@pytest.fixture
def setup_environment():
    return {"a":3, "b":4}

def test_add(setup_environment):
    assert add(**setup_environment) == 7
    # Chạy ổnd