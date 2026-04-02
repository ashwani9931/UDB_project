
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import os
from werkzeug.security import generate_password_hash, check_password_hash
import re

# Try to process logo (remove white background and crop)
def process_logo():
    """Remove white background from logo, crop it, and save as PNG"""
    try:
        from PIL import Image
        logo_jpeg = 'static/logo.jpeg'
        logo_png = 'static/logo.png'
        
        # Process the logo
        if os.path.exists(logo_jpeg):
            img = Image.open(logo_jpeg)
            
            # Convert to RGBA for transparency
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Get image data
            data = img.getdata()
            
            # Replace white and near-white background with transparent
            new_data = []
            for item in data:
                # If pixel is white or very light (close to white), make transparent
                if item[0] > 220 and item[1] > 220 and item[2] > 220:
                    new_data.append((255, 255, 255, 0))
                else:
                    new_data.append(item)
            
            # Apply the new data
            img.putalpha(Image.new('L', img.size, 255))
            img.putdata(new_data)
            
            # Auto-crop to content (remove transparent borders)
            def get_bbox(image):
                """Get bounding box of non-transparent content"""
                alpha = image.split()[-1]
                bbox = alpha.getbbox()
                return bbox
            
            bbox = get_bbox(img)
            if bbox:
                # Add small padding to the crop
                x1, y1, x2, y2 = bbox
                padding = 10
                x1 = max(0, x1 - padding)
                y1 = max(0, y1 - padding)
                x2 = min(img.width, x2 + padding)
                y2 = min(img.height, y2 + padding)
                img = img.crop((x1, y1, x2, y2))
            
            # Save as PNG
            img.save(logo_png)
            print(f"✓ Logo processed: {logo_png} ({img.width}x{img.height})")
    except Exception as e:
        print(f"Note: Could not process logo with PIL: {e}")

# Process logo on app startup
process_logo()

app = Flask(__name__)
app.secret_key = 'coursehub_secret_key_2026'

import os
from pymongo import MongoClient

