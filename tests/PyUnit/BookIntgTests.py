from flask import Flask
from flask.testing import FlaskClient
from main import app, is_valid_objectid, collection, get_book_by_id, update_book, delete_book
import unittest
from unittest.mock import patch
from bson import ObjectId



class TestBookStoreAPI(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_create_book_success(self):
        book_data = {
            "title": "The Great Gatsby",
            "author": "F. Scott Fitzgerald",
            "description": "A novel about the excess and decadence of the Roaring Twenties",
            "price": 12.99,
            "stock": 25,
            "sales": 500
        }

        response = self.client.post("/books/", json=book_data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Book inserted successfully!"})

    def test_create_book_empty_author(self):
        book_data = {
            "title": "The Great Gatsby",
            "author": "",
            "description": "A novel about the excess and decadence of the Roaring Twenties",
            "price": 12.99,
            "stock": 25,
            "sales": 500
        }

        response = self.client.post("/books/", json=book_data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"error": "Title and author cannot be empty"})


    def test_create_book_empty_title(self):
        book_data = {
            "title": "The Great Gatsby",
            "author": "",
            "description": "A novel about the excess and decadence of the Roaring Twenties",
            "price": 12.99,
            "stock": 25,
            "sales": 500
        }

        response = self.client.post("/books/", json=book_data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"error": "Title and author cannot be empty"})

    def test_create_book_invalid_price(self):
        book_data = {
            "title": "The Great Gatsby",
            "author": "F. Scott Fitzgerald",
            "description": "A novel about the excess and decadence of the Roaring Twenties",
            "price": 0,
            "stock": 25,
            "sales": 500
        }

        response = self.client.post("/books/", json=book_data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"error": "Invalid book data"})
        
    def test_create_book_invalid_stock(self):
        book_data = {
            "title": "The Great Gatsby",
            "author": "F. Scott Fitzgerald",
            "description": "A novel about the excess and decadence of the Roaring Twenties",
            "price": 100,
            "stock": 0,
            "sales": 500
        }

        response = self.client.post("/books/", json=book_data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"error": "Invalid book data"})
        
    def test_create_book_invalid_sale(self):
        book_data = {
            "title": "The Great Gatsby",
            "author": "F. Scott Fitzgerald",
            "description": "A novel about the excess and decadence of the Roaring Twenties",
            "price": 100,
            "stock": 10,
            "sales": -1
        }

        response = self.client.post("/books/", json=book_data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"error": "Invalid book data"})
        
    def test_get_all_books(self):
        # Assuming there are books in the database
        response = self.client.get('/books/')
        self.assertEqual(response.status_code, 200)
        
        
        data = response.json
        self.assertIsInstance(data, list)
        for book in data:
            self.assertIn("title", book)
            self.assertIn("author", book)
            self.assertIn("description", book)
            self.assertIn("price", book)
            self.assertIn("stock", book)
            self.assertIn("sales", book)
            
    def test_get_book_by_id_success(self):
        # Assuming there is a valid book_id in the database
        valid_book_id = '645c5ee39f04857283b34613'
        response = self.client.get(f'/books/{valid_book_id}')
        self.assertEqual(response.status_code, 200)
        

    def test_get_book_by_id_invalid_id(self):
        response = self.client.get('/books/invalid_id')
        self.assertEqual(response.status_code, 400)
        
    def test_get_book_by_id_not_found(self):
        # Assuming there is no book with this ID in the database
        non_existent_id = '645c5ee39f04857283b34603'
        response = self.client.get(f'/books/{non_existent_id}')
        self.assertEqual(response.status_code, 404)
        
    def test_update_book_success(self):
        # Assuming there is a valid book_id and update_data
        valid_book_id = '645c5ee39f04857283b34612'
        update_data = {"title": "Updated Title"}
        response = self.client.put(f'/books/{valid_book_id}', json=update_data)
        self.assertEqual(response.status_code, 200)
       
    def test_update_book_invalid_id(self):
        response = self.client.put('/books/invalid_id', json={"title": "Updated Title"})
        self.assertEqual(response.status_code, 400)
        
    def test_update_book_not_found(self):
        # Assuming there is no book with this ID in the database
        non_existent_id = str(ObjectId())
        response = self.client.put(f'/books/{non_existent_id}', json={"title": "Updated Title"})
        self.assertEqual(response.status_code, 404)
        
    def test_delete_book_invalid_id(self):
        response = self.client.delete('/books/invalid_id')
        self.assertEqual(response.status_code, 400)
       
    def test_delete_book_not_found(self):
        # Assuming there is no book with this ID in the database
        non_existent_id = str(ObjectId())
        response = self.client.delete(f'/books/{non_existent_id}')
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
