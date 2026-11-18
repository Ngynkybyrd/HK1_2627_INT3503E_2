from flask import Blueprint

from .users_data import get_user

bp = Blueprint("v1", __name__)


@bp.after_request
def add_sunset(response):
    # Ngày minh họa: v1 vẫn hoạt động, đồng thời thông báo kế hoạch ngừng.
    response.headers["Sunset"] = "Fri, 31 Dec 2027 23:59:59 GMT"
    return response


@bp.get("/users/<int:uid>")
def get(uid):
    user = get_user(uid)
    if user is None:
        return {"error": "User not found"}, 404
    return {
        "id": uid,
        "full_name": f"{user['first_name']} {user['last_name']}",
        "email": user["email"],
    }