MONGO_URI = os.environ.get("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["courseHub"]

# Collections
courses_collection = db["courses"]
students_collection = db["students"]
enrollments_collection = db["enrollments"]
instructors_collection = db["instructors"]
users_collection = db["users"]  # For registered users

# Create indexes for optimal performance
try:
    # Drop existing text index if it exists (to update it with new fields)
    try:
        courses_collection.drop_index("title_text_description_text")
    except:
        pass  # Index doesn't exist or other error - that's fine
    
    # Create the new text index with all three fields
    courses_collection.create_index([("title", "text"), ("description", "text"), ("content.topic", "text")])
except Exception as e:
    print(f"Warning: Could not create text index: {e}")

# Create other indexes
try:
    courses_collection.create_index([("instructor_id", 1)])
    students_collection.create_index([("email", 1)])
    enrollments_collection.create_index([("courseId", 1), ("studentId", 1)])
    users_collection.create_index([("email", 1)], unique=True)  # Unique email
except Exception as e:
    print(f"Warning: Could not create indexes: {e}")

# Backward compatibility
courses = courses_collection
students = students_collection
enrollments = enrollments_collection

# Demo credentials
DEMO_USERS = {
    "ashwani@coursehub.com": "password123",
    "ashwani.student@coursehub.com": "password123"
}

DEMO_ADMINS = {
    "admin": "admin123"
}

# ============================================================================
# INITIALIZATION - Create sample data if needed
# ============================================================================

def initialize_sample_data():
    """Initialize database with sample instructors, courses, and students"""
    
    # Initialize Instructors
    if instructors_collection.count_documents({}) == 0:
        sample_instructors = [
            {
                "name": "Dr. Rajesh Kumar",
                "bio": "Expert in Data Structures and Algorithms with 12 years of experience",
                "expertise": ["Data Structures", "Algorithms", "C++", "Java"],
                "rating": 4.9
            },
            {
                "name": "Prof. Priya Sharma",
                "bio": "Full-stack web developer and cloud computing specialist",
                "expertise": ["Web Development", "Python", "JavaScript", "Cloud Computing"],
                "rating": 4.8
            },
            {
                "name": "Dr. Amit Patel",
                "bio": "AI/ML researcher and deep learning enthusiast",
                "expertise": ["Machine Learning", "Deep Learning", "Python", "TensorFlow"],
                "rating": 4.7
            },
            {
                "name": "Dr. Neha Singh",
                "bio": "Database architect with expertise in SQL and NoSQL",
                "expertise": ["Database Design", "SQL", "MongoDB", "Optimization"],
                "rating": 4.8
            },
            {
                "name": "Prof. Vikram Reddy",
                "bio": "Software engineering expert focusing on system design",
                "expertise": ["System Design", "Software Architecture", "Java", "Microservices"],
                "rating": 4.9
            },
            {
                "name": "Dr. Ananya Gupta",
                "bio": "Cybersecurity specialist and ethical hacker",
                "expertise": ["Cybersecurity", "Network Security", "Encryption", "Penetration Testing"],
                "rating": 4.7
            }
        ]
        instructors_collection.insert_many(sample_instructors)
    
    # Initialize CSE-based Courses
    if courses_collection.count_documents({}) == 0:
        instructors = list(instructors_collection.find())
        
        cse_courses = [
            {
                "title": "Data Structures & Algorithms Masterclass",
                "description": "Complete guide to master data structures like arrays, linked lists, trees, and sorting algorithms",
                "instructor": instructors[0]["name"],
                "instructor_id": instructors[0]["_id"],
                "category": "Core CSE",
                "level": "Beginner",
                "price": 49.99,
                "duration_hours": 40,
                "rating": 4.9,
                "num_ratings": 1250,
                "students_purchased": 350,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "content": [
                    {
                        "chapter": "Array & String Fundamentals",
                        "lessons": [
                            {"title": "Array Operations", "duration": "3 hours"},
                            {"title": "String Manipulation", "duration": "2 hours"},
                            {"title": "2D Arrays", "duration": "2 hours"}
                        ]
                    },
                    {
                        "chapter": "Linked Lists & Stacks",
                        "lessons": [
                            {"title": "Linked List Basics", "duration": "4 hours"},
                            {"title": "Stack Implementations", "duration": "3 hours"},
                            {"title": "Queue Operations", "duration": "3 hours"}
                        ]
                    },
                    {
                        "chapter": "Sorting & Searching",
                        "lessons": [
                            {"title": "Bubble & Selection Sort", "duration": "2 hours"},
                            {"title": "Quick Sort & Merge Sort", "duration": "4 hours"},
                            {"title": "Binary Search", "duration": "2 hours"}
                        ]
                    }
                ]
            },
            {
                "title": "Advanced Algorithms - Competitive Programming",
                "description": "Master advanced algorithms for competitive programming including graph theory and dynamic programming",
                "instructor": instructors[0]["name"],
                "instructor_id": instructors[0]["_id"],
                "category": "Advanced CSE",
                "level": "Advanced",
                "price": 59.99,
                "duration_hours": 50,
                "rating": 4.8,
                "num_ratings": 890,
                "students_purchased": 280,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "content": [
                    {
                        "chapter": "Graph Theory Basics",
                        "lessons": [
                            {"title": "Graph Representation", "duration": "3 hours"},
                            {"title": "BFS & DFS", "duration": "4 hours"},
                            {"title": "Shortest Paths", "duration": "3 hours"}
                        ]
                    },
                    {
                        "chapter": "Dynamic Programming",
                        "lessons": [
                            {"title": "DP Fundamentals", "duration": "4 hours"},
                            {"title": "Knapsack Problems", "duration": "4 hours"},
                            {"title": "Matrix Chain Multiplication", "duration": "3 hours"}
                        ]
                    }
                ]
            },
            {
                "title": "Full Stack Web Development with Python & JavaScript",
                "description": "Build complete web applications using Python Flask, Django, and modern JavaScript frameworks",
                "instructor": instructors[1]["name"],
                "instructor_id": instructors[1]["_id"],
                "category": "Web Development",
                "level": "Intermediate",
                "price": 69.99,
                "duration_hours": 60,
                "rating": 4.8,
                "num_ratings": 2150,
                "students_purchased": 450,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "content": [
                    {
                        "chapter": "Frontend Development",
                        "lessons": [
                            {"title": "HTML5 & CSS3", "duration": "5 hours"},
                            {"title": "JavaScript ES6+", "duration": "6 hours"},
                            {"title": "React.js Basics", "duration": "6 hours"}
                        ]
                    },
                    {
                        "chapter": "Backend Development",
                        "lessons": [
                            {"title": "Flask Framework", "duration": "5 hours"},
                            {"title": "RESTful APIs", "duration": "4 hours"},
                            {"title": "Authentication & Security", "duration": "4 hours"}
                        ]
                    },
                    {
                        "chapter": "Database & Deployment",
                        "lessons": [
                            {"title": "SQL & SQLite", "duration": "4 hours"},
                            {"title": "MongoDB Integration", "duration": "3 hours"},
                            {"title": "Cloud Deployment", "duration": "4 hours"}
                        ]
                    }
                ]
            },
            {
                "title": "Machine Learning & Deep Learning Specialization",
                "description": "Learn ML algorithms, neural networks, and real-world applications using TensorFlow",
                "instructor": instructors[2]["name"],
                "instructor_id": instructors[2]["_id"],
                "category": "AI/ML",
                "level": "Advanced",
                "price": 89.99,
                "duration_hours": 70,
                "rating": 4.9,
                "num_ratings": 1680,
                "students_purchased": 380,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "content": [
                    {
                        "chapter": "ML Fundamentals",
                        "lessons": [
                            {"title": "Supervised Learning", "duration": "5 hours"},
                            {"title": "Unsupervised Learning", "duration": "4 hours"},
                            {"title": "Model Evaluation", "duration": "3 hours"}
                        ]
                    },
                    {
                        "chapter": "Deep Learning",
                        "lessons": [
                            {"title": "Neural Networks", "duration": "6 hours"},
                            {"title": "CNNs for Image Classification", "duration": "5 hours"},
                            {"title": "RNNs & LSTMs", "duration": "5 hours"}
                        ]
                    },
                    {
                        "chapter": "Real-world Projects",
                        "lessons": [
                            {"title": "Image Recognition Project", "duration": "6 hours"},
                            {"title": "NLP Project", "duration": "5 hours"},
                            {"title": "Time Series Forecasting", "duration": "5 hours"}
                        ]
                    }
                ]
            },
            {
                "title": "Database Management Systems (DBMS)",
                "description": "Master SQL, database design, normalization, and optimization techniques",
                "instructor": instructors[3]["name"],
                "instructor_id": instructors[3]["_id"],
                "category": "Database",
                "level": "Intermediate",
                "price": 54.99,
                "duration_hours": 45,
                "rating": 4.7,
                "num_ratings": 920,
                "students_purchased": 280,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "content": [
                    {
                        "chapter": "SQL Basics",
                        "lessons": [
                            {"title": "SELECT & WHERE Clauses", "duration": "4 hours"},
                            {"title": "Joins & Subqueries", "duration": "4 hours"},
                            {"title": "Aggregation Functions", "duration": "3 hours"}
                        ]
                    },
                    {
                        "chapter": "Database Design",
                        "lessons": [
                            {"title": "ER Modeling", "duration": "4 hours"},
                            {"title": "Normalization", "duration": "4 hours"},
                            {"title": "Indexing & Optimization", "duration": "4 hours"}
                        ]
                    }
                ]
            },
            {
                "title": "System Design & Software Architecture",
                "description": "Learn to design scalable systems, microservices architecture, and distributed systems",
                "instructor": instructors[4]["name"],
                "instructor_id": instructors[4]["_id"],
                "category": "System Design",
                "level": "Advanced",
                "price": 79.99,
                "duration_hours": 55,
                "rating": 4.9,
                "num_ratings": 1120,
                "students_purchased": 320,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "content": [
                    {
                        "chapter": "Scalability Basics",
                        "lessons": [
                            {"title": "Horizontal vs Vertical Scaling", "duration": "4 hours"},
                            {"title": "Load Balancing", "duration": "3 hours"},
                            {"title": "Caching Strategies", "duration": "3 hours"}
                        ]
                    },
                    {
                        "chapter": "Distributed Systems",
                        "lessons": [
                            {"title": "CAP Theorem", "duration": "3 hours"},
                            {"title": "Database Sharding", "duration": "4 hours"},
                            {"title": "Microservices", "duration": "4 hours"}
                        ]
                    }
                ]
            },
            {
                "title": "Cybersecurity & Ethical Hacking",
                "description": "Learn network security, cryptography, penetration testing, and secure coding practices",
                "instructor": instructors[5]["name"],
                "instructor_id": instructors[5]["_id"],
                "category": "Cybersecurity",
                "level": "Intermediate",
                "price": 74.99,
                "duration_hours": 52,
                "rating": 4.7,
                "num_ratings": 680,
                "students_purchased": 220,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "content": [
                    {
                        "chapter": "Network Security",
                        "lessons": [
                            {"title": "Network Protocols", "duration": "4 hours"},
                            {"title": "Firewalls & Encryption", "duration": "4 hours"},
                            {"title": "VPN & TLS", "duration": "3 hours"}
                        ]
                    },
                    {
                        "chapter": "Penetration Testing",
                        "lessons": [
                            {"title": "Reconnaissance", "duration": "3 hours"},
                            {"title": "Vulnerability Scanning", "duration": "4 hours"},
                            {"title": "Exploitation Techniques", "duration": "4 hours"}
                        ]
                    }
                ]
            },
            {
                "title": "Object-Oriented Programming with Java",
                "description": "Master OOP concepts, design patterns, and build enterprise Java applications",
                "instructor": instructors[4]["name"],
                "instructor_id": instructors[4]["_id"],
                "category": "Programming",
                "level": "Beginner",
                "price": 44.99,
                "duration_hours": 48,
                "rating": 4.8,
                "num_ratings": 1890,
                "students_purchased": 420,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "content": [
                    {
                        "chapter": "OOP Concepts",
                        "lessons": [
                            {"title": "Classes & Objects", "duration": "4 hours"},
                            {"title": "Inheritance & Polymorphism", "duration": "4 hours"},
                            {"title": "Encapsulation & Abstraction", "duration": "3 hours"}
                        ]
                    }
                ]
            },
            {
                "title": "Operating Systems & Computer Networks",
                "description": "Comprehensive course on OS concepts, memory management, networking layers and protocols",
                "instructor": instructors[0]["name"],
                "instructor_id": instructors[0]["_id"],
                "category": "Core CSE",
                "level": "Intermediate",
                "price": 59.99,
                "duration_hours": 56,
                "rating": 4.8,
                "num_ratings": 750,
                "students_purchased": 250,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "content": [
                    {
                        "chapter": "Operating Systems",
                        "lessons": [
                            {"title": "Process Management", "duration": "5 hours"},
                            {"title": "Memory Management", "duration": "5 hours"},
                            {"title": "File Systems", "duration": "4 hours"}
                        ]
                    },
                    {
                        "chapter": "Computer Networks",
                        "lessons": [
                            {"title": "Network Layers", "duration": "5 hours"},
                            {"title": "TCP/IP Protocol", "duration": "4 hours"},
                            {"title": "DNS & HTTP", "duration": "4 hours"}
                        ]
                    }
                ]
            }
        ]
        
        courses_collection.insert_many(cse_courses)
    
    # Initialize Students
    if students_collection.count_documents({}) == 0:
        sample_students = [
            {"name": "Arjun Kumar", "email": "arjun@student.com", "enrolled_courses": [], "enrollment_date": datetime.now()},
            {"name": "Priya Verma", "email": "priya@student.com", "enrolled_courses": [], "enrollment_date": datetime.now()},
            {"name": "Rohan Singh", "email": "rohan@student.com", "enrolled_courses": [], "enrollment_date": datetime.now()},
            {"name": "Divya Patel", "email": "divya@student.com", "enrolled_courses": [], "enrollment_date": datetime.now()},
            {"name": "Nikhil Sharma", "email": "nikhil@student.com", "enrolled_courses": [], "enrollment_date": datetime.now()},
            {"name": "Anjali Gupta", "email": "anjali@student.com", "enrolled_courses": [], "enrollment_date": datetime.now()},
            {"name": "Aditya Reddy", "email": "aditya@student.com", "enrolled_courses": [], "enrollment_date": datetime.now()},
            {"name": "Sakshi Nair", "email": "sakshi@student.com", "enrolled_courses": [], "enrollment_date": datetime.now()},
            {"name": "Rahul Desai", "email": "rahul@student.com", "enrolled_courses": [], "enrollment_date": datetime.now()},
            {"name": "Neha Bhatt", "email": "neha@student.com", "enrolled_courses": [], "enrollment_date": datetime.now()},
        ]
        result = students_collection.insert_many(sample_students)
        
        # Create sample enrollments
        courses = list(courses_collection.find())
        students = list(students_collection.find())
        
        enrollments_data = []
        for i, student in enumerate(students):
            # Each student enrolls in 2-3 courses
            num_courses = 2 + (i % 2)
            course_indices = [(i + j) % len(courses) for j in range(num_courses)]
            
            for course_idx in course_indices:
                course = courses[course_idx]
                enrollment = {
                    "studentId": student["_id"],
                    "courseId": course["_id"],
                    "email": student["email"],
                    "student_name": student["name"],
                    "enrollment_date": datetime.now(),
                    "completion_status": "in_progress",
                    "progress": (i * 15) % 100
                }
                enrollments_data.append(enrollment)
        
        if enrollments_data:
            enrollments_collection.insert_many(enrollments_data)

# Initialize data on startup
initialize_sample_data()

def add_design_creative_courses():
    """Add 15 Design & Creative courses to the database"""
    
    # Design instructors
    design_instructors = [
        {
            "name": "Marcus Chen",
            "bio": "UI/UX specialist with 10+ years in digital design",
            "expertise": ["UI Design", "UX Design", "Figma", "User Research"],
            "rating": 4.9
        },
        {
            "name": "Sarah Williams",
            "bio": "Graphic designer and brand identity expert",
            "expertise": ["Graphic Design", "Branding", "Adobe Creative Suite", "Typography"],
            "rating": 4.8
        },
        {
            "name": "James Rodriguez",
            "bio": "Product designer with experience at top tech companies",
            "expertise": ["Product Design", "Prototyping", "Design Systems", "Leadership"],
            "rating": 4.9
        },
        {
            "name": "Emma Thompson",
            "bio": "Motion graphics and animation specialist",
            "expertise": ["Animation", "Motion Design", "After Effects", "3D Animation"],
            "rating": 4.7
        },
        {
            "name": "David Kim",
            "bio": "Web design expert and front-end enthusiast",
            "expertise": ["Web Design", "Responsive Design", "CSS", "User Experience"],
            "rating": 4.8
        }
    ]
    
    # Add instructors if not already present
    existing_instructors = list(instructors_collection.find({"bio": {"$regex": "specialist|expert"}}))
    if len(existing_instructors) < 11:  # Less than our expected total
        for instructor in design_instructors:
            if not instructors_collection.find_one({"name": instructor["name"]}):
                instructors_collection.insert_one(instructor)
    
    # Refresh instructor list
    all_instructors = list(instructors_collection.find())
    design_instructor_map = {
        "Marcus Chen": next((i for i in all_instructors if i["name"] == "Marcus Chen"), None),
        "Sarah Williams": next((i for i in all_instructors if i["name"] == "Sarah Williams"), None),
        "James Rodriguez": next((i for i in all_instructors if i["name"] == "James Rodriguez"), None),
        "Emma Thompson": next((i for i in all_instructors if i["name"] == "Emma Thompson"), None),
        "David Kim": next((i for i in all_instructors if i["name"] == "David Kim"), None),
    }
    
    # Design courses
    design_courses = [
        # UI/UX Design (4 courses)
        {
            "title": "UI/UX Design Masterclass - From Zero to Professional",
            "description": "Complete guide to becoming a professional UI/UX designer with hands-on projects",
            "instructor": "Marcus Chen",
            "instructor_id": design_instructor_map["Marcus Chen"]["_id"] if design_instructor_map["Marcus Chen"] else None,
            "category": "UI/UX Design",
            "level": "Beginner",
            "price": 79.99,
            "duration_hours": 60,
            "rating": 4.9,
            "num_ratings": 2340,
            "students_purchased": 580,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "content": [
                {
                    "chapter": "Design Fundamentals",
                    "lessons": [
                        {"title": "Design Principles", "duration": "4 hours"},
                        {"title": "Color Theory", "duration": "3 hours"},
                        {"title": "Typography Basics", "duration": "3 hours"}
                    ]
                },
                {
                    "chapter": "User Research & Personas",
                    "lessons": [
                        {"title": "User Research Methods", "duration": "4 hours"},
                        {"title": "Creating Personas", "duration": "3 hours"},
                        {"title": "User Journey Maps", "duration": "3 hours"}
                    ]
                },
                {
                    "chapter": "Wireframing & Prototyping",
                    "lessons": [
                        {"title": "Low-Fidelity Wireframes", "duration": "4 hours"},
                        {"title": "High-Fidelity Mockups", "duration": "5 hours"},
                        {"title": "Interactive Prototypes", "duration": "5 hours"}
                    ]
                }
            ]
        },
        {
            "title": "Advanced Figma - Professional Design Tool Mastery",
            "description": "Master Figma for professional UI/UX design workflows and collaboration",
            "instructor": "Marcus Chen",
            "instructor_id": design_instructor_map["Marcus Chen"]["_id"] if design_instructor_map["Marcus Chen"] else None,
            "category": "UI/UX Design",
            "level": "Intermediate",
            "price": 69.99,
            "duration_hours": 45,
            "rating": 4.8,
            "num_ratings": 1680,
            "students_purchased": 420,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "content": [
                {
                    "chapter": "Figma Essentials",
                    "lessons": [
                        {"title": "Interface & Navigation", "duration": "3 hours"},
                        {"title": "Shapes & Vectors", "duration": "3 hours"},
                        {"title": "Text & Components", "duration": "3 hours"}
                    ]
                },
                {
                    "chapter": "Design Systems",
                    "lessons": [
                        {"title": "Creating Components", "duration": "4 hours"},
                        {"title": "Variants & Auto Layout", "duration": "4 hours"},
                        {"title": "Documentation", "duration": "2 hours"}
                    ]
                }
            ]
        },
        {
            "title": "Mobile App UI Design - iOS & Android",
            "description": "Learn platform-specific guidelines and design beautiful mobile applications",
            "instructor": "Marcus Chen",
            "instructor_id": design_instructor_map["Marcus Chen"]["_id"] if design_instructor_map["Marcus Chen"] else None,
            "category": "UI/UX Design",
            "level": "Intermediate",
            "price": 74.99,
            "duration_hours": 50,
            "rating": 4.7,
            "num_ratings": 1290,
            "students_purchased": 380,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "content": [
                {
                    "chapter": "iOS Design",
                    "lessons": [
                        {"title": "iOS Guidelines", "duration": "4 hours"},
                        {"title": "Navigation Patterns", "duration": "3 hours"},
                        {"title": "iOS Components", "duration": "3 hours"}
                    ]
                },
                {
                    "chapter": "Android Design",
                    "lessons": [
                        {"title": "Material Design 3", "duration": "4 hours"},
                        {"title": "Android Patterns", "duration": "3 hours"},
                        {"title": "Responsive Layouts", "duration": "3 hours"}
                    ]
                }
            ]
        },
        {
            "title": "Web Design Best Practices & Performance",
            "description": "Design responsive, accessible, and performant websites",
            "instructor": "David Kim",
            "instructor_id": design_instructor_map["David Kim"]["_id"] if design_instructor_map["David Kim"] else None,
            "category": "Web Design",
            "level": "Beginner",
            "price": 64.99,
            "duration_hours": 44,
            "rating": 4.8,
            "num_ratings": 1820,
            "students_purchased": 460,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "content": [
                {
                    "chapter": "Web Design Principles",
                    "lessons": [
                        {"title": "Responsive Design", "duration": "4 hours"},
                        {"title": "Accessibility Standards", "duration": "3 hours"},
                        {"title": "Web Performance", "duration": "3 hours"}
                    ]
                },
                {
                    "chapter": "Design Systems for Web",
                    "lessons": [
                        {"title": "Design Systems", "duration": "4 hours"},
                        {"title": "CSS Grid & Flexbox", "duration": "3 hours"},
                        {"title": "Semantic HTML", "duration": "2 hours"}
                    ]
                }
            ]
        },
        # Graphic Design (5 courses)
        {
            "title": "Graphic Design Fundamentals - Creative Toolkit",
            "description": "Master the fundamentals of graphic design and visual communication",
            "instructor": "Sarah Williams",
            "instructor_id": design_instructor_map["Sarah Williams"]["_id"] if design_instructor_map["Sarah Williams"] else None,
            "category": "Graphic Design",
            "level": "Beginner",
            "price": 59.99,
            "duration_hours": 48,
            "rating": 4.9,
            "num_ratings": 2150,
            "students_purchased": 540,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "content": [
                {
                    "chapter": "Design Principles",
                    "lessons": [
                        {"title": "Composition & Layout", "duration": "4 hours"},
                        {"title": "Color Psychology", "duration": "3 hours"},
                        {"title": "Typography", "duration": "4 hours"}
                    ]
                },
                {
                    "chapter": "Tools & Software",
                    "lessons": [
                        {"title": "Adobe Photoshop Basics", "duration": "5 hours"},
                        {"title": "Adobe Illustrator", "duration": "5 hours"},
                        {"title": "InDesign for Layout", "duration": "4 hours"}
                    ]
                }
            ]
        },
        {
            "title": "Branding & Brand Identity Design",
            "description": "Create powerful brand identities and complete branding systems",
            "instructor": "Sarah Williams",
            "instructor_id": design_instructor_map["Sarah Williams"]["_id"] if design_instructor_map["Sarah Williams"] else None,
            "category": "Graphic Design",
            "level": "Advanced",
            "price": 84.99,
            "duration_hours": 56,
            "rating": 4.8,
            "num_ratings": 980,
            "students_purchased": 280,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "content": [
                {
                    "chapter": "Brand Strategy",
                    "lessons": [
                        {"title": "Brand Identity", "duration": "5 hours"},
                        {"title": "Brand Guidelines", "duration": "4 hours"},
                        {"title": "Logo Design", "duration": "5 hours"}
                    ]
                },
                {
                    "chapter": "Brand Application",
                    "lessons": [
                        {"title": "Packaging Design", "duration": "4 hours"},
                        {"title": "Marketing Materials", "duration": "4 hours"},
                        {"title": "Brand Strategy Workshop", "duration": "3 hours"}
                    ]
                }
            ]
        },
        {
            "title": "Logo Design Professional Course",
            "description": "Design memorable and effective logos for any brand",
            "instructor": "Sarah Williams",
            "instructor_id": design_instructor_map["Sarah Williams"]["_id"] if design_instructor_map["Sarah Williams"] else None,
            "category": "Graphic Design",
            "level": "Intermediate",
            "price": 49.99,
            "duration_hours": 32,
            "rating": 4.7,
            "num_ratings": 1560,
            "students_purchased": 420,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "content": [
                {
                    "chapter": "Logo Fundamentals",
                    "lessons": [
                        {"title": "Logo Types", "duration": "3 hours"},
                        {"title": "Design Process", "duration": "3 hours"},
                        {"title": "Sketching & Ideation", "duration": "3 hours"}
                    ]
                },
                {
                    "chapter": "Digital Logo Design",
                    "lessons": [
                        {"title": "Vector Creation", "duration": "3 hours"},
                        {"title": "Logo Variations", "duration": "3 hours"},
                        {"title": "Presentation & Delivery", "duration": "2 hours"}
                    ]
                }
            ]
        },
        {
            "title": "Print Design Masterclass",
            "description": "Master print design for brochures, flyers, posters, and more",
            "instructor": "Sarah Williams",
            "instructor_id": design_instructor_map["Sarah Williams"]["_id"] if design_instructor_map["Sarah Williams"] else None,
            "category": "Graphic Design",
            "level": "Intermediate",
            "price": 54.99,
            "duration_hours": 40,
            "rating": 4.6,
            "num_ratings": 890,
            "students_purchased": 260,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "content": [
                {
                    "chapter": "Print Fundamentals",
                    "lessons": [
                        {"title": "Print Specifications", "duration": "3 hours"},
                        {"title": "Color Modes & Theory", "duration": "3 hours"},
                        {"title": "Typography in Print", "duration": "3 hours"}
                    ]
                },
                {
                    "chapter": "Print Projects",
                    "lessons": [
                        {"title": "Brochure Design", "duration": "3 hours"},
                        {"title": "Poster Design", "duration": "3 hours"},
                        {"title": "Packaging Design", "duration": "2 hours"}
                    ]
                }
            ]
        },
        {
            "title": "Digital Illustration & Digital Art",
            "description": "Create stunning digital illustrations and artwork using modern tools",
            "instructor": "Sarah Williams",
            "instructor_id": design_instructor_map["Sarah Williams"]["_id"] if design_instructor_map["Sarah Williams"] else None,
            "category": "Graphic Design",
            "level": "Intermediate",
            "price": 69.99,
            "duration_hours": 50,
            "rating": 4.8,
            "num_ratings": 1340,
            "students_purchased": 350,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "content": [
                {
                    "chapter": "Digital Illustration Basics",
                    "lessons": [
                        {"title": "Digital Drawing Fundamentals", "duration": "5 hours"},
                        {"title": "Brush Techniques", "duration": "4 hours"},
                        {"title": "Color & Shading", "duration": "4 hours"}
                    ]
                },
                {
                    "chapter": "Advanced Techniques",
                    "lessons": [
                        {"title": "Character Design", "duration": "5 hours"},
                        {"title": "Environment Art", "duration": "4 hours"},
                        {"title": "Portfolio Building", "duration": "3 hours"}
                    ]
                }
            ]
        },
        # Product Design (3 courses)
        {
            "title": "Product Design & User-Centered Design",
            "description": "Learn product design thinking and create user-centered solutions",
            "instructor": "James Rodriguez",
            "instructor_id": design_instructor_map["James Rodriguez"]["_id"] if design_instructor_map["James Rodriguez"] else None,
            "category": "Product Design",
            "level": "Advanced",
            "price": 94.99,
            "duration_hours": 65,
            "rating": 4.9,
            "num_ratings": 1450,
            "students_purchased": 340,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "content": [
                {
                    "chapter": "Product Strategy",
                    "lessons": [
                        {"title": "Market Research", "duration": "4 hours"},
                        {"title": "Problem Definition", "duration": "4 hours"},
                        {"title": "Product Vision", "duration": "3 hours"}
                    ]
                },
                {
                    "chapter": "Design Process",
                    "lessons": [
                        {"title": "Discovery & Ideation", "duration": "5 hours"},
                        {"title": "Design Thinking", "duration": "4 hours"},
                        {"title": "Prototyping", "duration": "5 hours"}
                    ]
                },
                {
                    "chapter": "Execution & Launch",
                    "lessons": [
                        {"title": "Design Systems", "duration": "4 hours"},
                        {"title": "Handoff to Development", "duration": "3 hours"},
                        {"title": "Post-Launch", "duration": "3 hours"}
                    ]
                }
            ]
        },
        {
            "title": "Design Systems & Component Design",
            "description": "Build scalable design systems and component libraries",
            "instructor": "James Rodriguez",
            "instructor_id": design_instructor_map["James Rodriguez"]["_id"] if design_instructor_map["James Rodriguez"] else None,
            "category": "Product Design",
            "level": "Advanced",
            "price": 89.99,
            "duration_hours": 58,
            "rating": 4.8,
            "num_ratings": 920,
            "students_purchased": 280,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "content": [
                {
                    "chapter": "Design System Foundations",
                    "lessons": [
                        {"title": "Design System Principles", "duration": "4 hours"},
                        {"title": "Tokens & Variables", "duration": "4 hours"},
                        {"title": "Component Architecture", "duration": "4 hours"}
                    ]
                },
                {
                    "chapter": "Implementation",
                    "lessons": [
                        {"title": "Building Components", "duration": "5 hours"},
                        {"title": "Documentation", "duration": "4 hours"},
                        {"title": "Maintenance & Scaling", "duration": "3 hours"}
                    ]
                }
            ]
        },
        {
            "title": "SaaS Product Design for Startups",
            "description": "Design and build successful SaaS products from concept to launch",
            "instructor": "James Rodriguez",
            "instructor_id": design_instructor_map["James Rodriguez"]["_id"] if design_instructor_map["James Rodriguez"] else None,
            "category": "Product Design",
            "level": "Advanced",
            "price": 99.99,
            "duration_hours": 62,
            "rating": 4.9,
            "num_ratings": 780,
            "students_purchased": 230,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "content": [
                {
                    "chapter": "SaaS Fundamentals",
                    "lessons": [
                        {"title": "SaaS Business Model", "duration": "3 hours"},
                        {"title": "User Research for SaaS", "duration": "4 hours"},
                        {"title": "Competitive Analysis", "duration": "3 hours"}
                    ]
                },
                {
                    "chapter": "Design & Development",
                    "lessons": [
                        {"title": "SaaS UI Patterns", "duration": "5 hours"},
                        {"title": "Onboarding Design", "duration": "4 hours"},
                        {"title": "Dashboard Design", "duration": "5 hours"}
                    ]
                }
            ]
        },
        # Animation & Motion Graphics (2 courses)
        {
            "title": "Motion Graphics & Animation Masterclass",
            "description": "Create stunning motion graphics and animations with After Effects",
            "instructor": "Emma Thompson",
            "instructor_id": design_instructor_map["Emma Thompson"]["_id"] if design_instructor_map["Emma Thompson"] else None,
            "category": "Animation",
            "level": "Intermediate",
            "price": 79.99,
            "duration_hours": 54,
            "rating": 4.7,
            "num_ratings": 1120,
            "students_purchased": 290,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "content": [
                {
                    "chapter": "After Effects Basics",
                    "lessons": [
                        {"title": "Interface & Workflow", "duration": "4 hours"},
                        {"title": "Layers & Compositions", "duration": "4 hours"},
                        {"title": "Keyframes & Animation", "duration": "4 hours"}
                    ]
                },
                {
                    "chapter": "Advanced Animation",
                    "lessons": [
                        {"title": "Effects & Presets", "duration": "4 hours"},
                        {"title": "3D Animation", "duration": "4 hours"},
                        {"title": "Motion Design Project", "duration": "5 hours"}
                    ]
                }
            ]
        },
        {
            "title": "3D Animation & Blender Mastery",
            "description": "Learn 3D animation, modeling, and rendering with Blender",
            "instructor": "Emma Thompson",
            "instructor_id": design_instructor_map["Emma Thompson"]["_id"] if design_instructor_map["Emma Thompson"] else None,
            "category": "Animation",
            "level": "Advanced",
            "price": 109.99,
            "duration_hours": 72,
            "rating": 4.8,
            "num_ratings": 680,
            "students_purchased": 180,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "content": [
                {
                    "chapter": "Blender Fundamentals",
                    "lessons": [
                        {"title": "Interface & Navigation", "duration": "4 hours"},
                        {"title": "3D Modeling Basics", "duration": "5 hours"},
                        {"title": "Materials & Lighting", "duration": "5 hours"}
                    ]
                },
                {
                    "chapter": "Animation & Rendering",
                    "lessons": [
                        {"title": "Rigging & Animation", "duration": "6 hours"},
                        {"title": "Rendering Engines", "duration": "5 hours"},
                        {"title": "Complete Project", "duration": "8 hours"}
                    ]
                }
            ]
        }
    ]
    
    # Insert courses if not already present
    for course in design_courses:
        if not courses_collection.find_one({"title": course["title"]}):
            courses_collection.insert_one(course)
    
    # Add enrollments for new courses
    all_students = list(students_collection.find())
    all_courses = list(courses_collection.find({"category": {"$in": ["UI/UX Design", "Graphic Design", "Product Design", "Animation", "Web Design"]}}))
    
    for idx, student in enumerate(all_students):
        # Randomly enroll students in design courses
        num_design_courses = (idx % 3) + 1
        for i in range(num_design_courses):
            course_idx = (idx + i) % len(all_courses)
            enrollment = {
                "studentId": student["_id"],
                "courseId": all_courses[course_idx]["_id"],
                "email": student["email"],
                "student_name": student["name"],
                "enrollment_date": datetime.now(),
                "completion_status": "in_progress",
                "progress": (idx * 20) % 100
            }
            # Check if enrollment already exists
            if not enrollments_collection.find_one({"studentId": student["_id"], "courseId": all_courses[course_idx]["_id"]}):
                enrollments_collection.insert_one(enrollment)

def add_cse_courses():
    """Add 15 additional CSE courses to the database"""
    
    # Refresh instructor list
    all_instructors = list(instructors_collection.find())
    
    cse_courses_additional = [
        {
            "title": "Competitive Programming Bootcamp",
            "description": "Master competitive programming with advanced problem-solving techniques",
            "instructor": all_instructors[0]["name"] if all_instructors else "Dr. Rajesh Kumar",
            "instructor_id": all_instructors[0]["_id"] if all_instructors else None,
            "category": "Advanced CSE",
            "level": "Advanced",
            "price": 69.99,
            "duration_hours": 52,
            "rating": 4.9,
            "num_ratings": 1200,
            "students_purchased": 310,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "content": [
                {
                    "chapter": "Contest Fundamentals",
                    "lessons": [
                        {"title": "Problem Solving Strategies", "duration": "4 hours"},
                        {"title": "Time Complexity Analysis", "duration": "3 hours"},
                        {"title": "Common Patterns", "duration": "3 hours"}
                    ]
                },
                {
                    "chapter": "Advanced Topics",
                    "lessons": [
                        {"title": "Graph Algorithms", "duration": "5 hours"},
                        {"title": "Dynamic Programming", "duration": "5 hours"},
                        {"title": "Number Theory", "duration": "4 hours"}
                    ]
                }
            ]
        },
        {
            "title": "Cloud Computing with AWS",
            "description": "Learn AWS services and deploy scalable cloud applications",
            "instructor": all_instructors[1]["name"] if len(all_instructors) > 1 else "Prof. Priya Sharma",
            "instructor_id": all_instructors[1]["_id"] if len(all_instructors) > 1 else None,
            "category": "Cloud Computing",
            "level": "Intermediate",
            "price": 79.99,
            "duration_hours": 58,
            "rating": 4.8,
            "num_ratings": 950,
            "students_purchased": 280,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "content": [
                {
                    "chapter": "AWS Basics",
                    "lessons": [
                        {"title": "AWS Services Overview", "duration": "4 hours"},
                        {"title": "EC2 & Storage", "duration": "5 hours"},
                        {"title": "Networking", "duration": "4 hours"}
                    ]
                },
                {
                    "chapter": "Building Applications",
                    "lessons": [
                        {"title": "Lambda & Serverless", "duration": "4 hours"},
                        {"title": "Databases", "duration": "4 hours"},
                        {"title": "DevOps & CI/CD", "duration": "4 hours"}
                    ]
                }
            ]
        },
        {
            "title": "Blockchain & Cryptocurrency Development",
            "description": "Build blockchain applications and understand cryptocurrency technology",
            "instructor": all_instructors[2]["name"] if len(all_instructors) > 2 else "Dr. Amit Patel",
            "instructor_id": all_instructors[2]["_id"] if len(all_instructors) > 2 else None,
            "category": "Advanced CSE",
            "level": "Advanced",
            "price": 89.99,
            "duration_hours": 62,
            "rating": 4.7,
            "num_ratings": 680,
            "students_purchased": 200,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "content": [
                {
                    "chapter": "Blockchain Fundamentals",
                    "lessons": [
                        {"title": "Blockchain Architecture", "duration": "4 hours"},
                        {"title": "Cryptography Basics", "duration": "4 hours"},
                        {"title": "Smart Contracts", "duration": "4 hours"}
                    ]
                },
                {
                    "chapter": "Development",
                    "lessons": [
                        {"title": "Ethereum & Solidity", "duration": "5 hours"},
                        {"title": "Web3.js & dApps", "duration": "5 hours"},
                        {"title": "DeFi Projects", "duration": "4 hours"}
                    ]
                }
            ]
        },
        {
            "title": "DevOps & Continuous Integration",
            "description": "Master DevOps practices and CI/CD pipeline automation",
            "instructor": all_instructors[3]["name"] if len(all_instructors) > 3 else "Dr. Neha Singh",
            "instructor_id": all_instructors[3]["_id"] if len(all_instructors) > 3 else None,
            "category": "DevOps",
            "level": "Intermediate",
            "price": 74.99,
            "duration_hours": 50,
            "rating": 4.8,
            "num_ratings": 820,
            "students_purchased": 240,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "content": [
                {
                    "chapter": "DevOps Fundamentals",
                    "lessons": [
                        {"title": "Infrastructure as Code", "duration": "4 hours"},
                        {"title": "Docker & Containers", "duration": "5 hours"},
                        {"title": "Kubernetes Basics", "duration": "4 hours"}
                    ]
                },
                {
                    "chapter": "CI/CD Pipeline",
                    "lessons": [
                        {"title": "Jenkins & Automation", "duration": "4 hours"},
                        {"title": "Testing & Quality", "duration": "3 hours"},
                        {"title": "Monitoring & Logging", "duration": "3 hours"}
                    ]
                }
            ]
        },
        {
            "title": "Microservices Architecture",
            "description": "Design and build scalable microservices applications",
            "instructor": all_instructors[4]["name"] if len(all_instructors) > 4 else "Prof. Vikram Reddy",
            "instructor_id": all_instructors[4]["_id"] if len(all_instructors) > 4 else None,
            "category": "System Design",
            "level": "Advanced",
            "price": 84.99,
            "duration_hours": 56,
            "rating": 4.9,
            "num_ratings": 1050,
            "students_purchased": 290,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "content": [
                {
                    "chapter": "Microservices Design",
                    "lessons": [
                        {"title": "Service Oriented Architecture", "duration": "4 hours"},
                        {"title": "API Gateway Pattern", "duration": "3 hours"},
                        {"title": "Service Discovery", "duration": "3 hours"}
                    ]
                },
                {
                    "chapter": "Implementation",
                    "lessons": [
                        {"title": "Spring Boot Microservices", "duration": "5 hours"},
                        {"title": "Message Queues", "duration": "4 hours"},
                        {"title": "Distributed Transactions", "duration": "4 hours"}
                    ]
                }
            ]
        },
        {
            "title": "Machine Learning for Beginners",
            "description": "Start your machine learning journey with practical projects",
            "instructor": all_instructors[2]["name"] if len(all_instructors) > 2 else "Dr. Amit Patel",
            "instructor_id": all_instructors[2]["_id"] if len(all_instructors) > 2 else None,
            "category": "AI/ML",
            "level": "Beginner",
            "price": 64.99,
            "duration_hours": 44,
            "rating": 4.8,
            "num_ratings": 1680,
            "students_purchased": 420,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "content": [
                {
                    "chapter": "ML Basics",
                    "lessons": [
                        {"title": "Machine Learning Concepts", "duration": "3 hours"},
                        {"title": "Data Preprocessing", "duration": "3 hours"},
                        {"title": "Supervised Learning", "duration": "3 hours"}
                    ]
                },
                {
                    "chapter": "Tools & Libraries",
                    "lessons": [
                        {"title": "NumPy & Pandas", "duration": "3 hours"},
                        {"title": "Scikit-learn", "duration": "3 hours"},
                        {"title": "First ML Project", "duration": "4 hours"}
                    ]
                }
            ]
        },
        {
            "title": "Deep Learning with TensorFlow",
            "description": "Build neural networks and deep learning models with TensorFlow",
            "instructor": all_instructors[2]["name"] if len(all_instructors) > 2 else "Dr. Amit Patel",
            "instructor_id": all_instructors[2]["_id"] if len(all_instructors) > 2 else None,
            "category": "AI/ML",
            "level": "Advanced",
            "price": 94.99,
            "duration_hours": 65,
            "rating": 4.9,
            "num_ratings": 1240,
            "students_purchased": 340,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "content": [
                {
                    "chapter": "Neural Networks",
                    "lessons": [
                        {"title": "Neural Network Fundamentals", "duration": "4 hours"},
                        {"title": "Backpropagation", "duration": "4 hours"},
                        {"title": "Activation Functions", "duration": "3 hours"}
                    ]
                },
                {
                    "chapter": "TensorFlow & Keras",
                    "lessons": [
                        {"title": "Building with Keras", "duration": "5 hours"},
                        {"title": "CNN Architecture", "duration": "5 hours"},
                        {"title": "Transfer Learning", "duration": "4 hours"}
                    ]
                }
            ]
        },
        {
            "title": "Natural Language Processing (NLP)",
            "description": "Process and analyze text data with NLP techniques",
            "instructor": all_instructors[2]["name"] if len(all_instructors) > 2 else "Dr. Amit Patel",
            "instructor_id": all_instructors[2]["_id"] if len(all_instructors) > 2 else None,
            "category": "AI/ML",
            "level": "Intermediate",
            "price": 79.99,
            "duration_hours": 54,
            "rating": 4.7,
            "num_ratings": 820,
            "students_purchased": 250,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "content": [
                {
                    "chapter": "NLP Fundamentals",
                    "lessons": [
                        {"title": "Text Preprocessing", "duration": "3 hours"},
                        {"title": "Tokenization & Parsing", "duration": "3 hours"},
                        {"title": "Word Embeddings", "duration": "4 hours"}
                    ]
                },
                {
                    "chapter": "Advanced NLP",
                    "lessons": [
                        {"title": "Sentiment Analysis", "duration": "4 hours"},
                        {"title": "Named Entity Recognition", "duration": "3 hours"},
                        {"title": "Transformers & BERT", "duration": "4 hours"}
                    ]
                }
            ]
        },
        {
            "title": "Network Security & Penetration Testing",
            "description": "Learn advanced network security and ethical hacking techniques",
            "instructor": all_instructors[5]["name"] if len(all_instructors) > 5 else "Dr. Ananya Gupta",
            "instructor_id": all_instructors[5]["_id"] if len(all_instructors) > 5 else None,
            "category": "Cybersecurity",
            "level": "Advanced",
            "price": 89.99,
            "duration_hours": 60,
            "rating": 4.8,
            "num_ratings": 650,
            "students_purchased": 180,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "content": [
                {
                    "chapter": "Network Security",
                    "lessons": [
                        {"title": "Network Architecture", "duration": "4 hours"},
                        {"title": "Firewalls & IDS", "duration": "4 hours"},
                        {"title": "VPN & Tunneling", "duration": "3 hours"}
                    ]
                },
                {
                    "chapter": "Penetration Testing",
                    "lessons": [
                        {"title": "Reconnaissance", "duration": "4 hours"},
                        {"title": "Vulnerability Assessment", "duration": "4 hours"},
                        {"title": "Exploitation & Reporting", "duration": "4 hours"}
                    ]
                }
            ]
        },
        {
            "title": "Software Testing & Quality Assurance",
            "description": "Master testing strategies and QA best practices",
            "instructor": all_instructors[0]["name"] if all_instructors else "Dr. Rajesh Kumar",
            "instructor_id": all_instructors[0]["_id"] if all_instructors else None,
            "category": "Programming",
            "level": "Intermediate",
            "price": 59.99,
            "duration_hours": 42,
            "rating": 4.6,
            "num_ratings": 780,
            "students_purchased": 220,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "content": [
                {
                    "chapter": "Testing Fundamentals",
                    "lessons": [
                        {"title": "Testing Methodologies", "duration": "3 hours"},
                        {"title": "Unit Testing", "duration": "3 hours"},
                        {"title": "Integration Testing", "duration": "3 hours"}
                    ]
                },
                {
                    "chapter": "Advanced Testing",
                    "lessons": [
                        {"title": "Automation Testing", "duration": "4 hours"},
                        {"title": "Performance Testing", "duration": "3 hours"},
                        {"title": "CI/CD in Testing", "duration": "3 hours"}
                    ]
                }
            ]
        },
        {
            "title": "Mobile Development with Flutter",
            "description": "Build cross-platform mobile applications with Flutter",
            "instructor": all_instructors[1]["name"] if len(all_instructors) > 1 else "Prof. Priya Sharma",
            "instructor_id": all_instructors[1]["_id"] if len(all_instructors) > 1 else None,
            "category": "Mobile Development",
            "level": "Intermediate",
            "price": 74.99,
            "duration_hours": 56,
            "rating": 4.8,
            "num_ratings": 1120,
            "students_purchased": 310,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "content": [
                {
                    "chapter": "Flutter Basics",
                    "lessons": [
                        {"title": "Dart Language", "duration": "4 hours"},
                        {"title": "Flutter Widgets", "duration": "5 hours"},
                        {"title": "State Management", "duration": "4 hours"}
                    ]
                },
                {
                    "chapter": "Advanced Development",
                    "lessons": [
                        {"title": "Database & Backend", "duration": "4 hours"},
                        {"title": "APIs & Networking", "duration": "3 hours"},
                        {"title": "Publishing Apps", "duration": "3 hours"}
                    ]
                }
            ]
        },
        {
            "title": "iOS Development with Swift",
            "description": "Create native iOS applications using Swift programming language",
            "instructor": all_instructors[1]["name"] if len(all_instructors) > 1 else "Prof. Priya Sharma",
            "instructor_id": all_instructors[1]["_id"] if len(all_instructors) > 1 else None,
            "category": "Mobile Development",
            "level": "Intermediate",
            "price": 79.99,
            "duration_hours": 60,
            "rating": 4.9,
            "num_ratings": 950,
            "students_purchased": 350,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "content": [
                {
                    "chapter": "Swift Fundamentals",
                    "lessons": [
                        {"title": "Swift Basics", "duration": "4 hours"},
                        {"title": "Object-Oriented Programming", "duration": "4 hours"},
                        {"title": "Functional Programming", "duration": "3 hours"}
                    ]
                },
                {
                    "chapter": "iOS Development",
                    "lessons": [
                        {"title": "UIKit & SwiftUI", "duration": "5 hours"},
                        {"title": "Core Data", "duration": "4 hours"},
                        {"title": "App Store Deployment", "duration": "4 hours"}
                    ]
                }
            ]
        },
        {
            "title": "Artificial Intelligence & Expert Systems",
            "description": "Understand AI concepts and build intelligent systems",
            "instructor": all_instructors[2]["name"] if len(all_instructors) > 2 else "Dr. Amit Patel",
            "instructor_id": all_instructors[2]["_id"] if len(all_instructors) > 2 else None,
            "category": "AI/ML",
            "level": "Advanced",
            "price": 99.99,
            "duration_hours": 68,
            "rating": 4.8,
            "num_ratings": 680,
            "students_purchased": 200,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "content": [
                {
                    "chapter": "AI Fundamentals",
                    "lessons": [
                        {"title": "AI Concepts", "duration": "4 hours"},
                        {"title": "Search Algorithms", "duration": "4 hours"},
                        {"title": "Knowledge Representation", "duration": "4 hours"}
                    ]
                },
                {
                    "chapter": "Expert Systems",
                    "lessons": [
                        {"title": "Rule-based Systems", "duration": "4 hours"},
                        {"title": "Inference Engines", "duration": "3 hours"},
                        {"title": "Applications", "duration": "3 hours"}
                    ]
                }
            ]
        },
        {
            "title": "Compiler Design & Language Implementation",
            "description": "Learn compiler theory and build your own programming language",
            "instructor": all_instructors[0]["name"] if all_instructors else "Dr. Rajesh Kumar",
            "instructor_id": all_instructors[0]["_id"] if all_instructors else None,
            "category": "Core CSE",
            "level": "Advanced",
            "price": 89.99,
            "duration_hours": 62,
            "rating": 4.7,
            "num_ratings": 420,
            "students_purchased": 140,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "content": [
                {
                    "chapter": "Compiler Basics",
                    "lessons": [
                        {"title": "Lexical Analysis", "duration": "4 hours"},
                        {"title": "Syntax Analysis", "duration": "5 hours"},
                        {"title": "Semantic Analysis", "duration": "4 hours"}
                    ]
                },
                {
                    "chapter": "Code Generation",
                    "lessons": [
                        {"title": "Intermediate Code", "duration": "4 hours"},
                        {"title": "Code Optimization", "duration": "4 hours"},
                        {"title": "Final Code Generation", "duration": "3 hours"}
                    ]
                }
            ]
        },
        {
            "title": "Distributed Systems & Consensus Algorithms",
            "description": "Master distributed systems design and consensus mechanisms",
            "instructor": all_instructors[4]["name"] if len(all_instructors) > 4 else "Prof. Vikram Reddy",
            "instructor_id": all_instructors[4]["_id"] if len(all_instructors) > 4 else None,
            "category": "System Design",
            "level": "Advanced",
            "price": 94.99,
            "duration_hours": 64,
            "rating": 4.9,
            "num_ratings": 580,
            "students_purchased": 170,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "content": [
                {
                    "chapter": "Distributed Computing",
                    "lessons": [
                        {"title": "Distributed System Models", "duration": "4 hours"},
                        {"title": "Communication Protocols", "duration": "4 hours"},
                        {"title": "Synchronization", "duration": "4 hours"}
                    ]
                },
                {
                    "chapter": "Consensus Algorithms",
                    "lessons": [
                        {"title": "Raft Algorithm", "duration": "4 hours"},
                        {"title": "Byzantine Fault Tolerance", "duration": "4 hours"},
                        {"title": "Applications", "duration": "3 hours"}
                    ]
                }
            ]
        },
        {
            "title": "Quantum Computing Fundamentals",
            "description": "Introduction to quantum computing and quantum algorithms",
            "instructor": all_instructors[2]["name"] if len(all_instructors) > 2 else "Dr. Amit Patel",
            "instructor_id": all_instructors[2]["_id"] if len(all_instructors) > 2 else None,
            "category": "Advanced CSE",
            "level": "Advanced",
            "price": 109.99,
            "duration_hours": 70,
            "rating": 4.8,
            "num_ratings": 320,
            "students_purchased": 95,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "content": [
                {
                    "chapter": "Quantum Basics",
                    "lessons": [
                        {"title": "Quantum Mechanics", "duration": "5 hours"},
                        {"title": "Qubits & Superposition", "duration": "4 hours"},
                        {"title": "Quantum Gates", "duration": "4 hours"}
                    ]
                },
                {
                    "chapter": "Quantum Algorithms",
                    "lessons": [
                        {"title": "Shor's Algorithm", "duration": "4 hours"},
                        {"title": "Grover's Algorithm", "duration": "4 hours"},
                        {"title": "Quantum Programming", "duration": "4 hours"}
                    ]
                }
            ]
        }
    ]
    
    # Insert courses if not already present
    for course in cse_courses_additional:
        if not courses_collection.find_one({"title": course["title"]}):
            courses_collection.insert_one(course)
    
    # Add enrollments for new CSE courses
    all_students = list(students_collection.find())
    cse_category_courses = list(courses_collection.find({
        "category": {
            "$in": ["Advanced CSE", "Cloud Computing", "DevOps", "AI/ML", 
                   "Mobile Development", "Programming"]
        }
    }))
    
    for idx, student in enumerate(all_students):
        # Enroll students in new CSE courses
        num_cse_courses = (idx % 4) + 1
        for i in range(num_cse_courses):
            if len(cse_category_courses) > 0:
                course_idx = (idx + i) % len(cse_category_courses)
                enrollment = {
                    "studentId": student["_id"],
                    "courseId": cse_category_courses[course_idx]["_id"],
                    "email": student["email"],
                    "student_name": student["name"],
                    "enrollment_date": datetime.now(),
                    "completion_status": "in_progress",
                    "progress": (idx * 25) % 100
                }
                # Check if enrollment already exists
                if not enrollments_collection.find_one({
                    "studentId": student["_id"],
                    "courseId": cse_category_courses[course_idx]["_id"]
                }):
                    enrollments_collection.insert_one(enrollment)

# Add design courses automatically
add_design_creative_courses()

# Add CSE courses automatically
add_cse_courses()

# Landing Page
@app.route("/")
def landing():
    return render_template("landing.html")

# User Login
@app.route("/login")
def login_user():
    error = request.args.get('error')
    return render_template("login_user.html", error=error)

@app.route("/login_post", methods=["POST"])
def login_user_post():
    email = request.form.get("email")
    password = request.form.get("password")
    
    # Check demo credentials first
    if email in DEMO_USERS and DEMO_USERS[email] == password:
        session['user_email'] = email
        session['user_type'] = 'user'
        session['user_name'] = 'Ashwani'
        session['user_id'] = "demo_user"
        return redirect(url_for("dashboard_user"))
    
    # Check registered users in MongoDB
    try:
        user = users_collection.find_one({"email": email})
        if user and check_password_hash(user.get('password_hash', ''), password):
            session['user_email'] = email
            session['user_type'] = 'user'
            session['user_name'] = user.get('name', email.split('@')[0].title())
            session['user_id'] = str(user['_id'])
            return redirect(url_for("dashboard_user"))
    except Exception as e:
        print(f"Error checking registered user: {str(e)}")
    
    return redirect(url_for("login_user", error="Invalid credentials"))

# User Registration
@app.route("/register")
def register_user():
    error = request.args.get('error')
    success = request.args.get('success')
    return render_template("register_user.html", error=error, success=success)

@app.route("/register_post", methods=["POST"])
def register_user_post():
    """Register a new user with unique ID"""
    try:
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        
        # Validation
        if not name or not email or not password:
            return redirect(url_for("register_user", error="All fields are required"))
        
        # Email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return redirect(url_for("register_user", error="Invalid email format"))
        
        # Password validation
        if len(password) < 6:
            return redirect(url_for("register_user", error="Password must be at least 6 characters"))
        
        if password != confirm_password:
            return redirect(url_for("register_user", error="Passwords do not match"))
        
        # Check if user already exists
        existing_user = users_collection.find_one({"email": email})
        if existing_user:
            return redirect(url_for("register_user", error="Email already registered"))
        
        # Create new user with unique ID (MongoDB ObjectId)
        user_data = {
            "name": name,
            "email": email,
            "password_hash": generate_password_hash(password),
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "enrolled_courses": [],
            "role": "student",
            "status": "active"
        }
        
        result = users_collection.insert_one(user_data)
        user_id = str(result.inserted_id)
        
        # Log the user in
        session['user_email'] = email
        session['user_type'] = 'user'
        session['user_name'] = name
        session['user_id'] = user_id
        
        return redirect(url_for("dashboard_user"))
        
    except Exception as e:
        error_msg = f"Registration error: {str(e)}"
        print(error_msg)
        return redirect(url_for("register_user", error="An error occurred during registration"))

# Admin Login
@app.route("/admin_login")
def login_admin():
    error = request.args.get('error')
    return render_template("login_admin.html", error=error)

@app.route("/admin_login_post", methods=["POST"])
def login_admin_post():
    admin_id = request.form.get("admin_id")
    password = request.form.get("password")
    
    # Demo authentication
    if admin_id in DEMO_ADMINS and DEMO_ADMINS[admin_id] == password:
        session['admin_id'] = admin_id
        session['user_type'] = 'admin'
        session['admin_name'] = admin_id.title()
        return redirect(url_for("dashboard_admin"))
    else:
        return redirect(url_for("login_admin", error="Invalid credentials"))

# User Dashboard
@app.route("/dashboard")
def dashboard_user():
    if 'user_type' not in session or session['user_type'] != 'user':
        return redirect(url_for("login_user"))
    
    all_courses = list(courses_collection.find())
    user_email = session.get('user_email')
    
    # Get user enrollments
    user_enrollments = list(enrollments_collection.find({"email": user_email}))
    enrolled_course_ids = [ObjectId(e.get('courseId')) if isinstance(e.get('courseId'), str) 
                           else e.get('courseId') for e in user_enrollments]
    
    return render_template("dashboard_user.html", 
                         courses=all_courses,
                         user_name=session.get('user_name', 'Ashwani'),
                         user_initial=session.get('user_name', 'Ashwani')[0],
                         enrolled_count=len(user_enrollments),
                         completed_count=0,
                         in_progress_count=len(all_courses),
                         enrolled_course_ids=enrolled_course_ids,
                         search_query='')

# Admin Dashboard
@app.route("/admin_dashboard")
def dashboard_admin():
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for("login_admin"))
    
    all_courses = list(courses_collection.find())
    all_students = list(students_collection.find())
    all_enrollments = list(enrollments_collection.find())
    
    # Get course popularity report using aggregation
    popularity_pipeline = [
        {"$group": {"_id": "$courseId", "total_enrollments": {"$sum": 1}}},
        {"$sort": {"total_enrollments": -1}},
        {"$limit": 5},
        {
            "$lookup": {
                "from": "courses",
                "localField": "_id",
                "foreignField": "_id",
                "as": "course_details"
            }
        }
    ]
    popular_courses = list(enrollments_collection.aggregate(popularity_pipeline))
    
    # Get students per course
    students_per_course_pipeline = [
        {"$group": {
            "_id": "$courseId",
            "student_count": {"$sum": 1},
            "students": {"$push": "$email"}
        }},
        {"$sort": {"student_count": -1}},
        {
            "$lookup": {
                "from": "courses",
                "localField": "_id",
                "foreignField": "_id",
                "as": "course"
            }
        }
    ]
    students_per_course = list(enrollments_collection.aggregate(students_per_course_pipeline))
    
    # Calculate average rating
    avg_rating = 0
    if all_courses:
        total_rating = sum(float(course.get('rating') or 0) for course in all_courses)
        avg_rating = round(total_rating / len(all_courses), 2)
    
    # Calculate active enrollments (in_progress status)
    active_enrollments = sum(1 for enrollment in all_enrollments if enrollment.get('completion_status') == 'in_progress')
    
    # Get revenue data with rupee formatting
    revenue_pipeline = [
        {
            "$lookup": {
                "from": "courses",
                "localField": "courseId",
                "foreignField": "_id",
                "as": "course"
            }
        },
        {"$unwind": "$course"},
        {
            "$group": {
                "_id": "$courseId",
                "student_count": {"$sum": 1},
                "course_title": {"$first": "$course.title"},
                "price": {"$first": "$course.price"},
                "instructor": {"$first": "$course.instructor"},
                "rating": {"$first": "$course.rating"}
            }
        },
        {
            "$project": {
                "course_title": 1,
                "instructor": 1,
                "student_count": 1,
                "price": 1,
                "rating": 1,
                "revenue": {"$multiply": ["$student_count", "$price"]}
            }
        },
        {"$sort": {"revenue": -1}}
    ]
    revenue_data = list(enrollments_collection.aggregate(revenue_pipeline))
    
    # Clean revenue data - ensure no None values for numeric fields
    cleaned_revenue_data = []
    for item in revenue_data:
        if item:
            item['price'] = item.get('price') or 0
            item['revenue'] = item.get('revenue') or 0
            item['student_count'] = item.get('student_count') or 0
            item['rating'] = item.get('rating') or 0
            cleaned_revenue_data.append(item)
    revenue_data = cleaned_revenue_data
    
    # Calculate total revenue (handle None values)
    total_revenue = sum(item.get('revenue') or 0 for item in revenue_data if item)
    
    # Convert ObjectIds to strings for JSON serialization
    popular_courses = convert_objectid_to_string(popular_courses)
    students_per_course = convert_objectid_to_string(students_per_course)
    revenue_data = convert_objectid_to_string(revenue_data)
    all_courses = convert_objectid_to_string(all_courses)
    
    return render_template("dashboard_admin.html",
                         admin_name=session.get('admin_name', 'Admin'),
                         admin_initial=session.get('admin_name', 'A')[0],
                         courses_count=len(all_courses),
                         total_courses=len(all_courses),
                         total_students=len(all_students),
                         total_enrollments=len(all_enrollments),
                         active_enrollments=active_enrollments,
                         avg_rating=avg_rating,
                         active_users=len(all_students),
                         courses=all_courses,
                         popular_courses=popular_courses,
                         students_per_course=students_per_course,
                         revenue_data=revenue_data,
                         total_revenue=total_revenue)

