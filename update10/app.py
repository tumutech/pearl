 
from flask import Flask, render_template, redirect, url_for, session, request, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask_wtf import FlaskForm, Form
from wtforms import StringField, IntegerField, TextAreaField, HiddenField, SelectField,PasswordField,BooleanField,SubmitField
from flask_wtf.file import FileField, FileAllowed
import random
from datetime import datetime
from wtforms_sqlalchemy.fields import QuerySelectField
from flask import Flask
from flask import Blueprint, render_template, request, flash, redirect,url_for
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user, logout_user, login_required,current_user,LoginManager
from flask_login import UserMixin
from wtforms.validators import DataRequired, Email,Length
from flask import  render_template
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_bootstrap import Bootstrap
from flask_msearch import Search

app = Flask(__name__)

photos = UploadSet('photos', IMAGES)

app.config['UPLOADED_PHOTOS_DEST'] = 'images'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pearl.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'mysecret'

configure_uploads(app, photos)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
admin=Admin(app, name='Control Panel')
manager = Manager(app)
manager.add_command('db', MigrateCommand)
search=Search()
search.init_app(app)

login_manager=LoginManager()
login_manager.login_view='login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))




    bootstrap = Bootstrap(app)




class User(UserMixin, db.Model):
    id=db.Column(db.Integer, primary_key=True)
    email=db.Column(db.String(100),unique=True)
    password=db.Column(db.String(120))
    name=db.Column(db.String(1000))
    is_admin=db.Column(db.Boolean, default=False)


class Controller(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.is_authenticated
        else:
            return abort(404)
        return current_user.is_authenticated
    def  not_auth(self):
        return "You are not authorized to view this pages"

admin.add_view(Controller(User, db.session))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('cart.html', error='error'),404

class Weight(db.Model):
    __searchbale__=['name']
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(1000))


class Shop(db.Model):
    __searchbale__=['name']
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(1000))




class Contact_info(db.Model):
    __searchbale__=['name']
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(1000))
    first=db.Column(db.String(1000))
    second=db.Column(db.String(1000))


class Location(db.Model):
    __searchbale__=['name']
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(1000))


class Category(db.Model):
    __searchbale__=['name']
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(1000))



class Brand(db.Model):
    __searchbale__=['name']
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(1000))


class Product(db.Model):
    __searchbale__=['name''description']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    price = db.Column(db.Integer) #in cents
    stock = db.Column(db.Integer)
    image=db.Column(db.String(100))
    description = db.Column(db.String(500))
    Cost_price= db.Column(db.Integer)
    pub_date=db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    brand_id=db.Column(db.Integer, db.ForeignKey('brand.id'), nullable=False)
    brand=db.relationship('Brand', backref=db.backref('brands', lazy=True))

    weight_id=db.Column(db.Integer, db.ForeignKey('weight.id'), nullable=False)
    weight=db.relationship('Weight', backref=db.backref('weights', lazy=True))

    location_id=db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    location=db.relationship('Location', backref=db.backref('locations', lazy=True))

    shop_id=db.Column(db.Integer, db.ForeignKey('shop.id'), nullable=False)
    shop=db.relationship('Shop', backref=db.backref('shops', lazy=True))


    
    category_id=db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    category=db.relationship('Category', backref=db.backref('categories', lazy=True))

    orders=db.relationship('Order_Item', backref='product', lazy=True)
    def __repr__(self):
        return '<Product>' % self.name
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(5))
    name = db.Column(db.String(20))
    phone_number = db.Column(db.Integer)
    email = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(100))
    status = db.Column(db.String(10))
    items = db.relationship('Order_Item', backref='order', lazy=True)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

    def order_total(self):
        return db.session.query(db.func.sum(Order_Item.quantity * Product.price)).join(Product).filter(Order_Item.order_id == self.id).scalar() + 3000

    def quantity_total(self):
        return db.session.query(db.func.sum(Order_Item.quantity)).filter(Order_Item.order_id == self.id).scalar()

class Order_Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer)




def weight_query():
    return Weight.query


def shop_query():
    return Shop.query
    
def location_query():
    return Location.query

def brand_query():
    return Brand.query

def category_query():
    return Category.query


