
import pytest

from app import create_app
from models import db, Book


@pytest.fixture()
def client():
    test_app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })

    with test_app.app_context():
        db.create_all()

        db.session.add_all([
            Book(
                title="Dune",
                author="Frank Herbert",
                genre="Sci-Fi",
                published_year=1965,
            ),
            Book(
                title="Foundation",
                author="Isaac Asimov",
                genre="Sci-Fi",
                published_year=1951,
            ),
            Book(
                title="The Hobbit",
                author="J.R.R. Tolkien",
                genre="Fantasy",
                published_year=1937,
            ),
            Book(
                title="The Fellowship of the Ring",
                author="J.R.R. Tolkien",
                genre="Fantasy",
                published_year=1954,
            ),
            Book(
                title="1984",
                author="George Orwell",
                genre="Dystopia",
                published_year=1949,
            ),
            Book(
                title="Animal Farm",
                author="George Orwell",
                genre="Dystopia",
                published_year=1945,
            ),
        ])

        db.session.commit()

    with test_app.test_client() as test_client:
        yield test_client

    with test_app.app_context():
        db.session.remove()
        db.drop_all()


def test_list_books_default_offset(client):
    response = client.get("/api/v1/books")

    assert response.status_code == 200

    data = response.get_json()
    assert data["strategy"] == "offset"
    assert len(data["items"]) == 6
    assert data["pagination"]["total"] == 6


def test_offset_pagination(client):
    response = client.get(
        "/api/v1/books?strategy=offset&limit=2&offset=0"
    )

    assert response.status_code == 200
    data = response.get_json()

    assert len(data["items"]) == 2
    assert data["pagination"]["limit"] == 2
    assert data["pagination"]["offset"] == 0
    assert data["pagination"]["has_next"] is True

    first_page_ids = {book["id"] for book in data["items"]}

    response = client.get(
        "/api/v1/books?strategy=offset&limit=2&offset=2"
    )

    assert response.status_code == 200
    second_page_ids = {
        book["id"] for book in response.get_json()["items"]
    }

    assert first_page_ids.isdisjoint(second_page_ids)


def test_cursor_pagination(client):
    response = client.get(
        "/api/v1/books?strategy=cursor&limit=2"
    )

    assert response.status_code == 200
    data = response.get_json()

    assert data["strategy"] == "cursor"
    assert len(data["items"]) == 2
    assert data["pagination"]["has_next"] is True

    next_cursor = data["pagination"]["next_cursor"]
    assert next_cursor is not None

    response = client.get(
        f"/api/v1/books?strategy=cursor&limit=2&cursor={next_cursor}"
    )

    assert response.status_code == 200
    next_data = response.get_json()

    first_page_ids = {book["id"] for book in data["items"]}
    second_page_ids = {
        book["id"] for book in next_data["items"]
    }

    assert first_page_ids.isdisjoint(second_page_ids)


def test_filter_by_genre(client):
    response = client.get("/api/v1/books?genre=Fantasy")

    assert response.status_code == 200

    books = response.get_json()["items"]
    assert len(books) == 2
    assert all(book["genre"] == "Fantasy" for book in books)


def test_multi_key_sort(client):
    response = client.get(
        "/api/v1/books?strategy=offset&sort=genre,-title"
    )

    assert response.status_code == 200

    books = response.get_json()["items"]
    actual = [(book["genre"], book["title"]) for book in books]

    assert actual == sorted(
        actual,
        key=lambda item: (item[0], item[1]),
    ) if False else actual  # Thay bằng kiểm tra bên dưới.

    # Genre tăng dần.
    assert [genre for genre, _ in actual] == sorted(
        genre for genre, _ in actual
    )

    # Trong mỗi genre, title giảm dần.
    genres = {genre for genre, _ in actual}

    for genre in genres:
        titles = [
            title for book_genre, title in actual
            if book_genre == genre
        ]
        assert titles == sorted(titles, reverse=True)


@pytest.mark.parametrize(
    "url",
    [
        "/api/v1/books?strategy=unknown",
        "/api/v1/books?limit=abc",
        "/api/v1/books?limit=0",
        "/api/v1/books?offset=-1",
        "/api/v1/books?sort=unknown_field",
        "/api/v1/books?strategy=cursor&cursor=abc",
    ],
)
def test_invalid_parameters_return_400(client, url):
    response = client.get(url)

    assert response.status_code == 400
