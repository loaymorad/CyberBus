from flask import Flask, render_template, session, redirect, url_for, request,flash
from PIL import Image
from werkzeug.utils import secure_filename
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import io
import os
import db
import re
import strong_password

app = Flask(__name__)

app.secret_key = 'NotHacker' # for using sessions

app.config['UPLOAD_FOLDER'] = 'static/uploads'
userdb_connection = db.connect_to_database('users.db')
productdb_connection = db.connect_to_database('products.db')
wishlistdb_connection = db.connect_to_database('wishlist.db')

limiter = Limiter(app=app, key_func=get_remote_address, default_limits=[
                  "50 per minute"], storage_uri="memory://")

valid_extension = {'jpg', 'jpeg', 'png', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in valid_extension

def allowed_file_size(file, MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024):
    file.seek(0, os.SEEK_END) # Go to the end of the file
    file_size = file.tell() # Get the size
    file.seek(0, os.SEEK_SET) # Go back to the start of the file
    return file_size <= MAX_FILE_SIZE_BYTES

def allowed_file_content(file):
    try:
        img = Image.open(file)
        img.verify()  # Verify the image
        file.seek(0)  # Reset file pointer to the beginning
        return True
    except (IOError, SyntaxError) as e:
        return False

@app.route('/')
def index():
    if 'username' in session:
        print(session['username'])
        products = db.get_products(productdb_connection) # array of tuples
        print(products)
        # send data from python to html
        return render_template('index.html', products=products)

    return redirect(url_for('login'))
        
@app.route('/register', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def register():
    if not 'username' in session: return redirect(url_for('login'))
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = db.get_user(userdb_connection, username)
        # already nor exist
        if password == "" or username == "":
            if strong_password.is_strong(password):   
                flash("Please enter all the required fields!","error")
                return redirect(url_for('register'))

        if user is None:
            db.add_user(userdb_connection, username, password)
            return redirect(url_for('index'))
        else:
            return "User already exists"
        

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
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
                session['username'] = username
                return redirect(url_for('index'))
            else:
                return "Incorrect username or password"
        else:
            return "User does not exist"

@app.route('/logout')
def logout():
    session.pop('username')
    return redirect(url_for('index'))


@app.route('/addProduct', methods=['GET', 'POST'])
def addProduct():
    if not 'username' in session: return redirect(url_for('login'))
    if request.method == 'GET':
        return render_template('addProduct.html')
    elif request.method == 'POST':
        title = request.form['title']
        price = request.form['price']
        product_image = request.files.get("image-upload")
        print(product_image)
        
        if title and price and product_image:
            if allowed_file(product_image.filename) and allowed_file_content(product_image):
                if allowed_file_size(product_image):
                    db.add_product(productdb_connection, title, price,product_image.filename)
                    product_image.save(os.path.join(app.config['UPLOAD_FOLDER'], product_image.filename))
                    return redirect(url_for('index'))
                else:
                    return "file is to large"
            else:
                return "file type is not allowed"
        
        return "write all your data"
    
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if not 'username' in session: return redirect(url_for('login'))
    return render_template('profile.html')

@app.route('/wishlist', methods=['GET', 'POST'])
def wishlist():
    if not 'username' in session: return redirect(url_for('login'))
    username = session.get('username')
    
    userid = db.get_userid_by_name(userdb_connection, username)
    if request.method == 'POST':
        productid = request.form['product_id']        
        # add it to wishlist connected to user id
        db.add_product_to_wishlist(wishlistdb_connection, userid, productid)

    elif request.method == 'GET':
        products = db.get_product_from_wishlist(wishlistdb_connection, productid)
        print(products)
        return render_template('wishlist.html', products=products)

@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if 'username' in session:
        print(session['username'])
        if session['username'] == 'admin':
            users = db.get_all_users(userdb_connection)
            products = db.get_all_products(productdb_connection)
            return render_template('panel.html', users = users, products = products)
        else:
            return f"Welcome, {session['username']}!"
    return "You are not logged in"

@app.route('/delete_user', methods=['POST'])
def delete_user():
    username = request.form.get('username')
    if username:
        db.delete_user_by_username(userdb_connection, username)
    return redirect(url_for('admin_panel'))

@app.route('/delete_product', methods=['POST'])
def delete_product():
    product_title = request.form.get('title')
    if product_title:
        db.delete_product_by_title(productdb_connection, product_title)
    return redirect(url_for('admin_panel'))

@app.route('/update_product', methods=['GET', 'POST'])
def update_product():
    if request.method == 'POST':
        product_id = request.form.get('product_id')  # Retrieve the product_id from the form
        new_title = request.form.get('title')
        new_price = request.form.get('price')
        product_image = request.files.get('image')
        
        # Retrieve current image filename
        product = db.get_product_by_id(productdb_connection, product_id)
        current_image = product[1]  # Assuming image is in the second column of the product tuple

        if product_image and allowed_file(product_image.filename) and allowed_file_content(product_image):
            if allowed_file_size(product_image):
                product_image.save(os.path.join(app.config['UPLOAD_FOLDER'], product_image.filename))
                # Remove old image if it exists
                old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], current_image)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
            else:
                    return "file is to large"
        else:
            product_image.filename = current_image  # Keep the old image if no new file is provided
        
        db.update_product(productdb_connection, product_id, new_title, product_image.filename, new_price)
        return redirect(url_for('admin_panel'))
    
    product_id = request.args.get('product_id')  # Retrieve product_id from query parameters
    if product_id:
        product = db.get_product_by_id(productdb_connection, product_id)
        return render_template('updateproduct.html', product=product)
    return "Product ID is required", 400


if __name__ == "__main__":
    db.make_user_table(userdb_connection)
    db.make_product_table(productdb_connection)
    db.make_wishlist_table(productdb_connection)
    app.run(debug=True)
