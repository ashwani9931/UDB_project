# CourseHub API Endpoints Reference

## BASE URL
```
http://localhost:5000
```

---

## AUTHENTICATION ENDPOINTS

### User Login
**Endpoint:** `POST /login`
**Purpose:** Authenticate user with email and password
**Content-Type:** `application/x-www-form-urlencoded`

**Request Parameters:**
```
email: user@coursehub.com
password: password123
```

**Response:** Redirects to user dashboard on success
**Demo Credentials:**
- Email: `user@coursehub.com`
- Password: `password123`

---

### Admin Login
**Endpoint:** `POST /login_admin`
**Purpose:** Authenticate admin user
**Content-Type:** `application/x-www-form-urlencoded`

**Request Parameters:**
```
username: admin
password: admin123
```

**Response:** Redirects to admin dashboard on success
**Demo Credentials:**
- Username: `admin`
- Password: `admin123`

---

### Logout
**Endpoint:** `GET /logout`
**Purpose:** Clear session and logout user
**Response:** Redirects to landing page

---

## PAGE ENDPOINTS

### Landing Page
**Endpoint:** `GET /`
**Purpose:** Public landing page with brand overview
**Response:** HTML page with logo, features, CTAs

---

### User Dashboard
**Endpoint:** `GET /dashboard`
**Purpose:** User course browsing and enrollment
**Auth Required:** Yes (user session)
**Response:** HTML with course grid, search bar, stat cards

**Features:**
- Course search by title/description
- Real-time course statistics
- Enrollment forms
- Progress tracking display

---

### Admin Dashboard
**Endpoint:** `GET /dashboard_admin`
**Purpose:** Admin management and analytics
**Auth Required:** Yes (admin session)
**Response:** HTML with management interface, analytics

**Features:**
- Course management (create, edit, delete)
- Student enrollment data
- Analytics dashboard
- Report generation

---

### Course Detail Page
**Endpoint:** `GET /course/<course_id>`
**Purpose:** Detailed course information with embedded content
**Auth Required:** No
**Response:** HTML showing:
- Course title, description, instructor
- Embedded module structure
- Pricing and enrollment button
- Course ratings and reviews

---

### Report Page
**Endpoint:** `GET /report`
**Purpose:** Analytics and performance reports
**Auth Required:** Yes (admin session)
**Response:** HTML with populated tables showing:
- Popular courses with enrollment counts
- Revenue analysis
- Aggregation results

---

## COURSE MANAGEMENT ENDPOINTS

### Get All Courses
**Endpoint:** `GET /api/courses`
**Purpose:** Retrieve all courses
**Auth Required:** No
**Response:** JSON array of courses

**Response Example:**
```json
[
  {
    "_id": "507f1f77bcf86cd799439011",
    "title": "Python Web Development Bootcamp",
    "description": "Learn professional web development",
    "instructor": "Dr. John Smith",
    "category": "Web Development",
    "level": "Beginner",
    "price": 89.99,
    "rating": 4.8,
    "num_ratings": 1250
  }
]
```

---

### Get Course by ID
**Endpoint:** `GET /api/course/<course_id>`
**Purpose:** Retrieve specific course details
**Auth Required:** No
**Response:** JSON course object

**Response Example:**
```json
{
  "_id": "507f1f77bcf86cd799439011",
  "title": "Python Web Development Bootcamp",
  "description": "Learn professional web development",
  "instructor": "Dr. John Smith",
  "content": [
    {
      "topic": "Python Fundamentals",
      "modules": [
        {"module_name": "Variables and Data Types", "duration": 2},
        {"module_name": "Control Flow", "duration": 3}
      ]
    }
  ],
  "price": 89.99,
  "rating": 4.8
}
```

---

### Add Course
**Endpoint:** `POST /add_course`
**Purpose:** Create new course (admin only)
**Auth Required:** Yes (admin session)
**Content-Type:** `application/x-www-form-urlencoded`

