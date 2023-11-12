from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
from pydantic import BaseModel
from typing import Optional, List

app = Flask(__name__)

# MongoDB setup
client = MongoClient("mongodb://localhost:27017")
database = client["booksstore"]
collection = database["books"]

class BooksStore(BaseModel):
    title: str
    author: str
    description: str
    price: float
    stock: int
    sales: int

# Route to create a book
@app.route('/books/', methods=['POST'])
def create_book():
    data = request.json

    # Validate the incoming book data
    if data.get('price', 0) <= 0 or data.get('stock', 0) <= 0 or data.get('sales', 0) < 0:
        return jsonify({"error": "Invalid book data"}), 400
    
    if not data.get('title') or not data.get('author'):
        return jsonify({"error": "Title and author cannot be empty"}), 400


    # Insert the book into the database
    result = collection.insert_one(data)

    # Return a success message
    return jsonify({"message": "Book inserted successfully!"})

# Route to get books aggregation
@app.route('/books/aggregation/', methods=['GET'])
def get_books_aggregation():
    # Similar aggregation pipeline as in the FastAPI example
    pipeline = [
    {
        "$facet": {
            "total_books": [
                {"$count": "count"}
            ],
            "bestselling_books": [
                {"$sort": {"sales": -1}},
                {"$limit": 5}
            ],
            "top_authors": [
                {"$group": {"_id": "$author", "total_stock": {"$sum": "$stock"}}},
                {"$sort": {"total_stock": -1}},
                {"$limit": 5},
                {"$project": {"_id": 0, "author": "$_id", "total_stock": 1}}
            ]
        }
    }
]

    # Perform the aggregation query
    result = list(collection.aggregate(pipeline))

    # Return the result as response
    return jsonify(result)

# Route to get all books
@app.route('/books/', methods=['GET'])
def get_all_books():
    books = list(collection.find())
    
    # Convert ObjectId to strings
    for book in books:
        book['_id'] = str(book['_id'])
    
    return jsonify(books)

# Route to get a book by ID
@app.route('/books/<book_id>', methods=['GET'])
def get_book_by_id(book_id):
    if not is_valid_objectid(book_id):
        return jsonify({"error": "Invalid book ID"}), 400

    book = collection.find_one({"_id": ObjectId(book_id)})
    if book:
        # Convert ObjectId to string
        book['_id'] = str(book['_id'])
        return jsonify(book)
    else:
        return jsonify({"error": "Book not found"}), 404

# Route to update a book by ID
@app.route('/books/<book_id>', methods=['PUT'])
def update_book(book_id):
    if not is_valid_objectid(book_id):
        return jsonify({"error": "Invalid book ID"}), 400
    
    book_id = ObjectId(book_id)

    # Check if the book exists in the MongoDB collection
    book = collection.find_one({"_id": book_id})
    if book is None:
        return jsonify({"error": "Book not found"}), 404
    
    # Update the book document in the MongoDB collection
    update_data = request.json
    result = collection.update_one({"_id": ObjectId(book_id)}, {"$set": update_data})    
    
    if result:
        # Convert ObjectId to string in the updated book
        updated_book = collection.find_one({"_id": ObjectId(book_id)})
        updated_book['_id'] = str(updated_book['_id'])
        return jsonify(updated_book)
    else:
        return jsonify({"error": "Book not found"}), 404

# Route to delete a book by ID
@app.route('/books/<book_id>', methods=['DELETE'])
def delete_book(book_id):
    if not is_valid_objectid(book_id):
        return jsonify({"error": "Invalid book ID"}), 400
    
    book_id = ObjectId(book_id)

    # Check if the book exists in the MongoDB collection
    book = collection.find_one({"_id": book_id})
    if book is None:
        return jsonify({"error": "Book not found"}), 404
    
    result = collection.delete_one({"_id": book_id})

    if result.deleted_count == 1:
        return jsonify({"message": "Book deleted successfully"})
    else:
        return jsonify({"error": "Book not found"}), 404

# Function to check if an object ID is valid
def is_valid_objectid(objectid_str):
    if len(objectid_str) != 24:
        return False
    try:
        ObjectId(objectid_str)
        return True
    except Exception:
        return False

if __name__ == '__main__':
    app.run(debug=True)
