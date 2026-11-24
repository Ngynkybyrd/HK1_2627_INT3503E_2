from uuid import uuid4


def v1_create_order(body):
    return {"account_id": body["account_id"], "status": "created"}


def v2_create_order(body):
    return {
        "account_id": body["account_id"],
        "status": "created",
        "order_id": str(uuid4()),
    }
