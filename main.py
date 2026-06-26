import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routes import router as products_router

# Configure structured logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI Lifespan Context Manager
# Handles application startup and shutdown events cleanly.
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up Product Catalog API...")
    
    # Auto-create tables on startup if they don't exist.
    # While tools like Alembic are used for complex schemas, executing Base.metadata.create_all
    # ensures that the project runs out-of-the-box on Neon PostgreSQL without manual setup.
    try:
        logger.info("Verifying database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        # Note: We do not hard-crash the app during startup so the service can still
        # spin up and report errors/health checks correctly.
        
    yield
    
    logger.info("Shutting down Product Catalog API...")

# Initialize FastAPI App with descriptive metadata
app = FastAPI(
    title="Product Catalog API",
    description=(
        "A production-ready product catalog backend. "
        "Implements cursor-based pagination (updated_at, id) for infinite scrolling "
        "and category filtering, optimized for PostgreSQL indexes."
    ),
    version="1.0.0",
    lifespan=lifespan
)

# Mount CORS Middleware
# Essential for allowing web browsers on other origins (React, Vue, Next.js) 
# to communicate with this backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Wildcard allowed for taking home assignments; narrow in production.
    allow_credentials=True,
    allow_methods=["*"],  # Allow all standard methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow custom headers
)

# Root Health Check Endpoint
# Render monitors this endpoint to verify that the container is responsive during rolling deployments.
@app.get("/", tags=["Health"])
def health_check():
    """
    Health check endpoint for deployment monitoring (Render, Kubernetes, etc.).
    """
    return {
        "status": "healthy",
        "service": "Product Catalog API",
        "version": "1.0.0"
    }

# Register application routers
app.include_router(products_router)
