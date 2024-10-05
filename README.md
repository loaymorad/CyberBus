# Flask E-Commerce Application

This is a simple e-commerce application built with Flask. The application allows users to register, log in, view products, add products, and manage a wishlist.

## Features

- **User Authentication**: Register and log in with username and password.
- **Product Management**: View and add products to the catalog.
- **Wishlist**: Add products to a wishlist and view them later.

## Installation

1. **Clone the repository**:

    ```bash
    git clone https://github.com/loaymorad/CyberBus.git
    cd flask-ecommerce
    ```

3. **Install dependencies**:

    flask

4. **Set up the database**:

    The application uses SQLite for the database. The database schema is automatically created when you run the application.

5. **Run the application**:

    ```bash
    python app.py
    ```

    The application will be accessible at `http://127.0.0.1:5000/`.

## Database Schema

The application uses three SQLite tables:

- **users**:
    - `id`: INTEGER PRIMARY KEY AUTOINCREMENT
    - `username`: TEXT NOT NULL UNIQUE
    - `password`: TEXT NOT NULL

- **products**:
    - `id`: INTEGER PRIMARY KEY AUTOINCREMENT
    - `title`: TEXT NOT NULL
    - `price`: INTEGER NOT NULL
    - `description`: TEXT NOT NULL

- **wishlist**:
    - `id`: INTEGER PRIMARY KEY AUTOINCREMENT
    - `img`: TEXT NOT NULL
    - `title`: TEXT NOT NULL
    - `price`: INTEGER NOT NULL

## Routes

- `/`: Displays the main page with a list of products.
- `/register`: Register a new user.
- `/login`: Log in to an existing account.
- `/addProduct`: Add a new product to the catalog.
- `/product`: View a specific product (template available).
- `/profile`: View and edit user profile (template available).
- `/wishlist`: View products added to the wishlist.

## Contributing

If you'd like to contribute, please fork the repository and use a feature branch. Pull requests are warmly welcome.
