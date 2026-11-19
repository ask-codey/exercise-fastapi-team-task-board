"""Crew Board's dependencies for who may do what: the signed-in user, and a check for a role. For you to write.

  oauth2_scheme        reads the token from the request's Authorization: Bearer header. With no token, it answers
                       401 {"status": 401, "title": "Unauthorized", "detail": "Not authenticated"} by itself.
  get_current_user     decodes the token with SECRET_KEY and ALGORITHM from security.py and loads the user whose id is
                       in its "sub", from the database, as {"id", "name", "email", "role"}. A token that's made up,
                       changed or expired, or whose user isn't there any more, answers 401 with the detail
                       "Your token isn't valid. Sign in again." and the header WWW-Authenticate: Bearer.
  CurrentUser          the type hint a route uses to get the signed-in user: user: CurrentUser
  require_role(role)   makes a dependency that gets the signed-in user and answers 403 with the detail
                       "You need the admin role for that." (with the role it was given) when their role isn't role.
"""
import sqlite3
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

import crew_data
from database import get_db
from security import ALGORITHM, SECRET_KEY

# Write oauth2_scheme, get_current_user, CurrentUser and require_role here, in that order.
