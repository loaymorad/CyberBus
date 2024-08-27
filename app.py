from flask import Flask, render_template, session, redirect, url_for, request,flash
import os
import db
import re
import strong_password
from markupsafe import escape
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

app.secret_key = 'NotHacker' # for using sessions

limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["50 per minute"], storage_uri="memory://")
app.config['SESSION_COOKIE_HTTPONLY'] = False

app.config['UPLOAD_FOLDER'] = 'static/uploads'
userdb_connection = db.connect_to_database('users.db')
productdb_connection = db.connect_to_database('products.db')
wishlistdb_connection = db.connect_to_database('wishlist.db')
comments_connection = db.connect_to_database('comments.db')



valid_extension = {'jpg', 'jpeg', 'png', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in valid_extension

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
            if allowed_file(product_image.filename):
                db.add_product(productdb_connection, title, price,product_image.filename)
                product_image.save(os.path.join(app.config['UPLOAD_FOLDER'], product_image.filename))
                return redirect(url_for('index'))
            else:
                return "file not allowed"
        
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
    productid = None
    
    if request.method == 'POST':
        productid = request.form['product_id']        
        # add it to wishlist connected to user id
        db.add_product_to_wishlist(wishlistdb_connection, userid[0], productid)

    if productid:
        all_products = db.get_product_from_wishlist(wishlistdb_connection, productid)

        user_products = set()
        total_price = 0
        for product in all_products:
            product_details = db.get_products_by_id(productdb_connection, product[2])
            # Convert the list to a tuple
            total_price += product_details[3]
        

        return render_template('wishlist.html', products=user_products, total_price=total_price)

    else:
        return render_template('wishlist.html')
  
@app.route('/search_results', methods=['GET', 'POST'])
def search():
    if not 'username' in session: return redirect(url_for('login'))
    if request.method == 'GET' :
       return render_template('/search_results.html') #, products_results=products_results)#########
    
    elif request.method == 'POST' :
       search_query = request.form.get('search_query')
      
       products_results = db.search_product(productdb_connection, search_query) 
       print(products_results)
       print(search_query)
       return render_template('/search_results.html', products_results=products_results)#########


@app.route('/comments', methods=['GET', 'POST'])
def addComment():
    if not 'username' in session: return redirect(url_for('login'))
    comments = db.get_comments(comments_connection)
    if request.method == 'POST':
        text = escape(request.form['comment'])
        username = session.get('username')
        if username:
            db.add_comment(comments_connection, username, text)
            comments = db.get_comments(comments_connection)
        else:
            return("You must be logged in to post a comment.", "warning")

    return render_template('comments.html', comments=comments)

@app.route('/clear_comments', methods=['GET','POST'])
def clearComments():
    db.clear_comments(comments_connection)
    return redirect(url_for('addComment'))

@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if 'username' in session:
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
    product_id = request.form.get('id')
    if product_id:
        db.delete_product_by_title(productdb_connection, product_id)
    return redirect(url_for('admin_panel'))


if __name__ == "__main__":
    db.make_user_table(userdb_connection)
    db.make_product_table(productdb_connection)
    db.make_wishlist_table(wishlistdb_connection)
    db.init_comments_table(comments_connection)
    
    app.run(debug=True)
