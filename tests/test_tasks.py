# Tests for Crew Board's rules about who may do what. Run them with: pytest (in the exercise folder, with the virtual
# environment active). They set their own JWT_SECRET, so you don't need to set one to run them.
# Before every test, the fixture throwaway_database makes a new database file in pytest's tmp_path, runs the
# migrations on it (the users and tasks tables, the practice team and their four tasks), and tells the app to use that
# file instead of crew_board.db (app.dependency_overrides). The fixtures maya, theo and sofia sign in through
# POST /auth/token, the way the docs page's Authorize button does, and give back the header that sends their token.
# Each test sends requests with TestClient as one of the team, or with no token at all, and checks the answers.
# A failing test says what it sent, what it expected and what came back.
# You don't need to change this file.
import os

os.environ["JWT_SECRET"] = "test-secret-for-the-crew-board-tests-only"

import sqlite3

import pytest
from fastapi.testclient import TestClient

from database import get_db, migrate, open_db
from main import app
from security import create_token

# raise_server_exceptions=False: a crash comes back as the 500 answer a caller would get, instead of stopping the test.
client = TestClient(app, raise_server_exceptions=False)

TASK_1 = {"id": 1, "title": "Book the room for the sprint demo", "owner_id": 1, "done": False}
TASK_2 = {"id": 2, "title": "Write the release notes", "owner_id": 2, "done": False}
TASK_3 = {"id": 3, "title": "Fix the typo on the sign-in page", "owner_id": 3, "done": True}
TASK_4 = {"id": 4, "title": "Order new whiteboard markers", "owner_id": 2, "done": False}
RETRO = {"title": "Plan the team retro"}

TITLES = {401: "Unauthorized", 403: "Forbidden", 404: "Not Found"}
NOT_SIGNED_IN = "Not authenticated"
NOT_VALID = "Your token isn't valid. Sign in again."
NOT_THE_OWNER = "Only the task's owner or an admin may change it."
NOT_AN_ADMIN = "You need the admin role for that."


@pytest.fixture(autouse=True)
def throwaway_database(tmp_path):
    """Before every test: a new database file in tmp_path, migrated, with the practice team and their four tasks,
    that every request uses instead of crew_board.db. After the test: the app's own get_db again. Gives the test the
    file's path."""
    path = tmp_path / "crew_board_test.db"
    conn = open_db(path)
    migrate(conn)
    conn.close()

    def get_test_db():
        conn = open_db(path)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    app.dependency_overrides[get_db] = get_test_db
    yield path
    app.dependency_overrides.clear()


def sign_in(email, password):
    """Signs in with POST /auth/token, the form the docs page's Authorize button sends, and gives back the header
    that sends the token: {"Authorization": "Bearer <the token>"}."""
    response = client.post("/auth/token", data={"username": email, "password": password})
    assert response.status_code == 200, f"Signing in as {email} should answer 200, but it answered {response.text}"
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def maya():
    """Maya, user 1, an admin."""
    return sign_in("maya@example.com", "practice-maya")


@pytest.fixture
def theo():
    """Theo, user 2, a member, who owns tasks 2 and 4."""
    return sign_in("theo@example.com", "practice-theo")


@pytest.fixture
def sofia():
    """Sofia, user 3, a member, who owns task 3."""
    return sign_in("sofia@example.com", "practice-sofia")


def rows(path, sql, params=()):
    """Reads rows straight from the database file, the way a check after the request would, as a list of tuples."""
    conn = sqlite3.connect(path)
    found = conn.execute(sql, params).fetchall()
    conn.close()
    return found


def body_of(response):
    """The answer's JSON, or its text when the answer isn't JSON."""
    try:
        return response.json()
    except ValueError:
        return response.text


def check_status(request, response, status):
    """Fails with a message that says what the request answered, when its status code isn't the one expected."""
    assert response.status_code == status, (
        f"{request} should answer {status}, but it answered {response.status_code} with {response.text}"
    )


