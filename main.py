import motor.motor_asyncio
from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bookstore import BookStore
from typing import Optional, List
from bson import ObjectId
import json
from json import JSONEncoder


app = FastAPI()

client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
database = client["BookStore"]
collection = database["books"]

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return JSONEncoder.default(self, obj)

@app.post("/books/")
async def create_book(book: BookStore):
    # Validate the incoming book data using Pydantic
    if book.price <= 0:
        return {"error": "Price must be greater than zero"}
    if book.stock < 0:
        return {"error": "Stock must be a non-negative integer"}

    # convert book model to dictionary
    book_dict = book.dict()

    # insert the book document into the MongoDB collection
    #book_dict['_id'] = str(ObjectId())

    # insert the book document into the MongoDB collection
    result = await collection.insert_one(book_dict)

    # Return the stored book data as response
    #return { "id": str(result.inserted_id), **book_dict }
    # Return a success message instead of a dictionary
    return "Book inserted successfully!"

@app.get("/books/aggregation/")
async def get_books_aggregation():
    pipeline = [
    {
        "$facet": {
            "total_books": [
                {"$count": "count"}
            ],
            "bestselling_books": [
                {"$sort": {"stock": -1}},
                {"$limit": 5}
            ],
            "top_authors": [
                {"$group": {"_id": "$author", "books": {"$push": "$title"}}},
                {"$project": {"_id": 0, "author": "$_id", "book_count": {"$size": "$books"}}},
                {"$sort": {"book_count": -1}},
                {"$limit": 5}
            ]
        }
    }
]

    # perform the aggregation query
    cursor = collection.aggregate(pipeline)

    # convert cursor to list
    result = await cursor.to_list(length=100)

    # return the result as response
    #return result
    return json.loads(json.dumps(result, cls=CustomJSONEncoder))

# GET /books: Retrieves a list of all books in the store
@app.get("/books/", response_model=List[BookStore])
async def get_all_books():
    books = []
    async for book in collection.find():
        books.append(BookStore(**book))
    return books


# GET /books/{book_id}: Retrieves a specific book by ID
@app.get("/books/{book_id}", response_model=BookStore)
async def get_book_by_id(book_id: str):
    print(book_id)
    book = await collection.find_one({"_id": ObjectId(book_id)})
    if book:
        return BookStore(**book)
    else:
        raise HTTPException(status_code=404, detail="Book not found")


# POST /books: Adds a new book to the store
@app.post("/books/", response_model=BookStore)
async def create_book(book: BookStore):
    # Validate the incoming book data using Pydantic
    if book.price <= 0:
        raise HTTPException(status_code=400, detail="Price must be greater than zero")
    if book.stock < 0:
        raise HTTPException(status_code=400, detail="Stock must be a non-negative integer")

    # convert book model to dictionary
    book_dict = book.dict()

    # insert the book document into the MongoDB collection
    result = await collection.insert_one(book_dict)

    # Return the stored book data as response
    return { "id": str(result.inserted_id), **book_dict }


# PUT /books/{book_id}: Updates an existing book by ID
@app.put("/books/{book_id}", response_model=BookStore)
async def update_book(book_id: str, update_data: dict):
    book_id = ObjectId(book_id)
    # update the book document in the MongoDB collection
    result = await collection.update_one({"_id": ObjectId(book_id)}, {"$set": update_data})
    if result.modified_count == 1:
        updated_book = await collection.find_one({"_id": ObjectId(book_id)})
        return BookStore(**updated_book)
    else:
        raise HTTPException(status_code=404, detail="Book not found")


# DELETE /books/{book_id}: Deletes a book from the store by ID
@app.delete("/books/{book_id}")
async def delete_book(book_id: str):
    result = await collection.delete_one({"_id": ObjectId(book_id)})
    if result.deleted_count == 1:
        return {"message": "Book deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Book not found")


@app.get("/search")
async def search_books(title: Optional[str] = None, author: Optional[str] = None, min_price: Optional[float] = None, max_price: Optional[float] = None):
    # Construct a query object based on the search parameters
    query = {}
    if title:
        query["title"] = {"$regex": title, "$options": "i"}  # search title case-insensitively
    if author:
        query["author"] = {"$regex": author, "$options": "i"}  # search author case-insensitively
    if min_price is not None and max_price is not None:
        query["price"] = {"$gte": min_price, "$lte": max_price}
    elif min_price is not None:
        query["price"] = {"$gte": min_price}
    elif max_price is not None:
        query["price"] = {"$lte": max_price}

    # Search for books matching the query
    cursor = collection.find(query)

    # Convert the cursor to a list of books
    books = [BookStore(**book) async for book in cursor]

    # Return the list of books as response
    return books


