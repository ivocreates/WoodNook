from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
import os
import json
from datetime import datetime
import uuid

from config import Config
from models import db, User, Category, Product, CartItem, Order, OrderItem, Review, ContactMessage

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Helper functions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def generate_order_number():
    return f"WN{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"

# Routes
@app.route('/')
def index():
    featured_products = Product.query.filter_by(is_featured=True, is_active=True).limit(8).all()
    categories = Category.query.all()
    latest_products = Product.query.filter_by(is_active=True).order_by(Product.created_at.desc()).limit(4).all()
    return render_template('index.html', 
                         featured_products=featured_products,
                         categories=categories,
                         latest_products=latest_products)

@app.route('/products')
def products():
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category', type=int)
    search = request.args.get('search', '')
    sort_by = request.args.get('sort', 'newest')
    
    query = Product.query.filter_by(is_active=True)
    
    # Filter by category
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    # Search filter
    if search:
        query = query.filter(Product.name.contains(search) | 
                           Product.description.contains(search))
    
    # Sorting
    if sort_by == 'price_low':
        query = query.order_by(Product.price.asc())
    elif sort_by == 'price_high':
        query = query.order_by(Product.price.desc())
    elif sort_by == 'name':
        query = query.order_by(Product.name.asc())
    else:  # newest
        query = query.order_by(Product.created_at.desc())
    
    products = query.paginate(page=page, per_page=app.config['PRODUCTS_PER_PAGE'], error_out=False)
    categories = Category.query.all()
    
    return render_template('products.html', 
                         products=products,
                         categories=categories,
                         current_category=category_id,
                         search_query=search,
                         sort_by=sort_by)

@app.route('/product/<int:id>')
def product_detail(id):
    product = Product.query.get_or_404(id)
    reviews = Review.query.filter_by(product_id=id).order_by(Review.created_at.desc()).all()
    related_products = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product.id,
        Product.is_active == True
    ).limit(4).all()
    
    return render_template('product_detail.html', 
                         product=product,
                         reviews=reviews,
                         related_products=related_products)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        quantity = int(request.form.get('quantity', 1))
        
        # Check if item already in cart
        cart_item = CartItem.query.filter_by(
            user_id=current_user.id,
            product_id=product_id
        ).first()
        
        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = CartItem(
                user_id=current_user.id,
                product_id=product_id,
                quantity=quantity
            )
            db.session.add(cart_item)
        
        db.session.commit()
        flash(f'{product.name} added to cart!', 'success')
        
        # Check if it's an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': f'{product.name} added to cart!'})
        
        return redirect(url_for('product_detail', id=product_id))
    
    except Exception as e:
        db.session.rollback()
        # Check if it's an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Failed to add item to cart. Please try again.'}), 500
        
        flash('Failed to add item to cart. Please try again.', 'error')
        return redirect(url_for('product_detail', id=product_id))

@app.route('/cart')
@login_required
def cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.total_price for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/update_cart/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    if cart_item.user_id != current_user.id:
        flash('Unauthorized action', 'error')
        return redirect(url_for('cart'))
    
    quantity = int(request.form.get('quantity', 1))
    if quantity <= 0:
        db.session.delete(cart_item)
    else:
        cart_item.quantity = quantity
    
    db.session.commit()
    flash('Cart updated!', 'success')
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:item_id>')
@login_required
def remove_from_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    if cart_item.user_id != current_user.id:
        flash('Unauthorized action', 'error')
        return redirect(url_for('cart'))
    
    db.session.delete(cart_item)
    db.session.commit()
    flash('Item removed from cart!', 'info')
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('cart'))
    
    if request.method == 'POST':
        # Process the checkout form submission
        return place_order()
    
    # Calculate totals for GET request
    subtotal = sum(item.total_price for item in cart_items)
    tax = subtotal * 0.18  # 18% GST for India
    shipping = 50 if subtotal < 500 else 0  # Free shipping over ₹500
    total = subtotal + tax + shipping
    
    return render_template('checkout.html', 
                         cart_items=cart_items,
                         subtotal=subtotal,
                         tax=tax,
                         shipping=shipping,
                         total=total)

