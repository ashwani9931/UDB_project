# MongoDB Shell Commands - CourseHub Database Testing

## Database & Collection Info

```javascript
// Connect to database
use course_platform

// List all collections
show collections

// Get collection statistics
db.courses.stats()
db.students.stats()
db.enrollments.stats()
db.instructors.stats()
```

---

## SCHEMA EXAMPLES

### View Course Document
```javascript
// Get a sample course with embedded content
db.courses.findOne()

// Result shows:
{
  "_id": ObjectId("..."),
  "title": "Complete Python Web Development Bootcamp",
  "description": "Learn to build professional web applications",
  "instructor": "Dr. John Smith",
  "category": "Web Development",
  "level": "Beginner",
  "price": 89.99,
  "duration_hours": 40,
  "rating": 4.8,
  "content": [
    {
      "topic": "Python Fundamentals",
      "modules": [
        {"module_name": "Variables and Data Types", "duration": 2},
        {"module_name": "Control Flow", "duration": 3}
      ]
    }
  ]
}
```

### View Student Document
```javascript
db.students.findOne()

// Result:
{
  "_id": ObjectId("..."),
  "name": "John Doe",
  "email": "john@example.com",
  "enrolled_courses": [ObjectId("..."), ObjectId("...")],
  "enrollment_date": ISODate("2026-03-30T...")
}
```

### View Enrollment Document
```javascript
db.enrollments.findOne()

// Result:
{
  "_id": ObjectId("..."),
  "studentId": ObjectId("..."),
  "courseId": ObjectId("..."),
  "email": "john@example.com",
  "student_name": "John Doe",
  "enrollment_date": ISODate("2026-03-30T..."),
  "completion_status": "in_progress",
  "progress": 0
}
```

---

## CRUD OPERATIONS

### CREATE - Insert Course
```javascript
db.courses.insertOne({
  "title": "Advanced React",
  "description": "Master React hooks and state management",
  "instructor": "Sarah Chen",
  "category": "Web Development",
  "level": "Advanced",
  "price": 129.99,
  "duration_hours": 50,
  "rating": 0,
  "num_ratings": 0,
  "created_at": new Date(),
  "updated_at": new Date(),
  "content": [
    {
      "topic": "React Basics",
      "modules": [
        {"module_name": "Components", "duration": 3},
        {"module_name": "Hooks", "duration": 3}
      ]
    }
  ]
})
```

### READ - Find Courses
```javascript
// Find all courses
db.courses.find()

// Find specific course
db.courses.findOne({"title": "Python Web Development Bootcamp"})

// Find by category
db.courses.find({"category": "Web Development"})

// Find by level
db.courses.find({"level": "Intermediate"})

// Find by price range
db.courses.find({"price": {$gte: 100, $lte: 150}})

// Count courses
db.courses.countDocuments()
```

### UPDATE - Modify Course
```javascript
// Update single field
db.courses.updateOne(
  {"title": "Python Web Development Bootcamp"},
  {$set: {"price": 79.99}}
)

// Update multiple fields
db.courses.updateOne(
  {"_id": ObjectId("...")},
  {$set: {
    "rating": 4.9,
    "num_ratings": 2500,
    "updated_at": new Date()
  }}
)

// Update students per course
db.enrollments.updateOne(
  {"_id": ObjectId("...")},
  {$set: {"progress": 50}}
)
```

### DELETE - Remove Course
```javascript
// Delete single course
db.courses.deleteOne({"_id": ObjectId("...")})

// Delete all enrollments for a course
db.enrollments.deleteMany({"courseId": ObjectId("...")})

// Delete entire collection
db.courses.deleteMany({})
```

---

## AGGREGATION PIPELINES

### 1. Most Popular Courses
```javascript
db.enrollments.aggregate([
  {
    $group: {
      _id: "$courseId",
      total_students: {$sum: 1}
    }
  },
  {$sort: {total_students: -1}},
  {$limit: 10},
  {
    $lookup: {
      from: "courses",
      localField: "_id",
      foreignField: "_id",
      as: "course_info"
    }
  },
  {$unwind: "$course_info"},
  {
    $project: {
      _id: 0,
      course_id: "$_id",
      course_name: "$course_info.title",
      instructor: "$course_info.instructor",
      total_students: 1,
      price: "$course_info.price",
      rating: "$course_info.rating"
    }
  }
])
```

