import pytest
from fastapi.testclient import TestClient
from main import app
import os

def test_cors_middleware():
    client = TestClient(app)
    response = client.options("/", headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "GET"})
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"

    response = client.options("/", headers={"Origin": "http://malicious.com", "Access-Control-Request-Method": "GET"})
    assert response.status_code == 400 or response.headers.get("access-control-allow-origin") != "http://malicious.com"
