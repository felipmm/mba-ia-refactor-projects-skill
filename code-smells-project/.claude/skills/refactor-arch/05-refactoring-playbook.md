# Reference: Refactoring Playbook

Use this file during **Phase 3** to apply concrete transformations for each anti-pattern found in Phase 2. Each pattern includes before/after code examples for both Python and Node.js where applicable.

---

## Pattern 1 — SQL Injection → Parameterized Queries

**Fixes:** AP-01

### Python (sqlite3)
```python
# BEFORE — vulnerable to injection
cursor.execute("SELECT * FROM users WHERE id = " + str(user_id))
cursor.execute("INSERT INTO users VALUES ('" + name + "', '" + email + "')")

# AFTER — parameterized queries
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
cursor.execute("INSERT INTO users VALUES (?, ?)", (name, email))
```

### Python (SQLAlchemy)
```python
# BEFORE
db.session.execute(f"SELECT * FROM users WHERE email = '{email}'")

# AFTER
from sqlalchemy import text
db.session.execute(text("SELECT * FROM users WHERE email = :email"), {"email": email})
# Or better: use the ORM
User.query.filter_by(email=email).first()
```

### Node.js (sqlite3)
```javascript
// BEFORE — vulnerable
db.all("SELECT * FROM users WHERE id = " + req.params.id, callback)

// AFTER — parameterized
db.all("SELECT * FROM users WHERE id = ?", [req.params.id], callback)
db.run("INSERT INTO users (name, email) VALUES (?, ?)", [name, email], callback)
```

---

## Pattern 2 — Hardcoded Secrets → Config Module + Env Vars

**Fixes:** AP-02

### Python
```python
# BEFORE (app.py)
app.config['SECRET_KEY'] = 'minha-chave-super-secreta-123'
EMAIL_PASSWORD = 'senha123'

# AFTER (src/config/settings.py)
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change-me-in-production')
    EMAIL_USER = os.environ.get('EMAIL_USER', '')
    EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')
    DATABASE_PATH = os.environ.get('DATABASE_PATH', 'app.db')
    DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'
```

```
# .env.example (created in project root — never commit .env itself)
SECRET_KEY=your-secret-key-here
EMAIL_USER=app@example.com
EMAIL_PASSWORD=your-email-password
DATABASE_PATH=app.db
DEBUG=false
```

### Node.js
```javascript
// BEFORE (utils.js)
const config = { dbUser: 'admin', dbPass: 'password123', paymentKey: 'live_key_abc' }

// AFTER (src/config/index.js)
module.exports = {
    PORT: process.env.PORT || 3000,
    DB_PATH: process.env.DB_PATH || ':memory:',
    PAYMENT_API_KEY: process.env.PAYMENT_API_KEY,
    SECRET_KEY: process.env.SECRET_KEY,
}
```

---

## Pattern 3 — God Class → Model / Controller / Route Separation

**Fixes:** AP-03

### Node.js (splitting AppManager.js)
```javascript
// BEFORE — AppManager.js does everything
class AppManager {
    initDb() { /* CREATE TABLE + seed */ }
    setupRoutes(app) {
        app.post('/api/checkout', (req, res) => {
            // DB query + business logic + response all here
        })
    }
}

// AFTER — split into layers

// src/models/enrollmentModel.js — data access only
const db = require('../database');
function createEnrollment(userId, courseId) {
    return new Promise((resolve, reject) => {
        db.run('INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
            [userId, courseId],
            function(err) { err ? reject(err) : resolve(this.lastID) }
        )
    })
}
module.exports = { createEnrollment }

// src/controllers/checkoutController.js — business logic only
const CourseModel = require('../models/courseModel')
const EnrollmentModel = require('../models/enrollmentModel')
async function processCheckout({ userId, courseId, cardNumber }) {
    const course = await CourseModel.findById(courseId)
    if (!course) throw new Error('Course not found')
    if (!cardNumber.startsWith('4')) throw new Error('Payment refused')
    const enrollmentId = await EnrollmentModel.createEnrollment(userId, courseId)
    return { enrollmentId }
}
module.exports = { processCheckout }

// src/routes/checkoutRoutes.js — routing only
const express = require('express')
const router = express.Router()
const { processCheckout } = require('../controllers/checkoutController')
router.post('/checkout', async (req, res, next) => {
    try {
        const result = await processCheckout(req.body)
        res.json({ msg: 'Sucesso', ...result })
    } catch (err) {
        next(err)
    }
})
module.exports = router
```

