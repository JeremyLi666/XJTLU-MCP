from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime

class UserProfile(BaseModel):
    """User academic profile schema"""
    user_id: str = Field(..., description="Unique user identifier")
    major: str = Field("Economics", description="Academic major")
    academic_year: str = Field("2025-2026", description="Current academic year")
    current_semester: str = Field("Fall", description="Current semester")
    target_program: str = Field("", description="Target graduate program or career goal")
    completed_courses: List[str] = Field(default_factory=list, description="List of completed course codes")
    available_credits: int = Field(20, description="Available credits for semester")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "student123",
                "major": "Economics",
                "academic_year": "2025-2026",
                "current_semester": "Fall",
                "target_program": "HKU MFWM",
                "completed_courses": ["ECO107", "ECO108", "ECO102", "FIN101"],
                "available_credits": 20
            }
        }

class QueryRequest(BaseModel):
    """Academic query request schema"""
    query: str = Field(..., description="User's academic query", min_length=3, max_length=500)
    user_profile: UserProfile = Field(..., description="User's academic profile")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Explain finance courses for HKU MFWM preparation",
                "user_profile": {
                    "user_id": "student123",
                    "major": "Economics",
                    "academic_year": "2025-2026",
                    "current_semester": "Fall",
                    "target_program": "HKU MFWM",
                    "completed_courses": ["ECO107", "ECO108", "ECO102", "FIN101"],
                    "available_credits": 20
                }
            }
        }

class CourseExplanationResponse(BaseModel):
    """Course explanation response schema"""
    type: str = Field("course_explanation", description="Response type")
    subjects: List[str] = Field(..., description="Subject keywords extracted from query")
    matched_courses: List[Dict[str, Any]] = Field(..., description="List of matched courses")
    explanation: str = Field(..., description="AI-generated explanation")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance score")
    academic_year: str = Field(..., description="Academic year context")
    target_program: str = Field("", description="Target program for context")
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "course_explanation",
                "subjects": ["fin"],
                "matched_courses": [
                    {
                        "code": "ECO305",
                        "name": "Monetary Economics",
                        "credits": 5,
                        "description": "Analysis of monetary policy transmission mechanisms...",
                        "semester": 4,
                        "prerequisites": ["ECO108", "ECO216"],
                        "career_paths": ["Central Banking", "Financial Regulation"]
                    }
                ],
                "explanation": "Finance courses in XJTLU's Economics programme provide rigorous training...",
                "relevance_score": 0.92,
                "academic_year": "2025-2026",
                "target_program": "HKU MFWM"
            }
        }

class SemesterPlanResponse(BaseModel):
    """Semester plan response schema"""
    type: str = Field("semester_plan", description="Response type")
    recommended_courses: List[Dict[str, Any]] = Field(..., description="List of recommended courses")
    total_credits: int = Field(..., description="Total credits for semester")
    workload_assessment: str = Field(..., description="Workload level assessment")
    strategic_advice: str = Field(..., description="AI-generated strategic advice")
    gap_analysis: List[str] = Field(default_factory=list, description="Academic gap analysis")
    career_alignment: float = Field(..., ge=0.0, le=1.0, description="Career alignment score")
    academic_year: str = Field(..., description="Academic year")
    semester: str = Field(..., description="Semester")
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "semester_plan",
                "recommended_courses": [
                    {
                        "code": "ECO305",
                        "name": "Monetary Economics",
                        "credits": 5,
                        "semester": 4,
                        "prerequisites": ["ECO108", "ECO216"]
                    }
                ],
                "total_credits": 15,
                "workload_assessment": "moderate",
                "strategic_advice": "This semester plan provides strong preparation for HKU's Family Wealth Management program...",
                "gap_analysis": ["Missing quantitative finance course"],
                "career_alignment": 0.85,
                "academic_year": "2025-2026",
                "semester": "Fall"
            }
        }

class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Invalid query format",
                "detail": "Query must be at least 3 characters long",
                "timestamp": "2025-01-12T14:30:00Z"
            }
        }