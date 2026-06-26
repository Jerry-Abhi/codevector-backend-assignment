from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
import crud
import schemas

# Create an API router with a prefix of /api and tags for grouping in Swagger docs
router = APIRouter(prefix="/api", tags=["Products"])

@router.get(
    "/products",
    response_model=schemas.PaginatedProductResponse,
    summary="Retrieve products with cursor-based pagination",
    description=(
        "Returns a list of products ordered by newest first (updated_at DESC, id DESC).\n"
        "Supports optional filtering by category and cursor-based pagination to avoid duplication."
    )
)
def read_products(
    limit: int = Query(
        20, 
        ge=1, 
        le=100, 
        description="Number of products to return per page. Min: 1, Max: 100."
    ),
    category: Optional[str] = Query(
        None, 
        description="Filter products by an exact, case-sensitive category string."
    ),
    cursor: Optional[str] = Query(
        None, 
        description="The base64 encoded cursor token received from the previous response next_cursor."
    ),
    db: Session = Depends(get_db)
):
    try:
        # Fetch the results from the database CRUD logic
        items, next_cursor, has_more = crud.get_products(
            db=db,
            limit=limit,
            category=category,
            cursor=cursor
        )
        
        # Return structured paginated response
        return schemas.PaginatedProductResponse(
            items=items,
            next_cursor=next_cursor,
            limit=limit,
            has_more=has_more
        )
    except ValueError as e:
        # If the cursor was invalid (tampered with or malformed base64), raise a 400 Bad Request
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Pagination error: {str(e)}"
        )
