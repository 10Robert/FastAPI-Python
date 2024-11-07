from fastapi import Body, FastAPI

app = FastAPI()

BOOKS = [
    {"title": "São Paulo fc", "Ano": 2010, "category": "animation", "Author": "Azevedo"},
    {"title": "Palmeiras", "Ano": 2009, "category": "classic film", "Author": "Lucas"},
    {"title": "Santos", "Ano": 2015, "category": "comedy", "Author": "Robert"},
]

@app.get("/books/byauthor/")
async def read_books_by_author_query(author: str):
    books_to_return = []

    for book in BOOKS:
        if book.get("Author").casefold() == author.casefold():
            books_to_return.append(book)

    return books_to_return

@app.delete("/books/delete_book/{book_title}")
async def delete_book(book_title: str):
    for i in range(len(BOOKS)):
        if BOOKS[i].get("title").casefold() == book_title.casefold():
            BOOKS.pop(i)
            break

@app.get("/books")
async def read_all_Books():
    return BOOKS

@app.get("/books/mybooks")
async def read_all_books():
    return {"Mybook": "My favorite book!"}

@app.get("/books/category")
async def read_category_books(category: str):
    books_to_return = []
    for books in BOOKS:
        if books.get("category").casefold() == category.casefold():
            books_to_return.append(books)
    return books_to_return

@app.get("/books/{author}/")
async def read_category_by_query(author: str, category: str):
    books_to_return = []
    for book in BOOKS:
        if book.get("category").casefold() == category.casefold() and \
            book.get("Author").casefold() == author.casefold():
            books_to_return.append(book)
    return books_to_return

@app.get("/books/{title_book}")
async def read_book(title_book: str):
    for book in BOOKS:
        if book.get("title").casefold() == title_book.casefold(): # type: ignore
            return book
     
@app.post("/books/create_book")
async def create_book(new_book=Body()):
    BOOKS.append(new_book)

@app.put("/books/update_book")
async def update_book(update_book=Body()):
    for i in range(len(BOOKS)):
        if BOOKS[i].get("title").casefold() == update_book.get("title").casefold(): # type: ignore
            BOOKS[i] = update_book

@app.get("/books/byauthor/{author}")
async def read_books_by_author_path(author: str):
    books_to_return = []

    for book in BOOKS:
        if book.get("Author").casefold() == author.casefold(): # type: ignore
            books_to_return.append(book)

    return books_to_return




"""

@app.get("/books/{book_title}")
async def read_my_book(book_title: str):
    for book_title in BOOKS:
        if BOOKS.get("title").casefold() == book_title.casefold():
            return book

"""