class AddProduct(FlaskForm):
    name = StringField('Name')
    price = IntegerField('Price')
    cost=IntegerField('Cost_price')
    stock = IntegerField('Stock')
    description = TextAreaField('Description')
    image = FileField('Image', validators=[FileAllowed(IMAGES, 'Only images are accepted.')])
    shop=QuerySelectField(query_factory=shop_query, allow_blank=True, get_label='name')
    location=QuerySelectField(query_factory=location_query, allow_blank=True, get_label='name')
    category=QuerySelectField(query_factory=category_query , allow_blank=True, get_label='name')
    weight=QuerySelectField(query_factory=weight_query , allow_blank=True, get_label='name')
    brand=QuerySelectField(query_factory=brand_query , allow_blank=True, get_label='name')
class AddToCart(FlaskForm):
    quantity = IntegerField('Quantity')
    id = HiddenField('ID')




class AddCategory(FlaskForm):
    name = StringField('name')

class AddContact(FlaskForm):
    name = StringField('name')
    first=IntegerField('first')
    second=IntegerField('second')

class AddBrand(FlaskForm):
    name = StringField('name')

class AddWeight(FlaskForm):
    name = StringField('name')

class AddLocation(FlaskForm):
    name = StringField('name')

class AddShop(FlaskForm):
    name = StringField('name')






class Checkout(FlaskForm):
    name = StringField('Your Name', validators=[DataRequired()])

    phone_number = StringField('Your Phone Number', validators=[DataRequired()])
    email = StringField('Email Optional')
    address = StringField('Address(Point of Delivery', validators=[DataRequired()])

def handle_cart():
    products = []
    grand_total = 0
    index = 0
    quantity_total = 0

    for item in session['cart']:
        product = Product.query.filter_by(id=item['id']).first()

        quantity = int(item['quantity'])
        total = quantity * product.price
        grand_total += total

        quantity_total += quantity

        products.append({'id' : product.id, 'name' : product.name, 'price' :  product.price, 'image' : product.image, 'quantity' : quantity, 'total': total, 'index': index})
        index += 1
    
    grand_total_plus_shipping = grand_total + 3000

    return products, grand_total, grand_total_plus_shipping, quantity_total



@app.route('/')
def index():
    page= request.args.get('page',1,type=int)
    products= Product.query.filter(Product.stock>0).paginate(page=page, per_page=6)
    brands=Brand.query.join(Product, (Brand.id == Product.brand_id)).all()
    categories=Category.query.join(Product, (Category.id == Product.category_id)).all()

    return render_template('cart.html', products=products,brands=brands,categories=categories, index='index')

@app.route('/product/<id>')
def product(id):
    product = Product.query.filter_by(id=id).first()

    form = AddToCart()

    return render_template('cart.html', product=product,title='View_Product ',form=form,viewproduct='viewproduct' )

@app.route('/quick-add/<id>')
def quick_add(id):
    if 'cart' not in session:
        session['cart'] = []

    session['cart'].append({'id' : id, 'quantity' : 1})
    session.modified = True

    return redirect(url_for('index'))

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    if 'cart' not in session:
        session['cart'] = []

    form = AddToCart()

    if form.validate_on_submit():

        session['cart'].append({'id' : form.id.data, 'quantity' : form.quantity.data})
        session.modified = True

    return redirect(url_for('index'))



