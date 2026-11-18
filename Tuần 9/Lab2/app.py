from functools import wraps

from flask import Flask, jsonify, request

app = Flask(__name__)
app.json.ensure_ascii = False

LATEST = "2"
SUPPORTED = {"1", "2", "2024-06-20"}
USERS = {
    1: {"first_name": "Văn", "last_name": "Nguyễn", "email": "a@vnu.vn"},
    2: {"first_name": "Trang", "last_name": "Trần", "email": "b@vnu.vn"},
}


def api_version(supported=SUPPORTED, default=LATEST):
    def decorate(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            version = request.headers.get("X-API-Version", default)
            if version not in supported:
                return jsonify(error="unsupported version"), 400

            body, status = fn(version, *args, **kwargs)
            response = jsonify(body)
            response.status_code = status
            response.headers["X-API-Version-Served"] = version
            return response

        return wrapper

    return decorate


@app.get("/users/<int:uid>")
@api_version()
def get_user(version, uid):
    user = USERS.get(uid)
    if user is None:
        return {"error": "User not found"}, 404
    if version == "1":
        return {
            "id": uid,
            "full_name": f"{user['first_name']} {user['last_name']}",
        }, 200
    return {"id": uid, **user}, 200


if __name__ == "__main__":
    app.run(debug=True)
