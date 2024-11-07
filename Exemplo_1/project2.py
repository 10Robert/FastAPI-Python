from fastapi import FastAPI, Path, Query, HTTPException
from pydantic import BaseModel, Field
import uvicorn 
from typing import Optional
from starlette import status

app = FastAPI()

class Book:
    id: int
    title: str
    author: str
    description: str
    rating: int

    def __init__(self, id, title, author, description, rating, published_date):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date

class BookRequest(BaseModel):
    id: Optional[int] = Field(description="ID is not needed on create", default=None)
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=0, lt=6)
    published_date: int = Field(gt=1999, lt=2031)

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "A new book",
                "author": "codingwithroby",
                "description": "A new description of a book",
                "rating": 5,
                "published_date": 2024,
            }
        }
    }

BOOKS = [
    Book(1, "Computer Science Pro", "codingwithroby", "A very nice book!", 5, 2000),
    Book(2, "Master endpoints", "codingwithroby", "A very nice book!", 2, 2012),
    Book(3, "HP1", "Author 1", "A very nice book!", 5, 2010),
    Book(4, "HP2", "Author 2", "A very nice book!", 3, 2015),
    Book(5, "HP3", "Author 3", "A very nice book!", 4 , 2024),
]

@app.get("/books", status_code=status.HTTP_200_OK)
async def read_all_Books():
    return BOOKS

@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def read_book(book_id: int = Path(gt=0)):
    book_changed = False
    for book in BOOKS:
        if book.id == book_id:
            book_changed = True
            return book
    if not book_changed:
        raise HTTPException(status_code=404, detail="Item not Found")
    

@app.get("/books/", status_code=status.HTTP_200_OK)
async def read_books_by_rating(book_rating: int = Query(gt=0, lt=6)):
    books_to_return = []
    for book in BOOKS:
        if book.rating == book_rating:
            books_to_return.append(book)
    return books_to_return

@app.get("/books/publish/", status_code=status.HTTP_200_OK)
async def read_books_by_publish_date(published_date: int = Query(gt=1999, lt=2031)):
    books_to_return = []
    for book in BOOKS:
        if book.published_date == published_date:
            books_to_return.append(book)
    return books_to_return
    

@app.post("/create-book", status_code=status.HTTP_201_CREATED)
async def create_book(book_request:BookRequest):
    new_book = Book(**book_request.model_dump())
    BOOKS.append(find_book_id(new_book))

@app.put("/books/update_book", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book:BookRequest):
    book_changed = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book.id:
            BOOKS[i] = book  # type: ignore
            book_changed = True
    if not book_changed:
        raise HTTPException(status_code=404, detail="Item Not Found")


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int = Path(gt=0)):
    book_changed = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            BOOKS.pop(i)
            book_changed = True
            break
    if not book_changed:
        raise HTTPException(status_code=404, detail="Item Not Found")

def find_book_id(book: Book):

    book.id = 1 if BOOKS == 0 else BOOKS[-1].id + 1

    """
    if len(BOOKS) > 0:
        book.id = BOOKS[-1].id + 1

    else:
        book.id = 1
    """

    return book



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
