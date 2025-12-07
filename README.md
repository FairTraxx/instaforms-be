# InstaForms Backend

A Django REST API backend for creating and managing dynamic forms with real-time submissions.

## Features

- 🚀 **Dynamic Form Builder**: Create forms with various field types (text, email, select, etc.)
- 📊 **Form Management**: Full CRUD operations for forms and fields
- 📝 **Form Submissions**: Public API for form submissions with validation
- 🔐 **Authentication**: Token-based authentication for form creators
- 📱 **REST API**: Complete RESTful API with Django REST Framework
- 🌐 **CORS Support**: Cross-origin resource sharing enabled
- 👨‍💼 **Admin Interface**: Django admin for easy management

## Tech Stack

- **Backend**: Django 4.2, Django REST Framework
- **Database**: SQLite (default), PostgreSQL ready
- **Authentication**: Django Token Authentication
- **API Documentation**: Django REST Framework browsable API

## Quick Start

### Prerequisites

- Python 3.8+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd instaforms-be
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment setup**
   ```bash
   # Create .env file (optional)
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Database setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000/`

## API Endpoints

> 📚 **For detailed API documentation with request/response examples, see [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)**

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/profile/` - Get user profile
- `PATCH /api/auth/profile/` - Update user profile
- `POST /api/auth/change-password/` - Change password

### Forms (Authenticated)
- `GET /api/forms/` - List user's forms
- `POST /api/forms/` - Create new form
- `GET /api/forms/{id}/` - Get form details
- `PUT /api/forms/{id}/` - Update form
- `DELETE /api/forms/{id}/` - Delete form
- `POST /api/forms/{id}/add_field/` - Add field to form
- `GET /api/forms/{id}/submissions/` - Get form submissions

### Form Fields (Authenticated)
- `GET /api/fields/` - List user's form fields
- `PUT /api/fields/{id}/` - Update field
- `DELETE /api/fields/{id}/` - Delete field

### Public Forms (No Authentication)
- `GET /api/public/forms/` - List active forms
- `GET /api/public/forms/{id}/` - Get public form details
- `POST /api/public/forms/{id}/submit/` - Submit form response

### Submissions (Authenticated)
- `GET /api/submissions/` - List user's form submissions

## Form Field Types

- `text` - Single line text input
- `email` - Email input with validation
- `number` - Numeric input
- `textarea` - Multi-line text input
- `select` - Dropdown selection
- `radio` - Radio button selection
- `checkbox` - Checkbox selection
- `date` - Date picker
- `file` - File upload

## Example Usage

### Registering a New User

```python
import requests

# Register new user with email and password only
response = requests.post('http://localhost:8000/api/auth/register/', {
    'email': 'john@example.com',
    'password': 'SecurePassword123!',
    'password2': 'SecurePassword123!'
})

# Extract token from response
token = response.json()['token']
user = response.json()['user']
print(f"Registration successful! Token: {token}")
print(f"Username: {user['username']} (auto-generated from email)")

# Optional: Add first name and last name later
profile_response = requests.patch(
    'http://localhost:8000/api/auth/profile/',
    json={'first_name': 'John', 'last_name': 'Doe'},
    headers={'Authorization': f'Token {token}'}
)
```

### Logging In

```python
import requests

# Login with email and password
response = requests.post('http://localhost:8000/api/auth/login/', {
    'email': 'john@example.com',
    'password': 'SecurePassword123!'
})

token = response.json()['token']
user_data = response.json()['user']
print(f"Welcome back, {user_data['first_name']}!")
```

### Creating a Form

```python
import requests

# Create form with authentication
form_data = {
    'title': 'Contact Form',
    'description': 'Get in touch with us',
    'is_active': True
}

response = requests.post(
    'http://localhost:8000/api/forms/',
    json=form_data,
    headers={'Authorization': f'Token {token}'}
)

form = response.json()
form_id = form['id']
```

### Adding Fields to Form

```python
# Add a text field
field_data = {
    'label': 'Your Name',
    'field_type': 'text',
    'required': True,
    'placeholder': 'Enter your full name',
    'order': 1
}

response = requests.post(
    f'http://localhost:8000/api/forms/{form_id}/add_field/',
    json=field_data,
    headers={'Authorization': f'Token {token}'}
)

# Add an email field
email_field = {
    'label': 'Email Address',
    'field_type': 'email',
    'required': True,
    'placeholder': 'your.email@example.com',
    'order': 2
}

response = requests.post(
    f'http://localhost:8000/api/forms/{form_id}/add_field/',
    json=email_field,
    headers={'Authorization': f'Token {token}'}
)
```

### Submitting a Form (Public)

```python
submission_data = {
    'responses': [
        {
            'field_id': 1,
            'value': 'John Doe'
        },
        {
            'field_id': 2,
            'value': 'john@example.com'
        }
    ]
}

response = requests.post(
    f'http://localhost:8000/api/public/forms/{form_id}/submit/',
    json=submission_data
)
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Database Configuration

For PostgreSQL:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'instaforms',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## Development

### Running Tests

```bash
python manage.py test
```

### Code Style

```bash
# Install development dependencies
pip install black flake8

# Format code
black .

# Check code style
flake8
```

## Deployment

### Production Settings

1. Set `DEBUG=False`
2. Configure proper `SECRET_KEY`
3. Set up production database
4. Configure static files serving
5. Set up proper CORS origins

### Using Gunicorn

```bash
pip install gunicorn
gunicorn instaforms.wsgi:application --bind 0.0.0.0:8000
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support, please open an issue on GitHub or contact the development team.
