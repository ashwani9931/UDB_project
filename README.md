# 🎓 CourseHub – Online Course Platform 

 **Live Demo:** https://udb-project.onrender.com

---

##  Project Overview

**CourseHub** is a full-stack web application designed to manage online courses, instructors, and student enrollments — similar to platforms like Udemy.

It provides both **Admin Dashboard** and **User Dashboard**, enabling seamless course management and learning experience.

---

##  Features

###  Admin Dashboard

* View analytics (total courses, students, enrollments, revenue)
* Course popularity insights
* Manage courses and instructors
*  Revenue analysis by course

---

###  User Dashboard

*  Browse available courses
*  Enroll in courses
*  Track progress (in-progress, completed)
* Search courses by title, topic, or instructor

---

###  Course Management

*  Add new courses
*  Course details (title, description, instructor)
*  Embedded course content structure

---

###  Data & Analytics

*  Number of students per course
*  Most popular courses
*  Revenue per course
*  Aggregation queries using MongoDB

---

###  Search Functionality

*  Full-text search using MongoDB text index
* Fast and efficient course discovery

---

##  Tech Stack

###  Backend

* Python (Flask)
* MongoDB Atlas (Cloud Database)
* PyMongo

###  Frontend

* HTML, CSS, JavaScript
* Modern UI with dashboard design

### Deployment

* Render (Backend Hosting)
* MongoDB Atlas (Database)

---

##  Database Design

Collections used:

* `courses`
* `students`
* `enrollments`
* `instructors`

###  Key Concepts

* Embedded documents for course content
* Aggregation pipelines for analytics
* Indexing for search optimization

---

##  Installation (Local Setup)

```bash
git clone https://github.com/your-username/UDB_project.git
cd UDB_project

pip install -r requirements.txt
```

###  Set Environment Variable

```bash
MONGO_URI=your_mongodb_atlas_url
```

###  Run App

```bash
python app.py
```

---

##  Deployment

The project is deployed using:

* Backend: Render
* Database: MongoDB Atlas

Live URL:
 https://udb-project.onrender.com

---

##  Screenshots

###  Landing Page

* Modern UI with call-to-action

### Admin Dashboard

* Analytics + charts

###  Courses Page

* List of available courses

###  User Dashboard

* Personalized learning stats

---

##  Key Functionalities Implemented

✔ Course creation & management
✔ Student enrollment system
✔ Aggregation queries (analytics)
✔ MongoDB indexing (search)
✔ Dashboard visualization
✔ Full-stack deployment

---

##  Future Improvements

*  Authentication (JWT / OAuth)
*  Payment integration
*  Mobile responsiveness
*  Video streaming support
*  AI course recommendations

---

##  Author

## Team Members

This project was developed collaboratively by:

*  **Ashwani Kumar** – Backend Development & Deployment
*  **Bidita** – UI/UX & Frontend Design
*  **Sudhanshu** – Database Design & Integration
*  **Ritam** – Testing & Analytics

---


---

##  If you like this project

Give it a star on GitHub and share it!

---
