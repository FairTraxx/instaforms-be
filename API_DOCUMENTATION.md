# InstaForms API Documentation

## Overview

InstaForms is a form builder and submission management API built with Django REST Framework. This API allows users to create, manage, and collect responses from custom forms.

## Base URL

```
http://localhost:8000
```

## Authentication

The API uses Token Authentication. After registering or logging in, include the token in the Authorization header:

```
Authorization: Token <your_token_here>
```

---

## Authentication Endpoints

### Register a New User

**Endpoint:** `POST /api/auth/register/`

**Authentication:** Not required

**Description:** Create a new user account using email and password. Username is automatically generated from the email address.

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "SecurePassword123!",
  "password2": "SecurePassword123!"
}
```

**Required Fields:**
- `email` (string): Valid and unique email address
- `password` (string): Password meeting security requirements
- `password2` (string): Password confirmation

**Success Response (201 Created):**
```json
{
  "user": {
    "id": 1,
    "username": "john",
    "email": "john@example.com",
    "first_name": "",
    "last_name": ""
  },
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "message": "User registered successfully"
}
```

**Error Response (400 Bad Request):**
```json
{
  "email": ["A user with this email already exists."],
  "password": ["This password is too common."]
}
```

**Note:** First name and last name can be added later via `PATCH /api/auth/profile/`

---

### Login

**Endpoint:** `POST /api/auth/login/`

**Authentication:** Not required

**Description:** Authenticate with email and password to receive a token.

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "SecurePassword123!"
}
```

**Success Response (200 OK):**
```json
{
  "user": {
    "id": 1,
    "username": "john",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "message": "Login successful"
}
```

**Error Response (400 Bad Request):**
```json
{
  "non_field_errors": ["Unable to log in with provided credentials."]
}
```

---

### Logout

**Endpoint:** `POST /api/auth/logout/`

**Authentication:** Required

**Description:** Logout the current user by deleting their authentication token.

**Request Headers:**
```
Authorization: Token <your_token>
```

**Success Response (200 OK):**
```json
{
  "message": "Logged out successfully"
}
```

---

### Get User Profile

**Endpoint:** `GET /api/auth/profile/`

**Authentication:** Required

**Description:** Retrieve the current user's profile information.

**Success Response (200 OK):**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "date_joined": "2024-01-01T00:00:00Z"
}
```

---

### Update User Profile

**Endpoint:** `PATCH /api/auth/profile/`

**Authentication:** Required

**Description:** Update the current user's profile information.

**Request Body:**
```json
{
  "email": "newemail@example.com",
  "first_name": "Jonathan",
  "last_name": "Smith"
}
```

**Note:** Username cannot be updated. All fields are optional. Use this endpoint to add your first name and last name after registration.

**Success Response (200 OK):**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "newemail@example.com",
  "first_name": "Jonathan",
  "last_name": "Smith",
  "date_joined": "2024-01-01T00:00:00Z"
}
```

---

### Change Password

**Endpoint:** `POST /api/auth/change-password/`

**Authentication:** Required

**Description:** Change the current user's password.

**Request Body:**
```json
{
  "old_password": "OldPassword123!",
  "new_password": "NewPassword123!",
  "new_password2": "NewPassword123!"
}
```

**Success Response (200 OK):**
```json
{
  "message": "Password changed successfully"
}
```

**Error Response (400 Bad Request):**
```json
{
  "old_password": ["Old password is incorrect."]
}
```

---

## Form Management Endpoints

### List All Forms

**Endpoint:** `GET /api/forms/`

**Authentication:** Required

**Description:** Get a list of all forms created by the authenticated user.

