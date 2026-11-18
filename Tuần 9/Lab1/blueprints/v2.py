from flask import Blueprint, request, url_for

from .users_data import create_user, get_user

bp = Blueprint("v2", __name__)


@bp.get("/users/<int:uid>")
def get(uid):
    user = get_user(uid)
    if user is None:
        return {"error": "User not found"}, 404
    return {"id": uid, **user}


@bp.post("/users")
def create():
    data = request.get_json(silent=True)
    fields = ("first_name", "last_name", "email")
    if not isinstance(data, dict) or any(
        not isinstance(data.get(field), str) or not data[field].strip()
        for field in fields
    ):
        return {"error": "first_name, last_name and email must be non-empty strings"}, 400

    uid, user = create_user(*(data[field].strip() for field in fields))
    return {"id": uid, **user}, 201, {"Location": url_for("v2.get", uid=uid)}