@app.route('/place_order', methods=['POST'])
@login_required
def place_order():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('cart'))
    
    # Get payment method - accept any method for simplicity
    payment_method = request.form.get('payment_method', 'cod')
    if not payment_method:
        payment_method = 'cod'  # Default to COD if none selected
    
    # Calculate totals
    subtotal = sum(item.total_price for item in cart_items)
    tax = subtotal * 0.18  # 18% GST for India
    shipping = 50 if subtotal < 500 else 0
    
    # Add COD charges if applicable
    if payment_method == 'cod' and subtotal < 500:
        shipping += 25  # COD charges
    
    total = subtotal + tax + shipping
    
    # Determine payment status based on method
    if payment_method == 'cod':
        payment_status = 'pending'  # COD orders are pending until delivered
    else:
        payment_status = 'paid'  # Demo UPI payments are auto-approved
    
    # Get payment details based on method (simplified)
    payment_details = {}
    if payment_method == 'upi':
        upi_id = request.form.get('upi_id', '').strip()
        if upi_id:  # Only store if provided, don't require it
            payment_details['upi_id'] = upi_id
    
    # Create order
    order = Order(
        user_id=current_user.id,
        order_number=generate_order_number(),
        total_amount=total,
        tax_amount=tax,
        shipping_amount=shipping,
        shipping_name=request.form['shipping_name'],
        shipping_email=request.form['shipping_email'],
        shipping_phone=request.form.get('shipping_phone', ''),
        shipping_address=request.form['shipping_address'],
        shipping_city=request.form['shipping_city'],
        shipping_state=request.form['shipping_state'],
        shipping_zip=request.form['shipping_zip'],
        shipping_country='India',
        payment_method=payment_method,
        status='pending',
        payment_status=payment_status,
        payment_transaction_id=f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:6].upper()}"
    )
    
    db.session.add(order)
    db.session.flush()  # To get order.id
    
    # Create order items
    for cart_item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            price=cart_item.product.price
        )
        db.session.add(order_item)
    
    # Clear cart
    CartItem.query.filter_by(user_id=current_user.id).delete()
    
    db.session.commit()
    
    # Display success message
    if payment_method == 'cod':
        flash(f'Order {order.order_number} placed successfully! You will pay ₹{total:.2f} on delivery.', 'success')
    else:
        flash(f'Order {order.order_number} placed successfully! Payment of ₹{total:.2f} processed.', 'success')
    
    return redirect(url_for('order_success', order_id=order.id))

@app.route('/order_success/<int:order_id>')
@login_required
def order_success(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('index'))
    
    return render_template('order_success.html', order=order)

@app.route('/orders')
@login_required
def orders():
    page = request.args.get('page', 1, type=int)
    orders = Order.query.filter_by(user_id=current_user.id)\
                        .order_by(Order.created_at.desc())\
                        .paginate(page=page, per_page=10, error_out=False)
    return render_template('orders.html', orders=orders)

@app.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id and not current_user.is_admin:
        flash('Unauthorized access', 'error')
        return redirect(url_for('index'))
    
    return render_template('order_detail.html', order=order)

@app.route('/add_review/<int:product_id>', methods=['POST'])
@login_required
def add_review(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Check if user has already reviewed this product
    existing_review = Review.query.filter_by(
        user_id=current_user.id,
        product_id=product_id
    ).first()
    
    if existing_review:
        flash('You have already reviewed this product!', 'warning')
        return redirect(url_for('product_detail', id=product_id))
    
    review = Review(
        user_id=current_user.id,
        product_id=product_id,
        rating=int(request.form['rating']),
        title=request.form['title'],
        comment=request.form['comment']
    )
    
    db.session.add(review)
    db.session.commit()
    
    flash('Review added successfully!', 'success')
    return redirect(url_for('product_detail', id=product_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'error')
            return redirect(url_for('register'))
        
        user = User(
            email=email,
            first_name=request.form['first_name'],
            last_name=request.form['last_name'],
            phone=request.form.get('phone', ''),
            address=request.form.get('address', ''),
            city=request.form.get('city', ''),
            state=request.form.get('state', ''),
            zip_code=request.form.get('zip_code', ''),
            country=request.form.get('country', 'India')
        )
        user.set_password(request.form['password'])
        
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        flash('Registration successful!', 'success')
        return redirect(url_for('index'))
    
    return render_template('auth/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user, remember=request.form.get('remember'))
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid email or password!', 'error')
    
    return render_template('auth/login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        try:
            # Update basic info
            current_user.first_name = request.form['first_name']
            current_user.last_name = request.form['last_name']
            current_user.email = request.form['email']
            current_user.phone = request.form.get('phone', '')
            
            # Check if password update is requested
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            if new_password:
                if not current_password:
                    flash('Current password is required to change password', 'error')
                    return render_template('profile.html')
                
                if not current_user.check_password(current_password):
                    flash('Current password is incorrect', 'error')
                    return render_template('profile.html')
                
                if new_password != confirm_password:
                    flash('New passwords do not match', 'error')
                    return render_template('profile.html')
                
                current_user.set_password(new_password)
            
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {str(e)}', 'error')
    
    return render_template('profile.html')

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    # Legacy route - redirect to profile
    return redirect(url_for('profile'))
    return redirect(url_for('profile'))

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        message = ContactMessage(
            name=request.form['name'],
            email=request.form['email'],
            subject=request.form['subject'],
            message=request.form['message']
        )
        db.session.add(message)
        db.session.commit()
        
        flash('Message sent successfully! We will get back to you soon.', 'success')
        return redirect(url_for('contact'))
    
    return render_template('contact.html')

@app.route('/about')
def about():
    return render_template('about.html')

# Admin routes
@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))
    
    # Dashboard stats
    total_products = Product.query.count()
    total_orders = Order.query.count()
    total_users = User.query.count()
    total_revenue = db.session.query(db.func.sum(Order.total_amount)).filter_by(payment_status='paid').scalar() or 0
    
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_products=total_products,
                         total_orders=total_orders,
                         total_users=total_users,
                         total_revenue=total_revenue,
                         recent_orders=recent_orders)

@app.route('/admin/products')
@login_required
def admin_products():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))
    
    page = request.args.get('page', 1, type=int)
    products = Product.query.order_by(Product.created_at.desc())\
                          .paginate(page=page, per_page=20, error_out=False)
    
    return render_template('admin/products.html', products=products)