@app.route('/home')
def home():
    page= request.args.get('page',1,type=int)
    page2= request.args.get('page',1,type=int)
    Stationary= Product.query.filter_by(category_id=1).paginate(page=page, per_page=6)
    General_merchandise= Product.query.filter_by(category_id=2).paginate(page=page, per_page=6)
    Entertainment= Product.query.filter_by(category_id=3).paginate(page=page, per_page=6)
    Electronics= Product.query.filter_by(category_id=4).paginate(page=page, per_page=6)
    Computers= Product.query.filter_by(category_id=5).paginate(page=page, per_page=6)
    Electrical= Product.query.filter_by(category_id=6).paginate(page=page, per_page=6)
    Top_rated = Product.query.filter_by(category_id=7).paginate(page=page, per_page=6)
    Featured = Product.query.filter_by(category_id=8).paginate(page=page, per_page=6)
    Mobile_phones= Product.query.filter_by(category_id=9).paginate(page=page, per_page=6)
    Shoe_store = Product.query.filter_by(category_id=10).paginate(page=page, per_page=6)
    Jewelry= Product.query.filter_by(category_id=11).paginate(page=page, per_page=6)
    Refreshments= Product.query.filter_by(category_id=14).order_by(Product.id.desc()).limit(5).all() 
    Furniture= Product.query.filter_by(category_id=13).paginate(page=page, per_page=6)
    form=Checkout()
    products= Product.query.filter(Product.stock>0).paginate(page=page, per_page=6)
    brands=Brand.query.join(Product, (Brand.id == Product.brand_id)).all()
    categories=Category.query.join(Product, (Category.id == Product.category_id)).all()


    return render_template('home.html',Furniture=Furniture,Refreshments=Refreshments,Shoe_store=Shoe_store,Jewelry=Jewelry,Mobile_phones=Mobile_phones,Featured=Featured,Top_rated=Top_rated,Computers=Computers,Electrical=Electrical,brands=brands,Entertainment=Entertainment,categories=categories ,Stationary=Stationary,General_merchandise=General_merchandise,form=form ,product=product, products=products)


@app.route('/cart')
def cart():
    brands=Brand.query.all()
    categories=Category.query.all()
    if 'cart' not in session:
            session['cart']=[]
    products, grand_total, grand_total_plus_shipping, quantity_total = handle_cart()

    return render_template('cart.html', cart='cart',products=products,brands=brands,categories=categories, grand_total=grand_total, grand_total_plus_shipping=grand_total_plus_shipping, quantity_total=quantity_total)

@app.route('/remove-from-cart/<index>')
def remove_from_cart(index):
    del session['cart'][int(index)]
    session.modified = True
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    form = Checkout()
    brands=Brand.query.all()
    categories=Category.query.all()
    products, grand_total, grand_total_plus_shipping, quantity_total = handle_cart()

    if form.validate_on_submit():

        order = Order()
        #order1=Order1()
        form.populate_obj(order)
        #form.populate_obj(order1)
        order.reference = ''.join([random.choice('ABCDE') for _ in range(5)])
        #order1.reference=order.reference
        order.status = 'PENDING'
        order.date_posted=datetime.now()
        #order1.status = 'Cleared'

        for product in products:
            order_item = Order_Item(quantity=product['quantity'], product_id=product['id'])
            order.items.append(order_item)

            product = Product.query.filter_by(id=product['id']).update({'stock' : Product.stock - product['quantity']})
            
            #order_item1 = Order_Item(quantity=product['quantity'], product_id=product['id'])
            #order1.items.append(order_item)

            
        db.session.add(order)
        #db.session.add(order1)
        db.session.commit()

        session['cart'] = []
        session.modified = True
        flash(f'{ form.name.data } your Order was made successfully, we will call your phone number { form.phone_number.data } to confirm and make deliveries. Thanks for doing business with us')
        return redirect(url_for('index'))

    return render_template('cart.html', checkout='checkout',form=form,brands=brands,categories=categories, grand_total=grand_total, grand_total_plus_shipping=grand_total_plus_shipping, quantity_total=quantity_total)


@app.route('/admin/add', methods=['GET', 'POST'])
@login_required
def add():
    form = AddProduct()

    if form.validate_on_submit():
        image_url = photos.url(photos.save(form.image.data))

        new_product = Product(name=form.name.data, Cost_price=form.cost.data,shop=form.shop.data,location=form.location.data,weight=form.weight.data,brand=form.brand.data,category=form.category.data , price=form.price.data, stock=form.stock.data, description=form.description.data, image=image_url)

        db.session.add(new_product)
        db.session.commit()

        return redirect(url_for('main'))

    return render_template('admin/addbrand.html',admin=True, form=form, addproduct='addproduct')

@app.route('/admin/order/<order_id>')
@login_required
def order(order_id):
    order = Order.query.filter_by(id=int(order_id)).first()

    return render_template('admin/addbrand.html', order=order, admin=True, vieworder='vieworder')