**Success Response (200 OK):**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Contact Form",
      "description": "Get in touch with us",
      "created_by": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe"
      },
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "is_active": true,
      "fields": []
    }
  ]
}
```

---

### Create a Form

**Endpoint:** `POST /api/forms/`

**Authentication:** Required

**Description:** Create a new form.

**Request Body:**
```json
{
  "title": "Contact Form",
  "description": "Get in touch with us",
  "is_active": true
}
```

**Required Fields:**
- `title` (string)

**Optional Fields:**
- `description` (string)
- `is_active` (boolean, default: true)

**Success Response (201 Created):**
```json
{
  "id": 1,
  "title": "Contact Form",
  "description": "Get in touch with us",
  "created_by": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "is_active": true,
  "fields": []
}
```

---

### Get Form Details

**Endpoint:** `GET /api/forms/{id}/`

**Authentication:** Required

**Description:** Retrieve detailed information about a specific form.

**Success Response (200 OK):**
```json
{
  "id": 1,
  "title": "Contact Form",
  "description": "Get in touch with us",
  "created_by": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "is_active": true,
  "fields": [
    {
      "id": 1,
      "label": "Full Name",
      "field_type": "text",
      "required": true,
      "placeholder": "Enter your name",
      "options": null,
      "order": 0
    }
  ]
}
```

---

### Update a Form

**Endpoint:** `PUT /api/forms/{id}/` or `PATCH /api/forms/{id}/`

**Authentication:** Required

**Description:** Update an existing form (PUT for full update, PATCH for partial).

**Request Body (PATCH):**
```json
{
  "title": "Updated Contact Form",
  "is_active": false
}
```

**Success Response (200 OK):**
```json
{
  "id": 1,
  "title": "Updated Contact Form",
  "description": "Get in touch with us",
  "created_by": {...},
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-02T00:00:00Z",
  "is_active": false,
  "fields": [...]
}
```

---

### Delete a Form

**Endpoint:** `DELETE /api/forms/{id}/`

**Authentication:** Required

**Description:** Delete a form and all associated fields and submissions.

**Success Response (204 No Content):**
No response body

---

### Add Field to Form

**Endpoint:** `POST /api/forms/{id}/add_field/`

**Authentication:** Required

**Description:** Add a new field to an existing form.

**Request Body:**
```json
{
  "label": "Email Address",
  "field_type": "email",
  "required": true,
  "placeholder": "your.email@example.com",
  "order": 1
}
```

**Field Types:**
- `text` - Single-line text input
- `email` - Email address input
- `number` - Numeric input
- `textarea` - Multi-line text input
- `select` - Dropdown selection
- `radio` - Radio button selection
- `checkbox` - Checkbox input
- `date` - Date picker
- `file` - File upload

**For select/radio/checkbox fields:**
```json
{
  "label": "Favorite Color",
  "field_type": "select",
  "required": false,
  "options": ["Red", "Blue", "Green"],
  "order": 2
}
```

**Success Response (201 Created):**
```json
{
  "id": 2,
  "label": "Email Address",
  "field_type": "email",
  "required": true,
  "placeholder": "your.email@example.com",
  "options": null,
  "order": 1
}
```

---

### Get Form Submissions

**Endpoint:** `GET /api/forms/{id}/submissions/`

**Authentication:** Required

**Description:** Retrieve all submissions for a specific form.

**Success Response (200 OK):**
```json
[
  {
    "id": 1,
    "form": {...},
    "submitted_at": "2024-01-01T12:00:00Z",
    "responses": [
      {
        "id": 1,
        "field": {
          "id": 1,
          "label": "Full Name",
          "field_type": "text",
          "required": true,
          "placeholder": "Enter your name",
          "options": null,
          "order": 0
        },
        "value": "Jane Smith"
      },
      {
        "id": 2,
        "field": {
          "id": 2,
          "label": "Email Address",
          "field_type": "email",
          "required": true,
          "placeholder": "your.email@example.com",
          "options": null,
          "order": 1
        },
        "value": "jane@example.com"
      }
    ]
  }
]
```

---

## Form Fields Endpoints

### List All Fields

**Endpoint:** `GET /api/fields/`

**Authentication:** Required

**Description:** Get a list of all form fields from the user's forms.

---

### Create a Field

**Endpoint:** `POST /api/fields/`

**Authentication:** Required

**Description:** Create a new form field (must specify form ID in request).

---

### Update a Field

**Endpoint:** `PUT /api/fields/{id}/` or `PATCH /api/fields/{id}/`

**Authentication:** Required

**Description:** Update an existing form field.

---

### Delete a Field

**Endpoint:** `DELETE /api/fields/{id}/`

**Authentication:** Required

**Description:** Delete a form field.

---

## Submissions Endpoints

### List All Submissions

**Endpoint:** `GET /api/submissions/`

**Authentication:** Required

**Description:** Get a list of all submissions for the user's forms.

---

### Get Submission Details

**Endpoint:** `GET /api/submissions/{id}/`

**Authentication:** Required

**Description:** Retrieve detailed information about a specific submission.

---

## Public Endpoints

### List Public Forms

**Endpoint:** `GET /api/public/forms/`

**Authentication:** Not required

**Description:** Get a list of all active public forms.

**Success Response (200 OK):**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Contact Form",
      "description": "Get in touch with us",
      "created_by": {...},
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "is_active": true,
      "fields": [...]
    }
  ]
}
```

---

### Get Public Form Details

**Endpoint:** `GET /api/public/forms/{id}/`

**Authentication:** Not required

**Description:** Retrieve detailed information about a public form including all fields.

---

### Submit a Form

**Endpoint:** `POST /api/public/forms/{id}/submit/`

**Authentication:** Not required

**Description:** Submit responses to a public form.

**Request Body:**
```json
{
  "responses": [
    {
      "field_id": 1,
      "value": "Jane Smith"
    },
    {
      "field_id": 2,
      "value": "jane@example.com"
    },
    {
      "field_id": 3,
      "value": "This is my message"
    }
  ]
}
```

**Success Response (201 Created):**
```json
{
  "message": "Form submitted successfully"
}
```

**Error Response (400 Bad Request):**
```json
{
  "responses": [
    {
      "field_id": ["This field is required."]
    }
  ]
}
```

---

## Error Responses

### 400 Bad Request
Returned when the request is malformed or validation fails.

### 401 Unauthorized
Returned when authentication is required but not provided or invalid.

### 403 Forbidden
Returned when the user doesn't have permission to access the resource.

### 404 Not Found
Returned when the requested resource doesn't exist.

### 500 Internal Server Error
Returned when an unexpected error occurs on the server.

---

## Pagination

List endpoints support pagination with the following query parameters:

- `page` - Page number (default: 1)
- `page_size` - Number of items per page (default: 20, max: 100)

Example:
```
GET /api/forms/?page=2&page_size=10
```

---

## Rate Limiting

Currently, there are no rate limits implemented. This may change in production.

---

## CORS

CORS is enabled for the following origins:
- `http://localhost:3000`
- `http://127.0.0.1:3000`

Additional origins can be configured in the settings.

---

## Support

For issues or questions, please contact the development team.