@app.route('/admin/product/add', methods=['GET', 'POST'])
@login_required
def admin_add_product():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Handle file upload
        image_url = None
        if 'image' in request.files:
            file = request.files['image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add timestamp to prevent conflicts
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            name, ext = os.path.splitext(filename)
            filename = f"{timestamp}_{name}{ext}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Create upload directory if it doesn't exist
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(file_path)
            image_url = f"uploads/{filename}"
        
        product = Product(
            name=request.form['name'],
            description=request.form['description'],
            price=float(request.form['price']),
            stock=int(request.form['stock']),
            category_id=int(request.form['category_id']),
            material=request.form.get('material', ''),
            dimensions=request.form.get('dimensions', ''),
            weight=request.form.get('weight', ''),
            age_group=request.form.get('age_range', ''),  # Map age_range to age_group
            image_url=image_url,
            is_featured=bool(request.form.get('is_featured')),
            slug=request.form['name'].lower().replace(' ', '-').replace(',', '').replace('\'', '')
        )
        
        db.session.add(product)
        db.session.commit()
        
        flash('Product added successfully!', 'success')
        return redirect(url_for('admin_products'))
    
    categories = Category.query.all()
    return render_template('admin/add_product.html', categories=categories)

@app.route('/admin/product/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_edit_product(id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))
    
    product = Product.query.get_or_404(id)
    
    if request.method == 'POST':
        # Handle file upload
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(file_path)
                product.image_url = f"uploads/{filename}"
        
        product.name = request.form['name']
        product.description = request.form['description']
        product.price = float(request.form['price'])
        product.stock = int(request.form['stock'])
        product.category_id = int(request.form['category_id'])
        product.material = request.form.get('material', '')
        product.dimensions = request.form.get('dimensions', '')
        product.weight = request.form.get('weight', '')
        product.age_group = request.form.get('age_range', '')  # Map age_range to age_group
        product.is_featured = bool(request.form.get('is_featured'))
        product.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('Product updated successfully!', 'success')
        return redirect(url_for('admin_products'))
    
    categories = Category.query.all()
    return render_template('admin/edit_product.html', product=product, categories=categories)

@app.route('/admin/product/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_delete_product(id):
    if not current_user.is_admin:
        if request.method == 'POST':
            return jsonify({'success': False, 'message': 'Access denied'}), 403
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))
    
    product = Product.query.get_or_404(id)
    
    try:
        db.session.delete(product)
        db.session.commit()
        
        if request.method == 'POST':
            return jsonify({'success': True, 'message': 'Product deleted successfully'})
        else:
            flash('Product deleted successfully!', 'success')
            return redirect(url_for('admin_products'))
    except Exception as e:
        db.session.rollback()
        if request.method == 'POST':
            return jsonify({'success': False, 'message': str(e)})
        else:
            flash(f'Error deleting product: {str(e)}', 'error')
            return redirect(url_for('admin_products'))

@app.route('/admin/orders')
@login_required
def admin_orders():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))
    
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status')
    
    query = Order.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    orders = query.order_by(Order.created_at.desc())\
                 .paginate(page=page, per_page=app.config['ORDERS_PER_PAGE'], error_out=False)
    
    return render_template('admin/orders.html', orders=orders, status_filter=status_filter)

@app.route('/admin/order/<int:id>')
@login_required
def admin_order_detail(id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))
    
    order = Order.query.get_or_404(id)
    return render_template('admin/order_detail.html', order=order)

