"""Crew Board's sign-in helpers: passwords checked with pwdlib (Argon2) and tokens made with PyJWT. Ready to use: you
don't need to change this file.

The tokens are signed with the secret in the environment variable JWT_SECRET (the README's Before you start shows how
to set it; the tests set their own). A token's payload holds the user's id as text in "sub" and when it expires in
"exp", an hour after sign-in:

  {"sub": "2", "exp": 1795449600}

Your get_current_user, in dependencies.py, checks a token with SECRET_KEY and ALGORITHM from this file.
"""
import os
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

SECRET_KEY = os.environ.get("JWT_SECRET", "")
if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET isn't set. The README's Before you start shows how to set it.")

ALGORITHM = "HS256"
TOKEN_MINUTES = 60

password_hash = PasswordHash.recommended()


def verify_password(password, hashed):
    """True when password matches the stored Argon2 hash."""
    return password_hash.verify(password, hashed)


def create_token(user_id, minutes=TOKEN_MINUTES):
    """A signed token for the user with this id, which expires after minutes (an hour unless you say otherwise; the
    tests make an expired one with a negative number)."""
    expires = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    return jwt.encode({"sub": str(user_id), "exp": expires}, SECRET_KEY, algorithm=ALGORITHM)
