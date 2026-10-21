import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.repository import DocumentRepository


@pytest.fixture
def client() -> TestClient:
    """Ứng dụng mới với kho rỗng cho từng test."""
    return TestClient(create_app(repository=DocumentRepository()))
