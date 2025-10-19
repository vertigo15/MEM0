import os
import logging
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import structlog

from mem0 import Memory

# Load environment variables
load_dotenv()

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Pydantic models for API requests and responses
class MemoryCreate(BaseModel):
    message: str = Field(..., description="The memory content to store")
    user_id: str = Field(..., description="User identifier")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")

class MemoryUpdate(BaseModel):
    message: Optional[str] = Field(None, description="Updated memory content")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Updated metadata")

class MemorySearch(BaseModel):
    query: str = Field(..., description="Search query")
    user_id: str = Field(..., description="User identifier")
    limit: Optional[int] = Field(default=10, description="Number of results to return")

class MemoryResponse(BaseModel):
    id: str
    message: str
    user_id: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    version: str
    database: str
    llm_provider: str
    storage_provider: str

# Global memory instance
memory_instance = None

def validate_environment():
    """Validate that all required environment variables are set"""
    # Basic validation - just check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        raise ValueError("Missing required environment variable: OPENAI_API_KEY")

def get_mem0_config():
    """Generate Mem0 configuration based on environment variables"""
    # Use minimal configuration with defaults
    config = {
        "vector_store": {
            "provider": "qdrant",
            "config": {
                "path": "/tmp/qdrant"
            }
        }
    }
    
    return config

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global memory_instance
    
    try:
        # Validate environment variables
        validate_environment()
        
        # Initialize Mem0
        config = get_mem0_config()
        memory_instance = Memory.from_config(config)
        
        logger.info("Mem0 application started successfully", 
                   llm_provider=os.getenv('LLM_PROVIDER'),
                   storage_provider=os.getenv('STORAGE_PROVIDER', 'none'))
        
        yield
        
    except Exception as e:
        logger.error("Failed to initialize Mem0 application", error=str(e))
        raise
    finally:
        logger.info("Mem0 application shutting down")

# Initialize FastAPI app
app = FastAPI(
    title="Mem0 API",
    description="REST API for Mem0 memory management system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_memory() -> Memory:
    """Dependency to get the memory instance"""
    if memory_instance is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Memory service is not available"
        )
    return memory_instance

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        return HealthResponse(
            status="healthy",
            version="1.0.0",
            database="qdrant",
            llm_provider=os.getenv('LLM_PROVIDER', 'unknown'),
            storage_provider=os.getenv('STORAGE_PROVIDER', 'none')
        )
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unhealthy"
        )

@app.post("/memory", response_model=Dict[str, str])
async def add_memory(
    memory_data: MemoryCreate,
    memory: Memory = Depends(get_memory)
):
    """Add a new memory"""
    try:
        result = memory.add(
            memory_data.message,
            user_id=memory_data.user_id,
            metadata=memory_data.metadata or {}
        )
        
        logger.info("Memory added successfully", 
                   user_id=memory_data.user_id,
                   result=result)
        
        return {"message": "Memory added successfully", "result": str(result)}
        
    except Exception as e:
        logger.error("Failed to add memory", 
                    user_id=memory_data.user_id,
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add memory: {str(e)}"
        )

@app.get("/memory/search")
async def search_memories(
    query: str = Query(..., description="Search query"),
    user_id: str = Query(..., description="User identifier"),
    limit: int = Query(10, description="Number of results to return"),
    memory: Memory = Depends(get_memory)
):
    """Search memories"""
    try:
        results = memory.search(
            query=query,
            user_id=user_id,
            limit=limit
        )
        
        logger.info("Memory search completed", 
                   user_id=user_id,
                   query=query,
                   results_count=len(results))
        
        return {"results": results, "count": len(results)}
        
    except Exception as e:
        logger.error("Failed to search memories", 
                    user_id=user_id,
                    query=query,
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search memories: {str(e)}"
        )

@app.get("/memory/user/{user_id}")
async def get_all_memories(
    user_id: str,
    memory: Memory = Depends(get_memory)
):
    """Get all memories for a user"""
    try:
        results = memory.get_all(user_id=user_id)
        
        logger.info("Retrieved all memories for user", 
                   user_id=user_id,
                   count=len(results))
        
        return {"memories": results, "count": len(results)}
        
    except Exception as e:
        logger.error("Failed to get all memories", 
                    user_id=user_id,
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get memories: {str(e)}"
        )

@app.get("/memory/{memory_id}")
async def get_memory_by_id(
    memory_id: str,
    memory: Memory = Depends(get_memory)
):
    """Get memory by ID"""
    try:
        result = memory.get(memory_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Memory not found"
            )
        
        logger.info("Retrieved memory by ID", memory_id=memory_id)
        
        return {"memory": result}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get memory by ID", 
                    memory_id=memory_id,
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get memory: {str(e)}"
        )

@app.put("/memory/{memory_id}")
async def update_memory(
    memory_id: str,
    memory_data: MemoryUpdate,
    memory: Memory = Depends(get_memory)
):
    """Update memory by ID"""
    try:
        update_data = {}
        if memory_data.message is not None:
            update_data['data'] = memory_data.message
        if memory_data.metadata is not None:
            update_data['metadata'] = memory_data.metadata
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No update data provided"
            )
        
        result = memory.update(memory_id, **update_data)
        
        logger.info("Memory updated successfully", 
                   memory_id=memory_id,
                   result=result)
        
        return {"message": "Memory updated successfully", "result": str(result)}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update memory", 
                    memory_id=memory_id,
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update memory: {str(e)}"
        )

@app.delete("/memory/{memory_id}")
async def delete_memory(
    memory_id: str,
    memory: Memory = Depends(get_memory)
):
    """Delete memory by ID"""
    try:
        memory.delete(memory_id)
        
        logger.info("Memory deleted successfully", memory_id=memory_id)
        
        return {"message": "Memory deleted successfully"}
        
    except Exception as e:
        logger.error("Failed to delete memory", 
                    memory_id=memory_id,
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete memory: {str(e)}"
        )

@app.get("/memory/history/{user_id}")
async def get_memory_history(
    user_id: str,
    limit: int = Query(50, description="Number of history items to return"),
    memory: Memory = Depends(get_memory)
):
    """Get memory history for a user"""
    try:
        results = memory.history(user_id=user_id, limit=limit)
        
        logger.info("Retrieved memory history", 
                   user_id=user_id,
                   count=len(results))
        
        return {"history": results, "count": len(results)}
        
    except Exception as e:
        logger.error("Failed to get memory history", 
                    user_id=user_id,
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get memory history: {str(e)}"
        )

# Error handlers
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    logger.error("ValueError occurred", error=str(exc))
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error("Unexpected error occurred", error=str(exc))
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config=None  # Use structlog configuration
    )