---

## Pattern 4 — Plaintext / Weak Passwords → Secure Hashing

**Fixes:** AP-05

### Python (replace MD5 with hashlib + salt)
```python
# BEFORE — MD5, no salt
import hashlib
password_hash = hashlib.md5(pwd.encode()).hexdigest()

# AFTER — SHA-256 with salt (no extra dependency)
import hashlib, secrets

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}:{digest}"

def verify_password(stored: str, provided: str) -> bool:
    salt, digest = stored.split(':')
    return hashlib.sha256((salt + provided).encode()).hexdigest() == digest
```

### Node.js (replace badCrypto with crypto module)
```javascript
// BEFORE — badCrypto
function badCrypto(text) { return Buffer.from(text).toString('base64').slice(0, 10) }

// AFTER — PBKDF2 with built-in crypto (no new dependency)
const crypto = require('crypto')

function hashPassword(password) {
    const salt = crypto.randomBytes(16).toString('hex')
    const hash = crypto.pbkdf2Sync(password, salt, 100000, 64, 'sha256').toString('hex')
    return `${salt}:${hash}`
}

function verifyPassword(stored, provided) {
    const [salt, hash] = stored.split(':')
    const verify = crypto.pbkdf2Sync(provided, salt, 100000, 64, 'sha256').toString('hex')
    return hash === verify
}
```

---

## Pattern 5 — N+1 Query → JOIN Query

**Fixes:** AP-06

### Python (sqlite3 — nested loops → single JOIN)
```python
# BEFORE — N+1: one query per order, then one per item
orders = cursor.execute("SELECT * FROM pedidos WHERE usuario_id = ?", (uid,)).fetchall()
for order in orders:
    cursor2 = conn.cursor()
    items = cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = ?", (order['id'],)).fetchall()
    for item in items:
        cursor3 = conn.cursor()
        product = cursor3.execute("SELECT nome FROM produtos WHERE id = ?", (item['produto_id'],)).fetchone()

# AFTER — single JOIN query
rows = cursor.execute("""
    SELECT p.id, p.total, p.status,
           ip.quantidade, ip.preco_unitario,
           pr.nome as produto_nome
    FROM pedidos p
    LEFT JOIN itens_pedido ip ON ip.pedido_id = p.id
    LEFT JOIN produtos pr ON pr.id = ip.produto_id
    WHERE p.usuario_id = ?
""", (uid,)).fetchall()
```

### Node.js (nested callbacks → JOIN)
```javascript
// BEFORE — N+1 with nested callbacks per course
db.all("SELECT * FROM courses", (err, courses) => {
    courses.forEach(course => {
        db.all("SELECT * FROM enrollments WHERE course_id = ?", [course.id], (err, enrollments) => {
            enrollments.forEach(e => {
                db.get("SELECT * FROM users WHERE id = ?", [e.user_id], (err, user) => { ... })
            })
        })
    })
})

// AFTER — single JOIN
db.all(`
    SELECT c.title, c.price,
           u.name as student_name,
           p.amount as paid
    FROM courses c
    LEFT JOIN enrollments e ON e.course_id = c.id
    LEFT JOIN users u ON u.id = e.user_id
    LEFT JOIN payments p ON p.enrollment_id = e.id
`, [], (err, rows) => { ... })
```

---

## Pattern 6 — Business Logic in Routes → Extract to Controller

**Fixes:** AP-07

### Python
```python
# BEFORE — discount logic in route handler
@app.route('/pedidos', methods=['POST'])
def criar_pedido():
    total = sum(item['preco'] * item['qty'] for item in items)
    if total > 10000:
        total *= 0.90  # 10% discount
    elif total > 5000:
        total *= 0.95  # 5% discount
    # ... insert into DB

# AFTER — route delegates to controller
# src/controllers/pedido_controller.py
def calcular_total_com_desconto(items):
    total = sum(item['preco'] * item['qty'] for item in items)
    if total > 10000:
        return total * 0.90
    elif total > 5000:
        return total * 0.95
    return total

# src/views/routes.py
@app.route('/pedidos', methods=['POST'])
def criar_pedido():
    total = pedido_controller.calcular_total_com_desconto(request.json['items'])
    # ... call model to insert
```

