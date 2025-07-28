@echo off
echo.
echo ====================================================
echo   🪵 WoodNook - Handcrafted Wooden Toys & Décor 🪵
echo ====================================================
echo.

echo 📦 Installing dependencies...
pip install -r requirements.txt

echo.
echo 🗄️ Setting up database and demo data...
python demo_setup.py

echo.
echo 🚀 Starting WoodNook application...
echo.
echo 💡 The application will start on: http://localhost:5000
echo.
echo 👤 Demo Accounts:
echo    Customer: customer@demo.com / demo123
echo    Admin:    admin@woodnook.com / admin123
echo.
echo 💳 Demo Payment: Use any test card details
echo.
echo ⚡ Press Ctrl+C to stop the server
echo.
echo ====================================================
echo.

python app.py