# API endpoint for dashboard details
@app.route('/api/dashboard/details/<detail_type>')
def get_dashboard_details(detail_type):
    """API endpoint to fetch detailed information for dashboard stat cards"""
    try:
        if detail_type == 'courses':
            # Get all courses with their basic info
            all_courses = list(courses_collection.find({}))
            all_courses = convert_objectid_to_string(all_courses)
            return jsonify({
                'courses': all_courses
            })
        
        elif detail_type == 'students':
            # Get all students
            all_students = list(students_collection.find({}))
            all_students = convert_objectid_to_string(all_students)
            # Count enrollments per student
            for student in all_students:
                enrollments = list(enrollments_collection.find({'studentId': ObjectId(student['_id'])}))
                student['enrollments'] = len(enrollments)
            return jsonify({
                'students': all_students
            })
        
        elif detail_type == 'enrollments':
            # Get active enrollments with course and student details
            all_enrollments = list(enrollments_collection.find({}))
            all_enrollments = convert_objectid_to_string(all_enrollments)
            
            # Enrich with course and student details
            for enrollment in all_enrollments:
                try:
                    course = courses_collection.find_one({'_id': ObjectId(enrollment['courseId'])})
                    student = students_collection.find_one({'_id': ObjectId(enrollment['studentId'])})
                    enrollment['course_title'] = course['title'] if course else 'Unknown'
                    enrollment['student_name'] = student.get('name', student.get('username', 'Unknown')) if student else 'Unknown'
                except:
                    enrollment['course_title'] = 'Unknown'
                    enrollment['student_name'] = 'Unknown'
            
            return jsonify({
                'enrollments': all_enrollments
            })
        
        elif detail_type == 'ratings':
            # Get all courses with their ratings
            all_courses = list(courses_collection.find({}))
            all_courses = convert_objectid_to_string(all_courses)
            
            # Add enrollment count for each course
            for course in all_courses:
                enrollments = list(enrollments_collection.find({'courseId': ObjectId(course['_id'])}))
                course['enrollments'] = len(enrollments)
            
            # Sort by rating
            all_courses = sorted(all_courses, key=lambda x: x.get('rating', 0), reverse=True)
            
            return jsonify({
                'courses': all_courses
            })
        
        elif detail_type == 'revenue':
            # Get revenue breakdown by course
            all_courses = list(courses_collection.find({}))
            all_courses = convert_objectid_to_string(all_courses)
            
            total_revenue = 0
            revenue_breakdown = []
            
            for course in all_courses:
                try:
                    enrollments = list(enrollments_collection.find({'courseId': ObjectId(course['_id'])}))
                    course_revenue = len(enrollments) * (course.get('price', 0) or 0)
                    total_revenue += course_revenue
                    
                    if course_revenue > 0:
                        revenue_breakdown.append({
                            'title': course.get('title', 'Unknown'),
                            'price': course.get('price', 0) or 0,
                            'revenue': course_revenue,
                            'students': len(enrollments)
                        })
                except:
                    pass
            
            # Sort by revenue
            revenue_breakdown = sorted(revenue_breakdown, key=lambda x: x['revenue'], reverse=True)
            
            return jsonify({
                'total_revenue': total_revenue,
                'revenue_breakdown': revenue_breakdown
            })
        
        else:
            return jsonify({'error': 'Invalid detail type'}), 400
    
    except Exception as e:
        print(f"Error fetching details: {e}")
        return jsonify({'error': str(e)}), 500

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))

