"""Crew Board's sign-in route. Ready to use: you don't need to change this file.

  POST /auth/token     A form, not JSON (the OAuth2 password form, so the docs page's Authorize button can use it):
                       username=theo@example.com and password=practice-theo.
                       200, {"access_token": "<a signed token>", "token_type": "bearer"}
                       401 for an email nobody has, or a wrong password, with the same detail for both:
                       "The email or password isn't right."

The practice team, from migrations/0003_add_the_team.sql:

  id  name   email              password        role
  1   Maya   maya@example.com   practice-maya   admin
  2   Theo   theo@example.com   practice-theo   member
  3   Sofia  sofia@example.com  practice-sofia  member
"""
import sqlite3
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

import crew_data
from database import get_db
from security import create_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token")
def sign_in(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    conn: sqlite3.Connection = Depends(get_db, scope="function"),
):
    user = crew_data.find_user_by_email(conn, form.username)
    if user is None or not verify_password(form.password, user["password_hash"]):
        raise HTTPException(
            status_code=401,
            detail="The email or password isn't right.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": create_token(user["id"]), "token_type": "bearer"}
