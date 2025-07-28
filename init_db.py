from app import app
from models import db, User, Category, Product, Order, OrderItem, Review
from datetime import datetime
import json

def init_database():
    with app.app_context():
        # Create all tables
        db.drop_all()
        db.create_all()
        
        print("Database tables created successfully!")
        
        # Create admin user
        admin = User(
            email='admin@woodnook.com',
            first_name='Admin',
            last_name='User',
            phone='+91-9876543210',
            address='123 Admin Street',
            city='Mumbai',
            state='Maharashtra',
            zip_code='400001',
            country='India',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create demo customer
        customer = User(
            email='customer@demo.com',
            first_name='John',
            last_name='Doe',
            phone='+91-9876543211',
            address='456 Customer Lane',
            city='Delhi',
            state='Delhi',
            zip_code='110001',
            country='India'
        )
        customer.set_password('demo123')
        db.session.add(customer)
        
        # Create categories
        categories_data = [
            {
                'name': 'Wooden Toys',
                'description': 'Safe, non-toxic wooden toys for children of all ages',
                'image_url': 'images/categories/toys.jpg'
            },
            {
                'name': 'Wall Décor',
                'description': 'Beautiful handcrafted wooden wall decorations',
                'image_url': 'images/categories/wall-decor.jpg'
            },
            {
                'name': 'Home Décor',
                'description': 'Elegant wooden pieces for your home',
                'image_url': 'images/categories/home-decor.jpg'
            },
            {
                'name': 'Gift Sets',
                'description': 'Curated gift sets for special occasions',
                'image_url': 'images/categories/gifts.jpg'
            },
            {
                'name': 'Kitchen Items',
                'description': 'Handcrafted wooden kitchen essentials',
                'image_url': 'images/categories/kitchen.jpg'
            },
            {
                'name': 'Garden Décor',
                'description': 'Weather-resistant wooden garden decorations',
                'image_url': 'images/categories/garden.jpg'
            }
        ]
        
        for cat_data in categories_data:
            category = Category(**cat_data)
            db.session.add(category)
        
        db.session.commit()
        
        # Create products
        products_data = [
            {
                'name': 'Wooden Building Blocks Set',
                'description': 'A classic set of 50 wooden building blocks in various shapes and sizes. Made from sustainable beech wood with smooth, rounded edges for safe play. Perfect for developing creativity, problem-solving skills, and hand-eye coordination in children.',
                'short_description': 'Classic 50-piece wooden building blocks set for creative play',
                'price': 1299.00,
                'original_price': 1599.00,
                'stock': 25,
                'category_id': 1,
                'material': 'Sustainable Beech Wood',
                'dimensions': '30cm x 20cm x 8cm',
                'weight': '1.2kg',
                'age_group': '3+ years',
                'care_instructions': 'Clean with a damp cloth. Avoid soaking in water.',
                'image_url': 'images/products/wooden-blocks.jpg',
                'is_featured': True,
                'slug': 'wooden-building-blocks-set'
            },
            {
                'name': 'Handcrafted Wooden Puzzle - Animals',
                'description': 'Beautiful handcrafted wooden puzzle featuring colorful farm animals. Each piece is carefully cut and sanded smooth, painted with non-toxic, child-safe paints. Helps develop problem-solving skills and animal recognition.',
                'short_description': 'Colorful farm animals wooden puzzle for toddlers',
                'price': 899.00,
                'original_price': 1099.00,
                'stock': 30,
                'category_id': 1,
                'material': 'Pine Wood with Non-toxic Paint',
                'dimensions': '25cm x 20cm x 1.5cm',
                'weight': '0.4kg',
                'age_group': '2-5 years',
                'care_instructions': 'Wipe clean with a dry cloth. Keep away from moisture.',
                'image_url': 'images/products/animal-puzzle.jpg',
                'is_featured': True,
                'slug': 'handcrafted-wooden-puzzle-animals'
            },
            {
                'name': 'Wooden Train Set with Track',
                'description': 'Complete wooden train set with locomotive, carriages, and 20-piece curved track. Encourages imaginative play and storytelling. Compatible with most standard wooden railway systems.',
                'short_description': 'Complete wooden train set with track pieces',
                'price': 2499.00,
                'original_price': 2999.00,
                'stock': 15,
                'category_id': 1,
                'material': 'Solid Birch Wood',
                'dimensions': 'Track: 100cm diameter when assembled',
                'weight': '2.5kg',
                'age_group': '3+ years',
                'care_instructions': 'Clean with a slightly damp cloth and dry immediately.',
                'image_url': 'images/products/train-set.jpg',
                'is_featured': True,
                'slug': 'wooden-train-set-with-track'
            },
            {
                'name': 'Rustic Wooden Wall Clock',
                'description': 'Handcrafted rustic wall clock made from reclaimed wood. Features large, easy-to-read numbers and silent quartz movement. Perfect for living rooms, kitchens, or offices with a natural aesthetic.',
                'short_description': 'Rustic handcrafted wall clock with silent movement',
                'price': 1799.00,
                'original_price': 2199.00,
                'stock': 20,
                'category_id': 2,
                'material': 'Reclaimed Oak Wood',
                'dimensions': '35cm x 35cm x 5cm',
                'weight': '1.8kg',
                'age_group': 'All ages',
                'care_instructions': 'Dust regularly with a soft cloth. Avoid direct sunlight.',
                'image_url': 'images/products/wall-clock.jpg',
                'is_featured': True,
                'slug': 'rustic-wooden-wall-clock'
            },
            {
                'name': 'Wooden Family Tree Photo Frame',
                'description': 'Beautiful laser-cut wooden family tree design that holds 8 photos of various sizes. Celebrates family bonds and makes a perfect gift for weddings, anniversaries, or housewarming.',
                'short_description': 'Laser-cut family tree frame for 8 photos',
                'price': 2299.00,
                'stock': 12,
                'category_id': 2,
                'material': 'Laser-cut Plywood',
                'dimensions': '50cm x 40cm x 2cm',
                'weight': '1.1kg',
                'age_group': 'All ages',
                'care_instructions': 'Dust gently with a soft brush. Keep away from moisture.',
                'image_url': 'images/products/family-tree-frame.jpg',
                'is_featured': False,
                'slug': 'wooden-family-tree-photo-frame'
            },
            {
                'name': 'Handcarved Wooden Bowls Set',
                'description': 'Set of 4 beautifully handcarved wooden bowls in different sizes. Perfect for serving salads, snacks, or as decorative pieces. Each bowl has unique wood grain patterns.',
                'short_description': 'Set of 4 handcarved wooden serving bowls',
                'price': 1599.00,
                'original_price': 1899.00,
                'stock': 18,
                'category_id': 3,
                'material': 'Mango Wood',
                'dimensions': 'Largest: 25cm dia, Smallest: 12cm dia',
                'weight': '1.5kg (set)',
                'age_group': 'All ages',
                'care_instructions': 'Hand wash only. Oil occasionally with food-safe wood oil.',
                'image_url': 'images/products/wooden-bowls.jpg',
                'is_featured': True,
                'slug': 'handcarved-wooden-bowls-set'
            },
            {
                'name': 'Wooden Candle Holders Trio',
                'description': 'Set of 3 elegant wooden candle holders in varying heights. Creates a beautiful ambiance for dinner parties or relaxing evenings. Holds standard taper candles.',
                'short_description': 'Elegant trio of wooden taper candle holders',
                'price': 1199.00,
                'stock': 22,
                'category_id': 3,
                'material': 'Teak Wood',
                'dimensions': 'Heights: 15cm, 20cm, 25cm',
                'weight': '0.8kg (set)',
                'age_group': 'Adult supervision required',
                'care_instructions': 'Wipe clean with a damp cloth. Remove wax drips promptly.',
                'image_url': 'images/products/candle-holders.jpg',
                'is_featured': False,
                'slug': 'wooden-candle-holders-trio'
            },
            {
                'name': 'Baby\'s First Wooden Toy Gift Set',
                'description': 'Carefully curated gift set for newborns and infants. Includes a wooden rattle, teething ring, and soft fabric blocks. All items are made with baby-safe materials and finishes.',
                'short_description': 'Complete wooden toy gift set for babies',
                'price': 1899.00,
                'original_price': 2299.00,
                'stock': 10,
                'category_id': 4,
                'material': 'Organic Maple Wood',
                'dimensions': 'Gift box: 30cm x 25cm x 10cm',
                'weight': '0.6kg',
                'age_group': '0-12 months',
                'care_instructions': 'Clean with mild soap and water. Air dry completely.',
                'image_url': 'images/products/baby-gift-set.jpg',
                'is_featured': True,
                'slug': 'baby-first-wooden-toy-gift-set'
            },
            {
                'name': 'Wooden Cutting Board with Handle',
                'description': 'Large, durable cutting board made from a single piece of bamboo. Features a convenient handle and juice groove around the edge. Perfect for bread, cheese, and general food preparation.',
                'short_description': 'Large bamboo cutting board with handle and groove',
                'price': 799.00,
                'original_price': 999.00,
                'stock': 35,
                'category_id': 5,
                'material': 'Bamboo',
                'dimensions': '40cm x 30cm x 2cm',
                'weight': '1.0kg',
                'age_group': 'All ages',
                'care_instructions': 'Hand wash with mild soap. Oil monthly with food-safe oil.',
                'image_url': 'images/products/cutting-board.jpg',
                'is_featured': False,
                'slug': 'wooden-cutting-board-with-handle'
            },
            {
                'name': 'Wooden Spice Rack with Jars',
                'description': 'Compact wooden spice rack with 12 glass jars and labels. Perfect for organizing your favorite spices and herbs. Mounts easily on wall or sits on counter.',
                'short_description': 'Wooden spice rack with 12 glass jars and labels',
                'price': 1399.00,
                'stock': 16,
                'category_id': 5,
                'material': 'Pine Wood with Glass Jars',
                'dimensions': '45cm x 15cm x 8cm',
                'weight': '2.2kg',
                'age_group': 'All ages',
                'care_instructions': 'Wipe wood with dry cloth. Jars are dishwasher safe.',
                'image_url': 'images/products/spice-rack.jpg',
                'is_featured': False,
                'slug': 'wooden-spice-rack-with-jars'
            },
            {
                'name': 'Garden Bird House - Traditional Design',
                'description': 'Charming traditional-style bird house made from cedar wood. Features a removable front panel for easy cleaning and drainage holes for weather protection.',
                'short_description': 'Traditional cedar wood bird house for garden',
                'price': 1099.00,
                'stock': 14,
                'category_id': 6,
                'material': 'Cedar Wood',
                'dimensions': '20cm x 15cm x 25cm',
                'weight': '0.9kg',
                'age_group': 'All ages',
                'care_instructions': 'Clean annually. Apply wood preservative if desired.',
                'image_url': 'images/products/bird-house.jpg',
                'is_featured': False,
                'slug': 'garden-bird-house-traditional-design'
            },
            {
                'name': 'Wooden Garden Plant Stakes Set',
                'description': 'Set of 6 decorative wooden plant stakes with cute garden-themed toppers. Perfect for marking herbs, vegetables, or flowers in your garden.',
                'short_description': 'Set of 6 decorative wooden garden plant stakes',
                'price': 599.00,
                'stock': 28,
                'category_id': 6,
                'material': 'Treated Pine Wood',
                'dimensions': 'Each stake: 30cm height',
                'weight': '0.4kg (set)',
                'age_group': 'All ages',
                'care_instructions': 'Weather-resistant. No special care required.',
                'image_url': 'images/products/plant-stakes.jpg',
                'is_featured': False,
                'slug': 'wooden-garden-plant-stakes-set'
            },
            {
                'name': 'Educational Wooden Alphabet Blocks',
                'description': 'Set of 26 wooden alphabet blocks featuring letters, numbers, and pictures. Perfect for early learning, spelling practice, and building. Made with non-toxic paints and rounded edges.',
                'short_description': '26-piece wooden alphabet learning blocks set',
                'price': 1499.00,
                'original_price': 1799.00,
                'stock': 20,
                'category_id': 1,
                'material': 'Beech Wood with Non-toxic Paint',
                'dimensions': 'Each block: 4cm x 4cm x 4cm',
                'weight': '1.8kg',
                'age_group': '2+ years',
                'care_instructions': 'Clean with a damp cloth. Air dry completely.',
                'image_url': 'images/products/alphabet-blocks.jpg',
                'is_featured': True,
                'slug': 'educational-wooden-alphabet-blocks'
            },
            {
                'name': 'Wooden Desk Organizer with Compartments',
                'description': 'Multi-compartment wooden desk organizer perfect for office or study space. Features slots for pens, paper, business cards, and a small drawer for miscellaneous items.',
                'short_description': 'Multi-compartment wooden desk organizer with drawer',
                'price': 1699.00,
                'stock': 11,
                'category_id': 3,
                'material': 'Oak Wood with Natural Finish',
                'dimensions': '35cm x 25cm x 12cm',
                'weight': '1.4kg',
                'age_group': 'All ages',
                'care_instructions': 'Dust regularly. Polish occasionally with wood polish.',
                'image_url': 'images/products/desk-organizer.jpg',
                'is_featured': False,
                'slug': 'wooden-desk-organizer-with-compartments'
            },
            {
                'name': 'Wedding Memory Box - Personalized',
                'description': 'Beautiful wooden memory box perfect for storing wedding keepsakes, love letters, and special mementos. Can be personalized with names and wedding date (engraving service available).',
                'short_description': 'Personalized wooden wedding memory keepsake box',
                'price': 2799.00,
                'original_price': 3299.00,
                'stock': 8,
                'category_id': 4,
                'material': 'Walnut Wood with Velvet Lining',
                'dimensions': '30cm x 20cm x 10cm',
                'weight': '1.3kg',
                'age_group': 'All ages',
                'care_instructions': 'Keep away from moisture. Dust with soft cloth.',
                'image_url': 'images/products/memory-box.jpg',
                'is_featured': True,
                'slug': 'wedding-memory-box-personalized'
            }
        ]
        
        for product_data in products_data:
            product = Product(**product_data)
            db.session.add(product)
        
        db.session.commit()
        
        # Create some demo reviews
        reviews_data = [
            {
                'user_id': 2,  # customer
                'product_id': 1,  # wooden blocks
                'rating': 5,
                'title': 'Excellent quality!',
                'comment': 'My 4-year-old loves these blocks. Great quality wood and perfect size for small hands.',
                'is_verified': True
            },
            {
                'user_id': 2,
                'product_id': 2,  # animal puzzle
                'rating': 4,
                'title': 'Beautiful puzzle',
                'comment': 'The colors are vibrant and the pieces fit perfectly. My daughter enjoys it every day.',
                'is_verified': True
            },
            {
                'user_id': 2,
                'product_id': 4,  # wall clock
                'rating': 5,
                'title': 'Perfect for our kitchen',
                'comment': 'Love the rustic look! It\'s completely silent and fits perfectly in our kitchen.',
                'is_verified': True
            },
            {
                'user_id': 2,
                'product_id': 6,  # wooden bowls
                'rating': 5,
                'title': 'Beautiful craftsmanship',
                'comment': 'These bowls are gorgeous and well-made. Use them for serving and as decoration.',
                'is_verified': True
            }
        ]
        
        for review_data in reviews_data:
            review = Review(**review_data)
            db.session.add(review)
        
        db.session.commit()
        
        print("Demo data populated successfully!")
        print("\nDemo accounts created:")
        print("Admin: admin@woodnook.com / admin123")
        print("Customer: customer@demo.com / demo123")
        print(f"\nTotal products created: {len(products_data)}")
        print(f"Total categories created: {len(categories_data)}")

if __name__ == '__main__':
    init_database()
