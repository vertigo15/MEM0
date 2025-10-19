# Mem0 API Test Suite

This directory contains comprehensive tests for the mem0 API, covering functionality, error handling, and edge cases.

## Test Structure

- `conftest.py` - Test configuration, fixtures, and utilities
- `test_health.py` - Health endpoint tests
- `test_memory_api.py` - Memory CRUD operations and search tests
- `test_error_handling.py` - Error handling and edge case tests

## Test Categories

### Unit Tests (`@pytest.mark.unit`)
- Fast tests that don't require external dependencies
- Test basic API responses and validation
- Health endpoint testing

### Integration Tests (`@pytest.mark.integration`)  
- Tests that interact with the actual API and database
- Memory creation, retrieval, search, and deletion
- Multi-user isolation testing
- Complete CRUD lifecycle testing

### Slow Tests (`@pytest.mark.slow`)
- Performance and stress tests
- Large payload handling
- Concurrent operation testing

## Running Tests

### Prerequisites
1. Make sure the mem0 API is running:
   ```bash
   docker-compose up -d
   ```

2. Install test dependencies:
   ```bash
   pip install -r test-requirements.txt
   ```

### Quick Start
Use the test runner script for the easiest experience:

```bash
# Run all tests
python run_tests.py

# Run only unit tests
python run_tests.py --type unit

# Run integration tests with verbose output
python run_tests.py --type integration --verbose

# Run with coverage report
python run_tests.py --coverage
```

### Manual pytest Commands

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m "not slow"

# Run specific test files
pytest tests/test_health.py
pytest tests/test_memory_api.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=app --cov-report=html
```

## Test Configuration

The tests are configured to:
- Automatically wait for API readiness (30 second timeout)
- Clean up test data after each test
- Use isolated test user IDs to avoid conflicts
- Handle API timeouts and retries gracefully

## Environment Variables

The tests use these environment variables (with defaults):
- `API_BASE_URL` - Base URL for API (default: `http://localhost:8000`)

## Sample Test Data

The test suite uses predefined test data:
- Test users: `test_user_123`, `test_user_456` 
- Sample memories with various metadata configurations
- Unicode and special character testing
- Large payload testing

## Test Coverage

The test suite covers:

### API Endpoints
- ✅ `GET /health` - Health check
- ✅ `POST /memory` - Create memory
- ✅ `GET /memory/user/{user_id}` - Get user memories
- ✅ `GET /memory/{memory_id}` - Get specific memory
- ✅ `PUT /memory/{memory_id}` - Update memory
- ✅ `DELETE /memory/{memory_id}` - Delete memory
- ✅ `GET /memory/search` - Search memories
- ✅ `GET /memory/history/{user_id}` - Get memory history

### Functionality
- ✅ Memory CRUD operations
- ✅ Search with various queries and limits
- ✅ User isolation (users can only access their own memories)
- ✅ Metadata handling (null, empty, complex objects)
- ✅ Unicode and special character support
- ✅ Error handling and validation
- ✅ Large payload handling
- ✅ Concurrent operations

### Edge Cases
- ✅ Invalid JSON payloads
- ✅ Missing required fields
- ✅ Nonexistent resources (404 handling)
- ✅ Method not allowed (405 handling)
- ✅ Very long user IDs and queries
- ✅ Zero, negative, and very large limits
- ✅ Concurrent memory creation

## Continuous Integration

To integrate with CI/CD:

```bash
# Install dependencies and run tests
python run_tests.py --skip-health-check --coverage

# Or use pytest directly
pytest --junitxml=test-results.xml --cov=app --cov-report=xml
```

## Troubleshooting

### API Not Responding
- Ensure Docker containers are running: `docker-compose ps`
- Check API health manually: `curl http://localhost:8000/health`
- Wait longer for API startup (can take 30+ seconds on first run)

### Test Failures
- Check API logs: `docker-compose logs mem0_app`
- Verify environment configuration
- Ensure clean test data (tests should clean up automatically)

### Performance Issues
- Skip slow tests: `pytest -m "not slow"`
- Run specific test files instead of full suite
- Check system resources and Docker memory limits

## Contributing

When adding new tests:
1. Use appropriate markers (`@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.slow`)
2. Follow existing patterns for fixtures and assertions
3. Add cleanup in test fixtures if needed
4. Update this README with new test coverage