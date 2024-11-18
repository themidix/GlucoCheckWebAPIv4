# GlucoCheck API

A Flask-based REST API for managing food items and nutritional information with user authentication.

## 🚀 Features

- User authentication with JWT tokens
- Food items management (CRUD operations)
- Nutritional information tracking
- Token-based authorization
- PostgreSQL database integration
- CORS support

## 📋 Prerequisites

- Python 3.7+
- PostgreSQL
- pip (Python package manager)

## 🛠️ Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd glucocheck-api
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory and add:
```env
SQLALCHEMY_DATABASE_URI=postgresql://username:password@host:port/database
SECRET_KEY=your_secret_key_here
JWT_REFRESH_SECRET_KEY=your_refresh_secret_key_here
```

## 📦 Dependencies

- Flask
- Flask-SQLAlchemy
- Flask-Bcrypt
- Flask-CORS
- PyJWT
- psycopg2-binary

## 🗄️ Database Structure

### Tables

1. **users**
   - id (Primary Key)
   - first_name
   - last_name
   - email (Unique)
   - password (Hashed)
   - role

2. **food_type**
   - id (Primary Key)
   - type (Unique)

3. **food_item**
   - id (Primary Key)
   - name
   - volume
   - food_type_id (Foreign Key)
   - timestamp
   - date_uploaded

4. **nutritional_information**
   - id (Primary Key)
   - food_item_id (Foreign Key)
   - calories
   - carbs
   - fat
   - protein

## 🔐 Authentication Endpoints

### Register User
```http
POST /register
Content-Type: application/json

{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "password": "secure_password"
}
```

### Login
```http
POST /login
Content-Type: application/json

{
    "email": "john@example.com",
    "password": "secure_password"
}
```

### Logout
```http
POST /logout
Authorization: Bearer <access_token>
```

### Refresh Token
```http
POST /refresh
Content-Type: application/json

{
    "refresh_token": "<refresh_token>"
}
```

## 🍎 Food Management Endpoints

### Save Food Items
```http
POST /save-food-items
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "foods": [
        {
            "name": "Apple",
            "type": "Fruit",
            "volume": 100,
            "calories": 52,
            "carbs": 14,
            "fat": 0.2,
            "protein": 0.3
        }
    ]
}
```

### Get Food Items
```http
GET /get-food-items
Authorization: Bearer <access_token>
```

### Delete Food Item
```http
DELETE /food-items/<food_item_id>
Authorization: Bearer <access_token>
```

### Delete All Data
```http
DELETE /delete-all
Authorization: Bearer <access_token>
```

## 🔒 Security Features

- Password hashing using Bcrypt
- JWT token-based authentication
- Token blacklisting for logout
- Access and refresh token system
- Protected routes with token verification

## 🏃 Running the Application

1. Start the Flask server:
```bash
python app.py
```

2. The server will start on `http://localhost:5000`

## 🧪 Testing

To run the tests:
```bash
python -m pytest
```

## 🛡️ Error Handling

The API implements comprehensive error handling for:
- Invalid credentials
- Missing required fields
- Database constraints
- Token validation
- Resource not found
- Server errors

## 📝 Response Formats

All responses follow the format:
```json
{
    "message": "Success/Error message",
    "data": {}, // Optional
    "error": "Error details" // In case of error
}
```

## ⚠️ Important Notes

1. Always use HTTPS in production
2. Keep secret keys secure
3. Implement rate limiting in production
4. Regular token cleanup from blacklist
5. Database backup strategy

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Open a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details