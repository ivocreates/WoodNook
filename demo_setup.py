from app import app
from models import db
from init_db import init_database

def create_demo_images():
    """Create placeholder images for demo"""
    import os
    from PIL import Image, ImageDraw, ImageFont
    
    # Create directories
    images_dir = os.path.join('static', 'images')
    products_dir = os.path.join(images_dir, 'products')
    categories_dir = os.path.join(images_dir, 'categories')
    
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(products_dir, exist_ok=True)
    os.makedirs(categories_dir, exist_ok=True)
    os.makedirs('static/uploads', exist_ok=True)
    
    # Colors for different categories
    colors = {
        'toys': '#FFE4B5',
        'wall-decor': '#F0E68C', 
        'home-decor': '#DDA0DD',
        'gifts': '#FFB6C1',
        'kitchen': '#98FB98',
        'garden': '#87CEEB'
    }
    
    # Create category images
    category_images = [
        ('toys.jpg', 'Wooden Toys', colors['toys']),
        ('wall-decor.jpg', 'Wall Décor', colors['wall-decor']),
        ('home-decor.jpg', 'Home Décor', colors['home-decor']),
        ('gifts.jpg', 'Gift Sets', colors['gifts']),
        ('kitchen.jpg', 'Kitchen Items', colors['kitchen']),
        ('garden.jpg', 'Garden Décor', colors['garden'])
    ]
    
    for filename, text, color in category_images:
        img = Image.new('RGB', (400, 300), color)
        draw = ImageDraw.Draw(img)
        
        # Try to use a font, fallback to default if not available
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        # Calculate text position
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (400 - text_width) // 2
        y = (300 - text_height) // 2
        
        draw.text((x, y), text, fill='#333333', font=font)
        img.save(os.path.join(categories_dir, filename))
    
    # Create product images
    product_images = [
        ('wooden-blocks.jpg', 'Building Blocks', colors['toys']),
        ('animal-puzzle.jpg', 'Animal Puzzle', colors['toys']),
        ('train-set.jpg', 'Train Set', colors['toys']),
        ('wall-clock.jpg', 'Wall Clock', colors['wall-decor']),
        ('family-tree-frame.jpg', 'Family Tree', colors['wall-decor']),
        ('wooden-bowls.jpg', 'Wooden Bowls', colors['home-decor']),
        ('candle-holders.jpg', 'Candle Holders', colors['home-decor']),
        ('baby-gift-set.jpg', 'Baby Gift Set', colors['gifts']),
        ('cutting-board.jpg', 'Cutting Board', colors['kitchen']),
        ('spice-rack.jpg', 'Spice Rack', colors['kitchen']),
        ('bird-house.jpg', 'Bird House', colors['garden']),
        ('plant-stakes.jpg', 'Plant Stakes', colors['garden']),
        ('alphabet-blocks.jpg', 'Alphabet Blocks', colors['toys']),
        ('desk-organizer.jpg', 'Desk Organizer', colors['home-decor']),
        ('memory-box.jpg', 'Memory Box', colors['gifts'])
    ]
    
    for filename, text, color in product_images:
        img = Image.new('RGB', (400, 400), color)
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        # Calculate text position
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (400 - text_width) // 2
        y = (400 - text_height) // 2
        
        draw.text((x, y), text, fill='#333333', font=font)
        img.save(os.path.join(products_dir, filename))
    
    # Create hero image
    hero_img = Image.new('RGB', (600, 400), '#F5F5DC')
    draw = ImageDraw.Draw(hero_img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 32)
    except:
        font = ImageFont.load_default()
    
    text = "Handcrafted\nWooden Toys"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (600 - text_width) // 2
    y = (400 - text_height) // 2
    
    draw.text((x, y), text, fill='#8B4513', font=font, align='center')
    hero_img.save(os.path.join(images_dir, 'hero-wooden-toys.jpg'))
    
    # Create placeholder images
    placeholder_img = Image.new('RGB', (400, 400), '#E0E0E0')
    draw = ImageDraw.Draw(placeholder_img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    text = "No Image\nAvailable"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (400 - text_width) // 2
    y = (400 - text_height) // 2
    
    draw.text((x, y), text, fill='#999999', font=font, align='center')
    placeholder_img.save(os.path.join(images_dir, 'placeholder-product.jpg'))
    placeholder_img.save(os.path.join(images_dir, 'placeholder-category.jpg'))
    
    print("Demo images created successfully!")

if __name__ == '__main__':
    print("Setting up WoodNook demo environment...")
    
    # Initialize database and data
    init_database()
    
    # Create demo images
    try:
        create_demo_images()
    except ImportError:
        print("Pillow not installed. Skipping image creation.")
        print("Install with: pip install Pillow")
    except Exception as e:
        print(f"Error creating images: {e}")
    
    print("\n" + "="*50)
    print("🪵 WoodNook Demo Setup Complete! 🪵")
    print("="*50)
    print("\n🚀 To start the application:")
    print("   python app.py")
    print("\n🌐 Then visit: http://localhost:5000")
    print("\n👤 Demo Accounts:")
    print("   Customer: customer@demo.com / demo123")
    print("   Admin:    admin@woodnook.com / admin123")
    print("\n📋 Features included:")
    print("   ✅ Complete e-commerce functionality")
    print("   ✅ Product catalog with categories")
    print("   ✅ Shopping cart and checkout")
    print("   ✅ User authentication")
    print("   ✅ Admin panel for management")
    print("   ✅ Order management")
    print("   ✅ Product reviews")
    print("   ✅ Responsive design")
    print("   ✅ Demo data and images")
    print("\n💳 Demo Payment:")
    print("   Use any test card details for checkout")
    print("\n🛠️ Tech Stack:")
    print("   Frontend: HTML, CSS, JavaScript, Bootstrap 5")
    print("   Backend: Python Flask")
    print("   Database: SQLite")
    print("   Images: Auto-generated placeholders")
    print("\n" + "="*50)
