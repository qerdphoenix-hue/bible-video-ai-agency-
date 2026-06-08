"""Pytest configuration and fixtures"""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app


@pytest.fixture(scope="session")
def client():
    """FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def sample_bible_passage():
    """Sample Bible passage for testing"""
    return {
        "book": "John",
        "chapter": 3,
        "verses": "16-18",
        "text": "For God so loved the world that he gave his one and only Son, that whoever believes in him shall not perish but have eternal life."
    }