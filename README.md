# 🚀 Product Catalog API

A production-ready backend built with **FastAPI** that supports browsing approximately **200,000 products** using **cursor-based pagination**, category filtering, and efficient database querying.

This project was developed as part of the **CodeVector Backend Take-Home Assignment**.

---

## ✨ Features

* Cursor-based pagination (avoids duplicates and missing records)
* Browse products ordered by newest first (`updated_at DESC, id DESC`)
* Filter products by category
* Efficient handling of large datasets (~200,000 products)
* Bulk product generation using a seed script
* RESTful API with automatic Swagger documentation
* Health check endpoint
* Clean and modular project structure

---

## 🛠 Tech Stack

* **Python**
* **FastAPI**
* **SQLAlchemy**
* **SQLite** *(can be switched to PostgreSQL with minimal configuration changes)*
* **Pydantic**
* **Uvicorn**

---

## 📂 Project Structure

```text
.
├── crud.py
├── database.py
├── main.py
├── models.py
├── routes.py
├── schemas.py
├── seed.py
├── requirements.txt
├── README.md
└── images/
    ├── swagger-home.png
    ├── products-endpoint.png
    └── health-endpoint.png
```

---

## 🚀 Getting Started

### Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/codevector-backend-assignment.git
cd codevector-backend-assignment
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Generate sample data

```bash
python seed.py
```

### Run the API

```bash
uvicorn main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

---

## 📌 API Endpoints

| Method | Endpoint        | Description                                  |
| ------ | --------------- | -------------------------------------------- |
| GET    | `/`             | Health Check                                 |
| GET    | `/api/products` | Browse products with cursor-based pagination |

### Query Parameters

| Parameter  | Description                         |
| ---------- | ----------------------------------- |
| `limit`    | Number of products per page         |
| `category` | Filter by category                  |
| `cursor`   | Cursor token from previous response |

---

## 📸 Screenshots

### Swagger UI

![Swagger UI](images/swagger-home.png)

---

### Products Endpoint

![Products Endpoint](images/products-endpoint.png)

---

### Health Endpoint

![Health Endpoint](images/health-endpoint.png)

---

## ⚡ Design Decisions

### Why Cursor Pagination?

Instead of OFFSET pagination, this project uses **cursor-based pagination** because it:

* Prevents duplicate records
* Prevents missing records when data changes
* Performs efficiently even with large datasets
* Maintains stable ordering using `updated_at` and `id`

---

### Product Ordering

Products are always returned using:

```sql
ORDER BY updated_at DESC, id DESC
```

This guarantees deterministic ordering even when multiple products share the same timestamp.

---

## 🌱 Seed Script

The repository includes a `seed.py` script that efficiently generates approximately **200,000 products**.

Each product contains:

* ID
* Name
* Category
* Price
* Created At
* Updated At

---

## 📈 Future Improvements

If given more time, I would add:

* PostgreSQL deployment (Neon/Supabase)
* Redis caching
* Docker support
* Authentication & Authorization
* Unit and Integration Tests
* CI/CD pipeline
* Logging and Monitoring

---

## 🤖 AI Usage

AI tools were used to assist with brainstorming, architecture discussions, documentation, and implementation suggestions. The generated code was reviewed, understood, tested, and adapted before being included in the final solution.

---

## 👨‍💻 Author

**Abhishek Anand**
