-- Migration 2: the tasks table, one row for each task on the board.
--   id        a whole number SQLite gives each new task (INTEGER PRIMARY KEY)
--   title     what needs doing: text, never missing
--   owner_id  the id of the user who owns the task: a whole number, never missing, that REFERENCES users (id)
--   done      0 while the task is open, 1 once it's done (SQLite keeps True and False as 1 and 0)
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    owner_id INTEGER NOT NULL REFERENCES users (id),
    done INTEGER NOT NULL DEFAULT 0
);
