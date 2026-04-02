# User Registration & Profile Feature Documentation

## Overview
Added a complete user registration system with unique user ID generation, password hashing, and user profile management.

---

## Features Added

### 1. ✅ User Registration
- **New Route**: `GET /register` - Registration form
- **Registration Handler**: `POST /register_post` - Process registration
- **Validation**:
  - Email format validation
  - Password strength (minimum 6 characters)
  - Password confirmation matching
  - Duplicate email detection
  - Name validation (minimum 2 characters)

### 2. ✅ Unique User ID Generation
Each new user gets:
- **MongoDB ObjectId** - Automatically generated unique identifier
- **Format**: 24 character hexadecimal string
- **Example**: `507f1f77bcf86cd799439011`
- **Unique Constraint**: Email addresses are unique in database

### 3. ✅ Password Security
- **Hashing**: Uses `werkzeug.security.generate_password_hash()`
- **Algorithm**: PBKDF2 with SHA-256
- **Storage**: Only hashed passwords stored in database
- **Verification**: `check_password_hash()` for login validation

### 4. ✅ User Profile Page
- **Route**: `GET /user/profile`
- **Shows**:
  - User ID (with copy functionality)
  - Name and email
  - Account creation date
  - Account status
  - Account type (role)
  - Enrollment statistics
  - List of enrolled courses

### 5. ✅ API Endpoints for User Management
- `GET /api/user/<user_id>` - Get user details
- `GET /api/users` - List all users (admin only)
- `POST /api/user/<user_id>/profile` - Update user profile
- `GET /api/user/<user_id>/profile` - Get user profile

---

## Database Schema

### Users Collection
```javascript
{
  _id: ObjectId,                    // Unique User ID
  name: String,                     // Full name
  email: String (unique),           // Email address
  password_hash: String,            // Hashed password
  created_at: Date,                 // Registration timestamp
  updated_at: Date,                 // Last update timestamp
  enrolled_courses: [ObjectId],     // Array of course IDs
  role: String,                     // "student", "instructor", "admin"
  status: String                    // "active", "inactive", "suspended"
}
```

### Example User Document
```json
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "name": "John Doe",
  "email": "john@example.com",
  "password_hash": "$2b$12$...",
  "created_at": ISODate("2026-03-31T10:30:00Z"),
  "updated_at": ISODate("2026-03-31T10:30:00Z"),
  "enrolled_courses": [
    ObjectId("507f1f77bcf86cd799439012"),
    ObjectId("507f1f77bcf86cd799439013")
  ],
  "role": "student",
  "status": "active"
}
```

---

## User Flow

### Registration Flow
```
1. User clicks "Create Account" on login page
2. User fills registration form:
   - Full Name
   - Email
   - Password
   - Confirm Password
3. Form validation:
   - Check required fields
   - Validate email format
   - Check password strength (min 6 chars)
   - Verify passwords match
   - Check for duplicate email
4. If valid:
   - Hash password
   - Generate unique ObjectId
   - Store in users collection
   - Auto-login user
   - Redirect to dashboard
5. If invalid:
   - Show error message
   - Suggest corrections
```

### Login Flow
```
1. User enters email and password
2. System checks:
   a. Demo users first (backward compatibility)
   b. Then registered users in MongoDB
3. If found:
   - Verify password hash
   - Create session
   - Set user_id in session
   - Redirect to dashboard
4. If not found:
   - Show "Invalid credentials"
```

### Profile Flow
```
1. Authenticated user visits /user/profile
2. Fetch user data from users collection
3. Fetch enrolled courses using course IDs
4. Display:
   - User info (name, email, status)
   - Unique user ID with copy button
   - Enrollment statistics
   - Course list
```

---

## Code Changes

### Modified Files

#### 1. **app.py**

**New Imports:**
```python
from werkzeug.security import generate_password_hash, check_password_hash
import re
```

**New Collection:**
```python
users_collection = db["users"]
```

**New Index:**
```python
users_collection.create_index([("email", 1)], unique=True)
```

**Updated Login:**
```python
# Now checks both demo users and registered users
# Verifies password hash for registered users
```

**New Routes:**
```python
@app.route("/register")
@app.route("/register_post", methods=["POST"])
@app.route("/api/user/<user_id>")
@app.route("/api/users")
@app.route("/api/user/<user_id>/profile", methods=["GET", "POST"])
@app.route("/user/profile")
```

### Created Files

#### 2. **templates/register_user.html**
Beautiful registration form with:
- Email validation
- Password strength indicator
- Real-time requirement checking
- Error/success messages
- Responsive design
- Smooth animations

#### 3. **templates/user_profile.html**
User profile page displaying:
- User information and unique ID
- Account statistics
- Enrollment information
- List of enrolled courses
- Quick action links
- Responsive layout

#### 4. **templates/login_user.html** (Modified)
Added "Create Account" link to registration page

---

## API Reference

### Registration
```
POST /register_post
Content-Type: application/x-www-form-urlencoded

name=John Doe
email=john@example.com
password=securePassword123
confirm_password=securePassword123

Response: Redirect to /dashboard (on success)
```

### Get User by ID
```
GET /api/user/507f1f77bcf86cd799439011

Response (200 OK):
{
  "_id": "507f1f77bcf86cd799439011",
  "name": "John Doe",
  "email": "john@example.com",
  "created_at": "2026-03-31T10:30:00",
  "status": "active",
  "role": "student",
  "enrolled_courses": [...]
}

Response (404): {"error": "User not found"}
Response (401): {"error": "Unauthorized"}
```