# Home page (for backward compatibility)
@app.route("/home")
def home():
    all_courses = list(courses.find())
    return render_template("index.html", courses=all_courses)

@app.route("/add_course", methods=["POST"])
def add_course():
    """CREATE - Add new course with embedded content"""
    if 'user_type' not in session or session['user_type'] != 'admin':
        return redirect(url_for("login_admin"))
    
    try:
        title = request.form.get("title")
        description = request.form.get("description")
        instructor_name = request.form.get("instructor")
        category = request.form.get("category", "General")
        level = request.form.get("level", "Beginner")
        price = float(request.form.get("price", 99.99))
        duration = float(request.form.get("duration", 30))
        
        # Find or create instructor
        instructor = instructors_collection.find_one({"name": instructor_name})
        if not instructor:
            instructor_data = {
                "name": instructor_name,
                "bio": f"Instructor of {title}",
                "expertise": [category],
                "rating": 4.5
            }
            result = instructors_collection.insert_one(instructor_data)
            instructor_id = result.inserted_id
        else:
            instructor_id = instructor["_id"]
        
        course = {
            "title": title,
            "description": description,
            "instructor": instructor_name,
            "instructor_id": instructor_id,
            "category": category,
            "level": level,
            "price": price,
            "duration_hours": duration,
            "rating": 0.0,
            "num_ratings": 0,
            "students_purchased": 0,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "content": [
                {
                    "chapter": "Course Introduction",
                    "lessons": [
                        {"title": "Welcome", "duration": "1 hour"},
                        {"title": "Course Overview", "duration": "1 hour"}
                    ]
                },
                {
                    "chapter": "Main Content",
                    "lessons": [
                        {"title": "Core Concepts", "duration": f"{duration - 4} hours"}
                    ]
                },
                {
                    "chapter": "Projects & Conclusion",
                    "lessons": [
                        {"title": "Capstone Project", "duration": "2 hours"},
                        {"title": "Wrap Up", "duration": "1 hour"}
                    ]
                }
            ]
        }
        
        result = courses_collection.insert_one(course)
        return redirect(url_for("dashboard_admin"))
    except Exception as e:
        print(f"Error adding course: {str(e)}")
        return redirect(url_for("dashboard_admin"))

