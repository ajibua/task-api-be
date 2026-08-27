# Task API

A to-do list API built with **FastAPI**, backed by **Postgres running in
Docker** with a persistent volume. Full CRUD (Create, Read, Update, Delete)
on tasks, interactive Swagger docs, proper HTTP status codes — and now,
the app and database start together with one command, and both survive a
restart.

Built across three assignments:
- W2 · A1 — CRUD API, in-memory storage
- W3 · A1 — swapped storage for SQLite
- W4 · A1 (this one) — swapped storage for Postgres in Docker

## How to run it

```bash
cp .env.example .env
docker compose up
```

That's it — the first `docker compose up` builds the app image, starts
Postgres with a named volume, runs `init.sql` to create the `tasks` table
and seed three example tasks (only because the volume is empty the first
time), waits for Postgres to report healthy, then starts the app.

Then visit:
- `http://127.0.0.1:8000/` — API info
- `http://127.0.0.1:8000/docs` — interactive Swagger UI
- `http://127.0.0.1:8000/health` — health check

To stop everything: `docker compose down` (add `-v` if you want to wipe the
volume and start completely fresh next time).

### Running without Docker (local dev)

You can also point the app at any Postgres — e.g. one installed locally —
by setting `DATABASE_URL` in `.env` to use `localhost` instead of `db`
(the `db` hostname only resolves inside the Docker Compose network):

```
DATABASE_URL=postgresql://taskapi:taskapi@localhost:5432/taskapi
```

Then:
```bash
pip install -r requirements.txt
psql -f init.sql  
uvicorn main:app --reload --port 8000
```

If `DATABASE_URL` isn't set at all, the app falls back to a local
`tasks.db` SQLite file, so it still runs without any database installed —
useful for a quick sanity check, but not how this assignment is meant to
be run.

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

All errors are returned as `{"error": "message"}` with the matching status
code. None of this changed from the SQLite version.

## Architecture: how the storage swap actually works

```
app/
├── models.py       # Task table definition (SQLModel)
├── schemas.py      # TaskCreate / TaskUpdate request bodies
├── database.py     # creates the SQLAlchemy engine from DATABASE_URL
├── repository.py   # TaskRepository interface + one implementation
├── service.py      # validation / business rules — knows nothing about SQL
└── routes.py        # FastAPI routes — knows nothing about SQL either
main.py             # wires it together, seeds the DB on startup
```

**Honest note on the "same interface as your in-memory one" requirement:**
rather than write a second, nearly-identical repository class for Postgres,
there's a **single** `SQLModelTaskRepository`, parameterized by whichever
SQLAlchemy engine it's constructed with. SQLModel/SQLAlchemy already
abstracts the SQL dialect — the same `session.exec(select(Task))` call
compiles to SQLite syntax or Postgres syntax depending on the engine, with
no code branching. Writing a second class that was otherwise identical
felt like it would fight the point of the exercise rather than prove it.

What genuinely didn't change when Postgres was swapped in:
- `app/service.py` — zero changes
- `app/routes.py` — zero changes
- every endpoint's URL, request body, and response shape — zero changes

What *did* change:
- `DATABASE_URL` in `.env`, from `sqlite:///tasks.db` to
  `postgresql://taskapi:taskapi@db:5432/taskapi`
- `init.sql` (new) creates the table with Postgres syntax (`SERIAL` instead
  of SQLite's `AUTOINCREMENT`), since raw SQL isn't fully portable — but
  this file lives entirely outside the application layer.

## Persistence: how it was verified

Two separate restarts were tested, since they prove different things:

**1. Restarting just the app** (`Ctrl+C`, then `uvicorn main:app` again, or
`docker compose restart app`): the app holds no state itself, so this was
never in question — but confirmed anyway by creating a task, restarting
the app process, and calling `GET /tasks` again. The task was still there.

**2. Restarting the database** (equivalent to `docker compose down` +
`docker compose up`, or a full container/volume-level restart): this is
the real test, since it's the one that would have wiped an in-memory or
un-mounted store. Verified by creating a task, stopping Postgres entirely,
starting it back up, and querying the table directly with `psql` — all
rows, including the newly created one, were still present. The named
volume (`pgdata` in `docker-compose.yml`) is what makes this work: Postgres
writes its data files there, and Docker keeps that volume around
independently of the container's lifecycle.

*(Screenshot: paste a screenshot here of `docker compose up`, a `curl`
creating a task, `docker compose down && docker compose up` again, and
`GET /tasks` still showing it.)*

## Environment variables

`.env` is git-ignored — it's never committed, since it's where real
credentials would live in a less toy-ish project. `.env.example` is
committed instead, showing the shape `.env` needs without real secrets:

```
DATABASE_URL=database-url
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=db
```

Copy it to get started: `cp .env.example .env`

## Project structure

```
app/                # layered application code (see Architecture above)
main.py             # FastAPI app creation, DB seeding, router wiring
init.sql            # creates the tasks table + seed data (Postgres, run once)
Dockerfile          # builds the app image
docker-compose.yml  # app + Postgres, wired together, with a persistent volume
.env.example         # committed template for .env
requirements.txt    # fastapi, uvicorn, sqlmodel, psycopg2-binary, python-dotenv, ...
```