@app.route('/brand/<int:id>')
def gt_brand(id):
    brands=Brand.query.all()
    categories=Category.query.all()
    products=Product.query.filter_by(brand_id=id)
    return render_template('cart.html', products=products,brands=brands,categories=categories, index='index')

@app.route('/category/<int:id>')
def gt_category(id):
    brands=Brand.query.all()
    categories=Category.query.all()
    products=Product.query.filter_by(category_id=id)
    return render_template('cart.html', products=products,brands=brands,categories=categories, cat='cat')






@app.route('/addbrand', methods=['GET','POST'])
@login_required
def addbrand():
    form=AddBrand()

    if form.validate_on_submit():
        new_brand = Brand(name=form.name.data)

        db.session.add(new_brand)
        db.session.commit()
        flash(f'The Brand { form.name.data } was added to your databaes successfully')
        return redirect(url_for('brand'))
    return render_template('admin/addbrand.html', brands='brands', form=form)

@app.route('/addweight', methods=['GET','POST'])
@login_required
def addweight():
    form=AddWeight()
    if form.validate_on_submit():
        new_brand = Weight(name=form.name.data)

        db.session.add(new_brand)
        db.session.commit()
        flash(f'The weight { form.name.data } was added to your databaes successfully')
        return redirect(url_for('weight'))
    return render_template('admin/addbrand.html',form=form, weights='weights')



@app.route('/addcategory', methods=['GET','POST'])
@login_required
def addcategory():
    form=AddCategory()
    if form.validate_on_submit():
        new_brand = Category(name=form.name.data)

        db.session.add(new_brand)
        db.session.commit()
        flash(f'The Category { form.name.data } was added to your databaes successfully')
        return redirect(url_for('category'))
    return render_template('admin/addbrand.html', form=form,categories='categories')

@app.route('/addshop', methods=['GET','POST'])
@login_required
def addshop():
    form=AddShop()
    if form.validate_on_submit():
        new_brand = Shop(name=form.name.data)

        db.session.add(new_brand)
        db.session.commit()
        flash(f'The shop { form.name.data } was added to your databaes successfully')
        return redirect(url_for('shop'))
    return render_template('admin/addbrand.html', form=form,shops='shops')


@app.route('/addlocation', methods=['GET','POST'])
@login_required
def addlocation():
    form=AddLocation()
    if form.validate_on_submit():
        new_brand = Location(name=form.name.data)

        db.session.add(new_brand)
        db.session.commit()
        flash(f'The location { form.name.data } was added to your databaes successfully')
        return redirect(url_for('location'))
    return render_template('admin/addbrand.html',form=form, locations='locations')

@app.route('/addcontact', methods=['GET','POST'])
@login_required
def addcontact():
    form=AddContact()
    if form.validate_on_submit():
        new_contact = Contact_info(name=form.name.data, first=form.first.data, second=form.second.data)

        db.session.add(new_contact)
        db.session.commit()
        flash(f'The contact { form.name.data } was added to your databaes successfully')
        return redirect(url_for('contact'))
    return render_template('admin/addbrand.html', contacts='contacts', form=form)



@app.route('/deletebrand/<int:id>', methods=['GET','POST'])
@login_required
def deletebrand(id):
    brand=Brand.query.get_or_404(id)
    db.session.delete(brand)
    db.session.commit()
    flash(f'Deleted successfully')
    if request.method=="POST":
        db.session.delete(brand)
        db.session.commit()
        flash(f'Deleted successfully')
        return redirect(url_for('brand'))
    flash(f'The Brand {brand.name}  cant be deleted')
    return redirect(url_for('brand'))

@app.route('/deleteweight/<int:id>', methods=['GET','POST'])
@login_required
def deleteweight(id):
    weight=Weight.query.get_or_404(id)
    db.session.delete(weight)
    db.session.commit()
    flash(f'Deleted successfully')
    if request.method=="POST":
        db.session.delete(weight)
        db.session.commit()
        flash(f'Deleted successfully')
        return redirect(url_for('main'))
    flash(f'The weight {weight.name}  cant be deleted')
    return redirect(url_for('main'))



