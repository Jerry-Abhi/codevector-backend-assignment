import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()

# Read the database URL from the environment
DATABASE_URL = os.getenv("DATABASE_URL")

# 1. Normalize connection prefix
# Render and Heroku often provide DATABASE_URL starting with "postgres://", 
# which SQLAlchemy 2.0 does not accept. We replace it with "postgresql://".
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Default to a local SQLite database if no DATABASE_URL is set in environment.
# This allows immediate zero-config local execution. In production (Render/Neon),
# the DATABASE_URL environment variable is provided, routing traffic to PostgreSQL.
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./products.db"

# 2. SSL and Driver Configuration
connect_args = {}
is_sqlite = DATABASE_URL.startswith("sqlite://")

if is_sqlite:
    # SQLite requires check_same_thread=False to be accessed from multiple threads in FastAPI
    connect_args["check_same_thread"] = False
else:
    # Neon PostgreSQL and similar cloud providers require SSL/TLS connections.
    # We apply sslmode="require" only if we're not connecting to a local address.
    if "localhost" not in DATABASE_URL and "127.0.0.1" not in DATABASE_URL:
        if "postgresql" in DATABASE_URL:
            connect_args["sslmode"] = "require"

# 3. Connection Pooling and Engine Setup
# We only apply PostgreSQL-specific pooling parameters if we aren't using SQLite.
if is_sqlite:
    engine = create_engine(
        DATABASE_URL,
        connect_args=connect_args
    )
else:
    engine = create_engine(
        DATABASE_URL,
        pool_size=20,          # Persistent connection pool size
        max_overflow=10,       # Burst capacity connection limit
        pool_recycle=1800,     # Connection recycle period (30 minutes)
        pool_pre_ping=True,    # Active connection health checks
        connect_args=connect_args
    )

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative Base for models to inherit from
Base = declarative_base()

def get_db():
    """
    FastAPI Dependency to provide a database session per request.
    Using 'yield' ensures that the session is automatically closed 
    after the request-response cycle completes, avoiding connection leaks.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
