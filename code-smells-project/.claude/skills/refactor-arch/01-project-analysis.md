# Reference: Project Analysis Heuristics

Use this file during **Phase 1** to detect the project's stack and architecture.

---

## Language Detection

| Signal | Language |
|--------|----------|
| `requirements.txt` present + `.py` files | Python |
| `package.json` present + `.js` files | Node.js |
| Both present | Check which has the entry point (`app.py` vs `src/app.js`) |

---

## Framework Detection

### Python
| Signal in source files | Framework |
|------------------------|-----------|
| `from flask import Flask` or `import flask` | Flask |
| `from django` | Django |
| `from fastapi import` | FastAPI |

Read the version from `requirements.txt`: `flask==3.1.1` → Flask 3.1.1

### Node.js
| Signal in source files | Framework |
|------------------------|-----------|
| `require('express')` or `import express` | Express |
| `require('fastify')` | Fastify |
| `require('koa')` | Koa |

Read the version from `package.json` under `"dependencies"`.

---

## Database Detection

| Signal | Database |
|--------|----------|
| `import sqlite3` + `sqlite3.connect('file.db')` | SQLite (file-based) |
| `new sqlite3.Database(':memory:')` | SQLite (in-memory — data lost on restart) |
| `from flask_sqlalchemy import SQLAlchemy` | SQLAlchemy ORM (likely SQLite or PostgreSQL) |
| `psycopg2` in requirements | PostgreSQL |
| `pymysql` or `mysql-connector` in requirements | MySQL |

---

## DB Table Mapping

### Raw SQLite (Python or Node.js)
Look for `CREATE TABLE` statements:
```sql
CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, ...)
```
Extract each table name.

### SQLAlchemy ORM (Python)
Look for classes that extend `db.Model`:
```python
class User(db.Model):
    __tablename__ = 'users'
```
Extract `__tablename__` values. If absent, SQLAlchemy uses the lowercased class name.

---

## Architecture Assessment

### Monolithic (all code in root, no layer separation)
Signs:
- All `.py` or `.js` files in the root directory
- A single large file (>300 LOC) containing routes, DB queries, and business logic
- No `models/`, `controllers/`, `routes/`, or `services/` directories

Assessment text: `Monolítica — tudo em N arquivos, sem separação de camadas`

### God Class (single class doing everything)
Signs:
- One class file >200 LOC
- Same class registers HTTP routes, executes DB queries, and contains business logic
- Method names span multiple domains (e.g., `handleCheckout`, `getReport`, `deleteUser` all in one class)

Assessment text: `God Class — uma única classe concentra roteamento, banco de dados e lógica de negócio`

### Partially Organized
Signs:
- Directories like `models/`, `routes/`, `services/` exist
- But business logic leaks into routes, or models contain controller logic

Assessment text: `Parcialmente organizada — camadas existem mas com responsabilidades misturadas`

---

## Domain Inference

Analyze endpoint paths and table/model names to infer the application domain:

| Endpoint/Table names contain | Domain |
|------------------------------|--------|
| `produto`, `pedido`, `estoque`, `loja` | E-commerce API |
| `task`, `tarefa`, `category`, `user` | Task Manager API |
| `course`, `enrollment`, `payment`, `student` | LMS / E-learning Platform |
| `user`, `auth`, `role`, `permission` | Identity / Auth Service |

---

## Source File Counting

Count only application source files — exclude:
- Seed files (`seed.py`, `seed.js`)
- Database init files (`database.py` that only has schema)
- Test files (`*_test.py`, `*.test.js`, `tests/`)
- Configuration files (`*.json`, `*.yaml`, `*.env`)

Count lines across all included source files for the LOC total.

---

## Endpoint Listing

### Flask (Python)
```python
# Registered via decorator
@app.route('/produtos', methods=['GET', 'POST'])
# Or via Blueprint
@produto_bp.route('/<int:id>', methods=['PUT', 'DELETE'])
```

### Express (Node.js)
```javascript
// Directly on app
app.get('/api/checkout', handler)
app.post('/api/checkout', handler)
// Via router
router.delete('/users/:id', handler)
```

List all unique METHOD + PATH combinations found.
