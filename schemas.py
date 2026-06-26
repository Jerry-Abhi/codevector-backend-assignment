from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

class ProductBase(BaseModel):
    """
    Shared fields between product creation and retrieval.
    """
    name: str = Field(..., max_length=255, description="Name of the product")
    category: str = Field(..., max_length=100, description="Category/Tag of the product")
    
    # We use Decimal for the API contract, matching our DB precision.
    price: Decimal = Field(
        ..., 
        gt=Decimal("0.00"), 
        max_digits=10, 
        decimal_places=2, 
        description="Price of the product (must be greater than 0)"
    )

class ProductCreate(ProductBase):
    """
    Schema for creating a new product (useful for validations during insertion).
    """
    pass

class ProductResponse(ProductBase):
    """
    Schema for serializing a single product.
    Includes database-generated fields like id, created_at, and updated_at.
    """
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        # Enable Pydantic v2 to serialize SQLAlchemy ORM objects into dictionary/JSON formats
        from_attributes = True

class PaginatedProductResponse(BaseModel):
    """
    Response envelope for paginated product lists.
    Wraps the items and embeds metadata required for cursor navigation.
    """
    items: List[ProductResponse] = Field(..., description="List of products in the current page")
    next_cursor: Optional[str] = Field(
        None, 
        description="Base64 encoded cursor token to fetch the next page. Null if no more pages."
    )
    limit: int = Field(..., description="Number of items requested for this page")
    has_more: bool = Field(
        ..., 
        description="Indicates if there is another page of data available."
    )