### 2. Students Per Course (with details)
```javascript
db.enrollments.aggregate([
  {
    $group: {
      _id: "$courseId",
      student_count: {$sum: 1},
      students: {
        $push: {
          name: "$student_name",
          email: "$email",
          enrollment_date: "$enrollment_date"
        }
      }
    }
  },
  {$sort: {student_count: -1}},
  {
    $lookup: {
      from: "courses",
      localField: "_id",
      foreignField: "_id",
      as: "course"
    }
  },
  {$unwind: "$course"},
  {
    $project: {
      _id: 0,
      course_title: "$course.title",
      student_count: 1,
      students: {$slice: ["$students", 5]}
    }
  }
])
```

### 3. Course Statistics (Revenue, etc.)
```javascript
db.courses.aggregate([
  {
    $lookup: {
      from: "enrollments",
      localField: "_id",
      foreignField: "courseId",
      as: "enrollments"
    }
  },
  {
    $project: {
      title: 1,
      category: 1,
      price: 1,
      rating: 1,
      total_enrollments: {$size: "$enrollments"},
      revenue: {$multiply: [{$size: "$enrollments"}, "$price"]},
      potential_revenue: {$multiply: [{$size: "$enrollments"}, "$price"]}
    }
  },
  {$sort: {revenue: -1}}
])
```

### 4. Most Popular Single Course
```javascript
db.enrollments.aggregate([
  {
    $group: {
      _id: "$courseId",
      enrollment_count: {$sum: 1}
    }
  },
  {$sort: {enrollment_count: -1}},
  {$limit: 1},
  {
    $lookup: {
      from: "courses",
      localField: "_id",
      foreignField: "_id",
      as: "course"
    }
  },
  {$unwind: "$course"},
  {
    $project: {
      _id: 0,
      course_title: "$course.title",
      instructor: "$course.instructor",
      category: "$course.category",
      enrollment_count: 1,
      price: "$course.price"
    }
  }
])
```

### 5. Instructor Performance Metrics
```javascript
db.courses.aggregate([
  {
    $lookup: {
      from: "enrollments",
      localField: "_id",
      foreignField: "courseId",
      as: "enrollments"
    }
  },
  {
    $group: {
      _id: "$instructor",
      total_courses: {$sum: 1},
      total_students: {$sum: {$size: "$enrollments"}},
      avg_rating: {$avg: "$rating"},
      total_revenue: {$sum: {$multiply: [{$size: "$enrollments"}, "$price"]}}
    }
  },
  {$sort: {total_students: -1}},
  {
    $project: {
      _id: 0,
      instructor: "$_id",
      total_courses: 1,
      total_students: 1,
      avg_rating: {$round: ["$avg_rating", 2]},
      total_revenue: {$round: ["$total_revenue", 2]}
    }
  }
])
```

### 6. Enrollment Trends (Time Series)
```javascript
db.enrollments.aggregate([
  {
    $group: {
      _id: {
        $dateToString: {
          format: "%Y-%m-%d",
          date: "$enrollment_date"
        }
      },
      daily_enrollments: {$sum: 1}
    }
  },
  {$sort: {_id: 1}},
  {
    $project: {
      _id: 0,
      date: "$_id",
      enrollments: "$daily_enrollments"
    }
  }
])
```

---

## TEXT SEARCH

### View Text Index
```javascript
// List all indexes
db.courses.getIndexes()

// Should show text index on: title, description, content.topic
```

### Perform Text Search
```javascript
// Basic text search
db.courses.find({$text: {$search: "Python"}})

// With relevance score
db.courses.find(
  {$text: {$search: "Web Development"}},
  {score: {$meta: "textScore"}}
).sort({score: {$meta: "textScore"}})

// Phrase search
db.courses.find({$text: {$search: "\"Web Development\""}})

// Exclude terms
db.courses.find({$text: {$search: "Python -intermediate"}})

// Get search count
db.courses.countDocuments({$text: {$search: "Machine Learning"}})
```

---

## INDEX MANAGEMENT

### View Current Indexes
```javascript
db.courses.getIndexes()
db.students.getIndexes()
db.enrollments.getIndexes()
```

### Create Indexes (if needed)
```javascript
// Text index
db.courses.createIndex({
  "title": "text",
  "description": "text",
  "content.topic": "text"
})

// Field indexes
db.courses.createIndex({"instructor_id": 1})
db.students.createIndex({"email": 1})
db.enrollments.createIndex({"courseId": 1, "studentId": 1})

// Index statistics
db.courses.stats({"indexDetails": true})
```

