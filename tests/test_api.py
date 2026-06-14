"""
tests/test_api.py
4 required PyTest functions for the Sentiment Analysis API.
Set BASE_URL via environment variable or defaults to localhost:5000.
"""

import os
import pytest
import requests

BASE_URL = os.environ.get("BASE_URL", "http://localhost:5000")


def test_health_endpoint():
    """GET /health -> HTTP 200; 'status':'healthy' and key 'model_version' present."""
    resp = requests.get(f"{BASE_URL}/health", timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    data = resp.json()
    assert data.get("status") == "healthy", f"Expected status=healthy, got: {data}"
    assert "model_version" in data, f"'model_version' key missing from response: {data}"


def test_predict_returns_label_and_confidence():
    """POST /predict -> HTTP 200; label in [POSITIVE, NEGATIVE]; 0<=confidence<=1; 'model_version' present."""
    payload = {"text": "The food was absolutely delicious and the chef clearly has exceptional skill"}
    resp = requests.post(f"{BASE_URL}/predict", json=payload, timeout=30)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    data = resp.json()
    assert data.get("label") in ("POSITIVE", "NEGATIVE"), \
        f"label must be POSITIVE or NEGATIVE, got: {data.get('label')}"
    confidence = data.get("confidence")
    assert confidence is not None, "'confidence' key missing from response"
    assert 0.0 <= confidence <= 1.0, f"confidence out of range [0,1]: {confidence}"
    assert "model_version" in data, f"'model_version' key missing from response: {data}"


def test_predict_negative_text():
    """POST /predict with negative text -> HTTP 200."""
    payload = {"text": "This is terrible, I hate it and it was the worst experience ever"}
    resp = requests.post(f"{BASE_URL}/predict", json=payload, timeout=30)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"


def test_health_returns_model_version_unstable():
    """GET /health -> model_version == 'unstable-v1' exactly."""
    resp = requests.get(f"{BASE_URL}/health", timeout=10)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    data = resp.json()
    assert data.get("model_version") == "unstable-v1", \
        f"Expected model_version='unstable-v1', got: {data.get('model_version')}"
