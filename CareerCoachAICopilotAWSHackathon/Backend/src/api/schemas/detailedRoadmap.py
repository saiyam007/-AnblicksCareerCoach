"""
Detailed Roadmap Schemas.

Request and response schemas for detailed roadmap generation endpoint.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class DetailedRoadmapRequest(BaseModel):
    """Request schema for detailed roadmap generation."""
    selectedCareerPath: Dict[str, Any] = Field(..., description="The career path selected by the user")
    
    class Config:
        json_schema_extra = {
            "example": {
                "selectedCareerPath": {
                    "title": "Computer Vision Engineer for Robotics",
                    "description": "Specialize in developing vision systems for robots, including object detection, recognition, tracking, 3D reconstruction, and visual servoing.",
                    "timeToAchieve": "1-2 years",
                    "averageSalary": "₹12-24 LPA (India) | $100,000-160,000 (International)",
                    "keySkillsRequired": [
                        "Computer Vision (OpenCV, PCL)",
                        "Deep Learning for Vision (CNNs, Vision Transformers)",
                        "3D Geometry & Camera Calibration",
                        "ROS Image Processing Pipelines",
                        "Python, C++, CUDA",
                        "Object Detection & Segmentation",
                        "Depth Sensing (Stereo Vision, RGB-D cameras)"
                    ]
                }
            }
        }


class DetailedRoadmapResponse(BaseModel):
    """Response schema for detailed roadmap generation."""
    success: bool = Field(True, description="Operation success status")
    message: str = Field(..., description="Success message")
    data: Dict[str, Any] = Field(..., description="Complete detailed roadmap structure")
    error: Optional[str] = Field(None, description="Error details (null on success)")
    code: int = Field(200, description="HTTP status code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Detailed roadmap generated successfully",
                "data": {
                    "careerTitle": "Computer Vision Engineer for Robotics",
                    "highLevelRoadmap": [
                        {
                            "phase": "Beginner",
                            "duration": "3-4 months",
                            "topics": [
                                {
                                    "topic": "Python Programming Fundamentals",
                                    "subtopics": [
                                        "Python syntax and data types",
                                        "Functions and modules",
                                        "Object-oriented programming",
                                        "File I/O and error handling"
                                    ]
                                }
                            ],
                            "resources": [
                                "Python for Computer Vision: https://opencv.org/python/"
                            ],
                            "outcomes": [
                                "Understand basic computer vision concepts"
                            ]
                        }
                    ],
                    "capstoneProjects": [
                        {
                            "title": "Autonomous Robot Navigation System",
                            "duration": "3 months",
                            "description": "Build a complete vision-based navigation system for a mobile robot using SLAM and object avoidance"
                        }
                    ]
                },
                "error": None,
                "code": 200
            }
        }