### Drop Indexes
```javascript
// Drop specific index
db.courses.dropIndex("title_text_description_text")

// Drop all indexes (keeps _id)
db.courses.dropIndexes()
```

---

## ANALYSIS QUERIES

### Statistical Analysis
```javascript
// Total enrollments
db.enrollments.countDocuments()

// Total unique students
db.students.countDocuments()

// Total courses
db.courses.countDocuments()

// Average course price
db.courses.aggregate([
  {$group: {_id: null, avg_price: {$avg: "$price"}}}
])

// Courses by category
db.courses.aggregate([
  {$group: {_id: "$category", count: {$sum: 1}}}
])

// Student enroll count distribution
db.enrollments.aggregate([
  {$group: {_id: "$email", enrollments: {$sum: 1}}},
  {$sort: {enrollments: -1}},
  {$limit: 10}
])
```

### Data Quality Checks
```javascript
// Find duplicate enrollments
db.enrollments.aggregate([
  {$group: {
    _id: {email: "$email", courseId: "$courseId"},
    count: {$sum: 1}
  }},
  {$match: {count: {$gt: 1}}}
])

// Find courses with no enrollments
db.courses.aggregate([
  {
    $lookup: {
      from: "enrollments",
      localField: "_id",
      foreignField: "courseId",
      as: "enrollments"
    }
  },
  {$match: {enrollments: {$size: 0}}}
])

// Find orphaned enrollments
db.enrollments.aggregate([
  {
    $lookup: {
      from: "courses",
      localField: "courseId",
      foreignField: "_id",
      as: "course"
    }
  },
  {$match: {course: {$size: 0}}}
])
```

---

## BULK OPERATIONS

### Insert Multiple
```javascript
db.courses.insertMany([
  {
    "title": "Course 1",
    "description": "Desc 1",
    "instructor": "Instructor 1",
    "category": "Category1",
    "price": 99.99
  },
  {
    "title": "Course 2",
    "description": "Desc 2",
    "instructor": "Instructor 2",
    "category": "Category2",
    "price": 129.99
  }
])
```

### Bulk Update
```javascript
db.enrollments.updateMany(
  {completion_status: "in_progress"},
  {$set: {progress: 50}}
)
```

### Bulk Delete
```javascript
// Delete all enrollments for a specific course
db.enrollments.deleteMany({courseId: ObjectId("...")})

// Delete all students with specific email domain
db.students.deleteMany({email: {$regex: "@oldemail.com$"}})
```

---

## PERFORMANCE TESTING

### Query Performance
```javascript
// Explain query plan
db.courses.find({$text: {$search: "Python"}}).explain("executionStats")

// Time a query
var start = Date.now()
db.courses.find({}).toArray()
var end = Date.now()
print("Query took " + (end - start) + "ms")

// Index usage
db.courses.aggregate([
  {$match: {category: "Web Development"}},
  {$group: {_id: "$instructor", count: {$sum: 1}}}
]).explain("executionStats")
```

---

## BACKUP & EXPORT

### Export Data
```javascript
// In system shell, not MongoDB shell:
// mongoexport --db course_platform --collection courses --out courses.json
// mongoexport --db course_platform --collection students --out students.json
```

### Import Data
```javascript
// In system shell:
// mongoimport --db course_platform --collection courses --file courses.json
```

---

## CLEANUP (For Testing)

### Reset Database
```javascript
// Delete all collections but keep database
db.courses.deleteMany({})
db.students.deleteMany({})
db.enrollments.deleteMany({})
db.instructors.deleteMany({})

// Drop entire database
db.dropDatabase()
```

---

## Quick Reference Card

```javascript
// Essential Commands
use course_platform          // Switch to database
show collections             // List all collections
db.courses.find()           // List all courses
db.courses.findOne()        // Get first course
db.courses.countDocuments() // Count courses
db.students.find()          // List all students
db.enrollments.find()       // List all enrollments

// Common Patterns
db.collection.insertOne({...})                    // Create
db.collection.find({query})                       // Read
db.collection.updateOne({query}, {$set: {...}})  // Update
db.collection.deleteOne({query})                  // Delete

// Aggregation
db.collection.aggregate([...stages...])

// Index
db.collection.createIndex({field: 1})
db.collection.getIndexes()

// Analysis
db.collection.stats()
db.collection.explain("executionStats")
```

---

*CourseHub MongoDB Reference*
*Use these commands to test and understand the database structure*
