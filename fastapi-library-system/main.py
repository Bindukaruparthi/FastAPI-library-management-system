from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI(title="City Library System", version="1.0.0")


# DATABASE (IN-MEMORY)


books = [
    {"id": 1, "title": "Python Basics", "author": "John Doe", "genre": "Tech", "is_available": True},
    {"id": 2, "title": "Data Science 101", "author": "Jane Smith", "genre": "Tech", "is_available": True},
    {"id": 3, "title": "World History", "author": "Alan Brown", "genre": "History", "is_available": True},
    {"id": 4, "title": "Physics Fundamentals", "author": "Albert Newton", "genre": "Science", "is_available": True},
    {"id": 5, "title": "English Literature", "author": "William Words", "genre": "Fiction", "is_available": True},
    {"id": 6, "title": "Machine Learning", "author": "Andrew Ng", "genre": "Tech", "is_available": True},
]

borrow_records = []
queue = []

book_counter = 7
record_counter = 1


# PYDANTIC MODELS


class BorrowRequest(BaseModel):
    member_name: str = Field(min_length=2)
    book_id: int = Field(gt=0)
    borrow_days: int = Field(gt=0, le=30)
    member_type: str = "regular"


class NewBook(BaseModel):
    title: str = Field(min_length=2)
    author: str = Field(min_length=2)
    genre: str = Field(min_length=2)
    is_available: bool = True



# HELPER FUNCTIONS


def find_book(book_id: int):
    return next((b for b in books if b["id"] == book_id), None)


def calculate_due_date(borrow_days: int, member_type: str):
    base = 15
    if member_type == "premium":
        return f"Return by Day {base + borrow_days + 30}"
    return f"Return by Day {base + borrow_days}"


def filter_books(genre=None, author=None, is_available=None):
    result = books

    if genre is not None:
        result = [b for b in result if b["genre"].lower() == genre.lower()]

    if author is not None:
        result = [b for b in result if b["author"].lower() == author.lower()]

    if is_available is not None:
        result = [b for b in result if b["is_available"] == is_available]

    return result



# DAY 1 - BASIC ROUTES


@app.get("/")
def home():
    return {"message": "Welcome to City Public Library"}


@app.get("/books")
def get_books():
    return {
        "total": len(books),
        "available_count": len([b for b in books if b["is_available"]]),
        "data": books
    }


@app.get("/books/{book_id}")
def get_book(book_id: int):
    book = find_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.get("/borrow-records")
def get_records():
    return {"total": len(borrow_records), "data": borrow_records}


@app.get("/books/summary")
def summary():
    genres = {}
    for b in books:
        genres[b["genre"]] = genres.get(b["genre"], 0) + 1

    return {
        "total_books": len(books),
        "available": len([b for b in books if b["is_available"]]),
        "borrowed": len([b for b in books if not b["is_available"]]),
        "genre_breakdown": genres
    }



# DAY 2-3 - BORROW SYSTEM


@app.post("/borrow")
def borrow_book(req: BorrowRequest):
    global record_counter

    book = find_book(req.book_id)

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if not book["is_available"]:
        raise HTTPException(status_code=400, detail="Book already borrowed")

    book["is_available"] = False

    record = {
        "record_id": record_counter,
        "member_name": req.member_name,
        "book_id": req.book_id,
        "book_title": book["title"],
        "status": "borrowed",
        "due_date": calculate_due_date(req.borrow_days, req.member_type)
    }

    borrow_records.append(record)
    record_counter += 1

    return record


@app.get("/books/filter")
def filter_books_api(
    genre: Optional[str] = None,
    author: Optional[str] = None,
    is_available: Optional[bool] = None
):
    return {
        "count": len(filter_books(genre, author, is_available)),
        "data": filter_books(genre, author, is_available)
    }



# DAY 4 - CRUD


@app.post("/books", status_code=201)
def add_book(book: NewBook):
    global book_counter

    for b in books:
        if b["title"].lower() == book.title.lower():
            raise HTTPException(status_code=400, detail="Book already exists")

    new_book = book.dict()
    new_book["id"] = book_counter
    book_counter += 1

    books.append(new_book)
    return new_book


@app.put("/books/{book_id}")
def update_book(book_id: int, is_available: Optional[bool] = None):
    book = find_book(book_id)

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if is_available is not None:
        book["is_available"] = is_available

    return book


@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    book = find_book(book_id)

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    books.remove(book)
    return {"message": "Book deleted", "title": book["title"]}



# DAY 5 - WORKFLOW (QUEUE + RETURN)


@app.post("/queue/add")
def add_queue(member_name: str, book_id: int):
    book = find_book(book_id)

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if book["is_available"]:
        raise HTTPException(status_code=400, detail="Book is available, no need to queue")

    queue.append({"member_name": member_name, "book_id": book_id})
    return {"message": "Added to queue"}


@app.post("/return/{book_id}")
def return_book(book_id: int):
    book = find_book(book_id)

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    book["is_available"] = True

    # check queue
    for q in queue:
        if q["book_id"] == book_id:
            queue.remove(q)
            book["is_available"] = False
            return {
                "message": "Reassigned to queued user",
                "user": q["member_name"]
            }

    return {"message": "Book returned and available"}


# DAY 6 - SEARCH / SORT / PAGINATION


@app.get("/books/search")
def search(keyword: str):
    result = [
        b for b in books
        if keyword.lower() in b["title"].lower()
        or keyword.lower() in b["author"].lower()
    ]

    if not result:
        return {"message": "No books found"}

    return {"total_found": len(result), "data": result}


@app.get("/books/sort")
def sort_books(sort_by: str = "title", order: str = "asc"):

    valid_fields = ["title", "author", "genre"]
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail="Invalid sort field")

    reverse = order == "desc"
    return sorted(books, key=lambda x: x[sort_by], reverse=reverse)


@app.get("/books/page")
def paginate(page: int = 1, limit: int = 3):
    start = (page - 1) * limit
    end = start + limit

    total_pages = (len(books) + limit - 1) // limit

    return {
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "data": books[start:end]
    }


@app.get("/borrow-records/search")
def search_records(member_name: str):
    result = [
        r for r in borrow_records
        if member_name.lower() in r["member_name"].lower()
    ]
    return result


@app.get("/borrow-records/page")
def paginate_records(page: int = 1, limit: int = 2):
    start = (page - 1) * limit
    end = start + limit

    return {
        "page": page,
        "data": borrow_records[start:end]
    }


@app.get("/books/browse")
def browse(
    keyword: Optional[str] = None,
    sort_by: str = "title",
    order: str = "asc",
    page: int = 1,
    limit: int = 3
):
    result = books

    if keyword:
        result = [
            b for b in result
            if keyword.lower() in b["title"].lower()
        ]

    reverse = order == "desc"
    result = sorted(result, key=lambda x: x[sort_by], reverse=reverse)

    start = (page - 1) * limit
    end = start + limit

    return {
        "total": len(result),
        "page": page,
        "limit": limit,
        "data": result[start:end]
    }