@app.route('/admin/order/update_status/<int:id>', methods=['POST'])
@app.route('/admin/order/<int:id>/status', methods=['POST'])
@login_required
def admin_update_order_status(id):
    if not current_user.is_admin:
        if request.is_json:
            return jsonify({'success': False, 'message': 'Access denied'}), 403
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))
    
    order = Order.query.get_or_404(id)
    
    if request.is_json:
        data = request.get_json()
        new_status = data.get('status')
    else:
        new_status = request.form['status']
    
    try:
        order.status = new_status
        order.updated_at = datetime.utcnow()
        
        if new_status == 'shipped':
            order.shipped_at = datetime.utcnow()
        elif new_status == 'delivered':
            order.delivered_at = datetime.utcnow()
        
        db.session.commit()
        
        if request.is_json:
            return jsonify({'success': True, 'message': 'Order status updated successfully'})
        else:
            flash(f'Order status updated to {new_status}!', 'success')
            return redirect(url_for('admin_order_detail', id=id))
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'success': False, 'message': str(e)})
        else:
            flash(f'Error updating order: {str(e)}', 'error')
            return redirect(url_for('admin_order_detail', id=id))

@app.route('/admin/categories')
@login_required
def admin_categories():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))
    
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)

@app.route('/admin/category/add', methods=['POST'])
@login_required
def admin_add_category():
    if not current_user.is_admin:
        if request.is_json:
            return jsonify({'success': False, 'message': 'Access denied'}), 403
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))
    
    try:
        category = Category(
            name=request.form['name'],
            description=request.form.get('description', '')
        )
        
        db.session.add(category)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'success': True, 'message': 'Category added successfully'})
        else:
            flash('Category added successfully!', 'success')
            return redirect(url_for('admin_categories'))
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'success': False, 'message': str(e)})
        else:
            flash(f'Error adding category: {str(e)}', 'error')
            return redirect(url_for('admin_categories'))

@app.route('/admin/category/edit/<int:id>', methods=['POST'])
@login_required
def admin_edit_category(id):
    if not current_user.is_admin:
        if request.is_json:
            return jsonify({'success': False, 'message': 'Access denied'}), 403
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))
    
    category = Category.query.get_or_404(id)
    try:
        category.name = request.form['name']
        category.description = request.form.get('description', '')
        db.session.commit()
        
        if request.is_json:
            return jsonify({'success': True, 'message': 'Category updated successfully'})
        else:
            flash('Category updated successfully!', 'success')
            return redirect(url_for('admin_categories'))
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'success': False, 'message': str(e)})
        else:
            flash(f'Error updating category: {str(e)}', 'error')
            return redirect(url_for('admin_categories'))

@app.route('/admin/category/delete/<int:id>', methods=['POST'])
@login_required
def admin_delete_category(id):
    if not current_user.is_admin:
        if request.is_json:
            return jsonify({'success': False, 'message': 'Access denied'}), 403
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))
    
    category = Category.query.get_or_404(id)
    if category.products:
        if request.is_json:
            return jsonify({'success': False, 'message': 'Cannot delete category with products'})
        else:
            flash('Cannot delete category with products', 'error')
            return redirect(url_for('admin_categories'))
    
    try:
        db.session.delete(category)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'success': True, 'message': 'Category deleted successfully'})
        else:
            flash('Category deleted successfully!', 'success')
            return redirect(url_for('admin_categories'))
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'success': False, 'message': str(e)})
        else:
            flash(f'Error deleting category: {str(e)}', 'error')
            return redirect(url_for('admin_categories'))

# API routes for AJAX
@app.route('/api/cart/count')
@login_required
def api_cart_count():
    count = CartItem.query.filter_by(user_id=current_user.id).count()
    return jsonify({'count': count})

# Static file serving for uploads
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# Context processors
@app.context_processor
def inject_categories():
    return dict(categories=Category.query.all())

@app.context_processor
def inject_cart_count():
    if current_user.is_authenticated:
        cart_count = CartItem.query.filter_by(user_id=current_user.id).count()
        return dict(cart_count=cart_count)
    return dict(cart_count=0)

@app.context_processor
def inject_builtins():
    return dict(min=min, max=max, range=range)

# Template filters
@app.template_filter('product_image')
def product_image_filter(product):
    """Returns product image URL with fallback to online placeholder"""
    if product and hasattr(product, 'image_url') and product.image_url:
        return url_for('static', filename=product.image_url)
    # Fallback to online placeholder image
    return "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400&h=300&fit=crop&crop=center"

@app.template_filter('safe_image')
def safe_image_filter(image_url, fallback_type='product'):
    """Returns image URL with fallback to online images"""
    if image_url:
        return url_for('static', filename=image_url)
    
    # Different fallback images based on type
    fallbacks = {
        'product': "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400&h=300&fit=crop&crop=center",
        'wooden_toy': "https://images.unsplash.com/photo-1558618644-fcd25c85cd64?w=400&h=300&fit=crop&crop=center",
        'home_decor': "https://images.unsplash.com/photo-1507914464562-6ff4ac29692f?w=400&h=300&fit=crop&crop=center",
        'furniture': "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400&h=300&fit=crop&crop=center"
    }
    
    return fallbacks.get(fallback_type, fallbacks['product'])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