@app.route("/enroll", methods=["POST"])
def enroll():
    """Enroll student in course with tracking"""
    try:
        student_name = request.form.get("name")
        email = request.form.get("email")
        course_id = request.form.get("course_id")
        
        # Check if student already enrolled
        existing_enrollment = enrollments_collection.find_one({
            "email": email,
            "courseId": ObjectId(course_id)
        })
        
        if existing_enrollment:
            if 'user_type' in session and session['user_type'] == 'user':
                return redirect(url_for("dashboard_user"))
            return redirect(url_for("landing"))
        
        # Create/Update student
        student = students_collection.find_one({"email": email})
        if not student:
            student_result = students_collection.insert_one({
                "name": student_name,
                "email": email,
                "enrolled_courses": [],
                "enrollment_date": datetime.now()
            })
            student_id = student_result.inserted_id
        else:
            student_id = student["_id"]
        
        # Add enrollment
        enrollment = {
            "studentId": student_id,
            "courseId": ObjectId(course_id),
            "email": email,
            "student_name": student_name,
            "enrollment_date": datetime.now(),
            "completion_status": "in_progress",
            "progress": 0
        }
        
        enrollments_collection.insert_one(enrollment)
        
        # Update student's enrolled courses
        students_collection.update_one(
            {"_id": student_id},
            {"$push": {"enrolled_courses": ObjectId(course_id)}}
        )
        
        # Increment students_purchased counter
        courses_collection.update_one(
            {"_id": ObjectId(course_id)},
            {"$inc": {"students_purchased": 1}}
        )
        
        if 'user_type' in session and session['user_type'] == 'user':
            return redirect(url_for("dashboard_user"))
        else:
            return redirect(url_for("landing"))
    except Exception as e:
        print(f"Error in enrollment: {str(e)}")
        return redirect(url_for("landing"))

