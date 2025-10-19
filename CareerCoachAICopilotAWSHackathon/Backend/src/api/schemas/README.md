# 📦 Schemas Package

Organized Pydantic schemas for API request and response validation.

## 📂 Structure

```
schemas/
├── __init__.py          # Exports all schemas
├── common.py            # Common/shared schemas
├── user.py              # User-related schemas
├── auth.py              # Authentication schemas
└── registration.py      # Registration schemas
```

## 📝 Files Overview

### **common.py** - Common Schemas
```python
- ResponseModel          # Standard API response
- HealthCheck            # Health check response
- ErrorResponse          # Error response
```

### **user.py** - User Schemas
```python
- UserBase               # Base user fields
- UserCreate             # Create user request
- UserLogin              # Login request
- UserUpdate             # Update user request
- UserResponse           # User response
```

### **auth.py** - Authentication Schemas
```python
- Token                  # Simple token response
- TokenResponse          # Full token with user info
- RefreshTokenRequest    # Refresh token request
- GoogleOAuthRequest     # Google Sign-In request
- GoogleTestLoginRequest # Test login (dev only)
```

### **registration.py** - Registration Schemas
```python
- CurrentInfo            # Current education/work info
- FutureInfo             # Future career goals
- PrimaryDetails         # Primary details wrapper
- UserRegistrationRequest    # Registration request
- MetaInfo               # Meta information
- UserRegistrationResponse   # Registration response
```

## 🔧 Usage

### **Import All Schemas:**
```python
from src.api.schemas import (
    UserResponse,
    TokenResponse,
    UserRegistrationRequest,
    ErrorResponse,
)
```

### **Import from Specific Module:**
```python
from src.api.schemas.user import UserResponse, UserUpdate
from src.api.schemas.auth import TokenResponse
from src.api.schemas.registration import UserRegistrationRequest
```

### **In Route Handlers:**
```python
from fastapi import APIRouter
from src.api.schemas import UserResponse, TokenResponse

@router.get("/profile", response_model=UserResponse)
async def get_profile():
    ...
```

##  Schema Categories

### **Request Schemas** (Input)
- `UserCreate`
- `UserLogin`
- `UserUpdate`
- `GoogleOAuthRequest`
- `RefreshTokenRequest`
- `UserRegistrationRequest`

### **Response Schemas** (Output)
- `UserResponse`
- `TokenResponse`
- `UserRegistrationResponse`
- `ResponseModel`
- `HealthCheck`
- `ErrorResponse`

### **Nested Schemas** (Components)
- `CurrentInfo`
- `FutureInfo`
- `PrimaryDetails`
- `MetaInfo`

##  Benefits of This Structure

1. **Organization** - Easy to find schemas by domain
2. **Maintainability** - Small, focused files
3. **Reusability** - Import only what you need
4. **Scalability** - Easy to add new schema files
5. **Clarity** - Clear separation of concerns

## 🔄 Migration Notes

**Old Import:**
```python
from ..schemas import TokenResponse, UserResponse
```

**New Import (still works!):**
```python
from ..schemas import TokenResponse, UserResponse
```

The `__init__.py` exports everything, so existing imports continue to work!

## 🎯 Adding New Schemas

### **Step 1: Create new schema file**
```bash
# Example: payment.py
src/api/schemas/payment.py
```

### **Step 2: Define schemas**
```python
# payment.py
from pydantic import BaseModel, Field

class PaymentRequest(BaseModel):
    amount: float
    currency: str
```

### **Step 3: Export in __init__.py**
```python
# __init__.py
from .payment import PaymentRequest

__all__ = [
    ...,
    "PaymentRequest",
]
```

### **Step 4: Use in routes**
```python
from src.api.schemas import PaymentRequest
```

## 📚 Best Practices

1. **Keep schemas focused** - One domain per file
2. **Use descriptive names** - Clear purpose
3. **Add examples** - In `Config.json_schema_extra`
4. **Document fields** - Use `Field(description=...)`
5. **Validate input** - Use `@validator` decorators
6. **Export in __init__** - For easy importing

## 🔍 Schema Validation

All schemas use Pydantic for validation:

```python
class UserRegistrationRequest(BaseModel):
    type: str = Field(pattern="^(Student|Professional)$")
    
    @validator("type")
    def validate_type(cls, v):
        if v not in ["Student", "Professional"]:
            raise ValueError("Invalid type")
        return v
```

## 📖 Related Documentation

- **API Docs**: http://localhost:8000/docs
- **Pydantic Docs**: https://docs.pydantic.dev/
- **FastAPI Schemas**: https://fastapi.tiangolo.com/tutorial/response-model/

---

**Last Updated:** 2025-10-10  
**Maintained By:** Backend Team

