
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
            price INTEGER NOT NULL,
            description TEXT NOT NULL
		)                   
    ''')
    
    connection.commit()
    
def make_wishlist_table(connection):
    cursor = connection.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS wishlist (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
            img TEXT NOT NULL,
			title TEXT NOT NULL,
            price INTEGER NOT NULL
		)                   
    ''')
    
    connection.commit()

# ------- AUTH -------

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


# ------- PRODUCTS -------

def add_product(connection, title, price, description,image_path=None):
    cursor = connection.cursor()
    
    cursor.execute('''
        INSERT INTO products (title, price, description,img) VALUES (?, ?, ?, ?)  
    ''', (title, price, description,image_path))
    
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
 
def add_product_to_wishlist(connection, img, title, price): # add when i click to a single product
    cursor = connection.cursor()
    
    cursor.execute('''
        INSERT INTO wishlist (img, title, price) VALUES (?, ?, ?)  
    ''', (img, title, price))
    
    connection.commit()

def get_product_from_wishlist(connection): # /wishlist
    cursor = connection.cursor()
    
    cursor.execute('''
        SELECT * FROM wishlist
    ''')
    
    connection.commit()  

    #-------------------------comments---------------------M

    def init_comments_table(connection):
        cursor = connection.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            text TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    connection.commit()

def add_comment(connection, username, text):
    cursor = connection.cursor()
    query = '''INSERT INTO comments (username, text) VALUES (?, ?)'''
    cursor.execute(query, (username, text))
    connection.commit()

def get_comments(connection):
    cursor = connection.cursor()
    query = '''
        SELECT comments.username, comments.text, comments.timestamp
        FROM comments
    '''
    cursor.execute(query)
    return cursor.fetchall()

def clear_comments(connection):
    cursor = connection.cursor()
    query = '''DELETE FROM comments'''
    cursor.execute(query)
    connection.commit()


    #-----------------product search-------------M
def search(connection, search_query):
    cursor = connection.cursor()
    query = '''SELECT product FROM products WHERE product LIKE ?'''
    cursor.execute(query, (f"%{search_query}%",))
    return cursor.fetchall()


def init_db(connection):
    cursor = connection.cursor()

    cursor.execute('''
		CREATE TABLE IF NOT EXISTS users (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			username TEXT NOT NULL UNIQUE,
			password TEXT NOT NULL
		)
	''')

    connection.commit()