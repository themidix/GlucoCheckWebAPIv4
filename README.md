# GlucoCheck API 🏥

A Flask-based REST API for managing food items and nutritional information with user authentication and AI-powered image analysis.

## 🚀 Features

- User authentication with JWT tokens and Google OAuth
- Food items management (CRUD operations)
- Nutritional information tracking
- AI-powered food image analysis
- Email services for password reset
- Token-based authorization
- PostgreSQL database integration
- CORS support

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL
- Google OAuth Credentials
- OpenAI API Key
- SMTP Server (for email services)

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
BASE_URL=http://localhost:5000

# Database Configuration
DATABASE_URI=postgresql://username:password@host:port/database

# JWT Configuration
SECRET_KEY=your_secret_key_here
REFRESH_SECRET_KEY=your_refresh_secret_key_here
ACCESS_TOKEN_EXPIRES=3600
REFRESH_TOKEN_EXPIRES=604800

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your_email@example.com
MAIL_PASSWORD=your_email_password
RESET_PASSWORD_TOKEN_EXPIRES=30

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_DISCOVERY_URL=https://accounts.google.com/.well-known/openid-configuration
GOOGLE_AUTH_BASE_URL=https://accounts.google.com/o/oauth2/auth
GOOGLE_TOKEN_URL=https://accounts.google.com/o/oauth2/token
GOOGLE_USER_INFO_URL=https://www.googleapis.com/oauth2/v1/userinfo

# OpenAI Configuration
API_KEY=your_openai_api_key
```

## 📦 Dependencies

- Flask
- Flask-SQLAlchemy
- Flask-JWT-Extended
- Flask-Bcrypt
- Flask-CORS
- Flask-Mail
- Flask-Migrate 
- flasgger
- psycopg2-binary
- requests
- oauthlib
- pyOpenSSL
- python-dotenv
- regex
- openai
- pillow

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
   - user_id (Foreign Key)

4. **nutritional_information**
   - id (Primary Key)
   - food_item_id (Foreign Key)
   - calories
   - carbs
   - fat
   - protein

## 🔐 Authentication Endpoints

### Standard Authentication
```http
POST /auth-user/register           # Register new user
POST /auth-user/login             # User login
POST /auth-user/logout            # User logout
POST /auth-user/refresh           # Refresh access token
POST /auth-user/forgot-password   # Request password reset
POST /auth-user/reset-password/<token>  # Reset password
POST /auth-user/profile/reset-password  # Reset password from profile
```

### Google OAuth
```http
GET /google-auth/google/login      # Initiate Google login
GET /google-auth/google/authorized # Google OAuth callback
GET /google-auth/google/logout     # Google logout
```

## 🍎 Food Management Endpoints

### Save Food Items
```http
POST /food/food-items
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

### Other Food Endpoints
```http
GET /food/food-items         # Get user's food items
DELETE /food/food-items      # Delete all food data
DELETE /food/food-items/<id> # Delete specific food item
```

### Image Analysis
```http
POST /image-information/analyze    # Analyze food image
```

## 🔒 Security Features

- Password hashing using Bcrypt
- JWT token-based authentication
- Token blacklisting for logout
- Access and refresh token system
- Protected routes with token verification
- OAuth 2.0 integration
- Password complexity validation
- Email verification

## 🏃 Running the Application

1. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

2. Start the Flask server:
```bash
flask run
```

3. The server will start on `http://localhost:5000`

## 🧪 Testing

To run the tests:
```bash
python -m pytest
```

## 📝 Response Format

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
6. Secure handling of image uploads
7. Monitor API usage limits

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Open a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details
