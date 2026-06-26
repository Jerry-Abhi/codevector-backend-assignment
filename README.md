# High-Performance Product Catalog API

A production-grade product catalog backend built using **FastAPI** and **PostgreSQL** (SQLAlchemy ORM). This system is designed to handle queries against a large database (seeded with 200,000 products) efficiently. It features a deterministic, cursor-based pagination system that is robust against concurrent database modifications, backed by optimized multi-column indexes.

---

## Architectural Decisions

### 1. Why FastAPI?
FastAPI was selected for this project due to several key benefits:
* **High Performance**: Built on top of Starlette and Pydantic, FastAPI is one of the fastest Python frameworks available, matching the performance of Node.js and Go. It achieves this by using Python's modern `async/await` features.
* **Automatic Validation & Serialization**: Integrates natively with Pydantic. It validates incoming request parameters (e.g. enforcing data type constraints on pagination limits) and serializes database models to JSON automatically, eliminating boilerplate code.
* **Interactive Documentation**: Out of the box, FastAPI generates standard OpenAPI schemas and hosts interactive Swagger UI (`/docs`) and ReDoc (`/redoc`) portals, which improves developer productivity and facilitates team collaboration.

### 2. Why PostgreSQL?
PostgreSQL was chosen as the database layer because:
* **ACID Compliance**: Ensures strong transactional integrity, which is essential when products are being added, updated, or purchased concurrently.
* **Advanced Indexing**: Offers native support for composite B-tree indexes, ordering directions (`DESC`/`ASC`), and multi-column index scans. This is critical for optimizing cursor pagination queries.
* **Scalability**: Can handle millions of rows and heavy concurrent read/write loads through connection pooling, read-replicas, and table partitioning.
* **Cloud Compatibility**: Fully supported by serverless database platforms like Neon and standard cloud platforms like AWS RDS, Google Cloud SQL, and Render.

---

## Pagination Strategy: Cursor-Based vs. OFFSET Pagination

### The Limitations of OFFSET Pagination
Most basic APIs use OFFSET pagination (e.g., `LIMIT 20 OFFSET 1000`). While simple, this approach has two fatal flaws in production:

1. **Performance Degradation (`O(N)` Complexity)**: 
   To execute `OFFSET 150000`, the database cannot jump directly to the 150,000th row. It must scan through all preceding 150,000 rows, load them into memory, discard them, and return only the next 20 rows. As the offset increases, query times degrade linearly, causing slow queries and database CPU exhaustion.
2. **Data Drifting (Inconsistent Pages)**:
   If a user is browsing page 1, and a new product is inserted at the top of the table:
   * All existing products shift down by 1 position.
   * When the user requests page 2, the last product from page 1 has shifted into page 2, causing the user to see a duplicate product.
   * Conversely, if a product is deleted, a product shifts up, causing the user to miss it entirely.

```
OFFSET Drift Example (New item inserted):
[Page 1: A, B] -> Insert "New" -> Table becomes: [New, A, B, C]
[Page 2 (OFFSET 2): B, C] -> User sees product 'B' twice!
```

### The Cursor-Based Pagination Solution
Cursor pagination uses an **opaque cursor** (a pointer to a specific row). Instead of specifying a page offset, the client requests items relative to the cursor:
* Our cursor represents the values of the sorting keys of the last element on the current page: `(updated_at, id)`.
* Because we sort by newest first (`updated_at DESC, id DESC`), the database query filters for items that are older than the cursor:
  ```sql
  WHERE (updated_at < cursor_updated_at)
     OR (updated_at = cursor_updated_at AND id < cursor_id)
  ```
* **Performance (`O(log N)`)**: Because the query uses a direct value filter on indexed columns, the database performs a fast B-tree traversal to locate the exact starting row and scans only the required `limit` rows. This execution speed is independent of how deep the user paginates.
* **Data Consistency**: Even if thousands of products are inserted or deleted concurrently, the cursor points to a specific physical point in time and key value. The next query resumes exactly *after* that point, ensuring no duplicates are seen and no products are skipped.

---

## Database Indexing Strategy

To guarantee sub-millisecond query execution on a database containing 200,000+ records, we defined two multi-column B-tree indexes matching our sorting and filtering queries:

1. `idx_products_updated_at_id` on `(updated_at DESC, id DESC)`
   * **Target Query**: Default catalog browse (`GET /api/products`).
   * **Why**: The database can traverse the B-tree to find the cursor's `(updated_at, id)` and read the subsequent nodes directly in index order. No expensive in-memory sorting (`filesort`) is performed.