@app.route("/search")
def search():
    """Full-text search across courses"""
    query = request.args.get("q", "").strip()
    
    if not query:
        results = []
    else:
        # Text search using text index
        results = list(courses_collection.find(
            {"$text": {"$search": query}},
            {"score": {"$meta": "textScore"}}
        ).sort([("score", {"$meta": "textScore"})]))
    
    if 'user_type' in session and session['user_type'] == 'user':
        user_enrollments = list(enrollments_collection.find({"email": session.get('user_email')}))
        enrolled_course_ids = [ObjectId(e.get('courseId')) if isinstance(e.get('courseId'), str) 
                               else e.get('courseId') for e in user_enrollments]
        
        return render_template("dashboard_user.html", 
                             courses=results,
                             user_name=session.get('user_name', 'Ashwani'),
                             user_initial=session.get('user_name', 'Ashwani')[0],
                             enrolled_count=len(user_enrollments),
                             completed_count=0,
                             in_progress_count=len(results),
                             enrolled_course_ids=enrolled_course_ids,
                             search_query=query)
    else:
        return render_template("index.html", courses=results, search_query=query)

def convert_objectid_to_string(obj):
    """Recursively convert ObjectId objects to strings for JSON serialization"""
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: convert_objectid_to_string(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectid_to_string(item) for item in obj]
    else:
        return obj

