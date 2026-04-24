# Library Management System - FastAPI Project

## Project Overview
This is a backend API project built using FastAPI.  
It simulates a real-world Library Management System with features like book borrowing, returning, queue handling, and advanced search and pagination.

---

## Features
- Add, View, Update, Delete Books (CRUD)
- Borrow and Return System
- Queue system for unavailable books
- Search books by keyword
- Sorting and Pagination
- Borrow records tracking
- Pydantic data validation
- RESTful API design

---

## Tech Stack
- FastAPI
- Python
- Pydantic
- Uvicorn

---

## Project Structure

fastapi-library-system/
│
├── main.py # Main FastAPI application
├── requirements.txt # Dependencies
├── README.md # Project documentation
└── screenshots/ # API testing screenshots

## How to Run the Project

### 1️. Install dependencies
```bash
pip install -r requirements.txt
2️. Run FastAPI server
uvicorn main:app --reload
3️. Open API documentation
http://127.0.0.1:8000/docs
