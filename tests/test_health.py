"""Tests for health endpoint."""

import pytest
import sys
import os
sys.path.append(os.path.dirname(__file__))
from conftest import assert_response_success


@pytest.mark.unit
def test_health_endpoint_returns_200(api_client, api_base_url):
    """Test that health endpoint returns 200 status."""
    response = api_client.get(f"{api_base_url}/health")
    assert response.status_code == 200


@pytest.mark.unit
def test_health_endpoint_structure(api_client, api_base_url):
    """Test that health endpoint returns expected structure."""
    response = api_client.get(f"{api_base_url}/health")
    assert_response_success(response)
    
    health_data = response.json()
    
    # Check required fields
    assert "status" in health_data
    assert "version" in health_data
    assert "database" in health_data
    assert "llm_provider" in health_data
    assert "storage_provider" in health_data
    
    # Check values
    assert health_data["status"] == "healthy"
    assert health_data["version"] == "1.0.0"
    assert health_data["database"] == "qdrant"
    assert health_data["llm_provider"] == "azure_openai"
    assert health_data["storage_provider"] == "azure_blob"


@pytest.mark.unit
def test_health_endpoint_content_type(api_client, api_base_url):
    """Test that health endpoint returns JSON content type."""
    response = api_client.get(f"{api_base_url}/health")
    assert response.headers.get("content-type", "").startswith("application/json")