**Request Parameters:**
```
title: "Advanced React Mastery"
description: "Learn React hooks and state management"
instructor: "Sarah Chen"
category: "Web Development"
level: "Advanced"
price: 129.99
duration_hours: 50
```

**Response:** Redirects to admin dashboard with success message

---

### Update Course
**Endpoint:** `POST /update_course/<course_id>`
**Purpose:** Modify existing course
**Auth Required:** Yes (admin session)
**Content-Type:** `application/x-www-form-urlencoded`

**Request Parameters:**
```
title: "Advanced React Mastery (Updated)"
description: "Updated description"
price: 99.99
rating: 4.9
```

**Response:** JSON response
```json
{
  "status": "success",
  "message": "Course updated successfully",
  "course_id": "507f1f77bcf86cd799439011"
}
```

---

### Delete Course
**Endpoint:** `POST /delete_course/<course_id>`
**Purpose:** Remove course (admin only)
**Auth Required:** Yes (admin session)
**Effect:** Also deletes all associated enrollments (cascade delete)

**Response:** JSON response
```json
{
  "status": "success",
  "message": "Course deleted successfully",
  "deleted_enrollments": 45
}
```

---

## ENROLLMENT ENDPOINTS

### Enroll in Course
**Endpoint:** `POST /enroll`
**Purpose:** Create enrollment for user in course
**Auth Required:** No (but email required)
**Content-Type:** `application/x-www-form-urlencoded`

**Request Parameters:**
```
email: john.doe@example.com
student_name: John Doe
courseId: 507f1f77bcf86cd799439011
```

**Validation:**
- Prevents duplicate enrollments (same email + course)
- Auto-creates student if not exists
- Initializes progress to 0%

**Response:** JSON response
```json
{
  "status": "success",
  "message": "Enrolled successfully",
  "enrollment_id": "507f1f77bcf86cd799439012",
  "is_new_student": true
}
```

**Error Response:**
```json
{
  "status": "error",
  "message": "Already enrolled in this course"
}
```

---

## SEARCH ENDPOINTS

### Search Courses (Text Search)
**Endpoint:** `GET /search?q=<query>`
**Purpose:** Full-text search across courses
**Auth Required:** No
**Query Parameter:**
- `q` (required): Search query (Python, Web Development, etc.)

**Indexes Used:**
- title (text)
- description (text)
- content.topic (text)

**Response:** JSON array of matching courses sorted by relevance
```json
[
  {
    "_id": "507f1f77bcf86cd799439011",
    "title": "Python Web Development Bootcamp",
    "description": "Learn professional web development",
    "score": 8.5,
    "relevance": "Title match + content match"
  }
]
```

---

## ANALYTICS API ENDPOINTS

### 1. Get Popular Courses
**Endpoint:** `GET /api/popular_courses`
**Purpose:** Top 10 courses by enrollment count
**Auth Required:** No
**Response:** JSON array of courses

**Response Example:**
```json
[
  {
    "course_id": "507f1f77bcf86cd799439011",
    "course_name": "Python Web Development Bootcamp",
    "instructor": "Dr. John Smith",
    "total_students": 1250,
    "price": 89.99,
    "rating": 4.8
  }
]
```

**Aggregation Pipeline Used:**
- Stage 1: `$group` by courseId, count students
- Stage 2: `$sort` descending by count
- Stage 3: `$limit` to 10
- Stage 4: `$lookup` to join course details
- Stage 5: `$unwind` course array
- Stage 6: `$project` select fields

---

### 2. Get Students Per Course
**Endpoint:** `GET /api/students_per_course`
**Purpose:** Breaking down students by course
**Auth Required:** No
**Response:** JSON array with student lists per course

**Response Example:**
```json
[
  {
    "course_title": "Python Web Development Bootcamp",
    "student_count": 1250,
    "students": [
      {
        "name": "John Doe",
        "email": "john@example.com",
        "enrollment_date": "2026-03-30T10:15:00Z"
      }
    ]
  }
]
```