def check_body(request, response, body):
    """Fails with a message that says what came back, when the body isn't the one expected."""
    assert body_of(response) == body, f"{request} should answer {body!r}, but it answered {body_of(response)!r}."


def check_problem(request, response, status, detail):
    """Checks an error answer: its status code, then the one error shape, part by part."""
    check_status(request, response, status)
    check_body(request, response, {"status": status, "title": TITLES[status], "detail": detail})


def check_bearer_header(request, response):
    """A 401 says how to sign in: its WWW-Authenticate header is Bearer."""
    header = response.headers.get("www-authenticate")
    assert header == "Bearer", (
        f"{request} answered 401, so its WWW-Authenticate header should be 'Bearer', but it's {header!r}."
    )


def test_1_get_tasks_with_no_token_answers_401_not_authenticated():
    response = client.get("/tasks")
    check_problem("GET /tasks with no token", response, 401, NOT_SIGNED_IN)
    check_bearer_header("GET /tasks with no token", response)


def test_2_get_tasks_with_a_made_up_token_answers_401_your_token_isnt_valid():
    response = client.get("/tasks", headers={"Authorization": "Bearer not-a-real-token"})
    check_problem("GET /tasks with a made-up token", response, 401, NOT_VALID)
    check_bearer_header("GET /tasks with a made-up token", response)


def test_3_get_tasks_with_an_expired_token_answers_401_your_token_isnt_valid():
    expired = {"Authorization": f"Bearer {create_token(2, minutes=-5)}"}
    response = client.get("/tasks", headers=expired)
    check_problem("GET /tasks with Theo's token from 5 minutes after it expired", response, 401, NOT_VALID)
    check_bearer_header("GET /tasks with an expired token", response)


def test_4_get_tasks_with_a_token_for_user_99_who_isnt_there_answers_401():
    nobody = {"Authorization": f"Bearer {create_token(99)}"}
    response = client.get("/tasks", headers=nobody)
    check_problem("GET /tasks with a real token for user 99, who isn't in the database", response, 401, NOT_VALID)


def test_5_get_tasks_as_theo_answers_200_with_the_4_tasks(theo):
    response = client.get("/tasks", headers=theo)
    check_status("GET /tasks as Theo", response, 200)
    check_body("GET /tasks as Theo", response, [TASK_1, TASK_2, TASK_3, TASK_4])


def test_6_get_tasks_2_as_sofia_answers_200_with_theos_task_2(sofia):
    response = client.get("/tasks/2", headers=sofia)
    check_status("GET /tasks/2 as Sofia", response, 200)
    check_body("GET /tasks/2 as Sofia", response, TASK_2)


def test_7_get_tasks_99_as_theo_answers_404_theres_no_task_99(theo):
    response = client.get("/tasks/99", headers=theo)
    check_problem("GET /tasks/99 as Theo", response, 404, "There's no task 99.")


def test_8_post_tasks_as_theo_answers_201_with_task_5_owned_by_theo(theo):
    response = client.post("/tasks", json=RETRO, headers=theo)
    check_status("POST /tasks as Theo", response, 201)
    check_body("POST /tasks as Theo", response, {"id": 5, "title": "Plan the team retro", "owner_id": 2, "done": False})


def test_9_post_tasks_as_theo_with_owner_id_3_in_the_body_still_makes_theos_task(theo, throwaway_database):
    response = client.post("/tasks", json={"title": "Plan the team retro", "owner_id": 3}, headers=theo)
    check_status("POST /tasks as Theo, with owner_id 3 in the body", response, 201)
    saved = rows(throwaway_database, "SELECT owner_id FROM tasks WHERE id = 5")
    assert saved == [(2,)], (
        f"A new task's owner is the signed-in user, Theo (2), whatever the body says, but task 5's owner_id is {saved}."
    )


