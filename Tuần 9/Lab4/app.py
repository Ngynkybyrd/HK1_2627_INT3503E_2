import os

from flask import Flask, jsonify, request

from gateway import dispatch


def create_app():
    app = Flask(__name__)
    v2_percent = int(os.environ.get("V2_PERCENT", "5"))
    if not 0 <= v2_percent <= 100:
        raise ValueError("V2_PERCENT must be between 0 and 100")
    app.config["V2_PERCENT"] = v2_percent

    @app.post("/orders")
    def create_order():
        body = request.get_json(silent=True)
        if not isinstance(body, dict):
            return jsonify(error="Expected a JSON object"), 400

        account_id = body.get("account_id")
        if not isinstance(account_id, str) or not account_id.strip():
            return jsonify(error="account_id must be a non-empty string"), 400

        version, order = dispatch(body)
        status = 201 if version == "v2" else 200
        return jsonify(order), status, {"X-Order-Handler": version}

    return app


app = create_app()


if __name__ == "__main__":
    app.run()
