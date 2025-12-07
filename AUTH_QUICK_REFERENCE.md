# Quick Reference: Authentication

## Registration

**Endpoint:** `POST /api/auth/register/`

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "password2": "SecurePassword123!"
}
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "username": "user",
    "email": "user@example.com",
    "first_name": "",
    "last_name": ""
  },
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "message": "User registered successfully"
}
```

**Notes:**
- Username is auto-generated from email (e.g., "user@example.com" → "user")
- If username exists, a number is appended (e.g., "user1", "user2")
- Only email and password are required
- Token is returned immediately upon registration
- First name and last name can be added later via `PATCH /api/auth/profile/`

---

## Login

**Endpoint:** `POST /api/auth/login/`

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "username": "user",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "message": "Login successful"
}
```

**Notes:**
- Only email and password are required
- No username login (email only)

---

## Using the Token

Include the token in the Authorization header for authenticated requests:

```bash
curl -X GET http://localhost:8000/api/forms/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

**Python Example:**
```python
import requests

headers = {
    'Authorization': f'Token {token}'
}

response = requests.get('http://localhost:8000/api/forms/', headers=headers)
```

---

## Key Changes from Standard Auth

1. **No username field in registration** - Username is auto-generated
2. **Email-only login** - No username login option
3. **Minimal registration** - Only email and password required
4. **First/last name optional** - Can be added later via profile update

---

## Testing

```bash
# 1. Register
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!","password2":"Test123!"}'

# 2. Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}'

# 3. Use token
curl -X GET http://localhost:8000/api/forms/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

