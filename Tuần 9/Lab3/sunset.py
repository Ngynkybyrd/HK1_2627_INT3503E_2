from datetime import datetime, timezone
from email.utils import format_datetime
from functools import wraps
import logging

from flask import jsonify, make_response, request

log = logging.getLogger("sunset")


def deprecate_at(sunset_date, replacement=None):
    def decorate(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            log.warning("deprecated_call %s %s", request.path, request.remote_addr)
            date = format_datetime(sunset_date, usegmt=True)
            if datetime.now(timezone.utc) >= sunset_date:
                return jsonify(error="gone", sunset=date, use_instead=replacement), 410

            response = make_response(fn(*args, **kwargs))
            response.headers["Sunset"] = date
            response.headers["Deprecation"] = "true"
            if replacement:
                response.headers["Link"] = f'<{replacement}>; rel="successor-version"'
            return response

        return wrapper

    return decorate
