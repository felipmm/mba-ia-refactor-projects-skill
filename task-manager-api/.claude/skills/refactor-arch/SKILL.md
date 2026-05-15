# Skill: /refactor-arch — Architectural Audit & Refactoring

You are an expert software architect. When this skill is invoked, execute the three phases below **sequentially and completely**. Use the reference files in this directory as your knowledge base throughout.

---

## PHASE 1 — PROJECT ANALYSIS

**Goal:** Detect the project's technology stack and current architecture. Print a structured summary before proceeding.

### Steps

1. **Detect language** by checking:
   - `requirements.txt` or `*.py` files present → Python
   - `package.json` or `*.js` files present → Node.js
   - Use `01-project-analysis.md` heuristics for confirmation

2. **Detect framework** by reading the main entry point:
   - `from flask import` or `import flask` → Flask (note version from requirements.txt)
   - `require('express')` → Express (note version from package.json)

3. **Detect database** by scanning source files:
   - `import sqlite3` / `sqlite3.connect(` → SQLite (file-based)
   - `new sqlite3.Database(':memory:')` → SQLite (in-memory)
   - `from flask_sqlalchemy` / `SQLAlchemy(` → SQLAlchemy ORM

4. **Map architecture** by examining directory structure and file contents:
   - Count Python/JS source files (exclude config, tests, seeds)
   - Count total lines of code across those files
   - Detect if code is monolithic (all in root) or layered (models/, routes/, controllers/ present)
   - Identify the domain by reading endpoint names and table/model names

5. **Identify DB tables** by reading:
   - `CREATE TABLE` statements (raw SQLite)
   - SQLAlchemy model class names and `__tablename__`

6. **List endpoints** by reading route definitions:
   - Flask: `@app.route(...)` or `@blueprint.route(...)`
   - Express: `app.get/post/put/delete(...)` or `router.get/post/...`

7. **Print Phase 1 summary** in this exact format:

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <Python | Node.js>
Framework:     <Flask X.X.X | Express X.X.X>
Dependencies:  <comma-separated list from requirements.txt or package.json>
Domain:        <inferred domain description>
Architecture:  <one-line description of current architecture>
Source files:  <N> files analyzed
DB tables:     <comma-separated table names>
================================
```

---

## PHASE 2 — ARCHITECTURE AUDIT

**Goal:** Read every source file, identify anti-patterns using the catalog in `02-antipattern-catalog.md`, and generate a structured report. **Do NOT modify any file in this phase.**

### Steps

1. Read **all** source files completely (not just headers).

2. For each file, cross-reference its content against every anti-pattern in `02-antipattern-catalog.md`. Record:
   - Exact file path and line number(s) where the pattern appears
   - Which anti-pattern it matches
   - Concrete description of what was found (quote the problematic code snippet)
   - Impact and recommendation

3. Compile all findings. Order them: CRITICAL → HIGH → MEDIUM → LOW. Within each severity, order by file name.

4. Generate the report using the template in `03-report-template.md`.

5. **STOP. Print the report. Then ask:**

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

**Wait for user confirmation. Do NOT proceed to Phase 3 until the user explicitly answers "y".**
If the user answers "n", stop and summarize what was found without making any changes.

---

## PHASE 3 — REFACTORING

**Goal:** Restructure the project to follow the MVC pattern, fix the identified issues, and validate the result.

### Steps

1. **Read** `04-mvc-guidelines.md` to determine the target directory structure for this project's stack.

2. **Read** `05-refactoring-playbook.md` to select the correct transformation patterns for each finding from Phase 2.

3. **Create the new MVC structure** — create new directories and files as defined in `04-mvc-guidelines.md`:
   - `src/config/` — externalize all configuration (env vars, no hardcoded secrets)
   - `src/models/` — one file per domain entity (data access + entity logic)
   - `src/controllers/` — one file per domain (business logic, orchestration)
   - `src/views/` (Python) or `src/routes/` (Node.js) — route definitions only, no business logic
   - `src/middlewares/` — error handler, centralized logging
   - `src/app.py` or `src/app.js` — composition root (register routes, middlewares, start server)

4. **Apply transformations** from `05-refactoring-playbook.md`:
   - Fix ALL CRITICAL findings first
   - Then HIGH, MEDIUM, LOW
   - Preserve all original endpoints (same HTTP method + path + response structure)
   - Use parameterized queries for all database access
   - Move secrets to environment variables (create `.env.example` with placeholder values)

5. **Keep the original files** during migration — only delete them after the new structure is fully working.

6. **Validate the refactoring:**

   For Python/Flask:
   ```bash
   cd src && pip install -r ../requirements.txt -q && python app.py &
   sleep 2
   # Test the first available endpoint
   curl -s http://localhost:5000/ | head -c 200
   ```

   For Node.js/Express:
   ```bash
   cd src && npm install --prefix .. -q && node app.js &
   sleep 2
   curl -s http://localhost:3000/ | head -c 200
   ```

   If the app fails to start, diagnose the error, fix it, and retry before reporting success.

7. **Print Phase 3 summary:**

```
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<print the actual directory tree created>

## Issues Fixed
CRITICAL: X fixed
HIGH: Y fixed
MEDIUM: Z fixed
LOW: W fixed

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```

---

## Important Rules

- **Never skip the confirmation step** between Phase 2 and Phase 3.
- **Never modify files during Phase 1 or Phase 2.**
- **Never invent findings** — every finding must reference exact file and line.
- If a finding is in a language or pattern not in the catalog, apply your best judgment using the severity scale.
- This skill must work for Python/Flask AND Node.js/Express projects without modification.
