from fastapi import APIRouter, HTTPException
from app.api.v1.schemas import QueryRequest, CourseExplanationResponse, SemesterPlanResponse, ErrorResponse
from app.MCP.dispatcher import AcademicDispatcher
from app.core.logger import get_logger
from typing import Union, Dict, Any

router = APIRouter()
dispatcher = AcademicDispatcher()
logger = get_logger(__name__)

@router.post("/ask",
             response_model=Union[CourseExplanationResponse, SemesterPlanResponse, Dict[str, Any]],
             responses={
                 400: {"model": ErrorResponse, "description": "Invalid request format"},
                 500: {"model": ErrorResponse, "description": "Internal server error"}
             })
async def ask_academic_question(request: QueryRequest):
    """
    Main academic query endpoint
    
    Processes user queries about courses, semester planning, and career alignment
    using the MCP (Model-Context-Protocol) architecture.
    
    - **query**: User's academic question
    - **user_profile**: Academic context including major, completed courses, career goals
    
    Returns structured response based on query intent
    """
    try:
        logger.info(f"Received query: '{request.query}' from user {request.user_profile.user_id}")
        
        # Dispatch to MCP architecture
        response = dispatcher.dispatch(
            query=request.query,
            user_context={
                "user_id": request.user_profile.user_id,
                "major": request.user_profile.major,
                "academic_year": request.user_profile.academic_year,
                "current_semester": request.user_profile.current_semester,
                "target_program": request.user_profile.target_program,
                "completed_courses": request.user_profile.completed_courses,
                "available_credits": request.user_profile.available_credits
            }
        )
        
        # Validate response structure
        if "type" not in response:
            raise ValueError("Invalid response format from dispatcher")
        
        logger.info(f"Generated response of type: {response['type']}")
        return response
        
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        raise HTTPException(
            status_code=400,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Server error processing query: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error processing your request"
        )

@router.get("/subjects",
            response_model=Dict[str, Any],
            responses={200: {"description": "List of available subject areas"}})
async def get_available_subjects():
    """
    Get available subject areas
    
    Returns the list of subject keywords that can be used in queries,
    based on XJTLU Economics curriculum structure.
    """
    subjects = {
        "eco": {"name": "Economics", "description": "Core economics principles and theories"},
        "stat": {"name": "Statistics & Econometrics", "description": "Statistical methods and economic analysis"},
        "fin": {"name": "Finance", "description": "Financial markets, institutions, and instruments"},
        "sustain": {"name": "Sustainability", "description": "Environmental, social and governance aspects"},
        "math": {"name": "Mathematics", "description": "Mathematical foundations for economic analysis"}
    }
    return {"subjects": subjects}

@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "XJTLU Academic Navigator API",
        "version": "1.0.0",
        "environment": "development",
        "timestamp": "2025-01-12T14:30:00Z"
    }