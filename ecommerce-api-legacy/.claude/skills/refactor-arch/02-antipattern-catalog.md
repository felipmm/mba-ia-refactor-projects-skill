# Reference: Anti-Pattern Catalog

Use this file during **Phase 2** to identify and classify findings. Every finding must reference an exact file path and line number. Apply the severity scale consistently across Python and Node.js projects.

---

## Severity Scale

| Level | Criteria |
|-------|----------|
| **CRITICAL** | Exposes sensitive data, enables unauthorized access, or completely violates separation of responsibilities |
| **HIGH** | Strongly violates MVC or SOLID principles, severely hurts maintainability and testability |
| **MEDIUM** | Standardization issues, code duplication, or moderate performance bottlenecks |
| **LOW** | Readability, naming, or minor quality issues |

---

## Anti-Pattern Catalog

### AP-01 — SQL Injection via String Concatenation
**Severity:** CRITICAL

**Detection signals:**
- Python: `"SELECT ... WHERE id = " + str(id)` or `f"SELECT ... WHERE name = '{name}'"` inside a query execution
- Python: `cursor.execute("..." + variable)` or `.format(variable)` used in SQL
- Node.js: Template literal or concatenation inside `db.run("SELECT ... " + req.body.x)`

**Why it's critical:** Allows an attacker to read, modify, or delete arbitrary database data. CVSSv3 score typically 9.8.

