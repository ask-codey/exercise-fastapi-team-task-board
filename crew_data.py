"""Crew Board's data module: every SQL statement the API runs, in one place. Ready to use: you don't need to change
this file.

Each function takes an open connection, conn, whose rows read by column name (sqlite3.Row), and gives back plain
Python values: a new row's id, a dictionary, a list of dictionaries, True or False, or None for a row that isn't there.
Nothing here knows about FastAPI or HTTP, and nothing here commits: get_db commits once the whole request has worked.
Every value goes into the SQL through a ? placeholder, never into the SQL's text.

  find_user(conn, user_id)              the user with that id, as {"id", "name", "email", "role"}, or None
  find_user_by_email(conn, email)       the same, with "password_hash" added (for signing in only), or None
  all_tasks(conn)                       every task, in id order, each {"id", "title", "owner_id", "done"}
  find_task(conn, task_id)              the task with that id, or None
  add_task(conn, title, owner_id)       adds a task owned by that user, not done yet, and returns its id
  update_task(conn, task_id, title, done)   sets the task's title and done, and returns the task
  delete_task(conn, task_id)            deletes the task: True when it was there, False when it wasn't
"""


def task_from_row(row):
    """A task row as a dictionary, with done as True or False (SQLite keeps it as 1 or 0)."""
    task = dict(row)
    task["done"] = bool(task["done"])
    return task


def find_user(conn, user_id):
    row = conn.execute("SELECT id, name, email, role FROM users WHERE id = ?", (user_id,)).fetchone()
    return None if row is None else dict(row)


def find_user_by_email(conn, email):
    row = conn.execute(
        "SELECT id, name, email, role, password_hash FROM users WHERE email = ?", (email,)
    ).fetchone()
    return None if row is None else dict(row)


def all_tasks(conn):
    rows = conn.execute("SELECT id, title, owner_id, done FROM tasks ORDER BY id").fetchall()
    return [task_from_row(row) for row in rows]


def find_task(conn, task_id):
    row = conn.execute("SELECT id, title, owner_id, done FROM tasks WHERE id = ?", (task_id,)).fetchone()
    return None if row is None else task_from_row(row)


def add_task(conn, title, owner_id):
    cursor = conn.execute("INSERT INTO tasks (title, owner_id, done) VALUES (?, ?, 0)", (title, owner_id))
    return cursor.lastrowid


def update_task(conn, task_id, title, done):
    conn.execute("UPDATE tasks SET title = ?, done = ? WHERE id = ?", (title, int(done), task_id))
    return find_task(conn, task_id)


def delete_task(conn, task_id):
    cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    return cursor.rowcount == 1
