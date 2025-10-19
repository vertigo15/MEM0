"""Tests for error handling and edge cases."""

import pytest
import json


@pytest.mark.unit
class TestErrorHandling:
    """Test API error handling."""
    
    def test_invalid_json_payload(self, api_client, api_base_url):
        """Test API response to invalid JSON."""
        response = api_client.post(
            f"{api_base_url}/memory",
            data="invalid json content",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_invalid_content_type(self, api_client, api_base_url):
        """Test API response to invalid content type."""
        valid_data = {
            "message": "Test memory",
            "user_id": "test_user"
        }
        
        response = api_client.post(
            f"{api_base_url}/memory",
            data=json.dumps(valid_data),
            headers={"Content-Type": "text/plain"}
        )
        
        # Should handle gracefully
        assert response.status_code in [400, 422]
    
    def test_nonexistent_endpoint(self, api_client, api_base_url):
        """Test response to nonexistent endpoint."""
        response = api_client.get(f"{api_base_url}/nonexistent/endpoint")
        
        assert response.status_code == 404
    
    def test_method_not_allowed(self, api_client, api_base_url):
        """Test wrong HTTP method on endpoint."""
        # Try POST on health endpoint (should only accept GET)
        response = api_client.post(f"{api_base_url}/health")
        
        assert response.status_code == 405  # Method not allowed
    
    def test_large_payload(self, api_client, api_base_url):
        """Test handling of large payloads."""
        large_message = "A" * 10000  # 10KB message
        large_data = {
            "message": large_message,
            "user_id": "test_user_123",
            "metadata": {"size": "large"}
        }
        
        response = api_client.post(
            f"{api_base_url}/memory",
            json=large_data
        )
        
        # Should either accept or reject gracefully
        assert response.status_code in [200, 201, 413, 422]  # 413 = Payload too large
    
    def test_special_characters_in_user_id(self, api_client, api_base_url):
        """Test handling of special characters in user_id."""
        special_user_id = "user@#$%^&*()_+-={}[]|\\:;\"'<>?,./"
        memory_data = {
            "message": "Test memory with special user ID",
            "user_id": special_user_id
        }
        
        response = api_client.post(
            f"{api_base_url}/memory",
            json=memory_data
        )
        
        # Should handle special characters appropriately
        assert response.status_code in [200, 201, 400, 422]
    
    def test_unicode_in_message(self, api_client, api_base_url):
        """Test handling of Unicode characters in message."""
        unicode_message = "Test with émojis 🚀 and ümlauts ñ 中文"
        memory_data = {
            "message": unicode_message,
            "user_id": "test_user_123"
        }
        
        response = api_client.post(
            f"{api_base_url}/memory",
            json=memory_data
        )
        
        # Should handle Unicode properly
        assert response.status_code in [200, 201]


@pytest.mark.integration
class TestEdgeCases:
    """Test edge cases in API behavior."""
    
    def test_concurrent_memory_creation(self, api_client, api_base_url):
        """Test concurrent memory creation for same user."""
        import threading
        import time
        
        results = []
        
        def create_memory(index):
            memory_data = {
                "message": f"Concurrent memory {index}",
                "user_id": "concurrent_user",
                "metadata": {"index": index}
            }
            response = api_client.post(f"{api_base_url}/memory", json=memory_data)
            results.append(response.status_code)
        
        # Create 5 memories concurrently
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_memory, args=(i,))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # All should succeed
        assert all(status in [200, 201] for status in results)
    
    def test_empty_metadata_object(self, api_client, api_base_url):
        """Test memory creation with empty metadata object."""
        memory_data = {
            "message": "Memory with empty metadata",
            "user_id": "test_user_123",
            "metadata": {}
        }
        
        response = api_client.post(f"{api_base_url}/memory", json=memory_data)
        
        assert response.status_code in [200, 201]
    
    def test_null_metadata(self, api_client, api_base_url):
        """Test memory creation with null metadata."""
        memory_data = {
            "message": "Memory with null metadata",
            "user_id": "test_user_123",
            "metadata": None
        }
        
        response = api_client.post(f"{api_base_url}/memory", json=memory_data)
        
        assert response.status_code in [200, 201]
    
    def test_very_long_user_id(self, api_client, api_base_url):
        """Test handling of very long user IDs."""
        long_user_id = "user_" + "x" * 1000  # 1005 character user ID
        memory_data = {
            "message": "Memory with very long user ID",
            "user_id": long_user_id
        }
        
        response = api_client.post(f"{api_base_url}/memory", json=memory_data)
        
        # Should either accept or reject appropriately
        assert response.status_code in [200, 201, 400, 422]
    
    def test_search_with_very_long_query(self, api_client, api_base_url):
        """Test search with very long query string."""
        long_query = "search " * 1000  # Very long search query
        
        response = api_client.get(
            f"{api_base_url}/memory/search",
            params={
                "query": long_query,
                "user_id": "test_user_123"
            }
        )
        
        # Should handle gracefully
        assert response.status_code in [400, 414, 422]


@pytest.mark.slow
class TestPerformanceEdgeCases:
    """Test performance-related edge cases."""
    
    def test_search_with_zero_limit(self, api_client, api_base_url):
        """Test search with limit=0."""
        response = api_client.get(
            f"{api_base_url}/memory/search",
            params={
                "query": "test",
                "user_id": "test_user_123",
                "limit": 0
            }
        )
        
        assert response.status_code == 422
        result = response.json()
        assert result["count"] == 0
        assert len(result["results"]) == 0
    
    def test_search_with_negative_limit(self, api_client, api_base_url):
        """Test search with negative limit."""
        response = api_client.get(
            f"{api_base_url}/memory/search",
            params={
                "query": "test",
                "user_id": "test_user_123",
                "limit": -1
            }
        )
        
        # Should handle negative limits appropriately
        assert response.status_code == 422
    
    def test_search_with_very_large_limit(self, api_client, api_base_url):
        """Test search with very large limit."""
        response = api_client.get(
            f"{api_base_url}/memory/search",
            params={
                "query": "test",
                "user_id": "test_user_123",
                "limit": 999999
            }
        )
        
        # Should handle large limits appropriately (may cap the limit)
        assert response.status_code == 422
