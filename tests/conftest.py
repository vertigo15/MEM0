"""Test configuration and fixtures for mem0 API tests."""

import pytest
import requests
import time
from typing import Dict, Any, Optional


@pytest.fixture(scope="session")
def api_base_url() -> str:
    """Base URL for the API."""
    return "http://localhost:8000"


@pytest.fixture(scope="session")
def api_client(api_base_url: str):
    """HTTP client for API requests."""
    # Wait for the API to be ready
    max_retries = 30
    for i in range(max_retries):
        try:
            response = requests.get(f"{api_base_url}/health", timeout=5)
            if response.status_code == 200:
                break
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    else:
        pytest.fail("API is not responding after 30 seconds")
    
    return requests.Session()


@pytest.fixture
def sample_memory_data() -> Dict[str, Any]:
    """Sample memory data for testing."""
    return {
        "message": "User prefers morning meetings and coffee",
        "user_id": "test_user_123",
        "metadata": {
            "category": "preferences",
            "importance": "high",
            "tags": ["meetings", "coffee"]
        }
    }


@pytest.fixture
def another_memory_data() -> Dict[str, Any]:
    """Another sample memory for testing."""
    return {
        "message": "User is working on the mem0 project using FastAPI",
        "user_id": "test_user_123",
        "metadata": {
            "category": "work",
            "project": "mem0",
            "technology": "FastAPI"
        }
    }


@pytest.fixture
def different_user_memory() -> Dict[str, Any]:
    """Memory data for a different user."""
    return {
        "message": "User loves Python programming and AI",
        "user_id": "test_user_456",
        "metadata": {
            "category": "interests",
            "skills": ["python", "ai"]
        }
    }


@pytest.fixture(autouse=True)
def cleanup_test_data(api_client, api_base_url):
    """Cleanup test data after each test."""
    yield
    
    # Cleanup: Get all memories for test users and delete them
    test_users = ["test_user_123", "test_user_456", "cleanup_user"]
    
    for user_id in test_users:
        try:
            response = api_client.get(f"{api_base_url}/memory/user/{user_id}")
            if response.status_code == 200:
                memories = response.json().get("memories", [])
                for memory in memories:
                    if "id" in memory:
                        api_client.delete(f"{api_base_url}/memory/{memory['id']}")
        except Exception:
            # Ignore cleanup errors
            pass


def assert_memory_structure(memory: Dict[str, Any]) -> None:
    """Assert that a memory object has the expected structure."""
    assert "id" in memory
    assert "message" in memory
    assert "user_id" in memory
    assert "metadata" in memory
    assert isinstance(memory["metadata"], dict)


def assert_response_success(response: requests.Response) -> None:
    """Assert that a response is successful."""
    assert response.status_code in [200, 201], f"Expected success but got {response.status_code}: {response.text}"
    assert response.headers.get("content-type", "").startswith("application/json")