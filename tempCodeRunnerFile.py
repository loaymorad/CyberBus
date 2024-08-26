from flask import Flask, render_template, session, redirect, url_for, request
import os
import db
from markupsafe import escape
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


app = Flask(__name__)

app.secret_key = 'NotHacker' # for using sessions

limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["50 per minute"], storage_uri="memory://")
app.config['SESSION_COOKIE_HTTPONLY'] = False

userdb_connection = db.connect_to_database('users.db')
productdb_connection = db.connect_to_database('products.db')
wishlistdb_connection = db.connect_to_database('wishlist.db')

db.make_user_table(userdb_connection)
db.make_product_table(productdb_connection)

valid_extension = {'jpg', 'jpeg', 'png', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in valid_extension

@app.route('/')
def index():
    if 'username' in session:
        products = db.get_products(productdb_connection) # array of tuples
        
        # send data from python to html
        return render_template('index.html', products=products)
    else:
        return redirect(url_for('login'))
        
@app.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = db.get_user(userdb_connection, username)
        # already nor exist
        if user is None:
            db.add_user(userdb_connection, username, password)
            return redirect(url_for('index'))
        else:
            return "User already exists"
        

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = db.get_user(userdb_connection, username)
        # already nor exist
        if user:
            pwd = db.get_user_password(userdb_connection, username)
            if password == pwd[0]:
                session['username'] = username  # Chatgpt: Store username in session
                return redirect(url_for('index'))
            else:
                return "Incorrect username or password"
        else:
            return "User does not exist"

@app.route('/product', methods=['GET', 'POST'])
def product():
    return render_template('product.html')

@app.route('/addProduct', methods=['GET', 'POST'])
def addProduct():
    if request.method == 'GET':
        return render_template('addProduct.html')
    elif request.method == 'POST':
        title = request.form['title']
        price = request.form['price']
        description = request.form['description']
        product_image = request.files.get("image-upload")
        filePath = None
        print(product_image)
        if product_image and allowed_file(product_image.filename):
            filePath = os.path.join("./static",product_image.filename)
            product_image.save(filePath)
        else:
            product_image = None
        
        if title and price and description and product_image:
            db.add_product(productdb_connection, title, price, description,filePath)
            return redirect(url_for('index'))
        
        return "write all your data"
    
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    return render_template('profile.html')

@app.route('/wishlist', methods=['GET', 'POST'])
def wishlist():
    if request.method == 'GET':
        products = db.get_product_from_wishlist(wishlistdb_connection)
        return render_template('wishlist.html', products=products)
    

def get_products(productdb_connection,search_query):
    cursor = productdb_connection.cursor()
    cursor.execute("SELECT * FROM products WHERE title LIKE %s", (f"%{search_query}%",))
    return cursor.fetchall()

@app.route('/profile', methods=['GET', 'POST'])
def search():
    if request.method == 'POST' :
       search_query = escape(request.form['search_query'])
       products_results = db.get_products(productdb_connection, search_query)
       print(products_results)
       return render_template('/results.html', products_results=products_results)#########
    return render_template('/profile.html')###########

if __name__ == "__main__":
    app.run(debug=True)
