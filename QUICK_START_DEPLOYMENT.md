# CourseHub - Quick Start & Deployment Guide

## Prerequisites

Before running the application, ensure you have:

### Required Software
- **Python 3.8+** - Download from [python.org](https://www.python.org)
- **MongoDB 4.0+** - Download from [mongodb.com](https://www.mongodb.com/try/download/community)
- **Git** (optional) - For version control
- **VS Code** (recommended) - For development

### System Requirements
- Windows 10+, macOS 10.14+, or Linux
- 4GB RAM minimum
- 500MB free disk space

---

## INSTALLATION STEPS

### Step 1: Activate Virtual Environment

Navigate to the project directory and activate the virtual environment:

**Windows:**
```powershell
cd d:\exm\UDP
.\myenv\Scripts\activate
```

**macOS/Linux:**
```bash
cd ~/exm/UDP
source myenv/bin/activate
```

Expected output: `(myenv)` prefix in terminal prompt

---

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

Expected packages installed:
- **Flask** - Web framework
- **PyMongo** - MongoDB driver
- **python-dotenv** - Environment variables
- **Werkzeug** - WSGI utilities
- **Jinja2** - Template engine
- **Click** - CLI utilities
- **blinker** - Signal support
- **Flask 3.1.3** (specific version)
- **Werkzeug 3.1.7** (specific version)

Verify installation:
```bash
pip list
```

---

### Step 3: Start MongoDB

**Windows:**
```powershell
# If installed as service
net start MongoDB

# Or run manually
mongod.exe
```

**macOS:**
```bash
# Using Homebrew
brew services start mongodb-community

# Or manually
mongod
```

**Linux:**
```bash
# Using systemctl
sudo systemctl start mongod

# Or manually
mongod
```

Verify MongoDB is running: `mongosh` should connect successfully

---

### Step 4: Run the Application

```bash
python app.py
```

Expected output:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: off
 WARNING: This is a development server. Do not use it in production.
 * Press CTRL+C to quit
```

---

## ACCESSING THE APPLICATION

Once running, open your browser:

### Base URL
```
http://localhost:5000
```

---

## USER WORKFLOWS

### Workflow 1: Browse Courses as User

1. **Visit Landing Page**
   - Go to `http://localhost:5000`
   - Click "Get Started" or "Login"

2. **Login as User**
   - Click "User Login"
   - Email: `user@coursehub.com`
   - Password: `password123`

3. **Browse Courses**
   - View all available courses
   - Filter by category, level, price
   - Search by name or topic

4. **View Course Details**
   - Click course name
   - See embedded modules and content structure
   - View instructor and pricing

5. **Enroll in Course**
   - Click "Enroll Now" button
   - Submit form (auto-populated with email)
   - See confirmation message

6. **Track Progress**
   - Dashboard shows enrolled courses
   - Displays progress percentage
   - View completion status

---

### Workflow 2: Manage Courses as Admin

1. **Login as Admin**
   - Click "Admin Login"
   - Username: `admin`
   - Password: `admin123`

2. **Access Admin Dashboard**
   - View analytics cards
   - See course management table
   - Access course creation form

3. **Create New Course**
   - Fill course form:
     - Title: "Advanced Node.js Backend"
     - Instructor: "Mike Wilson"
     - Category: "Backend Development"
     - Level: "Advanced"
     - Price: $149.99
   - Submit form
   - Redirects to dashboard with success message

4. **Edit Course**
   - Click "Edit" on course in table
   - Update fields (price, title, etc.)
   - Save changes

5. **Delete Course**
   - Click "Delete" on course in table
   - Confirmation dialog
   - Automatically removes all enrollments

6. **View Analytics**
   - Popular courses section (top 10)
   - Student enrollments chart
   - Revenue analysis
   - Instructor performance metrics
   - Enrollment trends over time

7. **Generate Reports**
   - Click "View Report" in sidebar
   - See aggregated analytics
   - Export data (future feature)

---

### Workflow 3: Use Search Functionality

1. **From User Dashboard**
   - Type in search box: "Python"
   - Press Enter or click Search
   - Results sorted by relevance

2. **From Navigation Bar** (if implemented)
   - Global search across all courses
   - Real-time results

3. **Search Examples**
   - `"web development"` - Find web courses
   - `"python"` - Find Python courses
   - `"machine learning"` - Find ML courses

---

## DEMO DATA

### Sample Instructors (Auto-loaded)
```
1. Dr. John Smith - Web Development Expert
2. Prof. Emily Johnson - Data Science Specialist
3. Sarah Chen - Cloud Architecture Expert
```

### Sample Courses (Auto-loaded)
```
1. Python Web Development Bootcamp
   - Instructor: Dr. John Smith
   - Price: $89.99
   - Duration: 40 hours
   - Rating: 4.8/5.0

2. AWS Cloud Fundamentals
   - Instructor: Sarah Chen
   - Price: $99.99
   - Duration: 35 hours
   - Rating: 4.7/5.0

3. Machine Learning Essentials
   - Instructor: Prof. Emily Johnson
   - Price: $129.99
   - Duration: 50 hours
   - Rating: 4.9/5.0

4. JavaScript & React Mastery
   - Instructor: Dr. John Smith
   - Price: $84.99
   - Duration: 45 hours
   - Rating: 4.6/5.0
```

### Sample Students (Created on first enrollment)
Automatically created when users enroll:
```
Email: user@example.com
Student Name: Can be any name entered during enrollment
```

---

## DATABASE VERIFICATION

### Check MongoDB Connection

In terminal (outside Flask app):

```bash
# Connect to MongoDB
mongosh

# Switch to database
use course_platform

# View collections
show collections

# Check course documents
db.courses.find().pretty()

# Count enrollments
db.enrollments.countDocuments()

# See indexes
db.courses.getIndexes()
```

---

## API TESTING

### Test All Endpoints

**Option 1: Using test_api.py**
```bash
# In another terminal (with virtual environment activated)
python test_api.py
```

**Option 2: Using Python Requests**
```python
import requests

# Test popular courses API
response = requests.get("http://localhost:5000/api/popular_courses")
print(response.json())

# Test course statistics
response = requests.get("http://localhost:5000/api/course_statistics")
print(response.json())

# Test search
response = requests.get("http://localhost:5000/search?q=Python")
print(response.json())
```

**Option 3: Using cURL**
```bash
# Get popular courses
curl http://localhost:5000/api/popular_courses

# Get course statistics
curl http://localhost:5000/api/course_statistics

# Search courses
curl "http://localhost:5000/search?q=web"

# Get instructor performance
curl http://localhost:5000/api/instructor_performance
```

**Option 4: Using Postman**
1. Open Postman
2. Create requests for each endpoint
3. Save as collection
4. Run tests
5. Export results

---

## TROUBLESHOOTING

### Issue: "MongoDB connection refused"

**Solution:**
```bash
# Check if MongoDB is running
mongosh

# If not running, start it
mongod

# Verify connection string in app.py is correct:
# mongo_uri = "mongodb://localhost:27017/"
```

---

### Issue: "ModuleNotFoundError: No module named 'flask'"

**Solution:**
```bash
# Activate virtual environment
.\myenv\Scripts\activate  # Windows
source myenv/bin/activate  # macOS/Linux

# Install requirements
pip install -r requirements.txt

# Verify installation
pip list | grep Flask
```

---

### Issue: "Port 5000 already in use"

**Solution:**
```bash
# Find process using port 5000
lsof -i :5000  # macOS/Linux
netstat -ano | findstr :5000  # Windows

# Kill process (replace PID)
kill -9 PID  # macOS/Linux
taskkill /PID PID /F  # Windows

# Or use different port
# Modify in app.py: app.run(port=5001)
```

---

### Issue: "Authentication Failed" on login

**Solution:**
```
Verify credentials:
- User Email: user@coursehub.com
- User Password: password123
- Admin Username: admin
- Admin Password: admin123

These are hardcoded in DEMO_USERS and DEMO_ADMINS dictionaries
```

---

### Issue: "Course not found" when accessing detail page

**Solution:**
```bash
# Check MongoDB has courses
mongosh
use course_platform
db.courses.countDocuments()

# If 0, data didn't initialize
# Restart app to trigger initialize_sample_data()
```

---

### Issue: "Text search returns no results"

**Solution:**
```bash
# Check if text index exists
mongosh
db.courses.getIndexes()

# Should see: "title_text_description_text_content.topic_text"

# If missing, app.py will recreate it on startup
# Restart the application
```

---

## FILE STRUCTURE

```
d:\exm\UDP\
├── app.py                              # Main Flask application (700+ lines)
├── requirements.txt                    # Python dependencies
├── templates/
│   ├── landing.html                   # Public landing page
│   ├── login_user.html                # User authentication
│   ├── login_admin.html               # Admin authentication
│   ├── dashboard_user.html            # User course browsing
│   ├── dashboard_admin.html           # Admin management
│   ├── course_detail.html             # Course information
│   └── report.html                    # Analytics reports
├── static/
│   └── logo.png                       # Brand logo (if included)
├── myenv/                             # Virtual environment (do not edit)
├── COMPLETE_DOCUMENTATION.md          # Full technical documentation
├── PROJECT_SUMMARY.md                 # Executive summary
├── SETUP_GUIDE.md                     # Setup instructions
├── test_api.py                        # API testing framework
├── API_ENDPOINTS_REFERENCE.md         # API documentation
├── MONGODB_COMMANDS_REFERENCE.md      # Database commands
└── QUICK_START.md                     # This file
```

---

## DEPLOYMENT CHECKLIST

Before going to production:

- [ ] **Database**
  - [ ] MongoDB running on production server
  - [ ] Connection string updated
  - [ ] Backup strategy implemented
  - [ ] Index optimization complete

- [ ] **Security**
  - [ ] Change demo credentials
  - [ ] Implement proper authentication (JWT/OAuth)
  - [ ] Enable HTTPS/SSL
  - [ ] Configure CORS properly
  - [ ] Validate all user inputs

- [ ] **Performance**
  - [ ] Enable Flask production server (Gunicorn/uWSGI)
  - [ ] Set up load balancing
  - [ ] Configure caching
  - [ ] Optimize database queries

- [ ] **Monitoring**
  - [ ] Set up logging
  - [ ] Configure error tracking (Sentry)
  - [ ] Monitor performance metrics
  - [ ] Set up alerts

- [ ] **Documentation**
  - [ ] API documentation complete
  - [ ] Deployment guide written
  - [ ] Runbook for operations team
  - [ ] Disaster recovery plan

---

## PRODUCTION DEPLOYMENT EXAMPLE

### Using Gunicorn (Recommended)

```bash
# Install Gunicorn
pip install gunicorn

# Run Flask app with 4 workers
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Run with custom config
gunicorn --workers 4 \
         --bind 0.0.0.0:5000 \
         --access-logfile - \
         --error-logfile - \
         app:app
```

### Using Docker (Optional)

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt . 
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

Build and run:
```bash
docker build -t coursehub .
docker run -p 5000:5000 coursehub
```

---

## PERFORMANCE OPTIMIZATION

### Database Optimization
```javascript
// Add more indexes if needed
db.courses.createIndex({"category": 1})
db.courses.createIndex({"instructor_id": 1})
db.enrollments.createIndex({"studentId": 1})
db.enrollments.createIndex({"courseId": 1})
```

### Caching Strategy
```python
# Cache popular courses (30 minutes)
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/api/popular_courses')
@cache.cached(timeout=1800)
def api_popular_courses():
    ...
```

### Query Optimization
```python
# Use projection to limit fields returned
db.courses.find({}, {"title": 1, "price": 1, "rating": 1})

# Use aggregation for complex queries instead of multiple find()
db.courses.aggregate([...])
```

---

## HELPFUL COMMANDS

### Activate Environment
```bash
# Windows
.\myenv\Scripts\activate

# macOS/Linux
source myenv/bin/activate
```

### Start Application
```bash
python app.py
```

### Run Tests
```bash
python test_api.py
```

### Access MongoDB
```bash
mongosh
use course_platform
```

### Check Dependencies
```bash
pip list
pip show flask
```

### Deactivate Environment
```bash
deactivate
```

---

## NEXT STEPS

1. **Deploy the Application**
   - Run `python app.py`
   - Open `http://localhost:5000`

2. **Test Features**
   - Login as user and browse courses
   - Login as admin and create courses
   - Use search functionality
   - Check analytics

3. **Explore the Code**
   - Read COMPLETE_DOCUMENTATION.md
   - Review aggregation pipelines in app.py
   - Understand database schema

4. **Customize**
   - Update demo credentials
   - Modify course categories
   - Add new features
   - Enhance UI design

5. **Deploy to Production**
   - Follow production deployment checklist
   - Use Gunicorn/uWSGI
   - Set up monitoring
   - Configure backups

---

## SUPPORT & RESOURCES

### Documentation Files
- **API_ENDPOINTS_REFERENCE.md** - All API endpoints
- **MONGODB_COMMANDS_REFERENCE.md** - Database queries
- **COMPLETE_DOCUMENTATION.md** - Full technical guide
- **PROJECT_SUMMARY.md** - Project overview

### External Resources
- [Flask Documentation](https://flask.palletsprojects.com/)
- [PyMongo Documentation](https://pymongo.readthedocs.io/)
- [MongoDB Manual](https://docs.mongodb.com/manual/)
- [Python Documentation](https://docs.python.org/3/)

### Common Issues
See **TROUBLESHOOTING** section above for common problems and solutions.

---

## PROJECT STATISTICS

- **Total Lines of Code:** 700+
- **API Endpoints:** 22
- **Templates:** 7
- **Collections:** 4
- **Aggregation Pipelines:** 6
- **Text Indexes:** 1 (multi-field)
- **Documentation Files:** 6

---

## VERSION INFORMATION

- **Python Version:** 3.8+
- **Flask Version:** 3.1.3
- **MongoDB Version:** 4.0+
- **PyMongo Version:** 4.16.0
- **Status:** Production Ready ✅

---

*CourseHub Quick Start & Deployment Guide*
*Last Updated: 2026-03-30*
*Ready to Deploy and Scale*