def test_10_post_tasks_with_no_token_answers_401_and_saves_nothing(throwaway_database):
    response = client.post("/tasks", json=RETRO)
    check_problem("POST /tasks with no token", response, 401, NOT_SIGNED_IN)
    count = rows(throwaway_database, "SELECT COUNT(*) FROM tasks")[0][0]
    assert count == 4, f"A refused request must save nothing: the tasks table has {count} rows, not 4."


def test_11_patch_tasks_2_as_theo_its_owner_answers_200_with_done_true(theo):
    response = client.patch("/tasks/2", json={"done": True}, headers=theo)
    check_status("PATCH /tasks/2 as Theo, its owner", response, 200)
    check_body("PATCH /tasks/2 as Theo, its owner", response, {**TASK_2, "done": True})


def test_12_patch_tasks_3_as_theo_answers_403_and_sofias_task_stays_as_it_was(theo, throwaway_database):
    response = client.patch("/tasks/3", json={"title": "Theo was here"}, headers=theo)
    check_problem("PATCH /tasks/3 (Sofia's) as Theo", response, 403, NOT_THE_OWNER)
    saved = rows(throwaway_database, "SELECT title FROM tasks WHERE id = 3")
    assert saved == [(TASK_3["title"],)], f"A refused change must change nothing, but task 3's title is now {saved}."


def test_13_patch_tasks_3_as_maya_an_admin_answers_200(maya):
    response = client.patch("/tasks/3", json={"done": False}, headers=maya)
    check_status("PATCH /tasks/3 (Sofia's) as Maya, an admin", response, 200)
    check_body("PATCH /tasks/3 (Sofia's) as Maya, an admin", response, {**TASK_3, "done": False})


def test_14_patch_tasks_99_as_theo_answers_404_theres_no_task_99(theo):
    response = client.patch("/tasks/99", json={"done": True}, headers=theo)
    check_problem("PATCH /tasks/99 as Theo", response, 404, "There's no task 99.")


def test_15_patch_tasks_2_with_no_token_answers_401():
    response = client.patch("/tasks/2", json={"done": True})
    check_problem("PATCH /tasks/2 with no token", response, 401, NOT_SIGNED_IN)


def test_16_delete_tasks_3_as_maya_answers_204_and_then_get_tasks_3_answers_404(maya):
    response = client.delete("/tasks/3", headers=maya)
    check_status("DELETE /tasks/3 as Maya, an admin", response, 204)
    assert response.content == b"", f"DELETE /tasks/3 should answer with no body, but it answered {response.text}"
    after = client.get("/tasks/3", headers=maya)
    check_problem("GET /tasks/3 after the delete", after, 404, "There's no task 3.")


def test_17_delete_tasks_3_as_sofia_its_owner_answers_403_and_the_task_stays(sofia, throwaway_database):
    response = client.delete("/tasks/3", headers=sofia)
    check_problem("DELETE /tasks/3 as Sofia, a member who owns it", response, 403, NOT_AN_ADMIN)
    count = rows(throwaway_database, "SELECT COUNT(*) FROM tasks WHERE id = 3")[0][0]
    assert count == 1, "Only an admin may delete: after Sofia's refused delete, task 3 must still be there."


def test_18_delete_tasks_99_as_maya_answers_404_theres_no_task_99(maya):
    response = client.delete("/tasks/99", headers=maya)
    check_problem("DELETE /tasks/99 as Maya", response, 404, "There's no task 99.")


def test_19_delete_tasks_99_as_theo_answers_403_before_looking_for_the_task(theo):
    response = client.delete("/tasks/99", headers=theo)
    check_problem("DELETE /tasks/99 as Theo, a member", response, 403, NOT_AN_ADMIN)


def test_20_delete_tasks_3_with_no_token_answers_401():
    response = client.delete("/tasks/3")
    check_problem("DELETE /tasks/3 with no token", response, 401, NOT_SIGNED_IN)