@app.route('/deletecontact/<int:id>', methods=['GET','POST'])
@login_required
def deletecontact(id):
    contact=Contact_info.query.get_or_404(id)
    db.session.delete(contact)
    db.session.commit()
    flash(f'Deleted successfully')
    if request.method=="POST":
        db.session.delete(contact)
        db.session.commit()
        flash(f'Deleted successfully')
        return redirect(url_for('main'))
    flash(f'The contact {contact.name}  cant be deleted')
    return redirect(url_for('main'))


@app.route('/deletelocation/<int:id>', methods=['GET','POST'])
@login_required
def deletelocation(id):
    location=Location.query.get_or_404(id)
    db.session.delete(location)
    db.session.commit()
    flash(f'Deleted successfully')
    if request.method=="POST":
        db.session.delete(location)
        db.session.commit()
        flash(f'Deleted successfully')
        return redirect(url_for('main'))
    flash(f'The location {location.name}  cant be deleted')
    return redirect(url_for('main'))



@app.route('/deletecategory/<int:id>', methods=['GET','POST'])
@login_required
def deletecategory(id):
    category=Category.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()
    flash(f'Deleted successfully')
    if request.method=="POST":
        db.session.delete(category)
        db.session.commit()
        flash(f'Deleted successfully')
        return redirect(url_for('category'))
    flash(f'The category {category.name}  cant be deleted')
    return redirect(url_for('category'))


@app.route('/deleteshop/<int:id>', methods=['GET','POST'])
@login_required
def deleteshop(id):
    shop=Shop.query.get_or_404(id)
    db.session.delete(shop)
    db.session.commit()
    flash(f'Deleted successfully')

    if request.method=="POST":
        db.session.delete(shop)
        db.session.commit()
        flash(f'Deleted successfully')
        return redirect(url_for('main'))
    flash(f'The shop {shop.name}  cant be deleted')
    return redirect(url_for('main'))


@app.route('/deleteproduct/<int:id>', methods=['GET','POST'])
@login_required
def deleteproduct(id):
    product=Product.query.get_or_404(id)
    if request.method=="POST":
        try:
            image= photos.url(photos.remove(product.image))

        except Exception as e:
            print(e)
        db.session.delete(product)
        db.session.commit()
        flash(f'Deleted successfully')
        return redirect(url_for('main'))
    flash(f'The Product {product.name}  cant be deleted')
    return redirect(url_for('main'))

@app.route('/deleteOrder/<order_id>', methods=['GET','POST'])
@login_required
def deleteOreder(order_id):
    order=Order.query.get_or_404(order_id=id)
    order_Item=Order_Item.query.get_or_404(order_id=id)
    if request.method=="POST":
        try:
            db.session.delete(order)
            db.session.delete(order_Item)
            

            db.session.commit()
            flash(f'Deleted successfully')
            return redirect(url_for('admin1'))

        except Exception as e:
            print(e)
        
    flash(f'The Product {product.name}  cant be deleted')
    return redirect(url_for('main'))

@app.route('/category', methods=['GET','POST'])
@login_required
def category():
    form=AddCategory()
    categories=Category.query.all()
    return render_template('admin/addbrand.html', admin=True,all='all', form=form,category='category', categories=categories)


@app.route('/brand', methods=['GET','POST'])
@login_required
def brand():
    form=AddBrand()
    form1=AddWeight()
    form2=AddCategory()
    form3=AddShop()
    form4=AddLocation()
    form5=AddContact()
    brands=Brand.query.all()
    categories=Category.query.all()
    contacts=Contact_info.query.all()
    locations=Location.query.all()
    shops=Shop.query.all()
    weights=Weight.query.all()
    return render_template('admin/addbrand.html', admin=True, all='all',form1=form1,form2=form2,form3=form3,form4=form4,form5=form5, brand='brand',form=form, brands=brands)


@app.route('/contacts', methods=['GET','POST'])
@login_required
def contact():
    form=AddContact()
    contacts=Contact_info.query.all()
    return render_template('admin/addbrand.html', admin=True, all='all',contact='contact',form=form,contacts=contacts)

@app.route('/shops', methods=['GET','POST'])
@login_required
def shop():
    form=AddShop()
    shops=Shop.query.all()
    return render_template('admin/addbrand.html', admin=True,all='all',shop='shop',form=form,shops=shops)