2. `idx_products_category_updated_at_id` on `(category, updated_at DESC, id DESC)`
   * **Target Query**: Category-filtered catalog browse (`GET /api/products?category=Electronics`).
   * **Why**: Placing `category` as the first column in the composite index allows PostgreSQL to perform an index seek directly to the matching category records. Since the rest of the index is already sorted by `updated_at DESC, id DESC`, it can fetch paginated results in a single, fast operation.

---

## Time and Space Complexity

| Operation | Time Complexity | Space Complexity | Notes |
| :--- | :--- | :--- | :--- |
| **Catalog Browse (No Filters)** | `O(log N)` | `O(K)` | Logarithmic search in index `idx_products_updated_at_id`. Space complexity `K` is the page limit. |
| **Filter by Category & Paginate** | `O(log N + M)` | `O(K)` | `N` is total rows, `M` is matching category rows. With the composite index, search reduces to `O(log M)` to seek the cursor. |
| **Bulk Database Seeding** | `O(S)` | `O(B)` | `S` is total seeded records (200k). `B` is batch chunk size (10k) loaded in memory at a time. |

---

## Scalability & Production Readiness

To scale this application to support millions of products and thousands of concurrent requests:
1. **Database Connection Pooling**: Prevents database connection exhaustion by reusing connections (configured in `database.py`).
2. **Read/Write Splitting (Read Replicas)**: Since product catalogs are read-heavy, routing `GET /api/products` queries to read-replicas while keeping write traffic on the primary database instance distributes the database load.
3. **Application Caching (Redis)**: Frequently accessed categories or page-one catalogs can be cached in Redis with a short time-to-live (TTL). This removes query load entirely from PostgreSQL.
4. **Horizontal Scaling**: Since FastAPI is stateless, the web app can be scaled horizontally behind an alb/load balancer (e.g., in AWS ECS, Kubernetes, or Render web services).

---

## Local Development Quickstart

### Prerequisites
* Python 3.10 or higher
* PostgreSQL running locally (or access to a remote database)

### 1. Set Up Environment Variables
Create a file named `.env` in the root of the project:
```env
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/products_db
```
*(Replace `yourpassword` and `products_db` with your local PostgreSQL credentials).*

### 2. Install Dependencies
Create a virtual environment and install the required packages:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
.\venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 3. Seed the Database
Run the high-speed seeding script to generate and insert 200,000 products:
```bash
python seed.py
```
*(This script will auto-create the database tables and indexes, then insert 200,000 products in batches of 10,000, which takes less than 15-20 seconds).*

### 4. Run the API Locally
Start the development server using Uvicorn:
```bash
uvicorn main:app --reload
```
The server will start at `http://127.0.0.1:8000`. You can access the interactive API docs at `http://127.0.0.1:8000/docs`.

---

## Deployment to Render & Neon

This project is fully structured for zero-configuration deployment on Render and Neon PostgreSQL.

### 1. Set Up Neon PostgreSQL
1. Create a free account at [Neon.tech](https://neon.tech).
2. Create a new project and select PostgreSQL version 15 or 16.
3. Copy the provided connection string (it will contain `postgres://` or `postgresql://`).

### 2. Deploy Web Service on Render
1. Create a free account at [Render](https://render.com).
2. Create a new **Web Service** and connect your GitHub repository.
3. Set the following configuration options:
   * **Runtime**: `Python 3` (or specify version in Environment)
   * **Build Command**: `pip install -r requirements.txt`
   * **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add the following **Environment Variables** in Render:
   * `DATABASE_URL`: paste your Neon connection string.
   * `PYTHONUNBUFFERED`: `1` (ensures logs are output immediately)
5. Click **Deploy Web Service**.

Render will provision the instance, install dependencies, spin up the server, and automatically run our lifespan startup hook to initialize the database tables and indexes on Neon.

---

## Future Improvements (If Given More Time)

If this were a commercial production app, the following features would be implemented next:
1. **Alembic Schema Migrations**: Instead of using `Base.metadata.create_all`, use Alembic to track schema versioning. This allows adding/removing columns without wiping production tables.
2. **Async Database Driver (`asyncpg`)**: Migrating SQLAlchemy to async calls using `asyncpg` would unlock FastAPI's full concurrent throughput potential.
3. **Product Search Index**: B-tree indexes are inefficient for fuzzy text search. Implementing PostgreSQL full-text search (`tsvector` and `GIN` indexes) or integrating Elasticsearch would allow fuzzy string searching on names.
4. **Integration Testing**: Implement a suite of tests using `pytest` and `httpx.AsyncClient` utilizing an isolated test database (e.g. via Testcontainers) to verify cursor pagination edge cases programmatically.
