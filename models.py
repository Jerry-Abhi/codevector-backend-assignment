from sqlalchemy import Column, Integer, String, Numeric, DateTime, Index, func
from database import Base

class Product(Base):
    __tablename__ = "products"

    # Auto-incrementing primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Product details
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    
    # Using Numeric (Decimal) instead of Float for money to avoid floating-point rounding errors.
    price = Column(Numeric(10, 2), nullable=False)
    
    # Timestamps (Timezone-aware for production systems to avoid server-region mismatch bugs)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # updated_at has an onupdate trigger handled by the database layer
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(), 
        nullable=False
    )

    # Composite B-tree Indexes for High-Performance Pagination
    # In a database with 200,000+ items, full table scans would slow down API requests.
    # We define composite indexes designed exactly to match our query order (updated_at DESC, id DESC).
    __table_args__ = (
        # 1. Index for default catalog browsing: sorted by newest updated products first.
        Index(
            "idx_products_updated_at_id", 
            updated_at.desc(), 
            id.desc()
        ),
        # 2. Index for category catalog browsing: filters by category, then sorts by newest.
        # Placing 'category' first allows the database to instantly filter down the search space
        # and scan the sorted results.
        Index(
            "idx_products_category_updated_at_id", 
            category, 
            updated_at.desc(), 
            id.desc()
        ),
    )
