import json
import os
from typing import Dict, Any, List
from app.core.config import settings
from app.core.logger import get_logger
from app.services.course_service import CourseService

logger = get_logger(__name__)

class PlanningService:
    """
    Planning Service - Generates semester plans based on academic context
    
    This service implements the business logic for academic planning,
    combining course data with user profiles to create personalized
    semester recommendations. Uses rule-based algorithms with AI enhancement.
    """
    
    # Credit limits per semester by academic year
    CREDIT_LIMITS = {
        "year_1": 15,
        "year_2": 20,
        "year_3": 20,
        "year_4": 15
    }
    
    # Core course sequences by specialization
    SPECIALIZATION_PATHS = {
        "quantitative_finance": {
            "core_sequence": ["ECO205", "ECO214", "ECO302", "FIN301", "ECO305"],
            "recommended_electives": ["ECO309", "ECO227", "MTH212"],
            "career_paths": ["Quantitative Analyst", "Risk Management", "Asset Allocation"]
        },
        "policy_analysis": {
            "core_sequence": ["ECO213", "ECO216", "ECO225", "ECO305", "ECO321"],
            "recommended_electives": ["ECO207", "ECO212", "POL201"],
            "career_paths": ["Central Banking", "Policy Advisor", "International Organizations"]
        },
        "sustainable_finance": {
            "core_sequence": ["ECO307", "ECO311", "ECO305", "FIN301", "ECO225"],
            "recommended_electives": ["ECO306", "ECO228", "ENV301"],
            "career_paths": ["ESG Investment", "Sustainable Finance", "Impact Investing"]
        }
    }
    
    def __init__(self):
        """Initialize planning service"""
        self.course_service = CourseService()
        self.academic_calendar = self._load_academic_calendar()
        logger.info("PlanningService initialized successfully")
    
    def _load_academic_calendar(self) -> Dict:
        """Load academic calendar data (mock)"""
        try:
            calendar_path = os.path.join(settings.MOCK_DATA_PATH, "academic_calendar.json")
            if os.path.exists(calendar_path):
                with open(calendar_path, "r") as f:
                    return json.load(f)
            else:
                # Default calendar if file doesn't exist
                return {
                    "2025-2026": {
                        "Fall": {"start": "2025-09-01", "end": "2025-12-15"},
                        "Spring": {"start": "2026-02-01", "end": "2026-05-15"}
                    }
                }
        except Exception as e:
            logger.error(f"Failed to load academic calendar: {str(e)}")
            return {}
    
    def generate_semester_plan(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate personalized semester plan
        
        :param user_context: User academic profile and preferences
        :return: Structured semester plan
        """
        try:
            # Extract user context
            academic_year = user_context.get("academic_year", "2025-2026")
            current_semester = user_context.get("current_semester", "Fall")
            major = user_context.get("major", "Economics")
            target_program = user_context.get("target_program", "")
            completed_courses = user_context.get("completed_courses", [])
            available_credits = user_context.get("available_credits", 20)
            
            # Determine specialization path
            specialization = self._determine_specialization(target_program, completed_courses)
            
            # Get recommended courses
            recommended_courses = self._get_recommended_courses(
                specialization,
                academic_year,
                current_semester,
                completed_courses
            )
            
            # Filter and prioritize courses
            filtered_courses = self._filter_courses(
                recommended_courses,
                completed_courses,
                available_credits
            )
            
            # Assess workload
            workload_level = self._assess_workload(filtered_courses, user_context)
            
            # Calculate career alignment
            career_alignment = self._calculate_career_alignment(
                filtered_courses,
                specialization,
                target_program
            )
            
            # Identify gaps
            gap_analysis = self._identify_gaps(
                filtered_courses,
                specialization,
                completed_courses
            )
            
            # Build response
            plan = {
                "academic_year": academic_year,
                "semester": current_semester,
                "specialization": specialization,
                "courses": filtered_courses,
                "total_credits": sum(course.get("credits", 5) for course in filtered_courses),
                "workload_level": workload_level,
                "career_alignment_score": career_alignment,
                "gap_analysis": gap_analysis,
                "credit_limit": available_credits,
                "calendar_dates": self.academic_calendar.get(academic_year, {}).get(current_semester, {})
            }
            
            logger.info(f"Generated semester plan with {len(filtered_courses)} courses")
            return plan
            
        except Exception as e:
            logger.error(f"Planning error: {str(e)}", exc_info=True)
            return self._get_default_plan(user_context)
    
    def _determine_specialization(self, target_program: str, completed_courses: List[str]) -> str:
        """
        Determine specialization path based on career goals
        
        :param target_program: Target graduate program or career goal
        :param completed_courses: List of completed course codes
        :return: Specialization path name
        """
        target_program = target_program.lower()
        
        if "hkU mfwm" in target_program or "family wealth" in target_program:
            return "quantitative_finance"
        elif "policy" in target_program or "central bank" in target_program:
            return "policy_analysis"
        elif "sustain" in target_program or "esg" in target_program:
            return "sustainable_finance"
        
        # Fallback to completed courses analysis
        quantitative_courses = ["ECO205", "ECO214", "ECO302", "MTH212"]
        policy_courses = ["ECO213", "ECO216", "ECO225", "POL201"]
        
        quantitative_count = sum(1 for c in completed_courses if c in quantitative_courses)
        policy_count = sum(1 for c in completed_courses if c in policy_courses)
        
        if quantitative_count > policy_count:
            return "quantitative_finance"
        elif policy_count > 0:
            return "policy_analysis"
        else:
            return "quantitative_finance"  # Default to quantitative path
    
    def _get_recommended_courses(self, specialization: str, academic_year: str, 
                                semester: str, completed_courses: List[str]) -> List[Dict]:
        """
        Get recommended courses for specialization and semester
        
        :param specialization: Specialization path
        :param academic_year: Academic year (e.g., "2025-2026")
        :param semester: Semester (Fall/Spring)
        :param completed_courses: List of completed course codes
        :return: List of recommended course dictionaries
        """
        path = self.SPECIALIZATION_PATHS.get(specialization, {})
        core_sequence = path.get("core_sequence", [])
        electives = path.get("recommended_electives", [])
        
        # Get all relevant courses
        all_courses = []
        for course_code in core_sequence + electives:
            course = self.course_service.get_course_by_code(course_code)
            if course:
                all_courses.append(course)
        
        # Filter by semester availability and prerequisites
        semester_courses = []
        for course in all_courses:
            # Check if course is offered in this semester (mock logic)
            course_semester = course.get("semester", 0)
            target_semester = 1 if semester.lower() == "fall" else 2
            
            # Simple semester availability check
            if course_semester == 0 or course_semester == target_semester:
                # Check prerequisites
                if self.course_service.check_prerequisites_met(course["code"], completed_courses):
                    semester_courses.append(course)
        
        # Sort by priority (core courses first)
        semester_courses.sort(key=lambda x: (
            x["code"] in core_sequence,  # Core courses first
            -x.get("credits", 5)         # Higher credits first
        ), reverse=True)
        
        return semester_courses
    
    def _filter_courses(self, recommended_courses: List[Dict], 
                       completed_courses: List[str], available_credits: int) -> List[Dict]:
        """
        Filter and prioritize courses based on constraints
        
        :param recommended_courses: List of recommended course dictionaries
        :param completed_courses: List of completed course codes
        :param available_credits: Available credits for semester
        :return: Filtered list of course dictionaries
        """
        selected_courses = []
        remaining_credits = available_credits
        
        # First pass: select core courses
        for course in recommended_courses:
            if course["code"] not in completed_courses and course["code"] not in [c["code"] for c in selected_courses]:
                course_credits = course.get("credits", 5)
                if course_credits <= remaining_credits:
                    selected_courses.append(course)
                    remaining_credits -= course_credits
        
        # Second pass: fill remaining credits with electives
        if remaining_credits >= 5:
            for course in recommended_courses:
                if (course["code"] not in completed_courses and 
                    course["code"] not in [c["code"] for c in selected_courses] and
                    course.get("credits", 5) <= remaining_credits):
                    selected_courses.append(course)
                    remaining_credits -= course.get("credits", 5)
                    if remaining_credits < 5:
                        break
        
        return selected_courses
    
    def _assess_workload(self, courses: List[Dict], user_context: Dict[str, Any]) -> str:
        """
        Assess workload level for selected courses
        
        :param courses: List of selected course dictionaries
        :param user_context: User academic profile
        :return: Workload level ("light", "moderate", "heavy")
        """
        total_credits = sum(course.get("credits", 5) for course in courses)
        course_count = len(courses)
        
        # Get user's academic history
        completed_courses = user_context.get("completed_courses", [])
        academic_year = user_context.get("academic_year", "2025-2026")
        
        # Determine credit limits based on academic year
        year_key = academic_year.split("-")[0][-1]  # Extract year number
        credit_limit = self.CREDIT_LIMITS.get(f"year_{year_key}", 20)
        
        # Calculate workload score
        credit_ratio = total_credits / credit_limit
        course_difficulty = sum(course.get("difficulty_level", 3) for course in courses) / max(course_count, 1)
        
        workload_score = credit_ratio * 0.6 + (course_difficulty / 5) * 0.4
        
        # Determine workload level
        if workload_score < 0.6:
            return "light"
        elif workload_score < 0.8:
            return "moderate"
        else:
            return "heavy"
    
    def _calculate_career_alignment(self, courses: List[Dict], specialization: str, 
                                   target_program: str) -> float:
        """
        Calculate career alignment score
        
        :param courses: List of selected course dictionaries
        :param specialization: Specialization path
        :param target_program: Target career program
        :return: Alignment score (0.0-1.0)
        """
        if not courses:
            return 0.0
        
        # Get specialization path details
        path = self.SPECIALIZATION_PATHS.get(specialization, {})
        core_courses = path.get("core_sequence", [])
        
        # Calculate core course coverage
        core_coverage = sum(1 for c in courses if c["code"] in core_courses) / max(len(core_courses), 1)
        
        # Career-specific adjustments
        if "HKU MFWM" in target_program:
            # Prioritize quantitative and finance courses
            quant_count = sum(1 for c in courses if any(tag in ["fin", "stat", "math"] for tag in c.get("tags", [])))
            alignment = 0.6 * core_coverage + 0.4 * (quant_count / max(len(courses), 1))
        else:
            alignment = core_coverage
        
        return min(max(alignment, 0.0), 1.0)
    
    def _identify_gaps(self, selected_courses: List[Dict], specialization: str, 
                      completed_courses: List[str]) -> List[str]:
        """
        Identify academic gaps in the plan
        
        :param selected_courses: List of selected course dictionaries
        :param specialization: Specialization path
        :param completed_courses: List of completed course codes
        :return: List of gap descriptions
        """
        gaps = []
        path = self.SPECIALIZATION_PATHS.get(specialization, {})
        core_sequence = path.get("core_sequence", [])
        
        # Check for missing core courses
        selected_codes = [c["code"] for c in selected_courses]
        missing_cores = [c for c in core_sequence if c not in completed_courses and c not in selected_codes]
        
        if missing_cores:
            gaps.append(f"Missing core courses: {', '.join(missing_cores[:2])}{' and others' if len(missing_cores)>2 else ''}")
        
        # Check for skill gaps
        has_quantitative = any(any(tag in ["stat", "math"] for tag in c.get("tags", [])) for c in selected_courses)
        has_finance = any("fin" in c.get("tags", []) for c in selected_courses)
        
        if specialization == "quantitative_finance" and not has_quantitative:
            gaps.append("Limited quantitative training - consider adding econometrics or mathematics courses")
        
        if specialization == "quantitative_finance" and not has_finance:
            gaps.append("Limited finance exposure - consider adding monetary economics or business finance courses")
        
        return gaps
    
    def _get_default_plan(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Get default plan when error occurs"""
        return {
            "academic_year": user_context.get("academic_year", "2025-2026"),
            "semester": user_context.get("current_semester", "Fall"),
            "specialization": "general_economics",
            "courses": [
                {
                    "code": "ECO213",
                    "name": "Macroeconomics I",
                    "credits": 5,
                    "description": "Core macroeconomics principles"
                },
                {
                    "code": "ECO217",
                    "name": "Microeconomics I",
                    "credits": 5,
                    "description": "Core microeconomics principles"
                }
            ],
            "total_credits": 10,
            "workload_level": "light",
            "career_alignment_score": 0.6,
            "gap_analysis": ["Default plan used due to system constraints"],
            "credit_limit": user_context.get("available_credits", 20),
            "note": "This is a default plan. For personalized recommendations, please ensure your academic profile is complete."
        }