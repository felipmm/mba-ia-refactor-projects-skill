# Reference: MVC Architecture Guidelines

Use this file during **Phase 3** to define the target directory structure and layer responsibilities. Apply the correct structure for the detected technology stack.

---

## Target Structure — Python / Flask

```
src/
├── config/
│   └── settings.py          # All configuration via os.environ; no hardcoded secrets
├── models/
│   ├── __init__.py
│   └── <entity>_model.py    # One file per domain entity (e.g., produto_model.py)
├── controllers/
│   ├── __init__.py
│   └── <entity>_controller.py  # Business logic per domain
├── views/
│   └── routes.py            # Route registration only; delegates to controllers
├── middlewares/
│   └── error_handler.py     # Centralized error handling
├── database.py              # DB connection / SQLAlchemy init
└── app.py                   # Composition root: create_app() factory
```

**Entry point:** `src/app.py` calls `create_app()`, registers blueprints and middlewares, then `app.run()` under `if __name__ == '__main__':`

---

## Target Structure — Node.js / Express

```
src/
├── config/
│   └── index.js             # All config from process.env; exports config object
├── models/
│   └── <entity>Model.js     # Data access per entity (DB queries + schema)
├── controllers/
│   └── <entity>Controller.js  # Business logic per domain
├── routes/
│   └── <entity>Routes.js    # express.Router() per domain
├── middlewares/
│   └── errorHandler.js      # Express error-handling middleware (4 params)
└── app.js                   # Composition root: create app, register routes, export
```

**Entry point:** `src/app.js` creates the Express instance, registers middleware and routes, exports it. A separate `server.js` (or `app.js` guarded by `require.main === module`) calls `app.listen()`.

---

## Layer Responsibilities

### Config Layer
- **Purpose:** Single source of truth for all configuration values.
- **Rules:**
  - Read from environment variables: `os.environ.get('SECRET_KEY')` (Python) / `process.env.SECRET_KEY` (Node.js)
  - Provide safe defaults only for non-sensitive values (`PORT = 5000`)
  - **Never** hardcode passwords, API keys, or secret keys
  - Create `.env.example` listing required variables without real values

### Model Layer
- **Purpose:** All data access and entity-level validation.
- **Rules:**
  - Execute all database queries (parameterized only — no string concatenation)
  - Define entity structure (columns, types, relationships)
  - Provide `to_dict()` / `toJSON()` serialization methods
  - No HTTP concepts (no `request`, `response`, `jsonify` imports)
  - No business rules that span multiple entities (those belong in Controller)

### Controller Layer
- **Purpose:** Business logic and orchestration.
- **Rules:**
  - Call one or more Models to fulfill a business operation
  - Apply business rules (discount logic, validation across entities, status transitions)
  - Return plain data (dict, object) — not HTTP responses
  - No direct DB queries — always delegate to Models
  - No route definitions (`@app.route`, `app.get(...)`)

### Route / View Layer
- **Purpose:** HTTP interface — map URLs to controllers.
- **Rules:**
  - Parse request parameters and body
  - Call the appropriate Controller method
  - Format the Controller's return value into an HTTP response (`jsonify`, `res.json`)
  - No business logic — thin layer only
  - Handle HTTP-level validation (missing required fields in body → 400)

### Middleware Layer
- **Purpose:** Cross-cutting concerns applied to all requests.
- **Content:**
  - **Error handler:** catches unhandled exceptions, returns consistent error JSON
  - **Request logger:** log method, path, status code (no sensitive data)
  - **Auth middleware:** verify token on protected routes (if authentication exists)

---

## Python/Flask — Application Factory Pattern

```python
# src/app.py
from flask import Flask
from .config.settings import Config
from .views.routes import register_routes
from .middlewares.error_handler import register_error_handlers

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    register_routes(app)
    register_error_handlers(app)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)
```

---

## Node.js/Express — App Factory Pattern

```javascript
// src/app.js
const express = require('express');
const config = require('./config');
const taskRoutes = require('./routes/taskRoutes');
const errorHandler = require('./middlewares/errorHandler');

function createApp() {
    const app = express();
    app.use(express.json());
    app.use('/api', taskRoutes);
    app.use(errorHandler);
    return app;
}

module.exports = createApp;

if (require.main === module) {
    const app = createApp();
    app.listen(config.PORT, () => console.log(`Server on port ${config.PORT}`));
}
```

---

## Naming Conventions

### Python
- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions/methods: `snake_case`
- Constants: `UPPER_SNAKE_CASE`

### Node.js
- Files: `camelCase.js` (models: `userModel.js`, controllers: `userController.js`)
- Classes: `PascalCase`
- Functions/constants: `camelCase`
- Config keys: `UPPER_SNAKE_CASE` for env var names, `camelCase` for the JS config object

---

## What Must Be Preserved After Refactoring

- All original HTTP endpoints (same METHOD + PATH)
- All original response structures (same JSON keys and shapes)
- All original database tables and schema (do not rename tables or columns)
- Application must boot without errors
- No new runtime dependencies added unless strictly necessary to fix a CRITICAL finding (e.g., `bcrypt` to replace MD5)
