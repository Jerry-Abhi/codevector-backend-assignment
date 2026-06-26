import base64
import json
from datetime import datetime
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from models import Product

def decode_cursor(cursor_str: str) -> Tuple[datetime, int]:
    """
    Decodes a base64 encoded cursor back to (updated_at, id).
    Raises ValueError if the cursor is malformed or invalid.
    """
    try:
        # 1. Base64 decode
        decoded_bytes = base64.b64decode(cursor_str.encode("utf-8"))
        decoded_str = decoded_bytes.decode("utf-8")
        data = json.loads(decoded_str)
        
        # 2. Extract fields
        dt_str = data["updated_at"]
        product_id = int(data["id"])
        
        # Handle the standard ISO 'Z' suffix (shorthand for UTC/Zulu) if present,
        # ensuring compatibility across different Python versions.
        if dt_str.endswith("Z"):
            dt_str = dt_str[:-1] + "+00:00"
            
        updated_at = datetime.fromisoformat(dt_str)
        return updated_at, product_id
    except Exception as e:
        raise ValueError("Invalid cursor format")

def encode_cursor(updated_at: datetime, product_id: int) -> str:
    """
    Encodes (updated_at, id) into an opaque, URL-safe base64 string.
    """
    cursor_dict = {
        "updated_at": updated_at.isoformat(),
        "id": product_id
    }
    json_str = json.dumps(cursor_dict)
    return base64.b64encode(json_str.encode("utf-8")).decode("utf-8")

def get_products(
    db: Session,
    limit: int = 20,
    category: Optional[str] = None,
    cursor: Optional[str] = None
) -> Tuple[List[Product], Optional[str], bool]:
    """
    Retrieves a paginated list of products from the database.
    Order is newest first: updated_at DESC, id DESC.
    
    Returns:
        Tuple of (items_list, next_cursor_string, has_more_boolean)
    """
    # Create the base query
    query = db.query(Product)
    
    # 1. Apply optional category filtering
    if category:
        query = query.filter(Product.category == category)
        
    # 2. Apply cursor filtering
    if cursor:
        cursor_updated_at, cursor_id = decode_cursor(cursor)
        
        # To paginate 'newest first' (descending order), we need items 
        # that are older (i.e. updated_at is less than the cursor's updated_at).
        # If updated_at is identical, we use the tie-breaker 'id' (id is less than the cursor's id).
        query = query.filter(
            or_(
                Product.updated_at < cursor_updated_at,
                and_(
                    Product.updated_at == cursor_updated_at,
                    Product.id < cursor_id
                )
            )
        )
            
    # 3. Sorting & Limit (The limit + 1 trick)
    # We sort by updated_at DESC, id DESC to ensure newest first.
    # We query limit + 1 rows. If the DB returns limit + 1 rows, it proves that 
    # there is a next page, meaning has_more is True.
    query = query.order_by(Product.updated_at.desc(), Product.id.desc()).limit(limit + 1)
    
    results = query.all()
    
    # Check if there are more items to fetch
    has_more = len(results) > limit
    
    # Slice the results down to the requested limit
    items = results[:limit]
    
    # Generate the next page's cursor using the details of the last item in the page
    next_cursor = None
    if has_more and items:
        last_item = items[-1]
        next_cursor = encode_cursor(last_item.updated_at, last_item.id)
        
    return items, next_cursor, has_more
