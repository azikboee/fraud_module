# tests/conftest.py
import pytest
import sys
import os
from pathlib import Path

# Добавляем корень проекта в Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture
def sample_transaction():
    return {
        "amount": 50000,
        "user_id": "test_user_123"
    }