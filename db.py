
def connect_to_database(name):
    import sqlite3
    return sqlite3.connect(name, check_same_thread=False)


# ------- TABLES -------

def make_user_table(connection):
        cursor = connection.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )                   
        ''')
        
        connection.commit()
    
def make_product_table(connection):
        cursor = connection.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                img TEXT NOT NULL,
                title TEXT NOT NULL,
                price INTEGER NOT NULL
            )                   
        ''')
        
        connection.commit()
    
def make_wishlist_table(connection):
        cursor = connection.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wishlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                userid INTEGER NOT NULL,
                productid INTEGER NOT NULL
            )                   
        ''')
        
        connection.commit()

# ------- USER -------

def add_user(connection, username, password):
    cursor = connection.cursor()
    
    cursor.execute('''
        INSERT INTO users (username, password) VALUES (?, ?)  
    ''', (username, password))
    
    connection.commit()
    

def get_user(connection, username):
    cursor = connection.cursor()
    
    cursor.execute('''
        SELECT * FROM users WHERE username = ?  
    ''', (username,))
    
    connection.commit()
    
    return cursor.fetchone()

def get_user_password(connection, username):
    cursor = connection.cursor()
    
    cursor.execute('''
        SELECT password FROM users WHERE username = ? 
    ''', (username,))
    
    connection.commit()
    
    return cursor.fetchone()

def get_userid_by_name(connection, name):
    cursor = connection.cursor()
    
    cursor.execute('''
        SELECT id FROM users WHERE username = ?
    ''', (name,))
    
    connection.commit()
    
    return cursor.fetchone()

def get_all_users(connection):
    cursor = connection.cursor()
    cursor.execute('''
        SELECT username FROM users
    ''')
    users = cursor.fetchall()
    return [{"username": user[0]} for user in users] 


def delete_user_by_username(connection, username):
    cursor = connection.cursor()

    cursor.execute('''
        DELETE FROM users WHERE username = ?
    ''', (username,))

    connection.commit()
    
    return cursor.fetchall()

# ------- PRODUCTS -------

def add_product(connection, title, price, image_path):
    cursor = connection.cursor()
    
    cursor.execute('''
        INSERT INTO products (img, title, price) VALUES (?, ?, ?)  
    ''', (image_path, title, price ))
    
    connection.commit()
    
def get_products(connection):
    cursor = connection.cursor()
    
    cursor.execute('''
        SELECT * FROM products  
    ''')
    
    connection.commit()
    
    return cursor.fetchall()

def search_products(connection, title):
    
    cursor = connection.cursor()
    
    cursor.execute('''
        SELECT * FROM products WHERE title LIKE ? 
    ''', title)
    
    connection.commit()
    
    return cursor.fetchall()
 
# ------- wishlist -------
 
def add_product_to_wishlist(connection, userid, productid): # add when i click to a single product
    cursor = connection.cursor()
    
    cursor.execute('''
        INSERT INTO wishlist (userid, productid) VALUES (?, ?)  
    ''', (userid, productid))
    
    connection.commit()

def get_product_from_wishlist(connection, userid): # 
    cursor = connection.cursor()
    
    cursor.execute('''
        SELECT * FROM wishlist where userid = ?
    ''', (userid,))
    
    connection.commit()  
    
    return cursor.fetchall() # get all products for that user

def get_all_products(connection):
    cursor = connection.cursor()
    cursor.execute('''
        SELECT * FROM products
    ''')
    products = cursor.fetchall()
    return products


def delete_product_by_title(connection, title):
    cursor = connection.cursor()
    
    cursor.execute('''
        DELETE FROM products WHERE title = ? 
    ''', (title,))
    
    connection.commit()