# CourseHub - Setup Guide

## Demo Credentials

### User Login
- **Email**: user@coursehub.com
- **Password**: password123

### Admin Login
- **Admin ID**: admin
- **Password**: admin123

## Application Features

### Landing Page (/)
- Professional welcome screen with the CourseHub logo
- Navigation to User Login and Admin Login
- Feature highlights and call-to-action buttons

### User Dashboard (/dashboard)
- Browse available courses
- Enroll in courses
- View enrollment statistics
- Search courses by keyword
- User profile and logout

### Admin Dashboard (/admin_dashboard)
- Add new courses
- View all courses and enrollments
- See enrollment reports and analytics
- View student statistics
- System management

### Authentication
- Session-based login system
- Secure logout functionality
- Admin-only access to course management
- User dashboard protection

## File Structure

```
d:\exm\UDP\
├── app.py                          # Flask application
├── requirements.txt                # Python dependencies
├── static/
│   └── logo.jpeg                  # CourseHub logo
├── templates/
│   ├── landing.html               # Landing page
│   ├── login_user.html            # User login page
│   ├── login_admin.html           # Admin login page
│   ├── dashboard_user.html        # User dashboard
│   ├── dashboard_admin.html       # Admin dashboard
│   ├── index.html                 # Legacy home page
│   ├── report.html                # Enrollment report
│   └── ...
└── myenv/                         # Python virtual environment
```

## Key Routes

| Route | Function | Access |
|-------|----------|--------|
| / | Landing page | Public |
| /login | User login page | Public |
| /login_post | Process user login | POST |
| /admin_login | Admin login page | Public |
| /admin_login_post | Process admin login | POST |
| /dashboard | User dashboard | Authenticated User |
| /admin_dashboard | Admin dashboard | Authenticated Admin |
| /add_course | Add new course | POST - Admin Only |
| /enroll | Enroll in course | POST - All |
| /search | Search courses | All |
| /logout | Logout | Authenticated |

## UI Highlights

1. **Modern Design**: Gradient backgrounds, smooth animations, industry-level styling
2. **Responsive**: Works on desktop and mobile devices
3. **Dark & Light Themes**: Admin dashboard has dark theme, user login has gradient theme
4. **Professional Components**: Cards, stat boxes, forms, tables
5. **Accessibility**: Clear navigation, readable fonts, good contrast

## How to Run

1. Ensure MongoDB is running on localhost:27017
2. Run: `python app.py`
3. Open browser: `http://localhost:5000`
4. Start from landing page and use demo credentials to login

## Demo Workflow

### As User:
1. Go to landing page
2. Click "User Login"
3. Enter: user@coursehub.com / password123
4. Access user dashboard
5. Browse and enroll in courses
6. Search for specific courses
7. Logout

### As Admin:
1. Go to landing page
2. Click "Admin"
3. Enter: admin / admin123
4. Access admin dashboard
5. Add new courses
6. View enrollment reports
7. Manage the platform
8. Logout
