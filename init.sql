-- Runs automatically the first time the Postgres container starts with an
-- empty data volume (via docker-entrypoint-initdb.d). On later starts,
-- Postgres skips this entirely since the volume already has data --
-- that's also how the seeded example tasks avoid being duplicated.

CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    done BOOLEAN NOT NULL DEFAULT FALSE
);

INSERT INTO tasks (title, done)
SELECT * FROM (VALUES
    ('Buy milk', FALSE),
    ('Walk the dog', FALSE),
    ('Read a book', TRUE)
) AS seed(title, done)
WHERE NOT EXISTS (SELECT 1 FROM tasks);
