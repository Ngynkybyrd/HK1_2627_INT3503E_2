
from flask import Blueprint, jsonify, request
from sqlalchemy import asc, desc

from models import Book, db

books_bp = Blueprint("books", __name__)


def apply_sort(query, sort_value):
    """Sắp xếp theo một hoặc nhiều trường."""
    allowed_fields = {
        "id": Book.id,
        "title": Book.title,
        "author": Book.author,
        "genre": Book.genre,
        "published_year": Book.published_year,
    }

    if not sort_value:
        return query.order_by(asc(Book.id))

    sort_parts = sort_value.split(",")

    for part in sort_parts:
        part = part.strip()

        if not part:
            return None, f"Thành phần sort không hợp lệ: '{part}'"

        descending = part.startswith("-")
        field_name = part[1:] if descending else part

        if field_name not in allowed_fields:
            return None, f"Không thể sort theo trường '{field_name}'"

        column = allowed_fields[field_name]
        query = query.order_by(desc(column) if descending else asc(column))

    return query, None


@books_bp.get("")
def list_books():
    # 1. Filter theo genre
    query = Book.query

    genre = request.args.get("genre")
    if genre:
        query = query.filter(Book.genre.ilike(genre))

    # 2. Sort nhiều khóa
    sort_value = request.args.get("sort", "id")
    query, error = apply_sort(query, sort_value)

    if error:
        return jsonify({"error": error}), 400

    # 3. Chọn chiến lược pagination
    strategy = request.args.get("strategy", "offset").lower()

    if strategy == "offset":
        try:
            limit = int(request.args.get("limit", 10))
            offset = int(request.args.get("offset", 0))
        except ValueError:
            return jsonify({
                "error": "limit và offset phải là số nguyên"
            }), 400

        if limit < 1 or limit > 100 or offset < 0:
            return jsonify({
                "error": "limit phải từ 1 đến 100; offset phải >= 0"
            }), 400

        total = query.count()
        books = query.offset(offset).limit(limit).all()

        return jsonify({
            "strategy": "offset",
            "items": [book.to_dict() for book in books],
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": total,
                "has_next": offset + len(books) < total,
            },
        })

    elif strategy == "cursor":
        try:
            limit = int(request.args.get("limit", 10))
        except ValueError:
            return jsonify({"error": "limit phải là số nguyên"}), 400

        if limit < 1 or limit > 100:
            return jsonify({
                "error": "limit phải từ 1 đến 100"
            }), 400

        # Cursor sử dụng ID làm mốc để lấy trang tiếp theo.
        cursor = request.args.get("cursor")

        if cursor:
            try:
                cursor_id = int(cursor)
            except ValueError:
                return jsonify({"error": "cursor phải là ID số nguyên"}), 400

            query = query.filter(Book.id > cursor_id)

        # Để cursor ổn định, chiến lược này sắp theo ID tăng dần.
        books = query.order_by(None).order_by(asc(Book.id)).limit(limit + 1).all()

        has_next = len(books) > limit
        books = books[:limit]

        next_cursor = books[-1].id if books and has_next else None

        return jsonify({
            "strategy": "cursor",
            "items": [book.to_dict() for book in books],
            "pagination": {
                "limit": limit,
                "next_cursor": next_cursor,
                "has_next": has_next,
            },
        })

    return jsonify({
        "error": "strategy phải là 'offset' hoặc 'cursor'"
    }), 400
