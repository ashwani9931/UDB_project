# CourseHub – Elevating the Online Learning Experience

 **Live Demo:** https://udb-project.onrender.com

Empowering educators and inspiring students through a seamless digital classroom.

---

## Project Overview

CourseHub is more than just a course manager; it’s a comprehensive full-stack ecosystem built to replicate the robust functionality of platforms like Udemy.

In a world where digital education is the new standard, CourseHub bridges the gap between complex data management and a clean, intuitive user interface.

Whether you are:
- an **Administrator** needing high-level analytics to drive revenue, or  
- a **Student** looking for your next career-changing skill  

CourseHub provides a centralized platform that feels natural and fast.

---

## Features

### The Admin Command Center

Data is only useful if it's readable. The Admin Dashboard provides a bird's-eye view of the entire platform.

- **Real-time Analytics:** View total student counts, active enrollments, and gross revenue  
- **Content Control:** Interface to onboard instructors and manage course material  
- **Trend Analysis:** Identify best-selling courses using automated insights  
- **Financial Breakdown:** Analyze revenue generated per course  

---

### The Learner’s Journey

Designed to minimize friction so students focus on learning.

- **Smart Discovery:** Search courses by title, topic, or instructor  
- **Progress Tracking:** Track "In-Progress" and "Completed" courses  
- **Seamless Enrollment:** One-click access to start learning  

---

## Tech Stack

| Layer       | Technology          | Why Used |
|------------|-------------------|---------|
| Backend     | Python (Flask)     | Lightweight and fast for REST APIs |
| Database    | MongoDB Atlas      | Flexible NoSQL document structure |
| Frontend    | HTML5, CSS3, JS    | Responsive design without heavy frameworks |
| Integration | PyMongo            | Efficient MongoDB connectivity |
| Hosting     | Render             | Scalable cloud deployment |

---

## Database Architecture

CourseHub leverages a NoSQL design for flexibility and performance.

### Key Concepts

- **Embedded Documents:** Course modules and lessons stored within course documents  
- **Aggregation Pipelines:** Used for analytics like revenue-per-course  
- **Full-Text Indexing:** Enables fast and scalable search functionality  

**Developer Note:** MongoDB Atlas allows focus on application logic instead of infrastructure management.

---

## Installation (Local Setup)

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/UDB_project.git
cd UDB_project
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file or export your MongoDB URI:
```bash
export MONGO_URI="your_mongodb_atlas_connection_string"
```

### 4. Run the Application
```bash
python app.py
```

Open your browser and go to:
http://localhost:5000

---

## Roadmap

- [ ] Secure Authentication (JWT, OAuth)  
- [ ] Payment Integration (Stripe)  
- [ ] AI Tutor for personalized recommendations  
- [ ] Live Streaming for real-time classes  

---

## Team

- **Ashwani Kumar** – Backend & Deployment  
- **Bidita** – UI/UX Design  
- **Sudhanshu** – Database Architecture  
- **Ritam** – Testing & Quality Assurance  

---
## Access Full Content
   ## Presentation Video
   ## PPT Slides
   ## project doc
    **Live Demo:** https://drive.google.com/drive/folders/1KCSs2nPt6tuP9WCjo7F8wdl5AzC-Q5cY?usp=sharing
## Support

If you find this project useful or learned something from it, consider giving it a star on GitHub.

---

Created by the CourseHub Team
