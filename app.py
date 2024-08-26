from flask import Flask, render_template, session, redirect, url_for, request
import os
import db

app = Flask(__name__)

app.secret_key = 'NotHacker' # for using sessions

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




if __name__ == "__main__":
    app.run(debug=True)
