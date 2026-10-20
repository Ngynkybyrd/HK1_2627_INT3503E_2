
from flask import Flask, jsonify

from models import Book, db
from routes.books import books_bp


def create_app(test_config=None):
    app = Flask(__name__)

    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI="sqlite:///bookstore.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    # Cho phép tests truyền cấu hình database riêng.
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    app.register_blueprint(books_bp, url_prefix="/api/v1/books")

    with app.app_context():
        db.create_all()

    @app.get("/")
    def home():
        return jsonify({"message": "Bookstore API is running"})

    return app


app = create_app()


def seed_books():
    with app.app_context():
        if Book.query.count() > 0:
            print("Database đã có dữ liệu, bỏ qua seed.")
            return

        sample_books = [
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
            Book(
                title="Pride and Prejudice",
                author="Jane Austen",
                genre="Romance",
                published_year=1813,
            ),
            Book(
                title="Emma",
                author="Jane Austen",
                genre="Romance",
                published_year=1815,
            ),
            Book(
                title="Neuromancer",
                author="William Gibson",
                genre="Sci-Fi",
                published_year=1984,
            ),
            Book(
                title="The Martian",
                author="Andy Weir",
                genre="Sci-Fi",
                published_year=2011,
            ),
            Book(
                title="Harry Potter and the Philosopher's Stone",
                author="J.K. Rowling",
                genre="Fantasy",
                published_year=1997,
            ),
            Book(
                title="The Name of the Wind",
                author="Patrick Rothfuss",
                genre="Fantasy",
                published_year=2007,
            ),
        ]

        db.session.add_all(sample_books)
        db.session.commit()
        print(f"Đã thêm {len(sample_books)} sách mẫu.")


if __name__ == "__main__":
    seed_books()
    app.run(debug=True)
