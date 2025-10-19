# User Journey Flow - Complete API Flow

## Overview
This document describes the complete user journey flow with proper caching logic to ensure AI-generated content is stored and reused from the database.

---

## 🔄 Complete User Journey

### **Stage 1: AUTHENTICATED**
**Endpoint:** `POST /v1/auth/google`
- User logs in with Google
- JWT tokens generated
- User record created in `Users` table
- **Stage:** `AUTHENTICATED`

---

### **Stage 2: BASIC_REGISTERED**
**Endpoint:** `POST /v1/registration/complete`
- User completes basic registration form
- Profile saved to `Users` table
- **Stage:** `BASIC_REGISTERED`

---

### **Stage 3: Questions Generation**
**Endpoint:** `POST /v1/ai/profile/questions`

#### **First Time (No Questions in DB):**
```
1. Request arrives with JWT token
2. Authenticate user
3. Validate profile completeness
4. Check DB for existing questions
   → NO questions found ❌
5. AI generates 5 personalized questions
6. Save questions to UserCareerRoadmaps table
   - status: "QUESTIONS_GENERATED"
   - questions: JSON string
   - profile: JSON string
7. Stage remains: BASIC_REGISTERED ✅
8. Return questions + roadmapId
```
**Time:** ~3-5 seconds | **Cost:** ~$0.002

#### **Second Time (Questions Exist in DB):**
```
1. Request arrives with JWT token
2. Authenticate user
3. Validate profile completeness
4. Check DB for existing questions
   → Questions found ✅
5. Return questions from DB (NO AI call)
6. Stage remains: BASIC_REGISTERED ✅
7. Return questions + roadmapId
```
**Time:** ~200-500ms | **Cost:** ~$0.0001

---

### **Stage 4: Answer Submission**
**Endpoint:** `POST /v1/ai/profile/roadmap`

#### **First Time (No Roadmap in DB):**
```
1. Request arrives with JWT token + answers
2. Authenticate user
3. Validate profile completeness
4. Get latest roadmap from DB
5. Check if roadmap exists
   → NO roadmap found ❌
6. AI generates 3-5 career paths
7. Save answers + roadmap to UserCareerRoadmaps table
   - status: "ROADMAP_COMPLETED"
   - answers: JSON string
   - roadmap: JSON string
8. Stage updated to: CAREER_PATHS_GENERATED ✅
9. Return career paths
```
**Time:** ~5-8 seconds | **Cost:** ~$0.005

#### **Second Time (Roadmap Exists in DB):**
```
1. Request arrives with JWT token + answers
2. Authenticate user
3. Validate profile completeness
4. Get latest roadmap from DB
5. Check if roadmap exists
   → Roadmap found ✅
6. Return roadmap from DB (NO AI call)
7. Stage remains: CAREER_PATHS_GENERATED ✅
8. Return career paths
```
**Time:** ~200-500ms | **Cost:** ~$0.0001

---

### **Stage 5: Career Path Selection**
**Endpoint:** `POST /v1/ai/profile/detailed-roadmap`

#### **Every Time (Always Generates New):**
```
1. Request arrives with JWT token + selected career path
2. Authenticate user
3. Validate journey stage
4. Get latest roadmap from DB
5. AI generates detailed roadmap (2-phase Bedrock Agent)
   - Phase 1: High-level roadmap
   - Phase 2: Subtopics
   - Phase 3: Merge roadmaps
6. Save detailed roadmap to UserCareerRoadmaps table
   - status: "DETAILED_ROADMAP_COMPLETED"
   - detailedRoadmap: JSON string
   - selectedCareerPath: JSON string
7. Stage updated to: ROADMAP_GENERATED ✅
8. Return detailed roadmap
```
**Time:** ~30-45 seconds | **Cost:** ~$0.02

**Note:** This endpoint does NOT cache results. It always generates a fresh detailed roadmap.

---

## 📊 Performance Comparison

| Endpoint | First Call | Subsequent Calls | Savings |
|----------|-----------|------------------|---------|
| `/questions` | 3-5 sec | 0.2-0.5 sec | **10x faster** |
| `/roadmap` | 5-8 sec | 0.2-0.5 sec | **16x faster** |
| `/detailed-roadmap` | 30-45 sec | 30-45 sec | **No caching** |

---

## 💰 Cost Savings

| Endpoint | First Call | Subsequent Calls | Savings |
|----------|-----------|------------------|---------|
| `/questions` | $0.002 | $0.0001 | **95% cheaper** |
| `/roadmap` | $0.005 | $0.0001 | **98% cheaper** |
| `/detailed-roadmap` | $0.02 | $0.02 | **No caching** |

---

## 🗄️ Database Storage

### **UserCareerRoadmaps Table Structure:**

```json
{
  "email": "user@example.com",
  "roadmapId": "550e8400-e29b-41d4-a716-446655440000",
  "status": "DETAILED_ROADMAP_COMPLETED",
  "questions": "[{\"id\":\"q1\",\"text\":\"...\"}]",
  "answers": "[{\"id\":\"q1\",\"answer\":\"...\"}]",
  "roadmap": "{\"careerPaths\":[...]}",
  "selectedCareerPath": "{\"title\":\"...\",\"description\":\"...\"}",
  "detailedRoadmap": "{\"careerTitle\":\"...\",\"highLevelRoadmap\":[...]}",
  "profile": "{...}",
  "createdAt": "2025-10-16T10:33:19.123456",
  "updatedAt": "2025-10-16T10:35:30.654321"
}
```

---

## ✅ Caching Logic Summary

### **Questions Endpoint:**
- ✅ Checks DB first
- ✅ Only generates if not found
- ✅ Returns cached questions if exist

### **Roadmap Endpoint:**
- ✅ Checks DB first
- ✅ Only generates if not found
- ✅ Returns cached roadmap if exist

### **Detailed Roadmap Endpoint:**
- ❌ No caching
- ✅ Always generates fresh detailed roadmap
- ✅ Stores in DB for reference

---

## 🎯 Key Benefits

1. **Performance:** 10-16x faster responses for returning users (questions & roadmap)
2. **Cost:** 95-98% cheaper AWS costs for cached endpoints
3. **Consistency:** Users always get the same questions and roadmap
4. **Reliability:** No duplicate AI calls for questions and roadmap
5. **User Experience:** Instant responses for cached content
6. **Fresh Content:** Detailed roadmap always generates fresh content for latest AI capabilities

---

## 🔄 User Journey Stages

```
AUTHENTICATED
    ↓
BASIC_REGISTERED (Questions generated)
    ↓
CAREER_PATHS_GENERATED (Answers submitted)
    ↓
CAREER_PATH_SELECTED (Path chosen)
    ↓
ROADMAP_GENERATED (Detailed roadmap ready)
    ↓
ROADMAP_ACTIVE (Journey in progress)
    ↓
JOURNEY_COMPLETED
```

---

## 📝 Notes

- All AI-generated content is stored as JSON strings in DynamoDB
- Content is parsed back to objects when retrieved
- Stage only advances when user completes the step
- Questions remain in `BASIC_REGISTERED` until answered
- Roadmap remains in `CAREER_PATHS_GENERATED` until path selected
- Detailed roadmap remains in `ROADMAP_GENERATED` until journey starts