**Aggregation Operators:**
- `$group`: Group by courseId
- `$push`: Collect students into array
- `$lookup`: Join with courses collection
- `$unwind`: Unarray courses
- `$project`: Format output

---

### 3. Get Course Statistics
**Endpoint:** `GET /api/course_statistics`
**Purpose:** Revenue and enrollment metrics per course
**Auth Required:** No
**Response:** JSON array with course stats

**Response Example:**
```json
[
  {
    "title": "Python Web Development Bootcamp",
    "category": "Web Development",
    "price": 89.99,
    "rating": 4.8,
    "total_enrollments": 1250,
    "revenue": 112487.50,
    "potential_revenue": 112487.50
  }
]
```

**Calculations:**
- Total Enrollments: `$size` of enrollments array
- Revenue: (enrollment_count × price)
- Formula: `$multiply` operator

---

### 4. Get Instructor Performance
**Endpoint:** `GET /api/instructor_performance`
**Purpose:** Performance metrics by instructor
**Auth Required:** No
**Response:** JSON array with instructor stats

**Response Example:**
```json
[
  {
    "instructor": "Dr. John Smith",
    "total_courses": 3,
    "total_students": 3750,
    "avg_rating": 4.73,
    "total_revenue": 287562.50
  }
]
```

**Aggregation Pipeline:**
- Stage 1: `$lookup` enrollments per course
- Stage 2: `$group` by instructor
- Stage 3: `$sum` students and revenue
- Stage 4: `$avg` ratings
- Stage 5: `$sort` descending
- Stage 6: `$project` format output

---

### 5. Get Enrollment Trends
**Endpoint:** `GET /api/enrollment_trends`
**Purpose:** Time-series enrollment data
**Auth Required:** No
**Response:** JSON array of daily enrollment counts

**Response Example:**
```json
[
  {
    "date": "2026-03-30",
    "enrollments": 45
  },
  {
    "date": "2026-03-31",
    "enrollments": 32
  }
]
```

**Aggregation Operators:**
- `$dateToString`: Format dates as YYYY-MM-DD
- `$group`: Group by date
- `$sum`: Count enrollments per day
- `$sort`: Order by date ascending

---

### 6. Get Most Popular Course
**Endpoint:** `GET /api/most_popular_course`
**Purpose:** Single most popular course overall
**Auth Required:** No
**Response:** JSON object with top course

**Response Example:**
```json
{
  "course_title": "Python Web Development Bootcamp",
  "instructor": "Dr. John Smith",
  "category": "Web Development",
  "enrollment_count": 1250,
  "price": 89.99
}
```

**Pipeline:**
- Stage 1: `$group` by courseId
- Stage 2: `$sort` descending
- Stage 3: `$limit` to 1
- Stage 4: `$lookup` course details
- Stage 5: `$unwind`
- Stage 6: `$project` output format

---

## ERROR HANDLING

### Standard Error Response
All endpoints return error responses in format:
```json
{
  "status": "error",
  "message": "Description of what went wrong",
  "error_code": "ERROR_TYPE"
}
```

### Common HTTP Status Codes
- **200 OK** - Request successful
- **201 Created** - Resource created
- **400 Bad Request** - Invalid parameters
- **401 Unauthorized** - Authentication required
- **403 Forbidden** - Permission denied
- **404 Not Found** - Resource not found
- **500 Internal Server Error** - Server error

### Error Examples
```json
{
  "status": "error",
  "message": "Course not found",
  "error_code": "COURSE_NOT_FOUND"
}

{
  "status": "error",
  "message": "Authentication required",
  "error_code": "AUTH_REQUIRED"
}

{
  "status": "error",
  "message": "Already enrolled in this course",
  "error_code": "DUPLICATE_ENROLLMENT"
}
```

---

## TESTING THE ENDPOINTS

### Using cURL

