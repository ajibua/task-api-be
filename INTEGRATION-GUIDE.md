# How to drop this into task-api-be

Everything here is pre-built and correct together, but the assignment
wants **≥6 honest commits, one per stage** — so integrate and commit
in this order rather than pasting it all in at once.

## Stage 0 — setup

1. Create the Supabase project, grab your Project URL + anon key
   (see README-AUTH-SECTION.md → Setup).
2. Add `SUPABASE_URL` / `SUPABASE_KEY` to `.env` and `.env.example`
   (see `env.example.append.txt`).
3. Add `supabase` to `requirements.txt` (see
   `requirements.append.txt`), then `pip install -r requirements.txt`.
4. Copy `app/supabase_client.py` into your repo's `app/` folder.
5. Run the server — it should start with no errors.
   **Checkpoint:** starts clean, no import errors.
   **Commit:** `Stage 0: setup server and supabase client`

## Stage 1 — signup & login

1. Copy `app/auth_schemas.py` into `app/`.
2. Copy `app/auth_routes.py` into `app/` — for this stage, temporarily
   ignore the `logout` route at the bottom (it needs Stage 4's guard;
   it's fine to leave it in, it just won't work until then).
3. In `main.py`, add:
   ```python
   from app.auth_routes import router as auth_router
   ```
   and `app.include_router(auth_router)` near the existing
   `app.include_router(router)`.
   **Checkpoint:** the signup/login curl calls in
   README-AUTH-SECTION.md return `201` / `200`.
   **Commit:** `Stage 1: signup and login routes working`

## Stage 2 — public route & unverified protected route

1. Copy `app/public_routes.py` into `app/`.
2. For this stage only, add a *temporary* minimal version of
   `/protected/profile` directly (skip `app/dependencies.py` and
   `app/protected_routes.py` for now) that just checks the header is
   present — e.g. a few lines inline in `main.py` or a throwaway
   route. The point of this stage is proving a 401 with no token,
   before real verification exists.
3. Wire `public_router` into `main.py` the same way as `auth_router`.
   **Checkpoint:** `GET /public/info` → 200, `GET /protected/profile`
   with no header → 401.
   **Commit:** `Stage 2: public route and unverified protected route`

## Stage 3 — real token verification

1. Copy `app/dependencies.py` into `app/`.
2. Replace your Stage-2 placeholder `/protected/profile` with the real
   one: copy `app/protected_routes.py` into `app/` (for now it's fine
   if it only has `/profile` — add `/dashboard` in Stage 4).
3. Wire `protected_router` into `main.py`.
   **Checkpoint:** valid token → 200 with your user details; change
   one character of the token → 401.
   **Commit:** `Stage 3: profile route token verification`

## Stage 4 — middleware reuse & logout

1. `app/dependencies.py` is already the reusable guard from Stage 3 —
   nothing new to write here, just reuse it.
2. Make sure `app/protected_routes.py` includes `/dashboard` too (it's
   already in the version provided) — same `Depends(get_current_user)`,
   no new auth code.
3. Uncomment/enable the `/auth/logout` route in `app/auth_routes.py`
   if you skipped it in Stage 1.
   **Checkpoint:** `/protected/dashboard` rejects a bad token (401)
   and accepts a good one (200), using the same guard.
   **Commit:** `Stage 4: auth middleware and logout endpoint`

## Stage 5 — Swagger UI

Nothing extra to add — `HTTPBearer` in `app/dependencies.py` already
makes FastAPI generate the padlock automatically at `/docs`.
1. Open `/docs`, confirm the lock icon appears on `/protected/*` and
   `/auth/logout` but not `/public/info` or `/auth/signup|login`.
2. Click **Authorize**, paste a token, run **Try it out** on
   `/protected/profile`.
3. Screenshot it for the README.
   **Commit:** `Stage 5: Swagger UI documentation with bearer auth`

## Stage 6 — publish

1. Append `README-AUTH-SECTION.md` to your existing `README.md`
   (drop in your Swagger screenshot where marked).
2. Double-check `.env` is git-ignored and was never committed;
   `.env.example` has placeholder values only.
3. Push.
   **Commit:** `Stage 6: publish to GitHub and write README`

## Full file list added

```
app/supabase_client.py     # Supabase client from env vars
app/auth_schemas.py        # SignUpRequest / LoginRequest
app/dependencies.py        # get_current_user — the one reusable guard
app/auth_routes.py         # /auth/signup, /auth/login, /auth/logout
app/protected_routes.py    # /protected/profile, /protected/dashboard
app/public_routes.py       # /public/info
main.py                    # updated: routers wired in, startup log added
```
