"""Crew Board's task board API: the app, its routers, the migrations it runs at startup, and the error handlers that
give every error one shape. Ready to use: you don't need to change this file.

Before you start it, set JWT_SECRET in the terminal (the README's Before you start shows how). Then run it with:
  fastapi dev main.py
and open http://127.0.0.1:8000/docs. Click Authorize, sign in as one of the team (maya@example.com with the password
practice-maya, theo@example.com with practice-theo, or sofia@example.com with practice-sofia), and try every route.
Stop it with Ctrl+C.

When the app starts, lifespan() runs every migration script in migrations/ that the database file, crew_board.db,
hasn't had yet: the users and tasks tables, then the practice team and their four tasks. The tests don't start the app
this way: each test makes its own throwaway database and runs the migrations on it.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import DATABASE_PATH, migrate, open_db
from errors import add_error_handlers
from routers import auth, tasks


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs once when the app starts: brings the database file up to date with the migration scripts."""
    conn = open_db(DATABASE_PATH)
    migrate(conn)
    conn.close()
    yield


app = FastAPI(title="Crew Board", lifespan=lifespan)
app.include_router(auth.router)
app.include_router(tasks.router)
add_error_handlers(app)
