"""Lab 1: functional and schema checks for the Books API."""

import pytest
from jsonschema import ValidationError, validate

from tools import get_book_schema


def test_list_books_empty(client):
    response = client.get("/books")
    assert response.status_code == 200
    assert response.get_json() == []


def test_get_missing_book(client):
    response = client.get("/books/9999")
    assert response.status_code == 404
    assert response.get_json()["code"] == "NOT_FOUND"


def test_create_book_requires_title(client):
    response = client.post("/books", json={"author": "Author"})
    assert response.status_code == 400
    assert any(error["field"] == "title" for error in response.get_json()["errors"])


def test_create_delete_and_get_book(client):
    created = client.post("/books", json={"title": "Book", "author": "Author"})
    assert created.status_code == 201
    book_id = created.get_json()["id"]
    deleted = client.delete(f"/books/{book_id}")
    assert deleted.status_code == 204
    assert deleted.data == b""
    assert client.get(f"/books/{book_id}").status_code == 404


def test_book_response_schema_rejects_unknown_field(client):
    response = client.post("/books", json={
        "title": "API Design Patterns",
        "author": "J.J. Geewax",
        "year": 2021,
        "isbn": "9781617295850",
    })
    assert response.status_code == 201
    book = response.get_json()
    schema = get_book_schema()
    validate(instance=book, schema=schema)

    with pytest.raises(ValidationError, match="Additional properties"):
        validate(instance={**book, "unexpected": "value"}, schema=schema)