@app.route('/locations', methods=['GET','POST'])
@login_required
def location():
    form=AddLocation()
    locations=Location.query.all()
    return render_template('admin/addbrand.html', all='all',admin=True,form=form,location='location' ,locations=locations)

@app.route('/weights', methods=['GET','POST'])
@login_required
def weight():
    form=AddWeight()
    weights=Weight.query.all()
    return render_template('admin/addbrand.html', all='all',admin=True,form=form,weight='weight', weights=weights)


@app.route('/mainpanel', methods=['GET', 'POST'])
@login_required
def main():
    products = Product.query.all()
    products_in_stock = Product.query.filter(Product.stock > 0).count()

    orders = Order.query.order_by(Order.date_posted.desc()).all()

    return render_template('admin/addbrand.html', admin=True,index='index',products=products, products_in_stock=products_in_stock, orders=orders)

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def Admin():
    products = Product.query.all()
    products_in_stock = Product.query.filter(Product.stock > 0).count()

    orders = Order.query.order_by(Order.date_posted.desc()).all()

    return render_template('admin/addbrand.html', admin=True,index='index',products=products, products_in_stock=products_in_stock, orders=orders)



@app.route('/adminproduct_view', methods=['GET', 'POST'])
@login_required
def adminproduct():
    products = Product.query.all()
    products_in_stock = Product.query.filter(Product.stock > 0).count()


    return render_template('admin/addbrand.html',admin=True, products=products, products_in_stock=products_in_stock, page='page')



class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me= BooleanField('Keep me logged in')
    submit = SubmitField('Log In')




@app.route('/profile')
@login_required
def profile():
    return render_template('admin/addbrand.html', user='user', admin=True,name=current_user.name, profile='profile')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email=form.email.data
        user = User.query.filter_by(email=email).first()
        password=form.password.data
        if user and check_password_hash(user.password, password):
            login_user(user, form.remember_me.data)
            return redirect(url_for('profile'))
        else:
            flash('Password or Email is incorrect,You are not allowed to LogIn ')
            return render_template('cart.html', admin=True,user='user',login='login', form=form)
    return render_template('cart.html', user='user',login='login', form=form)

'''@app.route('/login', methods=['POST'])
def login_post():
    email=request.form.get('email')
    password=request.form.get('password')
    remember= True if request.form.get('remember') else False

    user =User.query.filter_by(email=email).first()
    if not user and check_password_hash(user.password, password):
        
        return redirect(url_for('login'))


    login_user(user, remember=remember)



    return redirect(url_for('profile'))

'''


class SignupForm(FlaskForm):
    name =StringField('Name', validators=[DataRequired(), Length(1, 20)])
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),Email()])
    password = PasswordField('Password', validators=[DataRequired(),Length(1, 20)])
    password2 = PasswordField('Password', validators=[DataRequired(),Length(1, 20)])
    submit = SubmitField('SignIn')





@app.route('/signup', methods=['POST','GET'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        email=form.email.data
        name=form.name.data
        password=form.password.data
        password2=form.password2.data
        if password==password2:
            new_password=generate_password_hash(password, method='sha256')
            user =User.query.filter_by(email=email).first()

            if user:
                flash('Email address already exists!, if already registered')
                return redirect(url_for('signup'))

            new_user=User(email=email, name=name, password=new_password)
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('login'))
        else:
            flash('Password is not matching, Please Try Again')
            return redirect(url_for('signup'))
    return render_template('admin/addbrand.html', user='user', signup='signup', form=form)


@app.route('/result', methods=['GET','POST'])
def result():
    brands=Brand.query.all()
    categories=Category.query.all()
    searchword=request.args.get('q')
    productes = Product.query.msearch(searchword, fields=['name','description'])

    return render_template('cart.html',productes=productes,brands=brands,categories=categories, index='index')


@app.route('/admiro', methods=['POST','GET'])
def create_admin():
    form=SignupForm()
    if request.method=="POST":
        email=form.email.data
        name=form.name.data
        password=form.password.data
        new_user=User(email=email,password=password,name=name, is_admin=True)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('admin/addbrand.html', adminsignup='adminsignup', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))




if __name__ == '__main__':
    manager.run()