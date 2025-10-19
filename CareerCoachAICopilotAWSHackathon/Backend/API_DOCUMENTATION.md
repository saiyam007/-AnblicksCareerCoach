# Career Coach AI CoPilot - Complete API Documentation

## Overview
This document provides comprehensive API documentation for the Career Coach AI CoPilot backend system. It covers the complete user journey from authentication to assessment evaluation.

## Base URL
```
http://127.0.0.1:8000
```

## Authentication
All API endpoints (except `/v1/auth/google`) require Bearer token authentication:
```
Authorization: Bearer <access_token>
```

---

## 1. Google OAuth Authentication

### Endpoint
```
POST /v1/auth/google
```

### Description
Authenticates user with Google ID token and returns access/refresh tokens.

### Request Body
```json
{
  "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6..."
}
```

### Response
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "email": "tarunpatel2402@gmail.com",
    "full_name": "Tarun Patel",
    "first_name": "Tarun",
    "last_name": "Patel",
    "phone_number": null,
    "id": "d72c44aa-a9e4-438f-b7f5-f5d46bfbc9ea",
    "auth_provider": "google",
    "profile_picture_url": "https://lh3.googleusercontent.com/a/ACg8ocLR_ZwuvtAzXWvFl-sKmehCDgTc3yGgknlL2lSR6ut9dktXB5Gw=s96-c",
    "is_active": true,
    "is_verified": true,
    "status": "active",
    "role": "user",
    "created_at": "2025-10-16T19:55:49.995605",
    "last_login_at": null,
    "journey_stage": "AUTHENTICATED"
  }
}
```

### User Journey Stage
- **Before**: N/A (New user)
- **After**: `AUTHENTICATED`

---

## 2. Profile Completion

### Endpoint
```
POST /v1/ai/users/complete-profile
```

### Description
Completes user profile with career information and generates AI-powered profile summary.

### Headers
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

### Request Body
```json
{
  "academicInterests": "Machine Learning",
  "careerGoal": "AI Engineer",
  "country": "India",
  "currentEducationLevel": "Master degree",
  "fieldOfStudy": "Computer Science",
  "languagePreference": "English",
  "lookingFor": "Skill Development",
  "state": "Gujarat",
  "userType": "Student"
}
```

### Response
```json
{
  "success": true,
  "message": "Profile completed successfully with AI-generated summary",
  "data": {
    "firstName": "Tarun",
    "lastName": "Patel",
    "country": "India",
    "state": "Gujarat",
    "userType": "Student",
    "careerGoal": "AI Engineer",
    "lookingFor": "Skill Development",
    "languagePreference": "English",
    "currentEducationLevel": "Master degree",
    "fieldOfStudy": "Computer Science",
    "academicInterests": "Machine Learning",
    "preferredStudyDestination": null,
    "currentJobTitle": null,
    "industry": null,
    "email": "tarunpatel2402@gmail.com",
    "profile_summary": "Tarun Patel is a Masters degree student in Computer Science from Gujarat, India, specializing in Machine Learning. Currently focused on skill development to transition into an AI Engineer role, Tarun combines academic expertise with a strong interest in cutting-edge AI technologies. Seeking opportunities to enhance technical capabilities and build practical experience in artificial intelligence and machine learning applications.",
    "recordId": "PROFILE#LATEST",
    "updatedAt": "2025-10-16T19:59:14.248911"
  },
  "error": null,
  "code": 200
}
```

### User Journey Stage
- **Before**: `AUTHENTICATED`
- **After**: `BASIC_REGISTERED`

---

## 3. Generate Career Questions

### Endpoint
```
POST /v1/ai/profile/questions
```

### Description
Generates personalized career questions based on user's profile. Uses caching - returns existing questions if already generated.

### Headers
```
Authorization: Bearer <access_token>
```

### Request Body
```json
{}
```

### Response
```json
{
  "success": true,
  "message": "Retrieved 5 career questions successfully",
  "data": {
    "questions": [
      {
        "id": "q1",
        "text": "Do you have hands-on experience with deep learning frameworks like TensorFlow or PyTorch?"
      },
      {
        "id": "q2",
        "text": "Are you comfortable working with large datasets and data preprocessing techniques?"
      },
      {
        "id": "q3",
        "text": "Do you have experience deploying machine learning models in production environments?"
      },
      {
        "id": "q4",
        "text": "Are you interested in specializing in natural language processing or computer vision?"
      },
      {
        "id": "q5",
        "text": "Do you actively participate in AI/ML competitions or open-source projects?"
      }
    ],
    "roadmapId": "4573eccf-d1e5-4458-b7bd-c4d2326c83ab"
  },
  "error": null,
  "code": 200
}
```

### User Journey Stage
- **Before**: `BASIC_REGISTERED`
- **After**: `BASIC_REGISTERED` (remains same until answers submitted)

### Caching Behavior
- **First call**: Generates new questions via AI
- **Subsequent calls**: Returns cached questions from database
- **Profile update**: Deletes existing questions to generate fresh ones

---

## 4. Submit Answers & Generate Career Paths

### Endpoint
```
POST /v1/ai/profile/roadmap
```

### Description
Submits user answers to career questions and generates personalized career path recommendations.

### Headers
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

### Request Body
```json
[
  {
    "id": "q1",
    "text": "Do you have experience with machine learning frameworks?",
    "answer": "Yes"
  },
  {
    "id": "q2",
    "text": "Are you proficient in Python programming?",
    "answer": "Yes"
  },
  {
    "id": "q3",
    "text": "Do you have robotics project experience?",
    "answer": "No"
  },
  {
    "id": "q4",
    "text": "Are you familiar with French language basics?",
    "answer": "Yes"
  },
  {
    "id": "q5",
    "text": "Have you completed any AI/ML certifications?",
    "answer": "No"
  }
]
```

### Response
```json
{
  "success": true,
  "message": "Career roadmap generated successfully with 5 paths",
  "data": {
    "careerPaths": [
      {
        "title": "Machine Learning Engineer",
        "description": "Design, build, and deploy machine learning models and systems at scale...",
        "timeToAchieve": "6-12 months",
        "averageSalary": "₹8-18 LPA (India) | $95,000-$150,000 (US)",
        "keySkillsRequired": [
          "Python programming",
          "ML frameworks (TensorFlow, PyTorch, scikit-learn)",
          "Deep learning architectures",
          "MLOps and model deployment",
          "Data preprocessing and feature engineering",
          "Cloud platforms (AWS/GCP/Azure)",
          "Version control (Git)"
        ],
        "learningRoadmap": [
          "Complete advanced ML specializations (Coursera, Fast.ai)",
          "Obtain cloud ML certifications (AWS ML Specialty or GCP ML Engineer)",
          "Build 3-5 end-to-end ML projects with deployment",
          "Learn MLOps tools (MLflow, Kubeflow, Docker, Kubernetes)",
          "Contribute to open-source ML projects",
          "Practice on Kaggle competitions",
          "Create a strong GitHub portfolio showcasing deployed models"
        ],
        "aiRecommendation": {
          "reason": "Perfect alignment with your Master's in Computer Science, ML specialization, and Python/ML framework experience..."
        }
      }
      // ... 4 more career paths
    ]
  },
  "error": null,
  "code": 200
}
```

### User Journey Stage
- **Before**: `BASIC_REGISTERED`
- **After**: `CAREER_PATHS_GENERATED`

### Caching Behavior
- **First call**: Generates new career paths via AI
- **Subsequent calls**: Returns cached career paths from database

---

## 5. Generate Detailed Roadmap

### Endpoint
```
POST /v1/ai/profile/detailed-roadmap
```

### Description
Generates comprehensive detailed roadmap for selected career path using Bedrock Agent. **No caching** - always generates fresh content.

### Headers
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

### Request Body
```json
{
  "selectedCareerPath": {
    "averageSalary": "₹12-24 LPA (India) | $100,000-160,000 (International)",
    "description": "Specialize in developing vision systems for robots, including object detection, recognition, tracking, 3D reconstruction, and visual servoing.",
    "keySkillsRequired": [
      "Computer Vision (OpenCV, PCL)",
      "Deep Learning for Vision (CNNs, Vision Transformers)",
      "3D Geometry & Camera Calibration",
      "ROS Image Processing Pipelines",
      "Python, C++, CUDA",
      "Object Detection & Segmentation",
      "Depth Sensing (Stereo Vision, RGB-D cameras)"
    ],
    "timeToAchieve": "1-2 years",
    "title": "Computer Vision Engineer for Robotics"
  }
}
```

### Response
```json
{
  "success": true,
  "message": "Detailed roadmap generated successfully for Computer Vision Engineer for Robotics",
  "data": {
    "careerTitle": "Computer Vision Engineer for Robotics",
    "highLevelRoadmap": [
      {
        "phase": "Beginner",
        "duration": "3 months",
        "resources": {
          "Python for Computer Vision with OpenCV and Deep Learning": "https://www.udemy.com/course/python-for-computer-vision-with-opencv-and-deep-learning",
          "ROS for Beginners": "https://www.coursera.org/learn/ros-essentials",
          "Mathematics for Machine Learning Specialization": "https://www.coursera.org/specializations/mathematics-machine-learning"
        },
        "outcomes": [
          "Basic Python programming proficiency",
          "Understanding of fundamental CV concepts",
          "Ability to perform basic image processing tasks",
          "Basic ROS understanding"
        ],
        "topics": [
          {
            "topic": "Python programming fundamentals",
            "subtopics": [
              "Data structures and basic algorithms",
              "Object-oriented programming concepts",
              "NumPy and array operations",
              "File handling and image I/O",
              "Error handling and debugging"
            ]
          }
          // ... more topics
        ]
      }
      // ... Intermediate and Advanced phases
    ],
    "capstoneProjects": [
      {
        "title": "Autonomous Robot Navigation System",
        "duration": "2 months",
        "description": "Develop a complete visual navigation system for a robot using ROS and OpenCV..."
      }
      // ... more projects
    ]
  },
  "error": null,
  "code": 200
}
```

### User Journey Stage
- **Before**: `CAREER_PATHS_GENERATED`, `CAREER_PATH_SELECTED`, or `ROADMAP_GENERATED`
- **After**: `ROADMAP_GENERATED`

### Caching Behavior
- **No caching** - Always generates fresh detailed roadmap
- Stores selected career path and detailed roadmap in database

---

## 6. Assessment Question Generation

### Endpoint
```
POST /v1/assessment/generate-questions
```

### Description
Generates skill-based assessment questions for self-evaluation.

### Headers
```
Content-Type: application/json
```

### Request Body
```json
{
  "career_goal": "To build a career in Human Resource Management",
  "experience": "2 years",
  "name": "Riya Shah",
  "skill": "Employee Engagement"
}
```

### Response
```json
{
  "success": true,
  "message": "Assessment questions generated successfully for Employee Engagement",
  "data": [
    {
      "id": 1,
      "skill": "Employee Engagement",
      "question": "Which of the following strategies is most effective for increasing employee engagement in a remote work environment?",
      "options": {
        "A": "Regular virtual team-building activities",
        "B": "Increased surveillance of work hours",
        "C": "Reducing communication frequency",
        "D": "Implementing strict performance metrics"
      },
      "difficulty": "Medium",
      "correct_answer": null
    }
    // ... 9 more questions
  ],
  "error": null,
  "code": 200
}
```

---

## 7. Assessment Evaluation

### Endpoint
```
POST /v1/assessment/evaluate
```

### Description
Evaluates user's answers to assessment questions and provides detailed scoring.

### Headers
```
Content-Type: application/json
```

### Request Body
```json
{
  "responses": [
    {
      "difficulty": "Medium",
      "id": 1,
      "question": "Which of the following is a key driver of employee engagement?",
      "skill": "Employee Engagement",
      "user_answer": "High salaries"
    }
    // ... more responses
  ]
}
```

### Response
```json
{
  "success": true,
  "message": "Assessment evaluated successfully",
  "data": {
    "Skill": "Employee Engagement",
    "Total_Questions": 10,
    "Correct_Answers": 7,
    "Intermidiate_score": "75%",
    "Advanced_score": "60%",
    "theory_question_score": "80%",
    "Overall": "72%",
    "Summary": [
      "Good understanding of engagement strategies and employee motivation.",
      "Needs improvement in advanced techniques and data-driven approaches."
    ]
  },
  "error": null,
  "code": 200
}
```

---

## 8. User State Check

### Endpoint
```
GET /v1/users/me/state
```

### Description
Returns complete user journey state with current data and next actions.

### Headers
```
Authorization: Bearer <access_token>
```

### Response
```json
{
  "success": true,
  "message": "User journey state retrieved successfully. Current stage: CAREER_PATHS_GENERATED",
  "data": {
    "user": {
      "email": "tarunpatel2402@gmail.com",
      "journey_stage": "CAREER_PATHS_GENERATED"
      // ... other user fields
    },
    "journey_stage": "CAREER_PATHS_GENERATED",
    "stage_info": {
      "stage": "CAREER_PATHS_GENERATED",
      "order": 4,
      "description": "Paths available - user needs to select one",
      "is_valid": true
    },
    "progress": {
      "current_step": 4,
      "total_steps": 7,
      "progress_percentage": 57.1,
      "completed_steps": [
        "AUTHENTICATED",
        "BASIC_REGISTERED",
        "PROFILE_COMPLETED"
      ]
    },
    "current_data": {
      "questions": {
        "questions": [
          {
            "id": "q1",
            "text": "Do you have hands-on experience with deep learning frameworks?"
          }
          // ... more questions
        ]
      },
      "roadmap": {
        "careerPaths": [
          {
            "title": "Machine Learning Engineer"
            // ... career path data
          }
          // ... more career paths
        ]
      },
      "roadmap_id": "a4923351-06be-49fa-8985-c2785ae9e619"
    },
    "next_actions": [
      {
        "action": "answer_questions",
        "title": "Answer Questions",
        "description": "Answer the generated career questions",
        "endpoint": "/v1/ai/profile/roadmap",
        "method": "POST",
        "requires_data": true
      }
      // ... more actions
    ]
  },
  "error": null,
  "code": 200
}
```

---

## User Journey Stages

| Stage | Description | Next Actions |
|-------|-------------|--------------|
| `AUTHENTICATED` | User logged in via Google | Complete profile |
| `BASIC_REGISTERED` | Profile completed, AI summary generated | Generate questions |
| `PROFILE_COMPLETED` | Questions answered, career paths generated | Select career path |
| `CAREER_PATHS_GENERATED` | Career paths available for selection | Generate detailed roadmap |
| `CAREER_PATH_SELECTED` | Career path selected | Generate detailed roadmap |
| `ROADMAP_GENERATED` | Detailed roadmap generated | View dashboard, take assessments |
| `ROADMAP_ACTIVE` | User actively following roadmap | Continue learning, take assessments |
| `JOURNEY_COMPLETED` | User completed their learning journey | Explore new skills |
| `JOURNEY_PAUSED` | User paused their journey | Resume learning |

---

## Error Responses

### Standard Error Format
```json
{
  "success": false,
  "message": "Error description",
  "data": null,
  "error": {
    "type": "HTTPException",
    "path": "/v1/ai/profile/questions"
  },
  "code": 400
}
```

### Common HTTP Status Codes
- `200` - Success
- `400` - Bad Request (validation errors, invalid journey stage)
- `401` - Unauthorized (invalid/missing token)
- `404` - Not Found (endpoint not found)
- `500` - Internal Server Error (AI generation failures)

---

## Caching Strategy

| Endpoint | Caching Behavior | Notes |
|----------|------------------|-------|
| `/v1/ai/profile/questions` | ✅ Cached | Returns existing questions if available |
| `/v1/ai/profile/roadmap` | ✅ Cached | Returns existing career paths if available |
| `/v1/ai/profile/detailed-roadmap` | ❌ No caching | Always generates fresh content |
| Assessment endpoints | ❌ No caching | Always generates fresh content |

---

## Testing Guidelines

### 1. Authentication Flow
1. Call `/v1/auth/google` with valid Google ID token
2. Extract `access_token` from response
3. Use token in `Authorization: Bearer <token>` header for subsequent calls

### 2. User Journey Testing
1. **Complete Profile**: Call `/v1/ai/users/complete-profile`
2. **Generate Questions**: Call `/v1/ai/profile/questions`
3. **Submit Answers**: Call `/v1/ai/profile/roadmap` with answers
4. **Select Career Path**: Call `/v1/ai/profile/detailed-roadmap` with selected path
5. **Check State**: Call `/v1/users/me/state` to verify journey progression

### 3. Assessment Testing
1. **Generate Questions**: Call `/v1/assessment/generate-questions`
2. **Evaluate Answers**: Call `/v1/assessment/evaluate` with responses

### 4. Error Testing
- Test with invalid tokens
- Test with missing required fields
- Test with invalid journey stages
- Test network failures

---

## Database Tables

### Users Table
- **Primary Key**: `email` + `recordId`
- **Journey Stage**: Stored in `journey_stage` field
- **Profile Data**: Complete user profile with AI-generated summary

### UserCareerRoadmaps Table
- **Primary Key**: `email` + `roadmapId`
- **Data Stored**: Questions, answers, career paths, detailed roadmap, selected career path
- **Status**: Tracks roadmap completion status

---

## Performance Notes

- **AI Generation**: 2-5 seconds for questions/roadmaps, 15-30 seconds for detailed roadmaps
- **Caching**: Improves response time for repeated requests
- **Database**: DynamoDB for fast read/write operations
- **Concurrent Users**: Supports multiple users with separate roadmap records

---

This documentation serves as a complete reference for API testing, development, and integration. All endpoints are production-ready and follow consistent response patterns.
