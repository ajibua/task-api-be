# Task API

A small to-do list API built with **FastAPI**, backed by a real **SQLite**
database. Supports full CRUD (Create, Read, Update, Delete) on tasks, with
interactive Swagger docs and proper HTTP status codes throughout — and now,
data that survives a server restart.

Built for W2 · A1 (Build your first CRUD API) and W3 · A1 (Connecting your
CRUD to the database).

## How to run it

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

The first time it runs, it automatically creates `tasks.db` in the project
folder, creates the `tasks` table if missing, and seeds three example tasks
— but only if the table is empty. Every run after that just reuses what's
already there.

Then visit:
- `http://localhost:8000/` — API info
- `http://localhost:8000/docs` — interactive Swagger UI
- `http://localhost:8000/health` — health check

## Endpoints

| Method | Path             | Description                          | Success | Errors        |
|--------|------------------|---------------------------------------|---------|---------------|
| GET    | `/`              | API info (name, version, endpoints)   | 200     | —             |
| GET    | `/health`        | Health check                          | 200     | —             |
| GET    | `/tasks`         | List all tasks                        | 200     | —             |
| GET    | `/tasks/{id}`    | Get a single task                     | 200     | 404           |
| POST   | `/tasks`         | Create a task (`{"title": "..."}`)    | 201     | 400           |
| PUT    | `/tasks/{id}`    | Update a task's title and/or done     | 200     | 400, 404      |
| DELETE | `/tasks/{id}`    | Delete a task                         | 204     | 404           |

All errors are returned as `{"error": "message"}` with the matching status code.
None of the URLs, request bodies, or response shapes changed from the
in-memory version — only what's *behind* the endpoints changed.

## Example: curl -i output

```
$ curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d "{\"title\":\"Buy milk\"}"

HTTP/1.1 201 Created
date: Sun, 23 Aug 2026 13:33:09 GMT
server: uvicorn
content-length: 40
content-type: application/json

{"title":"Buy milk","id":4,"done":false}
```

## Swagger UI

`/docs` lists every endpoint with a description, and the full CRUD cycle
(create → list → update → delete) works via "Try it out."

*(Screenshot: run the server, open `http://localhost:8000/docs` in your
browser, and paste a screenshot here before submitting.)*

## Database

**Why SQLite:** no separate server process to install or run — it's a
single file, zero-config, and perfect for a project this size. It's also
the easiest on-ramp to SQL: the same `SELECT`/`INSERT`/`UPDATE`/`DELETE`
statements carry straight over to Postgres or MySQL later.

**Where it's stored:** `tasks.db` in the project root, created automatically
on first run. It's git-ignored — the database is a build artifact, not
something to commit; anyone cloning the repo gets a fresh one seeded with
the three example tasks.

**Library:** [SQLModel](https://sqlmodel.tiangolo.com/) (built on SQLAlchemy)
— it doubles as both the Pydantic request/response model and the database
table definition, so the `Task` class only needs to be written once.

**Example SQL query executed manually** (via Python's `sqlite3` module,
directly against `tasks.db` while the API was running):

```sql
UPDATE tasks SET done = 1;
```

Running that outside the API, then immediately hitting `GET /tasks`, showed
every task come back with `"done": true` — proof the API is just a thin
layer over the database, not a separate source of truth.

*(Screenshot: open `tasks.db` in DB Browser for SQLite or similar, and paste
a screenshot of the `tasks` table here before submitting.)*

## What changed from the in-memory version

- Tasks are stored in SQLite (`tasks.db`) instead of a Python list — **data
  now survives a server restart.**
- The database and `tasks` table are created automatically if missing.
- The three example tasks are only inserted the first time the table is
  empty — restarting the server never duplicates them.
- Every endpoint's URL, request body, and response shape is unchanged.

## Project structure

```
main.py            # the whole API — see docstrings for what each route does
requirements.txt   # fastapi, uvicorn, pydantic, sqlmodel, sqlalchemy, starlette
tasks.db            # created automatically on first run (git-ignored)
```