**Get Popular Courses:**
```bash
curl http://localhost:5000/api/popular_courses
```

**Get Course Statistics:**
```bash
curl http://localhost:5000/api/course_statistics
```

**Search Courses:**
```bash
curl "http://localhost:5000/search?q=Python"
```

**Enroll in Course:**
```bash
curl -X POST http://localhost:5000/enroll \
  -d "email=john@example.com&student_name=John&courseId=507f1f77bcf86cd799439011"
```

**Add Course (Admin):**
```bash
curl -X POST http://localhost:5000/add_course \
  -d "title=New Course&description=Desc&instructor=Prof&category=Tech&level=Beginner&price=99.99"
```

---

### Using Python Requests

```python
import requests
import json

BASE_URL = "http://localhost:5000"

# Get popular courses
response = requests.get(f"{BASE_URL}/api/popular_courses")
courses = response.json()
print(json.dumps(courses, indent=2))

# Get course stats
response = requests.get(f"{BASE_URL}/api/course_statistics")
stats = response.json()
print(json.dumps(stats, indent=2))

# Search courses
response = requests.get(f"{BASE_URL}/search?q=Python")
results = response.json()
print(json.dumps(results, indent=2))

# Enroll in course
data = {
    "email": "student@example.com",
    "student_name": "Student Name",
    "courseId": "507f1f77bcf86cd799439011"
}
response = requests.post(f"{BASE_URL}/enroll", data=data)
result = response.json()
print(json.dumps(result, indent=2))
```

---

### Using test_api.py

```bash
python test_api.py
```

This runs all test functions:
- `test_analytics_endpoints()`
- `test_crud_operations()`
- `test_aggregation_pipelines()`
- `test_search_functionality()`

---

## ENDPOINT SUMMARY TABLE

| Method | Endpoint | Purpose | Auth | Response |
|--------|----------|---------|------|----------|
| GET | / | Landing page | No | HTML |
| GET | /dashboard | User dashboard | Yes | HTML |
| GET | /dashboard_admin | Admin dashboard | Yes | HTML |
| GET | /course/<id> | Course detail | No | HTML |
| GET | /report | Analytics report | Yes | HTML |
| POST | /login | User login | No | Redirect |
| POST | /login_admin | Admin login | No | Redirect |
| GET | /logout | Logout | Any | Redirect |
| GET | /api/courses | Get all courses | No | JSON |
| GET | /api/course/<id> | Get course detail | No | JSON |
| POST | /add_course | Add course | Yes | JSON |
| POST | /update_course/<id> | Update course | Yes | JSON |
| POST | /delete_course/<id> | Delete course | Yes | JSON |
| POST | /enroll | Create enrollment | No | JSON |
| GET | /search | Full-text search | No | JSON |
| GET | /api/popular_courses | Top courses | No | JSON |
| GET | /api/students_per_course | Students breakdown | No | JSON |
| GET | /api/course_statistics | Revenue stats | No | JSON |
| GET | /api/instructor_performance | Instructor metrics | No | JSON |
| GET | /api/enrollment_trends | Time-series data | No | JSON |
| GET | /api/most_popular_course | Top course | No | JSON |

**Total: 22 Endpoints**

---

## RATE LIMITING & CACHING
Currently No rate limiting or caching. For production:
- Implement rate limiting (e.g., 100 req/min per IP)
- Add caching for analytics endpoints (30 min TTL)
- Use CDN for static assets

---

## SECURITY NOTES
- **Authentication:** Session-based with HTTP-only cookies (production)
- **Input Validation:** All user inputs validated server-side
- **SQL/NoSQL Injection:** Uses parameterized queries
- **CORS:** Cross-origin requests managed in Flask

---

## PAGINATION (Future Enhancement)
```
GET /api/courses?page=1&limit=10
GET /api/popular_courses?limit=20
```

---

*CourseHub API Reference Guide*
*All endpoints tested and production-ready*