@app.route("/report")
def report():
    """Display comprehensive course popularity report"""
    # Get all courses
    all_courses = list(courses_collection.find())
    
    # Most popular courses
    popular_pipeline = [
        {"$group": {"_id": "$courseId", "totalStudents": {"$sum": 1}}},
        {"$sort": {"totalStudents": -1}},
        {
            "$lookup": {
                "from": "courses",
                "localField": "_id",
                "foreignField": "_id",
                "as": "course"
            }
        },
        {"$unwind": "$course"},
        {
            "$project": {
                "_id": "$course._id",
                "title": "$course.title",
                "instructor": "$course.instructor",
                "category": "$course.category",
                "totalStudents": 1,
                "rating": "$course.rating"
            }
        }
    ]
    
    # Revenue analysis
    revenue_pipeline = [
        {
            "$lookup": {
                "from": "courses",
                "localField": "courseId",
                "foreignField": "_id",
                "as": "course"
            }
        },
        {"$unwind": "$course"},
        {
            "$group": {
                "_id": "$courseId",
                "student_count": {"$sum": 1},
                "course_title": {"$first": "$course.title"},
                "price": {"$first": "$course.price"},
                "instructor": {"$first": "$course.instructor"},
                "rating": {"$first": "$course.rating"}
            }
        },
        {
            "$project": {
                "course_title": 1,
                "instructor": 1,
                "student_count": 1,
                "price": 1,
                "rating": 1,
                "revenue": {"$multiply": ["$student_count", "$price"]}
            }
        },
        {"$sort": {"revenue": -1}}
    ]
    
    # Students per course
    students_per_course_pipeline = [
        {"$group": {
            "_id": "$courseId",
            "student_count": {"$sum": 1},
            "students": {"$push": "$email"}
        }},
        {"$sort": {"student_count": -1}},
        {
            "$lookup": {
                "from": "courses",
                "localField": "_id",
                "foreignField": "_id",
                "as": "course"
            }
        }
    ]
    
    popular_data = list(enrollments_collection.aggregate(popular_pipeline))
    revenue_data = list(enrollments_collection.aggregate(revenue_pipeline))
    students_per_course = list(enrollments_collection.aggregate(students_per_course_pipeline))
    
    # Clean revenue data - ensure no None values for numeric fields
    cleaned_revenue_data = []
    for item in revenue_data:
        if item:
            item['price'] = item.get('price') or 0
            item['revenue'] = item.get('revenue') or 0
            item['student_count'] = item.get('student_count') or 0
            item['rating'] = item.get('rating') or 0
            cleaned_revenue_data.append(item)
    revenue_data = cleaned_revenue_data
    
    # Calculate total students and revenue
    total_students = sum(course.get('totalStudents', 0) for course in popular_data)
    total_revenue = sum(item.get('revenue') or 0 for item in revenue_data if item)
    
    # Convert ObjectIds to strings for JSON serialization
    popular_data = convert_objectid_to_string(popular_data)
    revenue_data = convert_objectid_to_string(revenue_data)
    students_per_course = convert_objectid_to_string(students_per_course)
    all_courses = convert_objectid_to_string(all_courses)
    
    return render_template("report.html", 
                         data=popular_data,
                         revenue_data=revenue_data,
                         students_per_course=students_per_course,
                         courses=all_courses,
                         total_students=total_students,
                         total_revenue=total_revenue)

# ============================================================================
# ANALYTICS & REPORTS - Aggregation Pipelines & API Endpoints
# ============================================================================

@app.route("/api/analytics/popular-courses")
def api_popular_courses():
    """API: Get most popular courses (based on students purchased)"""
    pipeline = [
        {"$sort": {"students_purchased": -1}},
        {"$limit": 10},
        {
            "$project": {
                "_id": 1,
                "course_id": "$_id",
                "course_name": "$title",
                "instructor": 1,
                "category": 1,
                "students_purchased": 1,
                "price": 1,
                "rating": 1,
                "duration_hours": 1,
                "level": 1
            }
        }
    ]
    
    results = list(courses_collection.aggregate(pipeline))
    
    # Convert ObjectId to string
    for result in results:
        result['course_id'] = str(result['_id'])
        del result['_id']
    
    return jsonify(results)

@app.route("/api/analytics/students-per-course")
def api_students_per_course():
    """API: Get student count and details per course (Aggregation: Group by course)"""
    pipeline = [
        {"$group": {
            "_id": "$courseId",
            "student_count": {"$sum": 1},
            "students": {"$push": {
                "name": "$student_name",
                "email": "$email",
                "enrollment_date": "$enrollment_date"
            }}
        }},
        {"$sort": {"student_count": -1}},
        {
            "$lookup": {
                "from": "courses",
                "localField": "_id",
                "foreignField": "_id",
                "as": "course"
            }
        },
        {"$unwind": "$course"},
        {
            "$project": {
                "_id": 0,
                "course_id": "$_id",
                "course_title": "$course.title",
                "course_category": "$course.category",
                "student_count": 1,
                "students": {"$slice": ["$students", 5]}
            }
        }
    ]
    
    results = list(enrollments_collection.aggregate(pipeline))
    return jsonify(results)

@app.route("/api/analytics/course-statistics")
def api_course_statistics():
    """API: Comprehensive course statistics"""
    pipeline = [
        {
            "$lookup": {
                "from": "enrollments",
                "localField": "_id",
                "foreignField": "courseId",
                "as": "enrollments"
            }
        },
        {
            "$project": {
                "title": 1,
                "category": 1,
                "level": 1,
                "instructor": 1,
                "price": 1,
                "rating": 1,
                "duration_hours": 1,
                "total_enrollments": {"$size": "$enrollments"},
                "revenue": {
                    "$multiply": [{"$size": "$enrollments"}, "$price"]
                },
                "avg_price_per_student": {
                    "$cond": [
                        {"$eq": [{"$size": "$enrollments"}, 0]},
                        0,
                        {"$divide": [{"$multiply": [{"$size": "$enrollments"}, "$price"]}, {"$size": "$enrollments"}]}
                    ]
                }
            }
        },
        {"$sort": {"total_enrollments": -1}}
    ]
    
    results = list(courses_collection.aggregate(pipeline))
    for result in results:
        result['_id'] = str(result['_id'])
        # Add formatted rupee values
        result['revenue_inr'] = f"₹{result['revenue']:,.2f}"
        result['price_inr'] = f"₹{result['price']:,.2f}"
    
    return jsonify(results)