---

## Pattern 7 — Callback Hell → async/await (Node.js)

**Fixes:** AP-08

```javascript
// BEFORE — pyramid of doom
db.run(sql1, params1, function(err) {
    if (err) return res.status(500).json({ error: 'DB error' })
    db.run(sql2, params2, function(err) {
        if (err) return res.status(500).json({ error: 'DB error' })
        db.run(sql3, params3, function(err) {
            if (err) return res.status(500).json({ error: 'DB error' })
            res.json({ success: true })
        })
    })
})

// AFTER — promisify once, then async/await everywhere
const { promisify } = require('util')
// In database.js:
const dbRun = (sql, params) => new Promise((resolve, reject) =>
    db.run(sql, params, function(err) { err ? reject(err) : resolve(this) })
)
const dbGet = (sql, params) => new Promise((resolve, reject) =>
    db.get(sql, params, (err, row) => { err ? reject(err) : resolve(row) })
)
const dbAll = (sql, params) => new Promise((resolve, reject) =>
    db.all(sql, params, (err, rows) => { err ? reject(err) : resolve(rows) })
)

// In controller:
async function processCheckout(data) {
    await dbRun(sql1, params1)
    await dbRun(sql2, params2)
    const result = await dbRun(sql3, params3)
    return result
}
```

---

## Pattern 8 — Code Duplication → Extract Shared Method

**Fixes:** AP-09

### Python (overdue check duplicated across 6 route files)
```python
# BEFORE — same block repeated in task_routes.py, report_routes.py, user_routes.py, etc.
if task.due_date and task.status not in ['done', 'cancelled']:
    if datetime.utcnow() > task.due_date:
        task_dict['is_overdue'] = True
    else:
        task_dict['is_overdue'] = False

# AFTER — add method to Task model (models/task.py)
class Task(db.Model):
    def is_overdue(self):
        return (self.due_date is not None
                and self.status not in ('done', 'cancelled')
                and datetime.utcnow() > self.due_date)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'status': self.status,
            'is_overdue': self.is_overdue(),
            # ...
        }
# All routes now call: task.to_dict()
```

---

## Pattern 9 — Bare Exception Handlers → Specific Handlers

**Fixes:** AP-11

### Python
```python
# BEFORE
try:
    result = some_operation()
except:
    return jsonify({'error': 'Erro interno'}), 500

# AFTER
import logging
logger = logging.getLogger(__name__)

try:
    result = some_operation()
except ValueError as e:
    return jsonify({'error': str(e)}), 400
except Exception as e:
    logger.exception("Unexpected error in some_operation")
    return jsonify({'error': 'Internal server error'}), 500
```

### Node.js — centralized error handler middleware
```javascript
// src/middlewares/errorHandler.js
function errorHandler(err, req, res, next) {
    console.error(err.stack)
    const status = err.status || 500
    res.status(status).json({
        error: status < 500 ? err.message : 'Internal server error'
    })
}
module.exports = errorHandler

// Routes just call next(err) instead of handling errors inline:
router.post('/checkout', async (req, res, next) => {
    try {
        const result = await checkoutController.process(req.body)
        res.json(result)
    } catch (err) {
        next(err)  // delegate to error handler
    }
})
```

---

## Pattern 10 — Dangerous Admin Endpoints → Remove or Protect

**Fixes:** AP-04

### Python — remove or protect with authentication
```python
# BEFORE — anyone can reset the database
@app.route('/admin/reset-db', methods=['POST'])
def reset_database():
    init_db()
    return jsonify({'message': 'Database reset'})

@app.route('/admin/query', methods=['POST'])
def executar_query():
    sql = request.json.get('query')
    cursor.execute(sql)  # arbitrary SQL execution — extremely dangerous

# AFTER — option A: remove entirely (recommended for production)
# Delete the route handlers and route registrations.

# AFTER — option B: protect with admin token if the functionality is needed
import functools

def require_admin_token(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('X-Admin-Token')
        if token != os.environ.get('ADMIN_TOKEN'):
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/admin/reset-db', methods=['POST'])
@require_admin_token
def reset_database():
    init_db()
    return jsonify({'message': 'Database reset'})

# The /admin/query endpoint (arbitrary SQL execution) should always be removed,
# never merely protected — there is no safe way to expose this in production.
```
