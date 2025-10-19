# Assessment & Evaluation API Guide

## Overview

The Assessment API provides two endpoints for generating skill-based assessment questions and evaluating user responses using AWS Bedrock Agent.

## Endpoints

### 1. Generate Assessment Questions

**Endpoint:** `POST /v1/assessment/generate-questions`

**Description:** Generates 10 assessment questions for a specific skill based on user profile.

**Request Body:**
```json
{
  "name": "Riya Shah",
  "career_goal": "To build a career in Human Resource Management",
  "skill": "Employee Engagement",
  "experience": "2 years"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Assessment questions generated successfully for Employee Engagement",
  "data": [
    {
      "id": 1,
      "skill": "Employee Engagement",
      "question": "Which of the following is a key driver of employee engagement?",
      "options": {
        "A": "High salaries",
        "B": "Opportunities for growth",
        "C": "Flexible working hours",
        "D": "Free snacks in the office"
      },
      "difficulty": "Medium",
      "correct_answer": "B"
    },
    {
      "id": 2,
      "skill": "Employee Engagement",
      "question": "Explain the role of leadership in fostering employee engagement.",
      "difficulty": "Hard"
    }
  ],
  "error": null,
  "code": 200
}
```

**Question Distribution:**
- Total: 10 questions
- 70% Medium difficulty (7 questions)
- 30% Hard difficulty (3 questions)
- 1 theoretical question (no options)
- 1 scenario-based question
- 8-9 MCQ questions with 4 options (A-D)

---

### 2. Evaluate Assessment Answers

**Endpoint:** `POST /v1/assessment/evaluate`

**Description:** Evaluates user's assessment responses and generates scores with detailed feedback.

**Request Body:**
```json
{
  "responses": [
    {
      "id": 1,
      "skill": "Employee Engagement",
      "question": "Which of the following is a key driver of employee engagement?",
      "difficulty": "Medium",
      "user_answer": "High salaries"
    },
    {
      "id": 2,
      "skill": "Employee Engagement",
      "question": "Explain the role of leadership in fostering employee engagement.",
      "difficulty": "Hard",
      "user_answer": "Leaders should assign more work to employees so they stay engaged."
    }
  ]
}
```

**Response:**
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

**Score Breakdown:**
- **Intermidiate_score**: Percentage correct for medium difficulty questions
- **Advanced_score**: Percentage correct for hard difficulty questions
- **theory_question_score**: Percentage correct for theoretical questions
- **Overall**: Total percentage correct across all questions
- **Summary**: 2-5 feedback points about strengths and areas for improvement

---

## Architecture

### Files Created

1. **`src/api/schemas/assessment.py`**
   - Pydantic models for requests and responses
   - Type validation and documentation

2. **`src/api/services/assessmentService.py`**
   - Business logic for assessment generation and evaluation
   - AWS Bedrock Agent integration
   - Singleton pattern for service instance

3. **`src/api/routes/assessmentRoutes.py`**
   - FastAPI route handlers
   - Request validation and error handling
   - Standardized response formatting

4. **`src/main.py`** (Updated)
   - Registered assessment routes with prefix `/v1`

### AWS Bedrock Agent Configuration

- **Agent ID**: `8ASUXM7IMS`
- **Agent Alias ID**: `GLQAVGIYPL`
- **Region**: `us-east-2`
- **Session ID**: UUID generated per request

---

## Testing

### Using Swagger UI

1. Navigate to `http://localhost:8000/docs`
2. Find the **Assessment** section
3. Test both endpoints with the example payloads

### Using cURL

**Generate Questions:**
```bash
curl -X POST "http://localhost:8000/v1/assessment/generate-questions" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Riya Shah",
    "career_goal": "To build a career in Human Resource Management",
    "skill": "Employee Engagement",
    "experience": "2 years"
  }'
```

**Evaluate Answers:**
```bash
curl -X POST "http://localhost:8000/v1/assessment/evaluate" \
  -H "Content-Type: application/json" \
  -d '{
    "responses": [
      {
        "id": 1,
        "skill": "Employee Engagement",
        "question": "Which of the following is a key driver of employee engagement?",
        "difficulty": "Medium",
        "user_answer": "High salaries"
      }
    ]
  }'
```

---

## Error Handling

All endpoints return standardized error responses:

```json
{
  "success": false,
  "message": "Error message",
  "data": null,
  "error": {
    "type": "HTTPException",
    "path": "/v1/assessment/generate-questions"
  },
  "code": 400
}
```

**Common Error Codes:**
- `400`: Bad Request (validation errors, missing data)
- `500`: Internal Server Error (Bedrock Agent failures, unexpected errors)

---

## Integration Notes

1. **Authentication**: Currently no authentication required. Can be added using JWT tokens.
2. **Rate Limiting**: Can be added to prevent abuse.
3. **Caching**: Question generation can be cached per skill to reduce Bedrock API calls.
4. **Database Storage**: Assessment results can be stored in DynamoDB for historical tracking.

---

## Next Steps

1. Add authentication/authorization
2. Implement rate limiting
3. Add database storage for assessment history
4. Create analytics dashboard for assessment performance
5. Add support for multiple skills in a single assessment
6. Implement question bank and randomization

