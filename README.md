# 🪵 WoodNook - Handcrafted Wooden Toys & Décor

A charming online store for selling handcrafted wooden toys, home décor, and gifting sets with story-based product descriptions, eco-conscious branding, and smooth user experience.

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd WoodNook
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database:**
   ```bash
   python init_db.py
   ```

5. **Run the application:**
   ```bash
   python app.py
   ```

6. **Access the application:**
   - Main Store: http://localhost:5000
   - Admin Panel: http://localhost:5000/admin
   - Admin Credentials: admin@woodnook.com / admin123

## 📁 Project Structure

```
WoodNook/
├── app.py                  # Main Flask application
├── init_db.py             # Database initialization script
├── requirements.txt       # Python dependencies
├── config.py              # Configuration settings
├── models.py              # Database models
├── static/                # Static files (CSS, JS, Images)
│   ├── css/
│   ├── js/
│   ├── images/
│   └── uploads/           # Product images
├── templates/             # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── products.html
│   ├── product_detail.html
│   ├── cart.html
│   ├── checkout.html
│   ├── auth/
│   └── admin/
└── demo_data.py          # Demo data population
```

## 🧱 Features

### 👩‍🎨 Frontend Features
- ✅ Home page with aesthetic banner and featured items
- ✅ Products page with category filtering
- ✅ Product detail pages with ratings
- ✅ Shopping cart functionality
- ✅ User authentication (login/signup)
- ✅ Contact and About pages
- ✅ Fully responsive design

### 🛠 Admin Panel
- ✅ Add/edit/delete products
- ✅ View and manage orders
- ✅ Upload product images
- ✅ Manage categories
- ✅ Dashboard analytics

### 💸 E-Commerce Features
- ✅ Cart management
- ✅ Order processing
- ✅ Payment integration (demo)
- ✅ Order history
- ✅ Product reviews

## 🛒 Demo Data

The application comes pre-loaded with:
- 15+ sample products across categories
- Demo user accounts
- Sample orders and reviews
- Admin account for testing

## 💳 Payment Integration

**Demo Payment Credentials:**
- Card Number: 4242424242424242
- Expiry: Any future date (e.g., 12/25)
- CVV: Any 3 digits (e.g., 123)
- Name: Any name

## 🔐 User Accounts

**Demo Customer Account:**
- Email: customer@demo.com
- Password: demo123

**Admin Account:**
- Email: admin@woodnook.com
- Password: admin123

## 🛠 Tech Stack

- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Backend**: Python Flask
- **Database**: SQLite
- **Authentication**: Flask-Login
- **File Upload**: Flask-WTF
- **Styling**: Bootstrap 5 + Custom CSS

## 📱 Mobile Responsive

The application is fully responsive and optimized for:
- Desktop (1200px+)
- Tablet (768px - 1199px)
- Mobile (< 768px)

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production Deployment
1. Update `config.py` with production settings
2. Use a production WSGI server like Gunicorn
3. Configure environment variables
4. Use PostgreSQL for production database

## 🔧 Configuration

Edit `config.py` to customize:
- Database settings
- Secret keys
- Upload directories
- Payment gateway settings

## 📊 Database Schema

### Tables:
- **users**: User accounts and authentication
- **categories**: Product categories
- **products**: Product catalog
- **cart_items**: Shopping cart items
- **orders**: Order management
- **order_items**: Order line items
- **reviews**: Product reviews

## 🎯 Future Enhancements

- AI-powered product recommendations
- Advanced search with filters
- Wishlist functionality
- Multi-language support
- Blog section
- Newsletter subscription
- Social media integration

## 🐛 Troubleshooting

### Common Issues:

1. **Database not found**
   ```bash
   python init_db.py
   ```

2. **Missing dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Permission errors on uploads**
   - Check write permissions on `static/uploads/` directory

## 📞 Support

For support and questions:
- Email: support@woodnook.com
- GitHub Issues: [Create an issue](https://github.com/your-repo/issues)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Made with ❤️ for sustainable, handcrafted living**
