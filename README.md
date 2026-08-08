# Task API

A small in-memory to-do list API built with **FastAPI**. Supports full CRUD
(Create, Read, Update, Delete) on tasks, with interactive Swagger docs and
proper HTTP status codes throughout.

Built for W2 · A1 — Build your first CRUD API.

## How to run it

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

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

## Example: curl -i output

```
$ curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{"title":"Buy milk"}'

HTTP/1.1 201 Created
date: Sat, 08 Aug 2026 07:31:14 GMT
server: uvicorn
content-length: 40
content-type: application/json

{"id":4,"title":"Buy milk","done":false}
```

## Swagger UI

`/docs` lists every endpoint with a description, and the full CRUD cycle
(create → list → update → delete) works via "Try it out."

*(Screenshot: run the server, open `http://localhost:8000/docs` in your
browser, and paste a screenshot here before submitting.)*

## Data storage

Tasks are kept in a plain Python list in memory — there is no database yet.
That means **all data is lost when the server restarts.** This is intentional
for this stage of the assignment (databases arrive next week) and is a good
first lesson in why persistent storage matters: anything worth keeping needs
to survive a restart, and an in-memory list simply can't do that.

## Project structure

```
main.py            # the whole API — see docstrings for what each route does
requirements.txt   # fastapi, uvicorn, pydantic, starlette
```
