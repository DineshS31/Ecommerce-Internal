from flask import *
import pymongo
from werkzeug.security import generate_password_hash, check_password_hash

import constants

app = Flask(__name__)
app.secret_key = 'random string'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = ['jpeg', 'jpg', 'png', 'gif']
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["ecommerce_internal"]


def get_login_details():
    if 'email' not in session:
        logged_in = False
        first_name = ''
        no_of_items = 0
    else:
        logged_in = True
        user_info = db.users.find_one({"email": session['email']})
        userId, first_name = user_info['_id'], user_info['first_name']
        cart = list(db.cart.find({"user_id": userId}))
        no_of_items = len(cart)

    return (logged_in, first_name, no_of_items)


@app.route("/")
def root():
    logged_in, first_name, no_of_items = get_login_details()
    itemData = list(db.categories.find({}))
    return render_template('home.html', itemData=itemData, loggedIn=logged_in, firstName=first_name,
                           noOfItems=no_of_items)

@app.route("/add")
def admin():
    categories = constants.CATEGORIES
    return render_template('add.html', categories=categories)


@app.route("/addProduct", methods=["GET", "POST"])
def addItem():
    if request.method == "POST":
        product_name = request.json['product_name']
        price = float(request.json['price'])
        description = request.json['description']
        category = request.json['category']
        qty = int(request.json['qty'])
        image_url = request.json['image_url']
        products = {"product_name": product_name, "price": price, "description": description,
                    "category": category, "qty": qty, "image_url": image_url}
        db.products.insert_one(products)
        return jsonify({"success": True, "message": "Product added successfully!"})


@app.route("/remove")
def remove():
    products = list(db.products.find({}))
    return render_template('remove.html', data=products)

@app.route("/removeItem")
def removeItem():
    productId = request.args.get('productId')
    db.products.delete_one({"_id": productId})
    return redirect(url_for('root'))

@app.route("/displayCategory")
def displayCategory():

    loggedIn, firstName, noOfItems = get_login_details()
    categoryId = request.args.get("categoryId")

    return render_template('displayCategory.html', data=constants.CATEGORIES, loggedIn=loggedIn, firstName=firstName,
                           noOfItems=noOfItems, categoryName=constants.CATEGORIES[categoryId])

@app.route("/account/profile")
def profileHome():
    if 'email' not in session:
        return redirect(url_for('root'))
    loggedIn, firstName, noOfItems = get_login_details()
    return render_template("profileHome.html", loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

@app.route("/account/profile/edit")
def editProfile():
    if 'email' not in session:
        return redirect(url_for('root'))
    loggedIn, firstName, noOfItems = get_login_details()
    profileData = db.users.find_one({'email': session['email']})
    return render_template("editProfile.html", profileData=profileData, loggedIn=loggedIn,
                           firstName=firstName, noOfItems=noOfItems)

@app.route("/account/profile/changePassword", methods=["GET", "POST"])
def changePassword():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    if request.method == "POST":
        old_password = request.form['oldpassword']
        new_password = request.form['newpassword']

        user_info = db.users.find_one({'email': session['email']})
        if check_password_hash(user_info['password'], old_password):
            db.users.update_one({"email": session['email']},
                                {"$set": {"password": generate_password_hash(new_password)}})
            msg = "Password updated successfully!"
        else:
            msg = "Old password doesn't match!"
        return render_template("changePassword.html", msg=msg)
    else:
        return render_template("changePassword.html")


@app.route("/updateProfile", methods=["GET", "POST"])
def update_profile():
    if request.method == 'POST':
        email = request.form['email']
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        phone = request.form['phone']

        update_data = {"email": email, "first_name": first_name, "last_name": last_name,
                       "phone": phone}
        db.users.update_one({"email": email}, {"$set": update_data})
        flash("Profile updated successfully!")

        return redirect(url_for('editProfile'))


@app.route("/loginForm")
def login_form():
    if 'email' in session:
        return redirect(url_for('root'))
    else:
        return render_template('login.html', error='')


def is_valid(email, password):
    user_info = db.users.find_one({"email": email})
    if user_info:
        return check_password_hash(user_info['password'], password)
    else:
        return False


@app.route("/login", methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if is_valid(email, password):
            session['email'] = email
            flash('Logged In successfully')
            return redirect(url_for('root'))
        else:
            flash('Invalid Email/Password!', 'error')
            return render_template('login.html')
    else:
        return render_template('login.html')


@app.route("/productDescription")
def productDescription():
    loggedIn, firstName, noOfItems = get_login_details()
    productId = request.args.get('productId')
    productData = db.products.find_one({"_id": productId})
    return render_template("productDescription.html", data=productData, loggedIn=loggedIn,
                           firstName=firstName, noOfItems=noOfItems)


@app.route("/addToCart")
def addToCart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    else:
        productId = int(request.args.get('productId'))
        userId = db.users.find_one({"email": session['email']})['_id']
        db.cart.insert_one({"user_id": userId, "product_id": productId})
        flash("Product added successfully!")
        return redirect(url_for('root'))


@app.route("/cart")
def cart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    loggedIn, firstName, noOfItems = get_login_details()
    email = session['email']
    userId = db.users.find_one({"email": email})['_id']
    cart_data = db.cart.find_one({"user_id": userId})
    if cart_data:
        products = db.products.find({"_id": cart_data['product_id']})
        totalPrice = 0
        for row in products:
            totalPrice += row['price']
    else:
        products = []
        totalPrice = 0.0
    return render_template("cart.html", products=products, totalPrice=totalPrice,
                           loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)


@app.route("/removeFromCart")
def removeFromCart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    email = session['email']
    productId = int(request.args.get('productId'))
    userId = db.users.find_one({"email": email})
    db.cart.delete_one({"user_id": userId, "product_id": productId})
    flash("Removed successfully!")
    return redirect(url_for('root'))


@app.route("/logout")
def logout():
    session.pop('email', None)
    return redirect(url_for('root'))


@app.route("/register", methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']

        user_info = {"first_name": first_name, "last_name": last_name, "email": email,
                     "password": generate_password_hash(password), "phone": phone}
        db.users.insert_one(user_info)
        flash("User successfully registered!", "success")
        return render_template("login.html", error="")


@app.route("/registerationForm")
def registrationForm():
    return render_template("register.html")

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def parse(data):
    ans = []
    i = 0
    while i < len(data):
        curr = []
        for j in range(7):
            if i >= len(data):
                break
            curr.append(data[i])
            i += 1
        ans.append(curr)
    return ans


if __name__ == '__main__':
    app.run(debug=True, port=5155)
