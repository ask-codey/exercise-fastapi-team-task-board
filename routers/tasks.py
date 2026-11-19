"""Crew Board's tasks router: who may do what. For you to finish: the routes work, but none of them checks who is
asking yet.

Every request the router answers, with its status code and body (every error in the API's one shape, from
errors.py). The examples are for the tasks the API starts with, from migrations/0003_add_the_team.sql:
1 (Maya's), 2 and 4 (Theo's) and 3 (Sofia's).

Every request needs a signed-in user: its token in the Authorization: Bearer header.
  With no token:                401, detail "Not authenticated" (oauth2_scheme answers it)
  With a made-up or expired one: 401, detail "Your token isn't valid. Sign in again."
  Both with the header WWW-Authenticate: Bearer.

  GET    /tasks         Anyone signed in. 200, every task, in id order:
                        [{"id": 1, "title": "Book the room for the sprint demo", "owner_id": 1, "done": false}, ...]
  GET    /tasks/2       Anyone signed in. 200, task 2.
                        404 when there's no such task: detail "There's no task 99."
  POST   /tasks         Anyone signed in. Body {"title": "Plan the team retro"}.
                        201, the new task, owned by whoever is signed in, not done yet:
                        {"id": 5, "title": "Plan the team retro", "owner_id": 2, "done": false}
                        The owner is always the signed-in user: an owner_id in the body changes nothing.
  PATCH  /tasks/2       The task's owner, or an admin. Body with title, done or both: {"done": true}.
                        200, the task with only the fields sent changed.
                        403 for anyone else: detail "Only the task's owner or an admin may change it."
                        404 when there's no such task (before the owner is checked): detail "There's no task 99."
  DELETE /tasks/3       Admins only. 204, no body, and the task is gone.
                        403 for a member: detail "You need the admin role for that." (whether the task is there or not)
                        404 for an admin when there's no such task: detail "There's no task 99."
"""
import sqlite3

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

import crew_data
from database import get_db

router = APIRouter(prefix="/tasks", tags=["tasks"])


class TaskIn(BaseModel):
    title: str = Field(min_length=1, max_length=80)
    owner_id: int


class TaskChange(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=80)
    done: bool | None = None


def no_task(task_id):
    return HTTPException(status_code=404, detail=f"There's no task {task_id}.")


@router.get("")
def list_tasks(conn: sqlite3.Connection = Depends(get_db, scope="function")):
    return crew_data.all_tasks(conn)


@router.get("/{task_id}")
def read_task(task_id: int, conn: sqlite3.Connection = Depends(get_db, scope="function")):
    task = crew_data.find_task(conn, task_id)
    if task is None:
        raise no_task(task_id)
    return task


@router.post("", status_code=201)
def add_task(new_task: TaskIn, conn: sqlite3.Connection = Depends(get_db, scope="function")):
    task_id = crew_data.add_task(conn, new_task.title, new_task.owner_id)
    return crew_data.find_task(conn, task_id)


@router.patch("/{task_id}")
def change_task(task_id: int, change: TaskChange, conn: sqlite3.Connection = Depends(get_db, scope="function")):
    task = crew_data.find_task(conn, task_id)
    if task is None:
        raise no_task(task_id)
    changed = {**task, **change.model_dump(exclude_unset=True)}
    return crew_data.update_task(conn, task_id, changed["title"], changed["done"])


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, conn: sqlite3.Connection = Depends(get_db, scope="function")):
    if not crew_data.delete_task(conn, task_id):
        raise no_task(task_id)