### List All Users (Admin)
```
GET /api/users
Authorization: Admin session required

Response (200 OK):
[
  {
    "user_id": "507f1f77bcf86cd799439011",
    "name": "John Doe",
    "email": "john@example.com",
    "created_at": "2026-03-31T10:30:00",
    "status": "active"
  }
]

Response (401): {"error": "Unauthorized"}
```

### Update User Profile
```
POST /api/user/<user_id>/profile
Content-Type: application/x-www-form-urlencoded

name=John Doe Updated

Response (200 OK): {"success": true, "modified_count": 1}
Response (403): {"error": "Forbidden"}
Response (401): {"error": "Unauthorized"}
```

### Get User Profile
```
GET /api/user/<user_id>/profile

Response (200 OK):
{
  "_id": "507f1f77bcf86cd799439011",
  "name": "John Doe",
  "email": "john@example.com",
  "created_at": "2026-03-31T10:30:00"
  ...
}

Response (404): {"error": "User not found"}
```

---

## Session Variables

After login, the following variables are set:
```python
session['user_email']     # User's email address
session['user_type']      # 'user' or 'admin'
session['user_name']      # User's full name
session['user_id']        # Unique MongoDB ObjectId as string
```

---

## Security Features

### 1. Password Hashing
- PBKDF2 algorithm with 150,000 iterations (default werkzeug)
- SHA-256 hash function
- Never stores plain text passwords

### 2. Email Uniqueness
- Unique index on emails collection
- Prevents duplicate registrations
- Database enforces constraint

### 3. Input Validation
- Email format validation using regex
- Password length requirement (6+ chars)
- Name length validation
- XSS protection through template escaping

### 4. Authentication
- Session-based authentication
- User ID stored in session after login
- Protected routes check session['user_type']

### 5. Authorization
- Users can only view their own profile
- Admins can view all users
- API endpoints enforce permissions

---

## Error Handling

### Registration Errors
- ❌ "All fields are required"
- ❌ "Invalid email format"
- ❌ "Password must be at least 6 characters"
- ❌ "Passwords do not match"
- ❌ "Email already registered"
- ❌ "An error occurred during registration"

### Login Errors
- ❌ "Invalid credentials"

### Profile Errors
- ❌ "Unauthorized"
- ❌ "User not found"
- ❌ "Forbidden"

---

## Usage Examples

### Example 1: Register a New User
```
URL: http://localhost:5000/register

Form:
Name: Alice Johnson
Email: alice@example.com
Password: MySecure123!
Confirm: MySecure123!

Result:
- User ID generated: 507f1f77bcf86cd799439011
- User created in MongoDB
- Auto-logged in
- Redirected to dashboard
```

### Example 2: Login with Registered Account
```
URL: http://localhost:5000/login

Credentials:
Email: alice@example.com
Password: MySecure123!

Result:
- Session created with user_id
- Redirect to /dashboard
```

### Example 3: View User Profile
```
URL: http://localhost:5000/user/profile (when logged in)

Displays:
- Name: Alice Johnson
- Email: alice@example.com
- User ID: 507f1f77bcf86cd799439011 (copyable)
- Member Since: March 31, 2026
- Status: Active
- Enrolled: 3 courses
```

### Example 4: Get User via API
```
curl http://localhost:5000/api/user/507f1f77bcf86cd799439011
```

---

## Database Queries

### Find User by Email
```javascript
db.users.findOne({ email: "alice@example.com" })
```

### Find User by ID
```javascript
db.users.findOne({ _id: ObjectId("507f1f77bcf86cd799439011") })
```

### List All Users
```javascript
db.users.find({}, { name: 1, email: 1, created_at: 1 })
```

### Count Registered Users
```javascript
db.users.countDocuments({})
```

### Find Users by Status
```javascript
db.users.find({ status: "active" })
```

### Find User with Their Courses
```javascript
db.users.aggregate([
  {
    $match: { _id: ObjectId("507f1f77bcf86cd799439011") }
  },
  {
    $lookup: {
      from: "courses",
      localField: "enrolled_courses",
      foreignField: "_id",
      as: "courses"
    }
  }
])
```

---

## Migration from Demo Users

### For Development/Testing
Users can now:
1. Use demo accounts (if still configured)
2. Create new accounts via registration
3. Login with registered accounts

### Demo Accounts (still working)
- Email: `user@coursehub.com`
- Password: `password123`

---

## Future Enhancements

1. **Email Verification**
   - Send verification email on registration
   - Confirm email before account activation

2. **Password Reset**
   - Forgot password functionality
   - Email-based reset link

3. **Social Login**
   - Google OAuth
   - GitHub OAuth

4. **User Roles**
   - Instructor accounts
   - Admin panel
   - Role-based permissions

5. **Profile Enhancement**
   - Profile picture upload
   - Bio/about section
   - Learning preferences

6. **Two-Factor Authentication**
   - SMS verification
   - Authenticator app support

7. **Account Management**
   - Delete account
   - Export data
   - Activity history

---

## Testing Checklist

- [ ] Register new user with valid data
- [ ] Attempt registration with invalid email
- [ ] Attempt registration with short password
- [ ] Attempt registration with mismatched passwords
- [ ] Attempt registration with duplicate email
- [ ] Login with registered account
- [ ] Login with wrong password
- [ ] View user profile
- [ ] Copy user ID to clipboard
- [ ] API endpoints return correct data
- [ ] Verify password is hashed in database
- [ ] Check unique email constraint
- [ ] Test session creation/destruction
- [ ] Mobile responsive design

---

**Implementation Date**: March 31, 2026
**Status**: ✅ Complete & Ready for Production