**Example (Python):**
```python
# BEFORE (vulnerable)
cursor.execute("SELECT * FROM users WHERE id = " + str(user_id))

# Detection: any `execute(` call where the string argument contains `+` or `.format(` or f-string with a variable
```

---

### AP-02 — Hardcoded Secrets / Credentials
**Severity:** CRITICAL

**Detection signals:**
- `SECRET_KEY = "..."` or `app.config['SECRET_KEY'] = '...'` with a literal string value
- `password = '123'` or `'pass': 'hardcoded'` in source code (not in a .env file)
- Email credentials: `self.email_password = 'senha123'` or similar assignments in Python classes
- Node.js config objects: `{ password: 'actual_password', apiKey: 'live_key_...' }`
- Payment gateway keys, SMTP credentials, database passwords as string literals

**Why it's critical:** Credentials committed to source control are permanently exposed in git history.

---

### AP-03 — God Class / God File
**Severity:** CRITICAL

**Detection signals:**
- A single class or file (>200 LOC) that contains ALL of: HTTP route registration, database schema creation, database queries, business logic, and response formatting
- Class has methods that span unrelated domains (checkout + reporting + user deletion)
- Entry point file also contains all route handlers and DB logic (no separation)

**Why it's critical:** Impossible to test in isolation; any change affects everything; violates SRP completely.

---

### AP-04 — Dangerous Endpoints Without Authentication
**Severity:** CRITICAL

**Detection signals:**
- Routes named `/admin/reset-db`, `/admin/query`, or similar destructive paths
- The handler executes `DROP TABLE`, `DELETE FROM`, or arbitrary user-provided SQL
- No authentication middleware or token check before the route handler runs

**Why it's critical:** Anyone with network access can destroy all data or read/modify arbitrary records.

---

### AP-05 — Plaintext or Weak Password Hashing
**Severity:** HIGH

**Detection signals:**
- Passwords stored directly: `senha = request.json['senha']` then inserted into DB without hashing
- MD5 usage: `hashlib.md5(pwd.encode()).hexdigest()` — MD5 is broken for passwords (no salt, fast)
- Custom weak crypto: function named `badCrypto`, base64 encoding used as "encryption"
- Passwords logged to console alongside other data

**Why it's high:** Password compromise is irreversible. MD5 hashes are crackable in seconds with GPU.

---

### AP-06 — N+1 Query Pattern
**Severity:** HIGH

**Detection signals:**
- Python: `cursor.execute(...)` or `.query.get(id)` called **inside** a `for` loop that iterates over a previous query result
- Node.js: `db.get(...)` or `db.all(...)` called inside a callback of another `db.all(...)` — nested database calls per row
- Pattern: fetch list of N items, then for each item fetch related data individually

**Why it's high:** O(N) queries for a single request. 100 records = 100+ DB round trips. Application collapses under load.

---

### AP-07 — Business Logic in Routes / Controllers
**Severity:** HIGH

**Detection signals:**
- Discount calculation, tax computation, or pricing logic inside a route handler function
- Complex `if/elif` chains evaluating business rules directly in the HTTP handler
- Data transformation and formatting logic mixed with request parsing in the same function
- Database queries executed directly inside route handlers without a model/service layer

**Why it's high:** Business rules cannot be tested without an HTTP request; duplicated when reused across endpoints.

---

### AP-08 — Callback Hell (Node.js)
**Severity:** HIGH

**Detection signals:**
- Three or more levels of nested callbacks: `db.run(..., function() { db.run(..., function() { db.run(... })})`
- Manual counter tracking for async completion: `let pending = 5; if (--pending === 0) res.json(...)`
- No use of `Promise`, `async/await`, or `util.promisify` in the codebase

**Why it's high:** Extremely difficult to read, maintain, and handle errors correctly. Race conditions likely.

---

### AP-09 — Code Duplication
**Severity:** MEDIUM

**Detection signals:**
- Same logic block (>5 lines) repeated in 3 or more different files or functions without extraction
- Manual object serialization (building dicts/objects from DB rows) repeated in multiple route handlers when a `to_dict()` method already exists on the model
- Identical validation checks (e.g., overdue date comparison) copy-pasted across multiple endpoints

**Why it's medium:** Each copy must be maintained independently; bugs are fixed in one place but not others.

---

### AP-10 — Missing Input Validation
**Severity:** MEDIUM

**Detection signals:**
- Route handler accesses `request.json['field']` or `req.body.field` without checking if the key exists or if the value is the expected type
- No check for required fields before inserting into the database
- Numeric fields (price, quantity) not validated to be positive numbers
- Email fields accepted without format validation

**Why it's medium:** Leads to cryptic 500 errors instead of meaningful 400 responses; can cause DB constraint violations.

---

### AP-11 — Bare / Overly Broad Exception Handlers
**Severity:** MEDIUM

**Detection signals:**
- Python: `except:` (no exception type) or `except Exception:` that swallows all errors silently
- Node.js: `catch(e) {}` or `catch(e) { console.log(e) }` without re-throwing or proper handling
- Error handler returns a generic message without logging the actual exception details

**Why it's medium:** Hides bugs; makes debugging nearly impossible in production; masks security-relevant errors.

---

### AP-12 — Deprecated or Unsafe API Usage
**Severity:** MEDIUM

**Detection signals:**
- Flask: `app.run()` called at module level without `if __name__ == '__main__':` guard — prevents proper WSGI deployment
- SQLite: `check_same_thread=False` used without connection pooling — thread safety issues
- Node.js + Express 4.x: All routes registered directly on `app` instead of `express.Router()` — limits modularity
- `sqlite3.Database(':memory:')` for a production use case — all data lost on process restart
- Using `MD5` or `SHA1` for any security-sensitive purpose (deprecated for cryptography since 2012)

---

### AP-13 — Poor Variable Naming
**Severity:** LOW

**Detection signals:**
- Single-letter parameter names in non-trivial functions: `u`, `e`, `p`, `cc`, `c_id` where the context is not immediately obvious
- Abbreviations that require domain knowledge to decode: `usr`, `eml`, `pwd`, `cid` in a non-trivial function body
- Generic names like `data`, `result`, `item` used for domain-specific objects

**Why it's low:** Reduces readability; slows onboarding; not a security or correctness risk.

---

### AP-14 — Unused Imports
**Severity:** LOW

**Detection signals:**
- Python: `import os`, `import json`, `import sys` declared at the top of a file but none of their symbols (`os.`, `json.`, `sys.`) appear anywhere in the file body
- Node.js: `const something = require('module')` declared but `something` never referenced

**Why it's low:** Increases cognitive load; may indicate dead code paths or copy-paste errors.
