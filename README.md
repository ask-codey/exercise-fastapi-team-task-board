# Exercise: Team Task Board

Exercise code for the lesson **Exercise: Team Task Board** in the Python Web APIs course on [ask-codey.com](https://www.ask-codey.com).

Crew Board is a small team's task board: Maya is the admin, and Theo and Sofia are members. Its API keeps the team and their tasks in SQLite, and its sign-in route works: `POST /auth/token` checks an email and password and hands back a signed token. But none of the task routes asks for that token, so anyone can read, add, change or delete anything. You'll add the rules the team agreed on: anyone signed in reads the board and adds tasks, members change only their own tasks, and only an admin deletes. The work is all authorization: two dependencies and the task routes that use them. Tests sign in as each of the team, and with no token at all, and check every rule.

## What's here

- `dependencies.py`: the dependencies, for you to write: `oauth2_scheme`, `get_current_user`, `CurrentUser` and `require_role`. The comment at its top says exactly what each one does and answers.
- `routers/tasks.py`: the task routes, for you to finish. They work, but none of them checks who is asking. The comment at its top lists every request, who may send it, and the status code and body each one answers.
- `security.py`: the sign-in helpers, with pwdlib and PyJWT: `verify_password`, `create_token`, and the `SECRET_KEY` and `ALGORITHM` your `get_current_user` needs to check a token. A token's payload holds the user's id, as text, in `"sub"`. Ready to use.
- `routers/auth.py`: the sign-in route, `POST /auth/token`. Ready to use.
- `crew_data.py`: the data module, with every SQL statement the API runs: `find_user`, `all_tasks`, `find_task`, `add_task`, `update_task` and `delete_task`. The comment at its top says what each one takes and gives back. Ready to use.
- `database.py`: where the database file is, `open_db`, the migrations and `get_db`, which gives every request its own connection. Ready to use.
- `migrations/`: the users table, the tasks table, and the practice team with their four tasks. Ready to use.
- `errors.py`: the API's one error shape, `{"status": ..., "title": ..., "detail": ...}`, for every error, with the headers an `HTTPException` carries. Ready to use.
- `main.py`: makes the app, runs the migrations when it starts, adds both routers and the error handlers. Ready to use.
- `tests/test_tasks.py`: tests that make a throwaway database for every test, sign in as each of the team, and check every rule. You don't need to change this file.
- `requirements.txt`: the packages the app and the tests need, at exact versions. Ready to use.
- `pytest.ini`: tells pytest where the tests are and where to find your code. Ready to use.
- `.gitignore`: tells Git to leave out the virtual environment, the files Python and pytest make as they run, and database files (`*.db`). Ready to use.

The practice team, for signing in on the docs page:

| Name | Email (the username) | Password | Role | Owns |
|---|---|---|---|---|
| Maya | `maya@example.com` | `practice-maya` | admin | task 1 |
| Theo | `theo@example.com` | `practice-theo` | member | tasks 2 and 4 |
| Sofia | `sofia@example.com` | `practice-sofia` | member | task 3 |

## Before you start

The app and the tests need FastAPI, pwdlib, PyJWT and pytest, and they go in a virtual environment: a private set of packages for this folder only. In VS Code's terminal, in this folder, run these three commands.

On Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

On a Mac (zsh):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

- The first command makes the virtual environment, in a folder named `.venv`.
- The second turns it on for this terminal: the prompt starts with `(.venv)` from then on.
- The third installs the packages `requirements.txt` lists into it. It takes a minute: FastAPI brings several packages with it, and pwdlib brings Argon2.

*Virtual Environments and pip* explains all three. The `.venv` folder is in `.gitignore`, so Git leaves it out: these commands make it again on any computer.

If PowerShell answers that running scripts is disabled on this system, run this once, then run the second command again:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Each new terminal starts with the virtual environment off. If the prompt doesn't start with `(.venv)`, run the second command again. (VS Code often turns it on for you.)

**The app signs its tokens with a secret** it reads from the environment variable `JWT_SECRET`, so the secret is never written in the code. Before you start the app, set a practice one in the same terminal. On Windows (PowerShell):

```powershell
$env:JWT_SECRET = "change-me-practice-secret-for-crew-board"
```

On a Mac (zsh):

```bash
export JWT_SECRET="change-me-practice-secret-for-crew-board"
```

It lasts until you close that terminal; a new terminal needs it again. Without it, the app stops at once with *JWT_SECRET isn't set*. The tests set their own, so `pytest` works without it.

## Run it

```bash
fastapi dev main.py
```

Then open `http://127.0.0.1:8000/docs` in your browser. The docs page lists every route the app has. Click **Authorize**, type one of the team's emails as the username and their password, and click **Authorize** again: the page signs in at `/auth/token` and sends the token with every request you try. Then click a route, **Try it out** and **Execute**. To try someone else, click **Authorize**, **Logout**, and sign in again. Stop the app with **Ctrl+C**.

When the app starts, it runs the migrations on `crew_board.db`, a file beside `main.py` (it's made the first time): the two tables, then the practice team and their four tasks. To start again from those four tasks, stop the app, delete `crew_board.db`, and start it again.

## Check your work

```bash
pytest
```

No server needs to be running, and your `crew_board.db` is never touched: before every test, the tests make a new database file in a temporary folder, run the migrations on it, and point the app at it.

At first 8 of the 20 tests pass: the requests a signed-in user is allowed to make, such as Theo reading the board or Maya deleting a task, work already, because the routes don't check anything yet. The other 12 fail, and each one's message says what it sent, what it expected and what came back, for example *GET /tasks with no token should answer 401, but it answered 200 with [...]*. Each part you finish turns its tests green. When you're done, pytest's last line says `20 passed`.

## The rules

- Write `oauth2_scheme`, `get_current_user`, `CurrentUser` and `require_role` in `dependencies.py`, and change the routes in `routers/tasks.py`. Don't change the other files or the tests.
- Every task route needs a signed-in user. A missing token is answered by `oauth2_scheme` itself; a made-up or expired token, or one for a user who isn't in the database, answers 401 with the detail `Your token isn't valid. Sign in again.` and the header `WWW-Authenticate: Bearer`.
- A new task's owner is always the signed-in user's id. Its body has only a title: an `owner_id` sent in the body changes nothing.
- Only a task's owner, or an admin, may change it. Anyone else gets 403 with the detail `Only the task's owner or an admin may change it.` A task that isn't there answers 404 first.
- Only an admin may delete a task. A member gets 403 with the detail `You need the admin role for that.`, whether the task is there or not.
- Every check uses the user `get_current_user` loaded, never an id or a role the request sends.

## Tips

- **Start with `get_current_user`.** *Requiring a Signed-In User* writes it: `oauth2_scheme` hands it the token, `jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])` checks it, `except jwt.InvalidTokenError` catches a made-up, changed or expired one, and `crew_data.find_user(conn, int(payload["sub"]))` loads the user. Give it `conn: sqlite3.Connection = Depends(get_db, scope="function")` for the database.
- **Then `CurrentUser`,** `Annotated[dict, Depends(get_current_user)]`, and add `user: CurrentUser` to every task route. Tests 1 to 4 turn green.
- **The new task's owner is `user["id"]`.** Take `owner_id` out of `TaskIn`, and pass `user["id"]` to `crew_data.add_task`.
- **The PATCH route checks ownership after the 404,** as *Roles and Ownership: 401 or 403* shows: compare the task's `owner_id` with `user["id"]`, and let an admin through.
- **`require_role(role)` is a function that makes a dependency.** It defines `check_role(user: CurrentUser)`, which raises the 403 or returns the user, and returns `check_role`. The delete route uses it with `dependencies=[Depends(require_role("admin"))]` on its decorator.

## Hand it in

When it works, push your solution to a public repo of your own on GitHub, then paste that repo's address into **Submit your exercise** on the lesson page at [ask-codey.com](https://www.ask-codey.com). That's what completes the lesson. The lesson page shows the Git commands, step by step.
