# Reference: Audit Report Template

Use this template during **Phase 2** to format the audit report. Every section is mandatory. Do not omit fields or change the structure — this format will be saved as the deliverable report.

---

## Full Report Template

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <directory name of the project being analyzed>
Stack:   <Language> + <Framework X.X.X>
Files:   <N> analyzed | ~<total LOC> lines of code

## Summary
CRITICAL: <count> | HIGH: <count> | MEDIUM: <count> | LOW: <count>

## Findings

### [CRITICAL] <Anti-pattern Name>
File: <relative/path/to/file.ext>:<line> (or <start>-<end> for ranges)
Code: `<exact code snippet that triggered the finding>`
Description: <concrete description of what exactly is wrong — do not be generic>
Impact: <practical consequence if left unfixed>
Recommendation: <specific fix — reference the playbook pattern if applicable>

### [CRITICAL] <Next finding>
...

### [HIGH] <Anti-pattern Name>
File: <path>:<line>
Code: `<snippet>`
Description: ...
Impact: ...
Recommendation: ...

### [HIGH] <Next finding>
...

### [MEDIUM] <Anti-pattern Name>
...

### [LOW] <Anti-pattern Name>
...

================================
Total: <N> findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

---

## Formatting Rules

1. **Order strictly by severity**: All CRITICAL findings first, then all HIGH, then MEDIUM, then LOW.
2. **Within a severity level**: order by file name alphabetically, then by line number.
3. **File path**: use the path relative to the project root (e.g., `src/AppManager.js:45`, not the absolute path).
4. **Line references**:
   - Single line: `models.py:28`
   - Method or block: `models.py:187-199`
5. **Code snippet**: quote the exact problematic line(s), not a paraphrase.
6. **Description**: be specific. Bad: "SQL is not safe". Good: "String concatenation at line 28 builds a raw SQL query using `str(id)`, allowing integer overflow or type-based injection."
7. **Multiple occurrences of the same pattern**: create one finding per distinct file. In the description, note all line numbers within that file.
8. **Do not merge different anti-patterns** into one finding even if they are in the same file.

---

## Example Finding

```
### [CRITICAL] SQL Injection via String Concatenation
File: models.py:28-293
Code: `cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))`
Description: 19 queries across models.py construct SQL by concatenating Python
             variables directly into the query string. Lines affected: 28, 48,
             57, 68, 92, 110, 127, 140, 155, 157, 164, 174, 188, 192, 220,
             224, 280, 291, 293.
Impact: Attacker can inject arbitrary SQL to read, modify, or delete any data.
        The /admin/query endpoint already exposes arbitrary SQL execution.
Recommendation: Replace all string concatenation with parameterized queries.
                See Playbook Pattern 1: SQL Injection → Parameterized Queries.
```

---

## Phase 1 Summary Reference

For reference, the Phase 1 summary format (printed before the audit):

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <Python | Node.js>
Framework:     <Flask X.X.X | Express X.X.X>
Dependencies:  <comma-separated>
Domain:        <description>
Architecture:  <description>
Source files:  <N> files analyzed
DB tables:     <comma-separated>
================================
```
