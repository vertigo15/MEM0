# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is a Mem0 (Memory Management System) Docker application that provides a REST API for managing and searching memories using various LLM providers. The application is built with FastAPI and uses PostgreSQL with pgvector extension for vector similarity search.

## Architecture

- **Main Application**: `app.py` - Single FastAPI application file containing all API endpoints
- **Memory Management**: Uses the `mem0` library (`mem0ai==0.1.11`) for core memory operations
- **Database**: PostgreSQL with pgvector extension for vector storage and similarity search
- **LLM Providers**: Supports Azure OpenAI and AWS Bedrock
- **Storage**: Optional cloud storage via AWS S3 or Azure Blob Storage
- **Deployment**: Docker-first approach with multi-stage Dockerfile and docker-compose setup

### Key Components

1. **Memory Instance**: Global `Memory` object initialized from mem0 config at startup
2. **Configuration**: Environment-driven configuration via `.env` file with comprehensive validation
3. **API Models**: Pydantic models for request/response validation (MemoryCreate, MemoryUpdate, etc.)
4. **Structured Logging**: Uses `structlog` for JSON-formatted logging throughout the application

## Development Commands

### Environment Setup
```bash
# Copy environment template
cp .env.example .env
# Edit .env with your configuration values

# Virtual environment setup
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### Running the Application
```bash
# Development (local)
python app.py

# Docker development
docker-compose up --build

# Docker production
docker-compose up -d
```

### Docker Operations
```bash
# View logs
docker-compose logs -f mem0_app
docker-compose logs postgres

# Health check
curl http://localhost:8000/health

# Database access
docker-compose exec postgres psql -U postgres -d mem0_db
```

### Testing
This project currently has no test framework configured. When adding tests:
- Use pytest as the testing framework (not currently included in requirements.txt)
- Test database operations against a test PostgreSQL instance
- Mock the mem0 Memory class for unit tests
- Test API endpoints using FastAPI's test client

## Configuration Architecture

The application uses a sophisticated environment-based configuration system:

### Required Environment Variables
- **Database**: `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_USER`, `DATABASE_PASSWORD`, `DATABASE_NAME`
- **LLM Provider**: `LLM_PROVIDER` (either "azure_openai" or "aws_bedrock")

### LLM Provider Configuration
The `get_mem0_config()` function dynamically builds the mem0 configuration based on the chosen LLM provider:
- **Azure OpenAI**: Requires `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_DEPLOYMENT`
- **AWS Bedrock**: Requires `AWS_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `BEDROCK_MODEL_ID`

### Optional Storage Providers
- **AWS S3**: Set `STORAGE_PROVIDER=s3` and provide S3 credentials
- **Azure Blob**: Set `STORAGE_PROVIDER=azure_blob` and provide Azure storage credentials

## API Endpoints

The application follows RESTful patterns with these main endpoints:
- `POST /memory` - Add new memory
- `GET /memory/search` - Search memories with query
- `GET /memory/user/{user_id}` - Get all memories for user
- `GET /memory/{memory_id}` - Get specific memory
- `PUT /memory/{memory_id}` - Update memory
- `DELETE /memory/{memory_id}` - Delete memory
- `GET /memory/history/{user_id}` - Get memory history
- `GET /health` - Health check

## Error Handling

The application includes comprehensive error handling:
- Global exception handlers for `ValueError` and general exceptions
- Structured logging for all errors with context
- HTTP status codes following REST conventions
- Graceful degradation when memory service is unavailable

## Security Considerations

- Application runs as non-root user in Docker container
- Environment variables should never be committed to version control
- CORS is configured (currently allows all origins - should be restricted for production)
- Health checks and resource limits are configured in Docker setup

## Database Notes

The application expects PostgreSQL with the pgvector extension. The database connection is handled through the mem0 library's PostgreSQL provider configuration. No direct SQL is written in the application code - all database operations go through the mem0 abstraction layer.