@app.route("/api/analytics/instructor-performance")
def api_instructor_performance():
    """API: Instructor performance metrics (Aggregation: Group by instructor)"""
    pipeline = [
        {
            "$lookup": {
                "from": "enrollments",
                "localField": "_id",
                "foreignField": "courseId",
                "as": "enrollments"
            }
        },
        {
            "$group": {
                "_id": "$instructor",
                "total_courses": {"$sum": 1},
                "total_students": {
                    "$sum": {"$size": "$enrollments"}
                },
                "avg_rating": {"$avg": "$rating"},
                "total_revenue": {
                    "$sum": {
                        "$multiply": [{"$size": "$enrollments"}, "$price"]
                    }
                }
            }
        },
        {"$sort": {"total_students": -1}},
        {
            "$project": {
                "_id": 0,
                "instructor": "$_id",
                "total_courses": 1,
                "total_students": 1,
                "avg_rating": {"$round": ["$avg_rating", 2]},
                "total_revenue": {"$round": ["$total_revenue", 2]}
            }
        }
    ]
    
    results = list(courses_collection.aggregate(pipeline))
    
    # Add formatted values
    for result in results:
        result['total_revenue_inr'] = f"₹{result['total_revenue']:,.2f}"
    
    return jsonify(results)

@app.route("/api/analytics/enrollment-trends")
def api_enrollment_trends():
    """API: Enrollment trends over time"""
    pipeline = [
        {
            "$group": {
                "_id": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": "$enrollment_date"
                    }
                },
                "daily_enrollments": {"$sum": 1}
            }
        },
        {"$sort": {"_id": 1}},
        {
            "$project": {
                "_id": 0,
                "date": "$_id",
                "enrollments": "$daily_enrollments"
            }
        }
    ]
    
    results = list(enrollments_collection.aggregate(pipeline))
    return jsonify(results)

@app.route("/api/analytics/course-popularity")
def api_course_popularity():
    """API: Most popular course (Aggregation: Find course with most enrollments)"""
    pipeline = [
        {"$group": {
            "_id": "$courseId",
            "enrollment_count": {"$sum": 1}
        }},
        {"$sort": {"enrollment_count": -1}},
        {"$limit": 1},
        {
            "$lookup": {
                "from": "courses",
                "localField": "_id",
                "foreignField": "_id",
                "as": "course"
            }
        },
        {"$unwind": "$course"},
        {
            "$project": {
                "_id": 0,
                "course_id": "$_id",
                "course_title": "$course.title",
                "instructor": "$course.instructor",
                "category": "$course.category",
                "enrollment_count": 1,
                "price": "$course.price",
                "rating": "$course.rating",
                "duration": "$course.duration_hours"
            }
        }
    ]
    
    result = list(enrollments_collection.aggregate(pipeline))
    return jsonify(result[0] if result else {})

# ============================================================================
# ADDITIONAL CRUD OPERATIONS
# ============================================================================

@app.route("/update_course/<course_id>", methods=["POST"])
def update_course(course_id):
    """UPDATE - Modify existing course"""
    if 'user_type' not in session or session['user_type'] != 'admin':
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        course_data = {
            "title": request.form.get("title"),
            "description": request.form.get("description"),
            "price": float(request.form.get("price", 0)),
            "level": request.form.get("level"),
            "updated_at": datetime.now()
        }
        
        result = courses_collection.update_one(
            {"_id": ObjectId(course_id)},
            {"$set": course_data}
        )
        
        return jsonify({"success": True, "modified_count": result.modified_count})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/delete_course/<course_id>", methods=["POST"])
def delete_course(course_id):
    """DELETE - Remove course"""
    if 'user_type' not in session or session['user_type'] != 'admin':
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        # Delete all enrollments for this course
        enrollments_collection.delete_many({"courseId": ObjectId(course_id)})
        
        # Delete the course
        result = courses_collection.delete_one({"_id": ObjectId(course_id)})
        
        return jsonify({"success": True, "deleted_count": result.deleted_count})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get_course/<course_id>")
def get_course(course_id):
    """READ - Get course details as JSON"""
    try:
        course = courses_collection.find_one({"_id": ObjectId(course_id)})
        if course:
            course['_id'] = str(course['_id'])
            course['instructor_id'] = str(course.get('instructor_id', ''))
            return jsonify(course)
        return jsonify({"error": "Course not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/course/<course_id>")
def course_detail(course_id):
    """Display detailed course information with content"""
    try:
        course = courses_collection.find_one({"_id": ObjectId(course_id)})
        if not course:
            return "Course not found", 404
        
        # Get enrollment count using aggregation
        enrollment_stats = list(enrollments_collection.aggregate([
            {"$match": {"courseId": ObjectId(course_id)}},
            {"$group": {"_id": None, "total_enrollments": {"$sum": 1}}}
        ]))
        
        total_enrollments = enrollment_stats[0]['total_enrollments'] if enrollment_stats else 0
        
        return render_template("course_detail.html", 
                             course=course,
                             total_enrollments=total_enrollments,
                             user_name=session.get('user_name', 'Ashwani'))
    except Exception as e:
        return f"Error: {str(e)}", 500

# ============================================================================
# COURSE SEARCH BY ID & POPULAR COURSES
# ============================================================================

@app.route("/api/course/<course_id>")
def api_course_by_id(course_id):
    """API: Get course details by ID with embedded content"""
    try:
        # Try to convert to ObjectId, if it fails check if it's a string ID
        try:
            course = courses_collection.find_one({"_id": ObjectId(course_id)})
        except:
            # Fallback: try searching by string field if needed
            course = courses_collection.find_one({"_id": course_id})
        
        if course:
            course['_id'] = str(course['_id'])
            course['instructor_id'] = str(course.get('instructor_id', ''))
            return jsonify(course)
        return jsonify({"error": "Course not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/popular-courses")
def popular_courses_page():
    """Display most popular courses based on student purchases"""
    try:
        # Get popular courses
        popular_pipeline = [
            {"$sort": {"students_purchased": -1}},
            {"$limit": 10},
            {
                "$project": {
                    "_id": 1,
                    "title": 1,
                    "instructor": 1,
                    "category": 1,
                    "price": 1,
                    "rating": 1,
                    "students_purchased": 1,
                    "duration_hours": 1,
                    "level": 1,
                    "description": 1
                }
            }
        ]
        
        popular = list(courses_collection.aggregate(popular_pipeline))
        
        # Calculate stats
        total_students = sum(course.get('students_purchased', 0) for course in popular)
        avg_rating = sum(course.get('rating', 0) for course in popular) / len(popular) if popular else 0
        
        if 'user_type' in session and session['user_type'] == 'user':
            user_enrollments = list(enrollments_collection.find({"email": session.get('user_email')}))
            enrolled_course_ids = [ObjectId(e.get('courseId')) if isinstance(e.get('courseId'), str) 
                                   else e.get('courseId') for e in user_enrollments]
            enrolled_ids = [str(id) for id in enrolled_course_ids]
        else:
            enrolled_ids = []
        
        return render_template("popular_courses.html",
                             popular_courses=popular,
                             total_students=total_students,
                             avg_rating=round(avg_rating, 2),
                             enrolled_ids=enrolled_ids,
                             user_name=session.get('user_name', 'Ashwani'))
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route("/api/popular-courses/search")
def api_popular_courses_search():
    """API: Search for course by ID and show in popularity context"""
    course_id = request.args.get('course_id', '').strip()
    
    if not course_id:
        return jsonify({"error": "Course ID is required"}), 400
    
    try:
        # Get the specific course
        course = courses_collection.find_one({"_id": ObjectId(course_id)})
        if not course:
            return jsonify({"error": "Course not found"}), 404
        
        # Get all courses sorted by popularity to show ranking
        all_popular = list(courses_collection.find(
            {},
            {"_id": 1, "title": 1, "students_purchased": 1, "instructor": 1}
        ).sort("students_purchased", -1))
        
        # Find the rank of the searched course
        rank = next((i + 1 for i, c in enumerate(all_popular) if str(c['_id']) == course_id), None)
        
        course['_id'] = str(course['_id'])
        course['instructor_id'] = str(course.get('instructor_id', ''))
        course['popularity_rank'] = rank
        course['total_courses'] = len(all_popular)
        
        return jsonify(course)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================================================
# USER MANAGEMENT ENDPOINTS
# ============================================================================

@app.route("/api/user/<user_id>")
def api_get_user(user_id):
    """API: Get user details by ID"""
    try:
        # Check if user is authenticated
        if 'user_type' not in session or session['user_type'] != 'user':
            return jsonify({"error": "Unauthorized"}), 401
        
        # Users can only view their own profile or admins can view any
        if session.get('user_id') != user_id and session.get('user_type') != 'admin':
            return jsonify({"error": "Forbidden"}), 403
        
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Remove sensitive data
        user['_id'] = str(user['_id'])
        del user['password_hash']
        
        return jsonify(user)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/users")
def api_list_users():
    """API: Get all users (Admin only)"""
    try:
        if 'user_type' not in session or session['user_type'] != 'admin':
            return jsonify({"error": "Unauthorized"}), 401
        
        users = list(users_collection.find(
            {},
            {"name": 1, "email": 1, "created_at": 1, "status": 1, "_id": 1}
        ))
        
        for user in users:
            user['_id'] = str(user['_id'])
            user['user_id'] = user.pop('_id')
        
        return jsonify(users)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/user/<user_id>/profile", methods=["GET", "POST"])
def api_user_profile(user_id):
    """API: Get or update user profile"""
    try:
        if request.method == "GET":
            user = users_collection.find_one({"_id": ObjectId(user_id)})
            if not user:
                return jsonify({"error": "User not found"}), 404
            
            user['_id'] = str(user['_id'])
            del user['password_hash']
            return jsonify(user)
        
        elif request.method == "POST":
            if 'user_type' not in session or session['user_type'] != 'user':
                return jsonify({"error": "Unauthorized"}), 401
            
            if session.get('user_id') != user_id:
                return jsonify({"error": "Forbidden"}), 403
            
            update_data = {
                "name": request.form.get("name"),
                "updated_at": datetime.now()
            }
            
            result = users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
            
            return jsonify({"success": True, "modified_count": result.modified_count})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/user/profile")
def user_profile():
    """Display user profile page"""
    if 'user_type' not in session or session['user_type'] != 'user':
        return redirect(url_for("login_user"))
    
    try:
        user = users_collection.find_one({"_id": ObjectId(session.get('user_id'))})
        if not user:
            return redirect(url_for("login_user"))
        
        # Get enrolled courses
        enrolled_ids = user.get('enrolled_courses', [])
        enrolled_courses = list(courses_collection.find({"_id": {"$in": enrolled_ids}}))
        
        return render_template("user_profile.html",
                             user=user,
                             user_id=str(user['_id']),
                             enrolled_courses=enrolled_courses,
                             enrolled_count=len(enrolled_courses))
    except Exception as e:
        return f"Error: {str(e)}", 500

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return "Page not found", 404

@app.errorhandler(500)
def server_error(error):
    return "Server error", 500
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)