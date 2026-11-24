from datetime import timedelta
from email.utils import format_datetime
from unittest import TestCase
from unittest.mock import patch

from app import V1_SUNSET, app


def main():
    client = app.test_client()
    url = "/api/v1/users/1"
    sunset = format_datetime(V1_SUNSET, usegmt=True)

    with TestCase().assertLogs("sunset", level="WARNING") as logs:
        with patch("sunset.datetime") as clock:
            clock.now.return_value = V1_SUNSET - timedelta(seconds=1)
            before = client.get(url)
            clock.now.return_value = V1_SUNSET
            at_sunset = client.get(url)

    assert before.status_code == 200
    assert "full_name" in before.get_json()
    assert before.headers["Sunset"] == sunset
    assert before.headers["Deprecation"] == "true"
    assert before.headers["Link"] == '</api/v2/users>; rel="successor-version"'

    assert at_sunset.status_code == 410
    assert at_sunset.get_json() == {
        "error": "gone",
        "sunset": sunset,
        "use_instead": "/api/v2/users",
    }

    expected_log = f"deprecated_call {url} 127.0.0.1"
    assert [record.getMessage() for record in logs.records] == [expected_log] * 2

    print("1. Before sunset: HTTP 200, headers OK")
    print("2. At sunset: HTTP 410 Gone")
    print(f"3. Logs: {expected_log} ({len(logs.records)} calls)")


if __name__ == "__main__":
    main()
