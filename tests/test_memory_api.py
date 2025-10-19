"""Tests for memory API endpoints."""

import pytest
import json
import sys
import os
sys.path.append(os.path.dirname(__file__))
from conftest import assert_response_success, assert_memory_structure


@pytest.mark.integration
class TestMemoryCreation:
    """Test memory creation endpoint."""
    
    def test_create_memory_success(self, api_client, api_base_url, sample_memory_data):
        """Test successful memory creation."""
        response = api_client.post(
            f"{api_base_url}/memory",
            json=sample_memory_data,
            headers={"Content-Type": "application/json"}
        )
        
        assert_response_success(response)
        result = response.json()
        
        assert "message" in result
        assert "result" in result
        assert "successfully" in result["message"].lower()
    
    def test_create_memory_without_metadata(self, api_client, api_base_url):
        """Test memory creation without metadata."""
        memory_data = {
            "message": "Simple memory without metadata",
            "user_id": "test_user_123"
        }
        
        response = api_client.post(
            f"{api_base_url}/memory",
            json=memory_data,
            headers={"Content-Type": "application/json"}
        )
        
        assert_response_success(response)
        result = response.json()
        assert "successfully" in result["message"].lower()
    
    def test_create_memory_missing_required_field(self, api_client, api_base_url):
        """Test memory creation with missing required field."""
        incomplete_data = {
            "message": "Memory without user_id"
            # Missing user_id
        }
        
        response = api_client.post(
            f"{api_base_url}/memory",
            json=incomplete_data,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_create_memory_empty_message(self, api_client, api_base_url):
        """Test memory creation with empty message."""
        empty_data = {
            "message": "",
            "user_id": "test_user_123"
        }
        
        response = api_client.post(
            f"{api_base_url}/memory",
            json=empty_data,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422  # Validation error


@pytest.mark.integration
class TestMemoryRetrieval:
    """Test memory retrieval endpoints."""
    
    def test_get_user_memories_empty(self, api_client, api_base_url):
        """Test getting memories for user with no memories."""
        response = api_client.get(f"{api_base_url}/memory/user/nonexistent_user")
        
        assert_response_success(response)
        result = response.json()
        
        assert "memories" in result
        assert "count" in result
        assert result["count"] == 0
        assert result["memories"] == []
    
    def test_get_user_memories_with_data(self, api_client, api_base_url, sample_memory_data):
        """Test getting memories for user with existing memories."""
        # First create a memory
        create_response = api_client.post(
            f"{api_base_url}/memory",
            json=sample_memory_data
        )
        assert_response_success(create_response)
        
        # Then retrieve user memories
        response = api_client.get(f"{api_base_url}/memory/user/{sample_memory_data['user_id']}")
        
        assert_response_success(response)
        result = response.json()
        
        assert "memories" in result
        assert "count" in result
        assert result["count"] >= 1
        assert len(result["memories"]) >= 1
        
        # Check memory structure
        memory = result["memories"][0]
        assert_memory_structure(memory)
        assert memory["user_id"] == sample_memory_data["user_id"]


@pytest.mark.integration
class TestMemorySearch:
    """Test memory search functionality."""
    
    def test_search_memories_empty_query(self, api_client, api_base_url):
        """Test searching with empty query."""
        response = api_client.get(
            f"{api_base_url}/memory/search",
            params={"query": "", "user_id": "test_user_123"}
        )
        
        # Should handle empty query gracefully
        assert response.status_code in [200, 400]
    
    def test_search_memories_no_results(self, api_client, api_base_url):
        """Test searching with query that returns no results."""
        response = api_client.get(
            f"{api_base_url}/memory/search",
            params={
                "query": "very_specific_nonexistent_query_12345",
                "user_id": "test_user_123"
            }
        )
        
        assert_response_success(response)
        result = response.json()
        
        assert "results" in result
        assert "count" in result
        assert result["count"] == 0
    
    def test_search_memories_with_results(self, api_client, api_base_url, sample_memory_data):
        """Test searching with query that should return results."""
        # First create a memory
        create_response = api_client.post(
            f"{api_base_url}/memory",
            json=sample_memory_data
        )
        assert_response_success(create_response)
        
        # Search for memories related to the content
        response = api_client.get(
            f"{api_base_url}/memory/search",
            params={
                "query": "coffee meetings",
                "user_id": sample_memory_data["user_id"],
                "limit": 5
            }
        )
        
        assert_response_success(response)
        result = response.json()
        
        assert "results" in result
        assert "count" in result
        assert isinstance(result["results"], list)
    
    def test_search_memories_missing_user_id(self, api_client, api_base_url):
        """Test search without user_id parameter."""
        response = api_client.get(
            f"{api_base_url}/memory/search",
            params={"query": "test"}
        )
        
        assert response.status_code == 422  # Missing required parameter
    
    def test_search_memories_with_limit(self, api_client, api_base_url, sample_memory_data, another_memory_data):
        """Test search with limit parameter."""
        # Create multiple memories
        for memory_data in [sample_memory_data, another_memory_data]:
            api_client.post(f"{api_base_url}/memory", json=memory_data)
        
        response = api_client.get(
            f"{api_base_url}/memory/search",
            params={
                "query": "user",
                "user_id": sample_memory_data["user_id"],
                "limit": 1
            }
        )
        
        assert_response_success(response)
        result = response.json()
        
        assert len(result["results"]) <= 1


@pytest.mark.integration
class TestMemoryHistory:
    """Test memory history endpoint."""
    
    def test_get_memory_history_empty(self, api_client, api_base_url):
        """Test getting history for user with no memories."""
        response = api_client.get(f"{api_base_url}/memory/history/nonexistent_user")
        
        assert_response_success(response)
        result = response.json()
        
        assert "history" in result
        assert "count" in result
        assert result["count"] == 0
    
    def test_get_memory_history_with_limit(self, api_client, api_base_url, sample_memory_data):
        """Test getting history with limit parameter."""
        # Create a memory first
        api_client.post(f"{api_base_url}/memory", json=sample_memory_data)
        
        response = api_client.get(
            f"{api_base_url}/memory/history/{sample_memory_data['user_id']}",
            params={"limit": 10}
        )
        
        assert_response_success(response)
        result = response.json()
        
        assert "history" in result
        assert "count" in result
        assert len(result["history"]) <= 10


@pytest.mark.integration
class TestMemoryLifecycle:
    """Test complete memory lifecycle operations."""
    
    def test_memory_crud_lifecycle(self, api_client, api_base_url, sample_memory_data):
        """Test Create, Read, Update, Delete lifecycle."""
        user_id = sample_memory_data["user_id"]
        
        # 1. Create memory
        create_response = api_client.post(
            f"{api_base_url}/memory",
            json=sample_memory_data
        )
        assert_response_success(create_response)
        
        # 2. Get all user memories to find the created memory
        get_response = api_client.get(f"{api_base_url}/memory/user/{user_id}")
        assert_response_success(get_response)
        
        memories = get_response.json()["memories"]
        assert len(memories) >= 1
        
        created_memory = memories[0]  # Get first memory
        memory_id = created_memory["id"]
        
        # 3. Get specific memory by ID
        get_by_id_response = api_client.get(f"{api_base_url}/memory/{memory_id}")
        assert_response_success(get_by_id_response)
        
        retrieved_memory = get_by_id_response.json()["memory"]
        assert retrieved_memory["id"] == memory_id
        
        # 4. Update memory
        update_data = {
            "message": "Updated memory message",
            "metadata": {"updated": True}
        }
        update_response = api_client.put(
            f"{api_base_url}/memory/{memory_id}",
            json=update_data
        )
        assert_response_success(update_response)
        
        # 5. Delete memory
        delete_response = api_client.delete(f"{api_base_url}/memory/{memory_id}")
        assert_response_success(delete_response)
        
        # 6. Verify deletion
        get_deleted_response = api_client.get(f"{api_base_url}/memory/{memory_id}")
        assert get_deleted_response.status_code == 404
    
    def test_update_nonexistent_memory(self, api_client, api_base_url):
        """Test updating a memory that doesn't exist."""
        fake_memory_id = "nonexistent_memory_id_12345"
        update_data = {"message": "Updated message"}
        
        response = api_client.put(
            f"{api_base_url}/memory/{fake_memory_id}",
            json=update_data
        )
        
        # Should return 404 or 500 depending on implementation
        assert response.status_code in [404, 500]
    
    def test_delete_nonexistent_memory(self, api_client, api_base_url):
        """Test deleting a memory that doesn't exist."""
        fake_memory_id = "nonexistent_memory_id_12345"
        
        response = api_client.delete(f"{api_base_url}/memory/{fake_memory_id}")
        
        # Should handle gracefully
        assert response.status_code in [200, 404, 500]


@pytest.mark.integration
class TestMultiUserMemories:
    """Test memory isolation between users."""
    
    def test_user_memory_isolation(self, api_client, api_base_url, sample_memory_data, different_user_memory):
        """Test that users can only see their own memories."""
        # Create memories for different users
        api_client.post(f"{api_base_url}/memory", json=sample_memory_data)
        api_client.post(f"{api_base_url}/memory", json=different_user_memory)
        
        # Get memories for first user
        user1_response = api_client.get(
            f"{api_base_url}/memory/user/{sample_memory_data['user_id']}"
        )
        assert_response_success(user1_response)
        user1_memories = user1_response.json()["memories"]
        
        # Get memories for second user
        user2_response = api_client.get(
            f"{api_base_url}/memory/user/{different_user_memory['user_id']}"
        )
        assert_response_success(user2_response)
        user2_memories = user2_response.json()["memories"]
        
        # Verify isolation - users should only see their own memories
        for memory in user1_memories:
            assert memory["user_id"] == sample_memory_data["user_id"]
        
        for memory in user2_memories:
            assert memory["user_id"] == different_user_memory["user_id"]
    
    def test_search_user_isolation(self, api_client, api_base_url, sample_memory_data, different_user_memory):
        """Test that search results are isolated by user."""
        # Create memories for different users
        api_client.post(f"{api_base_url}/memory", json=sample_memory_data)
        api_client.post(f"{api_base_url}/memory", json=different_user_memory)
        
        # Search for user 1
        search_response = api_client.get(
            f"{api_base_url}/memory/search",
            params={
                "query": "user",
                "user_id": sample_memory_data["user_id"]
            }
        )
        assert_response_success(search_response)
        
        results = search_response.json()["results"]
        # All results should belong to the queried user
        for result in results:
            if "user_id" in result:
                assert result["user_id"] == sample_memory_data["user_id"]