"""
conftest.py — Fixtures compartilhadas para os testes do SPFC Champion Decision OS.
"""
import pytest
from fastapi.testclient import TestClient

from src.web.local_app import app


@pytest.fixture(scope="session")
def client():
    """TestClient do FastAPI para testes de integração das rotas web."""
    with TestClient(app) as c:
        yield c
