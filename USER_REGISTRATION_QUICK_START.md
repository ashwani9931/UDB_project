# User Registration Feature - Quick Reference

## 🆕 What's New?

### 1️⃣ User Registration System
Students can now create their own accounts with unique user IDs!

### 2️⃣ Unique User ID
Each user gets a **unique MongoDB ObjectId** (24-character hex string):
- Format: `507f1f77bcf86cd799439011`
- Generated automatically on registration
- Never changes
- Can be used to search/reference user

### 3️⃣ Password Security
Passwords are:
- ✅ Encrypted with PBKDF2
- ✅ Never stored as plain text
- ✅ Minimum 6 characters required
- ✅ Must be confirmed during registration

### 4️⃣ User Profile Page
New profile dashboard with:
- 👤 User information
- 🆔 Unique user ID (copy button)
- 📚 Enrolled courses list
- 📊 Learning statistics

---

## 🚀 How to Use

### Register a New Account

**Step 1: Go to Registration**
```
http://localhost:5000/register
```

**Step 2: Fill the Form**
- **Name**: Your full name (min 2 characters)
- **Email**: Your email address
- **Password**: At least 6 characters
- **Confirm Password**: Must match password above

**Step 3: Submit**
- Click "Create Account"
- System validates your data
- If valid, auto-logs you in and redirects to dashboard
- If invalid, shows error message

### Login with Your Account

**URL:**
```
http://localhost:5000/login
```

**Credentials:**
- Use the email you registered with
- Use the password you created

### View Your Profile

**URL:**
```
http://localhost:5000/user/profile
```

**On Profile Page:**
- See your unique User ID
- Click "Copy" button to copy ID to clipboard
- View all enrolled courses
- Check membership date

---

## 🔑 Your Unique User ID

### What is it?
- A 24-character unique identifier
- Generated automatically when you register
- Never changes
- Example: `507f1f77bcf86cd799439011`

### Where to Find It?
- Visit `/user/profile` after login
- Look for "Unique User ID" section
- Click "Copy" to copy to clipboard

### How to Use It?
- Search for specific users (admin feature)
- Get user details via API
- Reference your account
- Share with admins if needed

### API Examples
```bash
# Get your profile
curl http://localhost:5000/api/user/507f1f77bcf86cd799439011

# Update your profile
curl -X POST http://localhost:5000/api/user/507f1f77bcf86cd799439011/profile
```

---

## 🔐 Security Features

✅ **Password Hashing**: Using industry-standard PBKDF2  
✅ **Unique Emails**: Can't register with same email twice  
✅ **Input Validation**: All data validated before storage  
✅ **Session Management**: Secure session handling  
✅ **XSS Protection**: Template auto-escaping  

---

## 📱 User Registration Flow

```
Registration Page
      ↓
Enter Information
      ↓
Validate Data
      ├─ Invalid? → Show Error
      └─ Valid? → Continue
      ↓
Hash Password
      ↓
Generate User ID
      ↓
Store in Database
      ↓
Auto-Login
      ↓
Dashboard
```

---

## 🗄️ Behind the Scenes

### New MongoDB Collection
```
users collection:
{
  _id: ObjectId (Your Unique User ID),
  name: "Your Name",
  email: "your@email.com",
  password_hash: "encrypted...",
  enrolled_courses: [...],
  created_at: Date,
  status: "active",
  role: "student"
}
```

### New Database Index
- Unique constraint on `email` field
- Prevents duplicate registrations

---

## 📋 Forms & Validation

### Registration Form
```
Field           Type        Required   Min    Max     Validation
────────────────────────────────────────────────────────────────
Name            Text        Yes        2      100     Letters/spaces
Email           Email       Yes        -      -       Valid format
Password        Password    Yes        6      50      Any characters
Confirm         Password    Yes        6      50      Must match
```

### Password Requirements
- ✅ Minimum 6 characters
- ✅ Must match confirmation
- ✅ Real-time strength indicator
- ✅ Shows requirements checklist

### Error Messages
- ❌ "All fields are required"
- ❌ "Invalid email format"
- ❌ "Password must be at least 6 characters"
- ❌ "Passwords do not match"
- ❌ "Email already registered"

---

## 🔗 URL Reference

| Feature | URL | Method |
|---------|-----|--------|
| Register | `/register` | GET |
| Submit Registration | `/register_post` | POST |
| User Login | `/login` | GET |
| User Profile | `/user/profile` | GET |
| Get User (API) | `/api/user/<id>` | GET |
| List Users (Admin) | `/api/users` | GET |
| Update Profile (API) | `/api/user/<id>/profile` | POST |

---

## 🆚 Demo vs Registered Users

### Demo Users (Still Available)
- Email: `user@coursehub.com`
- Password: `password123`
- No ID stored in database
- For quick testing

### Registered Users (New)
- Create your own account
- Unique user ID generated
- Password securely hashed
- Full profile management
- Persistent account

---

## ⚙️ Session Variables

When logged in, these are set:
```python
session['user_id']       # Your unique ID
session['user_email']    # Your email
session['user_name']     # Your name
session['user_type']     # 'user' or 'admin'
```

---

## 🎯 Common Tasks

### Task: Find My User ID
```
1. Login to your account
2. Go to /user/profile
3. Look for "Unique User ID"
4. Click "Copy" to copy to clipboard
```

### Task: Register New Account
```
1. Go to /register (or click "Create Account" from login)
2. Fill in all fields
3. Click "Create Account"
4. Auto-logged in if successful
```

### Task: Get User Info via API
```
curl http://localhost:5000/api/user/507f1f77bcf86cd799439011
```

### Task: Update Profile
```
POST /api/user/<user_id>/profile
name=New Name
```

---

## 🐛 Troubleshooting

### "Email already registered"
- Use different email
- Check if you already have account
- Try password reset (if implemented)

### "Invalid email format"
- Use proper email: user@domain.com
- Check for typos
- Ensure @ symbol is present

### "Passwords do not match"
- Retype both passwords carefully
- Check for extra spaces
- Verify caps lock is off

### "Password must be at least 6 characters"
- Password is too short
- Minimum 6 characters required
- Try longer password

### Can't copy User ID
- Try again
- Check browser permissions
- Try manual copy (select & Ctrl+C)

---

## 📚 Feature Files

### Code Files
- `app.py` - Backend routes and logic
- `templates/register_user.html` - Registration form
- `templates/user_profile.html` - Profile page
- `templates/login_user.html` - Updated with registration link

### Documentation
- `USER_REGISTRATION_GUIDE.md` - Full technical docs
- `FEATURES_QUICK_START.md` - Popular courses guide

---

## ✨ Key Benefits

🎓 **Easy Registration** - Simple 4-field form  
🔐 **Secure** - Industry-standard password hashing  
🆔 **Unique ID** - Never worry about duplicates  
👤 **Profile Management** - Manage your account easily  
📱 **Mobile Friendly** - Works on all devices  
⚡ **Fast** - Quick validation and login  

---

## 🚀 Getting Started

1. **Start the app**
   ```
   python app.py
   ```

2. **Go to login page**
   ```
   http://localhost:5000/login
   ```

3. **Click "Create Account"**

4. **Fill registration form**

5. **Get Your Unique User ID!** 🎉

---

**Last Updated**: March 31, 2026
**Status**: ✅ Ready to Use
