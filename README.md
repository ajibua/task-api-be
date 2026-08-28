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
## Auth

Built for W2 · A4 — Auth · Login & protect. Adds real user accounts on
top of the existing task API, using **Supabase Auth** as the identity
provider: it stores accounts, hashes passwords, and signs JSON Web
Tokens. This app never touches a password directly — it only forwards
credentials to Supabase and verifies the tokens Supabase hands back.

### Setup

1. Create a free project at [supabase.com](https://supabase.com).
2. In **Project Settings → API**, copy your **Project URL** and **anon
   key** (never the `service_role` key — that one bypasses all
   security and must stay server-side-secret, and this project doesn't
   need it at all).
3. In **Authentication → Sign In / Providers → Email**, turn off
   **"Confirm email"** so a fresh signup can log in immediately (a
   practice-project convenience — leave this on in production).
4. Add to `.env` (see `.env.example`):
   ```
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_anon_key
   ```
5. `pip install -r requirements.txt` (now includes `supabase`).

### Endpoints

| Method | Path                 | Description                  | Auth required               | Success | Errors   |
| ------ | -------------------- | ----------------------------- | ---------------------------- | ------- | -------- |
| POST   | `/auth/signup`       | Create a new user account     | none                          | 201     | 400      |
| POST   | `/auth/login`        | Authenticate & return a JWT   | none                          | 200     | 400, 401 |
| POST   | `/auth/logout`       | End the user's session        | `Authorization: Bearer <token>` | 204     | 401      |
| GET    | `/protected/profile` | Read the caller's own profile | `Authorization: Bearer <token>` | 200     | 401      |
| GET    | `/protected/dashboard` | Second example protected route, same guard | `Authorization: Bearer <token>` | 200 | 401 |
| GET    | `/public/info`       | Public, unprotected data      | none                          | 200     | —        |

All errors are returned as `{"error": "message"}`, matching the
existing error shape from the tasks endpoints.

### How verification works

`app/dependencies.py` defines a single reusable guard,
`get_current_user`, applied via FastAPI's `Depends()` to every
protected route (`/protected/*` and `/auth/logout`):

1. Extracts the bearer token from the `Authorization` header.
2. Missing or malformed header → `401 {"error": "Access token required"}`.
3. Otherwise calls `supabase.auth.get_user(token)` — a real network
   call to Supabase, so an expired or tampered token is caught even
   though the token itself is never decoded locally.
4. Invalid/expired token → `401 {"error": "Invalid or expired token"}`.
5. Valid token → the route runs with the verified user attached.

Using FastAPI's `HTTPBearer` security scheme (rather than reading the
header manually) is what makes the padlock icon and "Authorize" button
appear automatically on `/docs` for every route that depends on it —
no manual `securitySchemes` config needed in the Python lane.

### Try it — curl

```bash
# Sign up
curl -i -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
# -> 201

# Log in
curl -i -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

curl -i http://localhost:8000/public/info

curl -i http://localhost:8000/protected/profile

curl -i http://localhost:8000/protected/profile \
  -H "Authorization: Bearer <PASTE_ACCESS_TOKEN_HERE>"
# -> 200, your user details

curl -i -X POST http://localhost:8000/auth/logout \
  -H "Authorization: Bearer <PASTE_ACCESS_TOKEN_HERE>"
# -> 204
```

### Try it — Swagger UI

Visit `http://localhost:8000/docs`, click **Authorize**, paste an
`access_token` from `/auth/login`, then **Try it out** on
`GET /protected/profile` — no curl needed. Protected routes show a
lock icon; `/public/info` does not.

![Swagger UI showing auth, protected, and public routes](sql-db/swagger_ui.png)
### 401 vs 403

This assignment only implements `401` (**"I don't know who you
are"** — no token, or a token Supabase rejects). `403` (**"I know
exactly who you are, and you still may not"**) is a stretch goal: it
would mean adding a role check *after* `get_current_user` succeeds —
e.g. an `/admin/*` route that checks `current_user`'s role/metadata
and returns `403` for anyone who isn't an admin.
