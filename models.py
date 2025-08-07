from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    city = db.Column(db.String(80))
    state = db.Column(db.String(80))
    zip_code = db.Column(db.String(20))
    country = db.Column(db.String(80))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    orders = db.relationship('Order', backref='user', lazy=True)
    cart_items = db.relationship('CartItem', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    products = db.relationship('Product', backref='category', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    short_description = db.Column(db.String(200))
    price = db.Column(db.Float, nullable=False)
    original_price = db.Column(db.Float)  # For showing discounts
    stock = db.Column(db.Integer, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    
    # Product details
    material = db.Column(db.String(100))
    dimensions = db.Column(db.String(100))
    weight = db.Column(db.String(50))
    age_group = db.Column(db.String(50))
    care_instructions = db.Column(db.Text)
    
    # SEO and management
    slug = db.Column(db.String(120), unique=True)
    image_url = db.Column(db.String(200))
    gallery_images = db.Column(db.Text)  # JSON string of image URLs
    is_featured = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    cart_items = db.relationship('CartItem', backref='product', lazy=True)
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    reviews = db.relationship('Review', backref='product', lazy=True)
    
    @property
    def average_rating(self):
        if self.reviews:
            return sum(review.rating for review in self.reviews) / len(self.reviews)
        return 0
    
    @property
    def review_count(self):
        return len(self.reviews)
    
    @property
    def discount_percentage(self):
        if self.original_price and self.original_price > self.price:
            return int(((self.original_price - self.price) / self.original_price) * 100)
        return 0
    
    @property
    def image(self):
        """Backward compatibility property for image_url"""
        return self.image_url

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def total_price(self):
        return self.quantity * self.product.price

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    
    # Order details
    total_amount = db.Column(db.Float, nullable=False)
    tax_amount = db.Column(db.Float, default=0)
    shipping_amount = db.Column(db.Float, default=0)
    discount_amount = db.Column(db.Float, default=0)
    
    # Status
    status = db.Column(db.String(50), default='pending')  # pending, confirmed, shipped, delivered, cancelled
    payment_status = db.Column(db.String(50), default='pending')  # pending, paid, failed, refunded
    
    # Shipping details
    shipping_name = db.Column(db.String(120))
    shipping_email = db.Column(db.String(120))
    shipping_phone = db.Column(db.String(20))
    shipping_address = db.Column(db.Text)
    shipping_city = db.Column(db.String(80))
    shipping_state = db.Column(db.String(80))
    shipping_zip = db.Column(db.String(20))
    shipping_country = db.Column(db.String(80))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    shipped_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    
    # Payment details
    payment_method = db.Column(db.String(50))
    payment_transaction_id = db.Column(db.String(100))
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    @property
    def total(self):
        """Backward compatibility property for total_amount"""
        return self.total_amount

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)  # Price at time of order
    
    @property
    def total_price(self):
        return self.quantity * self.price

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    title = db.Column(db.String(120))
    comment = db.Column(db.Text)
    is_verified = db.Column(db.Boolean, default=False)  # Verified purchase
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200))
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
