import os
import secrets
from random import choice
from string import ascii_letters, digits
from PIL import Image
from datetime import date
from flask import render_template, url_for, flash, redirect, request, abort
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm, UpdateAccountForm, ReservationForm, ReservationLoginForm
from app.models import User, Reservation, Room
from flask_login import login_user, current_user, logout_user, login_required

@app.route("/")
@app.route("/home")
def home():
    rooms = Room.query.all()
    return render_template('home.html',rooms=rooms)

@app.route("/about")
def about():
    return render_template('about.html',title='About')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created! You are now able to log in!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html',title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html',title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_profile_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename) # use the _ to remove the variable or not use it 
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    
    form_picture.save(picture_path)
    
    return picture_fn


@app.route("/account", methods=['GET','POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_profile_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/'+ current_user.image_file)
    return render_template('account.html',title='account', image_file=image_file, form=form)

def male_or_female(ID):
    strID = str(ID)

    if(int(strID[12]) % 2 == 0 ):
        return "Female"
    else:
        return "Male"


def Date_from_ID(ID):
    strID = str(ID)

    if(strID[0] == '3'):
        year = int('20' + strID[1:3])
    else:
        year = int('19' + strID[1:3])

    month = int(strID[3:5])

    day = int(strID[5:7])

    x = date(year, month, day)

    return x

def getavailable():
    choices=[ ('suite', 'Suite'), ('family', 'Family'), ('deluxe', 'Deluxe'), ('classic', 'Classic'), ('superior', 'Superior'), ('luxury', 'Luxury') ]
    rooms = Room.query.order_by(Room.id.desc()).filter_by(number = 0).all()
    for room in rooms:
        del choices[room.id-1]
    return choices


@app.route('/reservation', methods=['GET', 'POST'])
@app.route('/reservation/<room>', methods=['GET', 'POST'])
@login_required
def reservation(room = None):
    form = ReservationForm()
    form.room.choices = getavailable()
    if form.validate_on_submit():
        room = Room.query.filter_by(rname=form.room.data).first()
        if form.NationalID.data:
            gender = male_or_female(int(form.NationalID.data))
            dateID = Date_from_ID(int(form.NationalID.data))
        ReservationID = ''.join([choice(ascii_letters 
            + digits) for n in range(10)])
        reserve = Reservation(name=form.name.data, email=form.email.data, ReservationID=ReservationID, room=form.room.data, adults=form.adults.data, children=form.children.data, checkin=form.checkin.data, checkout=form.checkout.data, user=current_user)
        if form.NationalID.data:
            reserve.gender = male_or_female(int(form.NationalID.data))
            reserve.birthdate = Date_from_ID(int(form.NationalID.data))
            reserve.NationalID = form.NationalID.data
        room.number -= 1
        db.session.add(reserve)
        db.session.commit()
        flash('Your Reservation is Succesfull','success')
        return redirect(url_for('reservation_success', reservation_id = ReservationID))
    elif request.method == 'GET' and current_user.is_authenticated :
        form.name.data = current_user.username
        form.email.data = current_user.email
    if room:
        form.room.data = room
    return render_template('reservation.html', form=form)

@app.route('/reservation_success/<reservation_id>')
@login_required
def reservation_success(reservation_id):
    return render_template('ReservationSuc.html', ReservationID=reservation_id)

@app.route('/reservation_list')
@login_required
def reservation_list():
    if current_user.role == 'Admin':
        reservations = Reservation.query.order_by(Reservation.date_posted.desc()).all()
        return render_template('reservation_list.html', reservations=reservations)
    else:
        flash('You need to be admin to view this page.','danger')
        return redirect(url_for('home'))

@app.route('/reservation/<int:guest_id>/show')
@login_required
def reservation_show(guest_id):
    guest = Reservation.query.get_or_404(guest_id)
    if current_user.role == 'Admin' or current_user == guest.user:
        createDate = str(guest.date_posted)
        createDate = createDate[:10] + " (" + createDate[11:19] + ")"
        return render_template('reservation_details.html', title='Details', guest=guest, createDate=createDate)
    else:
        flash('You need to be admin to view this page.','danger')
        return redirect(url_for('home'))


@app.route('/reservation/<int:guest_id>/delete')
@login_required
def delete_reservation(guest_id):
    guest = Reservation.query.get_or_404(guest_id)
    if current_user.role == 'Admin' or current_user == guest.user:
        return render_template('reservation_delete.html', guest=guest)
    else:
        flash('You need to be admin to view this page.','danger')
        return redirect(url_for('home'))

@app.route('/reservation/<int:guest_id>/confirm_delete', methods=['POST'])
def confirm_delete_reservation(guest_id):
    if current_user.role == 'Admin':
        guest = Reservation.query.get_or_404(guest_id)
        room = Room.query.filter_by(rname=guest.room).first()
        room.number += 1
        db.session.delete(guest)
        db.session.commit()
        flash('Reservation has been deleted!', 'success')
        return redirect(url_for('reservation_list'))
    else:
        flash('You need to be admin to view this page.','danger')
        return redirect(url_for('home'))

@app.route('/reservation/<int:guest_id>/update', methods=['GET', 'POST'])
@login_required
def update_reservation(guest_id):
    guest = Reservation.query.get_or_404(guest_id)
    if current_user.role == 'Admin' or current_user == guest.user:
        form = ReservationForm()
        form.room.choices = getavailable()
        guest = Reservation.query.get_or_404(guest_id)
        room = Room.query.filter_by(rname=guest.room).first()
        if form.validate_on_submit():
            guest.name = form.name.data
            guest.email = form.email.data
            guest.checkin = form.checkin.data
            guest.checkout = form.checkout.data
            guest.adults = form.adults.data
            if guest.room != form.room.data:
                room.number += 1
                guest.room = form.room.data
                room = Room.query.filter_by(rname=form.room.data).first()
                room.number -= 1
            guest.children = form.children.data
            if form.NationalID.data:
                guest.NationalID = int(form.NationalID.data)
                guest.gender = male_or_female(int(form.NationalID.data))
                guest.birthdate = Date_from_ID(int(form.NationalID.data))
            else:
                guest.NationalID = None
                guest.gender = None
                guest.birthdate = None
            db.session.commit()
            flash('Reservation has been Updated!','success')
            return redirect(url_for('reservation_list'))
        elif request.method == 'GET':
            form.name.data = guest.name
            form.email.data = guest.email
            if guest.NationalID != None:
                form.NationalID.data = str(guest.NationalID)
            form.checkin.data = guest.checkin
            form.checkout.data = guest.checkout
            form.adults.data = guest.adults
            form.room.data = guest.room
            form.children.data = guest.children
        return render_template('update_reservation.html', title="Reservation Update", form=form)
    else:
        flash('You need to be admin to view this page.','danger')
        return redirect(url_for('home'))


@app.route("/user/reservation/Login", methods=['GET', 'POST'])
@login_required
def Reservation_login():
    form = ReservationLoginForm()
    if form.validate_on_submit():
        reservation = Reservation.query.filter_by(ReservationID=str(form.ReservationID.data)).first()
        if  current_user == reservation.user and reservation.ReservationID == form.ReservationID.data:
            return redirect(url_for('reservation_user_show', reservation_id=reservation.ReservationID))
        else:
            flash('Login Unsuccessful. Please check Reservation ID', 'danger')
    return render_template('user_reservation_login.html',title='Reservation Login', form=form)


@app.route('/reservation/<reservation_id>/show')
@login_required
def reservation_user_show(reservation_id):
    guest = Reservation.query.filter_by(ReservationID=reservation_id).first()
    return render_template('reservation_user_details.html', title='Details', guest=guest)
































""" @app.route('/products')
def products():
    products = Product.query.all()
    return render_template('Rooms.html', products=products)

@app.route("/post/new", methods=['GET','POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content= form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your Post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post', form=form)


@app.route("/post/<int:post_id>") # making a variable in route
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET','POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post', form=form)
    
@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect( url_for('post_show') )


@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page = page, per_page = 5)
    return render_template('user_posts.html', posts=posts, user=user)


@app.route("/productlist")
def product_list():
    products = Product.query.all()
    return render_template('product_list.html',products=products)




def save_product_picture(product_image):
    random_hex = secrets.token_hex(8)
    _, i_ext = os.path.splitext(product_image.filename)
    product_hex_name = random_hex + i_ext
    image_path = os.path.join(app.root_path, 'static/product_pics', product_hex_name)

    product_image.save(image_path)

    return product_hex_name



@app.route('/product/new', methods=['GET','POST'])
def new_product():
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(name=form.name.data, description=form.description.data, price=form.price.data)
        if form.image.data:
            image_file = save_product_picture(form.image.data)
            product.image = image_file
        db.session.add(product)
        db.session.commit()
        flash('Your Product has been created!', 'success')
        return redirect(url_for('product_list'))
    return render_template('create_product.html', title="Product",form=form)


@app.route('/product/<int:product_id>/update', methods=['GET', 'POST'])
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm()
    if form.validate_on_submit():
        product.name = form.name.data
        product.price = form.price.data
        product.description = form.description.data
        if form.image.data:
            image_file = save_product_picture(form.image.data)
            product.image = image_file
        db.session.commit()
        flash('Your Product has been Updated!','success')
        return redirect(url_for('product_list'))
    elif request.method == 'GET':
        form.name.data = product.name
        form.description.data = product.description
        form.price.data = product.price
    return render_template('create_product.html', title='Product',form=form)


@app.route('/product/<int:product_id>/delete')
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_delete.html', product=product)
    

@app.route('/product/<int:product_id>/confirm_delete', methods=['POST'])
def confirm_delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Your Product has been deleted!', 'success')
    return redirect(url_for('product_list'))


@app.route('/post/show')
def post_show():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page = page, per_page = 5)
    return render_template('posts_list.html', posts=posts)
 """