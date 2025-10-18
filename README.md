# Mem0 Docker Application

A complete Docker setup for deploying Mem0 (Memory Management System) with FastAPI, PostgreSQL, and pgvector support. This application provides a REST API for managing and searching memories using various LLM providers and storage backends.

## 🚀 Features

- **REST API**: Complete FastAPI application with Swagger documentation
- **Vector Database**: PostgreSQL with pgvector extension for efficient similarity search
- **Multi-LLM Support**: Azure OpenAI and AWS Bedrock integration
- **Cloud Storage**: Optional AWS S3 and Azure Blob Storage support
- **Docker Ready**: Multi-stage Dockerfile with security best practices
- **Health Monitoring**: Built-in health checks and structured logging
- **Production Ready**: Resource limits, security configurations, and error handling

## 📋 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check endpoint |
| `POST` | `/memory` | Add a new memory |
| `GET` | `/memory/search` | Search memories |
| `GET` | `/memory/user/{user_id}` | Get all memories for a user |
| `GET` | `/memory/{memory_id}` | Get memory by ID |
| `PUT` | `/memory/{memory_id}` | Update memory by ID |
| `DELETE` | `/memory/{memory_id}` | Delete memory by ID |
| `GET` | `/memory/history/{user_id}` | Get memory history |
| `GET` | `/docs` | Swagger API documentation |
| `GET` | `/redoc` | ReDoc API documentation |

## 🛠 Prerequisites

- Docker and Docker Compose
- At least 4GB of available RAM
- Access to either Azure OpenAI or AWS Bedrock

## 🏗 Project Structure

```
mem0/
├── app.py              # Main FastAPI application
├── requirements.txt    # Python dependencies
├── Dockerfile         # Multi-stage Docker build
├── docker-compose.yml # Docker Compose configuration
├── .env.example       # Environment variables template
├── .dockerignore      # Docker ignore file
├── init.sql           # PostgreSQL initialization script
└── README.md          # This file
```

## ⚙️ Configuration

### 1. Environment Setup

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
```

### 2. Database Configuration

The application uses PostgreSQL with pgvector extension:

```env
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_USER=postgres
DATABASE_PASSWORD=your-secure-password
DATABASE_NAME=mem0_db
```

### 3. LLM Provider Configuration

Choose between Azure OpenAI or AWS Bedrock:

#### Azure OpenAI
```env
LLM_PROVIDER=azure_openai
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
AZURE_OPENAI_API_VERSION=2024-02-01
```

#### AWS Bedrock
```env
LLM_PROVIDER=aws_bedrock
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
```

### 4. Storage Configuration (Optional)

#### AWS S3
```env
STORAGE_PROVIDER=s3
S3_BUCKET_NAME=your-bucket-name
S3_REGION=us-east-1
S3_ACCESS_KEY=your-s3-access-key
S3_SECRET_KEY=your-s3-secret-key
```

#### Azure Blob Storage
```env
STORAGE_PROVIDER=azure_blob
AZURE_STORAGE_ACCOUNT_NAME=yourstorageaccount
AZURE_STORAGE_ACCOUNT_KEY=your-storage-key
AZURE_STORAGE_CONTAINER_NAME=mem0-container
```

## 🚀 Quick Start

### 1. Clone and Setup
```bash
# Navigate to the project directory
cd mem0

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your actual configuration values
```

### 2. Run with Docker Compose
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service health
docker-compose ps
```

### 3. Access the Application
- **API**: http://localhost:8000
- **Swagger Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🐳 Docker Commands

### Development
```bash
# Build and start services
docker-compose up --build

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f mem0_app
docker-compose logs -f postgres

# Stop services
docker-compose down

# Remove volumes (careful - this deletes data!)
docker-compose down -v
```

### Production
```bash
# Pull latest images and restart
docker-compose pull && docker-compose up -d

# Scale the application
docker-compose up -d --scale mem0_app=3
```

## 📊 Monitoring and Logs

### Health Checks
- Application health: `curl http://localhost:8000/health`
- Database health: Built-in PostgreSQL health checks
- Container health: `docker-compose ps`

### Logs
- Application logs: `docker-compose logs mem0_app`
- Database logs: `docker-compose logs postgres`
- All logs: `docker-compose logs`

## 🔒 Security Considerations

1. **Environment Variables**: Never commit your `.env` file to version control
2. **Database Password**: Use strong, unique passwords
3. **API Keys**: Rotate API keys regularly
4. **Network**: Configure firewalls and network security groups
5. **TLS**: Enable HTTPS in production
6. **User Permissions**: The application runs as a non-root user

## 🛠 Development

### Local Development with Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server
python app.py
```

### Database Access
```bash
# Connect to PostgreSQL container
docker-compose exec postgres psql -U postgres -d mem0_db

# Run SQL queries
SELECT * FROM pg_extension WHERE extname = 'vector';
```

## 📈 Performance Tuning

### Application
```env
WORKERS=4  # Number of worker processes
LOG_LEVEL=INFO  # Reduce to WARNING in production
```

### Database
```env
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
```

### Docker Resources
```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2G
    reservations:
      cpus: '1.0'
      memory: 1G
```

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   ```bash
   # Check database container is running
   docker-compose ps postgres
   
   # Check database logs
   docker-compose logs postgres
   ```

2. **Application Won't Start**
   ```bash
   # Check environment variables
   docker-compose exec mem0_app env | grep -E "(DATABASE|LLM|AZURE|AWS)"
   
   # Check application logs
   docker-compose logs mem0_app
   ```

3. **Memory/Storage Issues**
   ```bash
   # Check disk space
   docker system df
   
   # Clean up unused resources
   docker system prune
   ```

### Log Analysis
```bash
# Filter application logs
docker-compose logs mem0_app | grep ERROR

# Monitor in real-time
docker-compose logs -f --tail=100 mem0_app
```

## 🔄 Backup and Restore

### Database Backup
```bash
# Create backup
docker-compose exec postgres pg_dump -U postgres mem0_db > backup.sql

# Restore backup
docker-compose exec -T postgres psql -U postgres mem0_db < backup.sql
```

### Volume Backup
```bash
# Backup PostgreSQL data volume
docker run --rm -v mem0_postgres_data:/data -v $(pwd):/backup ubuntu tar czf /backup/postgres_backup.tar.gz /data
```

## 📝 API Usage Examples

### Add Memory
```bash
curl -X POST "http://localhost:8000/memory" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "User prefers morning meetings",
       "user_id": "user123",
       "metadata": {"category": "preferences"}
     }'
```

### Search Memories
```bash
curl -X GET "http://localhost:8000/memory/search?query=morning%20meetings&user_id=user123&limit=5"
```

### Get User Memories
```bash
curl -X GET "http://localhost:8000/memory/user/user123"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter issues:

1. Check the [troubleshooting section](#-troubleshooting)
2. Review the application logs
3. Verify your environment configuration
4. Check that all required services are running

## 🔗 Resources

- [Mem0 Documentation](https://docs.mem0.ai/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [pgvector Extension](https://github.com/pgvector/pgvector)
- [Docker Documentation](https://docs.docker.com/)

---

**Note**: This setup is configured for both development and production use. Adjust the configuration according to your specific requirements and security policies.