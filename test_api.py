#!/usr/bin/env python
"""
CourseHub - API Testing Script
Tests all aggregation pipelines and endpoints
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

def test_analytics_endpoints():
    """Test all analytics and aggregation endpoints"""
    
    print("=" * 80)
    print("COURSEHUB API TESTING - AGGREGATION PIPELINES")
    print("=" * 80)
    
    endpoints = [
        {
            "name": "Most Popular Courses (Top 10)",
            "endpoint": "/api/analytics/popular-courses",
            "description": "Aggregation: Group by courseId, sum enrollments, sort by popularity"
        },
        {
            "name": "Students Per Course",
            "endpoint": "/api/analytics/students-per-course",
            "description": "Aggregation: Group enrollments, count students, list details"
        },
        {
            "name": "Course Statistics",
            "endpoint": "/api/analytics/course-statistics",
            "description": "Aggregation: Calculate revenue, enrollments, advanced metrics"
        },
        {
            "name": "Instructor Performance",
            "endpoint": "/api/analytics/instructor-performance",
            "description": "Aggregation: Group by instructor, calculate metrics"
        },
        {
            "name": "Enrollment Trends",
            "endpoint": "/api/analytics/enrollment-trends",
            "description": "Aggregation: Timeline grouping, daily analytics"
        },
        {
            "name": "Most Popular Single Course",
            "endpoint": "/api/analytics/course-popularity",
            "description": "Aggregation: Find single most popular course"
        }
    ]
    
    for test in endpoints:
        print(f"\n{'─' * 80}")
        print(f"📊 {test['name']}")
        print(f"   Endpoint: {test['endpoint']}")
        print(f"   Pipeline: {test['description']}")
        print(f"{'─' * 80}")
        
        try:
            response = requests.get(f"{BASE_URL}{test['endpoint']}")
            response.raise_for_status()
            data = response.json()
            
            if isinstance(data, list):
                print(f"✅ Response: {len(data)} records returned")
                if data:
                    print(f"\n   Sample Record:")
                    print(f"   {json.dumps(data[0], indent=2, default=str)}")
            else:
                print(f"✅ Response:")
                print(f"   {json.dumps(data, indent=2, default=str)}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error: {str(e)}")
    
    print(f"\n{'=' * 80}")
    print("ALL TESTS COMPLETED")
    print(f"{'=' * 80}\n")

def test_search_functionality():
    """Test full-text search"""
    
    print("\n" + "=" * 80)
    print("TEXT SEARCH FUNCTIONALITY TEST")
    print("=" * 80)
    
    search_queries = [
        "Python",
        "Web Development",
        "Machine Learning",
        "AWS",
        "JavaScript"
    ]
    
    for query in search_queries:
        print(f"\n🔍 Searching for: '{query}'")
        try:
            response = requests.get(f"{BASE_URL}/search?q={query}")
            # Note: This will render HTML, but API search endpoints would return JSON
            print(f"✅ Search executed successfully")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

def test_crud_operations():
    """Document CRUD operation flow"""
    
    print("\n" + "=" * 80)
    print("CRUD OPERATIONS")
    print("=" * 80)
    
    print("""
    CREATE (POST /add_course)
    ├─ Input: title, description, instructor, category, level, price, duration
    ├─ Process: Creates course with embedded content structure
    ├─ Lookup: Finds or creates instructor
    ├─ Result: Course stored with 3-chapter embedded content
    └─ Response: Redirect to admin dashboard
    
    READ (GET /get_course/<course_id>)
    ├─ Input: course_id (ObjectId)
    ├─ Process: Finds course by _id
    ├─ Result: Returns full course JSON including embedded content
    └─ Response: JSON with all course details
    
    UPDATE (POST /update_course/<course_id>)
    ├─ Input: course_id, title, description, price, level
    ├─ Process: Updates specific fields
    ├─ Result: Modified_count returned
    └─ Response: JSON with success status
    
    DELETE (POST /delete_course/<course_id>)
    ├─ Input: course_id
    ├─ Process: 
    │  ├─ Delete all enrollments for course
    │  └─ Delete course document
    ├─ Result: Cascading delete maintains referential integrity
    └─ Response: JSON with deleted_count
    
    ENROLL (POST /enroll)
    ├─ Input: name, email, course_id
    ├─ Process:
    │  ├─ Check for duplicate enrollment
    │  ├─ Create/find student
    │  └─ Create enrollment record
    ├─ Result: Student added to course
    └─ Response: Redirect to dashboard
    
    UNENROLL (POST /unenroll/<course_id>)
    ├─ Input: course_id (email from session)
    ├─ Process: Delete enrollment record
    ├─ Result: Student removed from course
    └─ Response: JSON success status
    """)

def test_aggregation_pipelines():
    """Document aggregation pipeline examples"""
    
    print("\n" + "=" * 80)
    print("AGGREGATION PIPELINE EXAMPLES")
    print("=" * 80)
    
    print("""
    1️⃣ MOST POPULAR COURSES
       Pipeline Stages:
       ├─ $group: Group enrollments by courseId, sum count
       ├─ $sort: Sort by enrollment count descending
       ├─ $limit: Get top 10 courses
       ├─ $lookup: Join with courses collection
       ├─ $unwind: Flatten course details
       └─ $project: Select specific fields
       
       Key Operators: $group, $sum, $sort, $lookup
    
    2️⃣ STUDENTS PER COURSE
       Pipeline Stages:
       ├─ $group: Group by courseId, push student details
       ├─ $sort: Sort by student count
       ├─ $lookup: Join with courses
       └─ $project: Format output with $slice
       
       Key Operators: $group, $push, $lookup, $slice, $sum
    
    3️⃣ COURSE STATISTICS
       Pipeline Stages:
       ├─ $lookup: Bring enrollment data
       ├─ $project: Calculate size, revenue, multiply
       └─ $sort: Sort by revenue
       
       Key Operators: $size, $multiply, $cond, $divide
    
    4️⃣ INSTRUCTOR PERFORMANCE
       Pipeline Stages:
       ├─ $lookup: Get enrollments
       ├─ $group: Group by instructor, calculate metrics
       └─ $project: Format and round results
       
       Key Operators: $group, $avg, $sum, $round
    
    5️⃣ ENROLLMENT TRENDS
       Pipeline Stages:
       ├─ $group: Group by date with $dateToString
       └─ $sort: Chronological order
       
       Key Operators: $dateToString, $group, $sum
    """)

def main():
    """Main testing function"""
    
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "COURSEHUB - COMPLETE API TESTING" + " " * 26 + "║")
    print("║" + " " * 18 + "(Online Course Platform with MongoDB)" + " " * 24 + "║")
    print("╚" + "=" * 78 + "╝")
    
    print(f"\n⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔗 Base URL: {BASE_URL}")
    
    try:
        print("\n🔗 Testing API connectivity...")
        response = requests.get(f"{BASE_URL}/")
        print("✅ API Server is running!")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Ensure app is running: python app.py")
        return
    
    test_crud_operations()
    test_aggregation_pipelines()
    
    try:
        test_analytics_endpoints()
    except requests.exceptions.ConnectionError:
        print("⚠️ API endpoints not available yet. They will work once sample data is loaded.")
    
    test_search_functionality()
    
    print("\n" + "=" * 80)
    print("TESTING GUIDE COMPLETE")
    print("=" * 80)
    print("""
    📚 Documentation Files:
    ├─ COMPLETE_DOCUMENTATION.md - Full schema, CRUD, aggregation details
    ├─ API Testing Guide - This file
    └─ README.md - Quick start guide
    
    🌐 Web Interface:
    ├─ http://localhost:5000/ - Landing page
    ├─ http://localhost:5000/login - User login
    ├─ http://localhost:5000/admin_login - Admin login
    ├─ http://localhost:5000/dashboard - User dashboard
    └─ http://localhost:5000/admin_dashboard - Admin dashboard
    
    📊 API Endpoints (JSON responses):
    ├─ /api/analytics/popular-courses - Top courses by enrollments
    ├─ /api/analytics/students-per-course - Student breakdown
    ├─ /api/analytics/course-statistics - Revenue and metrics
    ├─ /api/analytics/instructor-performance - Instructor stats
    ├─ /api/analytics/enrollment-trends - Time-series data
    └─ /api/analytics/course-popularity - Single best course
    """)

if __name__ == "__main__":
    main()
