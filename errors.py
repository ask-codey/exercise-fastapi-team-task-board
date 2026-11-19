"""Crew Board's one error shape. Ready to use: you don't need to change this file.

Every error answer is JSON with the status code, its standard title, what went wrong, and, for a request that breaks
the rules, a list of the fields with problems, modeled on RFC 9457's problem details:

  {"status": 401, "title": "Unauthorized", "detail": "Not authenticated"}
  {"status": 403, "title": "Forbidden", "detail": "You need the admin role for that."}
  {"status": 422, "title": "Unprocessable Content", "detail": "The request isn't valid.",
   "problems": [{"field": "title", "message": "Field required"}]}

An HTTPException you raise keeps its headers, so a 401's WWW-Authenticate: Bearer header reaches the caller.
"""
from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


def problem(status, detail, problems=None, headers=None):
    """The one error shape: the status, its standard title, what went wrong, and any field problems."""
    body = {"status": status, "title": HTTPStatus(status).phrase, "detail": detail}
    if problems is not None:
        body["problems"] = problems
    return JSONResponse(status_code=status, content=body, headers=headers)


def add_error_handlers(app: FastAPI):
    """Turns every error into the one shape: 422 for a request that breaks the rules, every HTTPException (yours and
    FastAPI's own, such as 401, 403 and 404) with its headers, and 500 for a crash."""

    @app.exception_handler(RequestValidationError)
    def validation_error(request: Request, exc: RequestValidationError):
        problems = [{"field": error["loc"][-1], "message": error["msg"]} for error in exc.errors()]
        return problem(422, "The request isn't valid.", problems)

    @app.exception_handler(StarletteHTTPException)
    def http_error(request: Request, exc: StarletteHTTPException):
        return problem(exc.status_code, exc.detail, headers=exc.headers)

    @app.exception_handler(Exception)
    def server_error(request: Request, exc: Exception):
        return problem(500, "Something went wrong on our side.")
