# 🚀 CodeVector Backend Assignment

A scalable backend API built with **FastAPI** to efficiently browse a catalog of approximately **200,000 products**.

The application supports:

* Cursor-based pagination
* Category filtering
* Fast product browsing
* Efficient database querying
* Bulk data generation
* Interactive API documentation using Swagger UI

---

## 🛠 Tech Stack

* **Language:** Python
* **Framework:** FastAPI
* **Database:** SQLite
* **ORM:** SQLAlchemy
* **Validation:** Pydantic
* **Server:** Uvicorn

---

## ✨ Features

* Browse products ordered by newest first
* Cursor-based pagination (no OFFSET pagination)
* Category filtering
* Seed script for generating ~200,000 products
* RESTful API
* Automatic Swagger API documentation
* Health check endpoint
* Modular project structure

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
    ├── swagger-ui.png
    ├── products-api.png
    └── health-api.png
```

---

## 🚀 Installation

Clone the repository

```bash
git clone https://github.com/Jerry-Abhi/codevector-backend-assignment.git
cd codevector-backend-assignment
```

Install dependencies

```bash
pip install -r requirements.txt
```

Generate sample data

```bash
python seed.py
```

Run the application

```bash
uvicorn main:app --reload
```

Open Swagger UI

```
http://127.0.0.1:8000/docs
```

---

## 📌 API Endpoints

| Method | Endpoint        | Description     |
| ------ | --------------- | --------------- |
| GET    | `/`             | Health Check    |
| GET    | `/api/products` | Browse products |

### Query Parameters

| Parameter | Description                 |
| --------- | --------------------------- |
| limit     | Number of products to fetch |
| category  | Filter by category          |
| cursor    | Cursor for next page        |

---

# 📸 Screenshots

## Swagger UI

![Swagger UI](images/swagger-ui.png)

---

## Products API

![Products API](images/products-api.png)

---

## Health Check

![Health Check](images/health-api.png)

---

## ⚡ Design Decisions

### Cursor-Based Pagination

This project uses **cursor pagination** instead of OFFSET pagination because it:

* Provides better performance for large datasets.
* Prevents duplicate records.
* Prevents missing records while data changes.
* Scales efficiently.

Products are sorted using:

```sql
ORDER BY updated_at DESC, id DESC
```

Using both `updated_at` and `id` guarantees consistent ordering.

---

## 🌱 Seed Script

The project includes a seed script that efficiently generates approximately **200,000 products**.

Each product contains:

* Product ID
* Name
* Category
* Price
* Created Timestamp
* Updated Timestamp

---

## 📈 Future Improvements

Given more time, I would add:

* PostgreSQL support
* Docker
* Redis caching
* Authentication & Authorization
* Unit and Integration Tests
* CI/CD Pipeline
* Logging & Monitoring

---

## 🤖 AI Usage

AI tools were used as a development assistant for brainstorming, implementation guidance, documentation, and reviewing the solution. All generated code was reviewed, understood, tested, and adapted before being included in the final project.

---

## 👨‍💻 Author

**Abhishek Anand**

GitHub: https://github.com/Jerry-Abhi
