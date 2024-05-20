# pyzzeria
Welcome to the PYzzeria web application! This application allows customers to browse, order, and manage pizza orders. It also includes an admin interface for managing pizzas, ingredients, and orders.

## Features
- Browse available pizzas and ingredients.
- Place orders for pizzas.
- User authentication and profile management.
- Admin interface for managing pizzas, ingredients, and orders.
- Search functionality for pizzas and ingredients.
- And many more.

## Installation

1. **Clone the repository:**

   ```sh
   git clone https://github.com/panicua/pyzzeria.git
   cd pizza-delivery
   
2. Create and activate **venv** (for Windows):
   ```sh
   python -m venv venv
   source venv/Scripts/activate
   
3. Install **requirements.txt** to your **venv**:
   ```sh
   pip install -r requirements.txt
4. Create .env file inside the project, and add there:
   ```sh
   SECRET_KEY=Change_it_to_your_secret_key
   DEBUG=True
5. Create migrations and apply them:
   ```sh
   python manage.py makemigrations
   python manage.py migrate
6. (Optional) Create a superuser to get access to admin panel:
   ```sh
   python manage.py createsuperuser
7. Start the server:
   ```sh
    python manage.py runserver
