# Inventory Management API

## Overview
This is an Inventory Management API built with Django and Django REST Framework. It provides endpoints for user registration, login, and item management (CRUD operations).

## Features
- User registration and authentication using JWT tokens
- CRUD operations for inventory items
- Redis caching for item retrieval
- Detailed logging for tracking API usage and errors

## Technologies
- Django
- Django REST Framework
- Django REST Framework Simple JWT
- Redis (for caching)
- PostgreSQL (for developing)

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/inventory-management.git
   cd inventory-management
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`

   pip install -r requirements.txt
   python manage.py makemigrations
   python manage.py migrate
   python manage.py runserver

Make sure Redis is installed and running. You can follow the Redis installation guide for your operating system.
Configure your settings.py to connect to your Redis instance for caching.
Update your database settings in settings.py to connect to PostgreSQL for production (if applicable).

**API Documentation**

**User Registration**
Endpoint: /api/register/
Method: POST
Request Body:
{
    "username": "testuser",
    "password": "testpass"
}
Response:
201 Created: User registered successfully.
400 Bad Request: Validation errors.

**User Login**
Endpoint: /api/login/
Method: POST
Request Body:
{
    "username": "testuser",
    "password": "testpass"
}
Response:
200 OK: JWT tokens returned.
400 Bad Request: Invalid credentials.

**Item Management**
Create Item
Endpoint: /api/items/
Method: POST
Request Body:
{
    "name": "Test Item",
    "description": "A description of the test item",
    "price": 100.0
}
Response:
201 Created: Item created successfully.
400 Bad Request: Item already exists.

**Retrieve Item**
Endpoint: /api/items/{item_id}/
Method: GET
Response:
200 OK: Item details.
404 Not Found: Item does not exist.

**Update Item**
Endpoint: /api/items/{item_id}/
Method: PUT
Request Body:
{
    "name": "Updated Item",
    "description": "Updated description",
    "price": 150.0
}
Response:
200 OK: Item updated successfully.
404 Not Found: Item does not exist.

**Delete Item**
Endpoint: /api/items/{item_id}/
Method: DELETE
Response:
204 No Content: Item deleted successfully.
404 Not Found: Item does not exist.

**Thank You**
