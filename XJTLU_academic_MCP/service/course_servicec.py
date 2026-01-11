import os
import json
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

class CourseService:
    """
    Course Service - Manages all course-related data operations
    
    This service encapsulates the course data access logic, providing
    a clean interface for searching and retrieving course information.
    Currently uses mock data but designed for easy integration with real APIs.
    """
    
    def __init__(self):
        """Initialize course service with mock data"""
        self.courses = self._load_mock_courses()
        self._build_keyword_index()
        logger.info(f"CourseService initialized with {len(self.courses)} courses")
    
    def _load_mock_courses(self) -> List[Dict]:
        """Load mock course data from JSON file"""
        try:
            mock_path = os.path.join(settings.MOCK_DATA_PATH, "xjtlu_economics_courses.json")
            with open(mock_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load mock courses: {str(e)}")
            return []
    
    def _build_keyword_index(self):
        """Build keyword index for efficient searching"""
        self.keyword_index = {}
        
        # Subject keywords mapping
        self.subject_keywords = {
            "eco": ["eco", "economics", "micro", "macro", "economic", "econ"],
            "stat": ["stat", "econometrics", "data", "statistics", "quantitative", "metrics"],
            "fin": ["fin", "finance", "monetary", "financial", "banking", "investment"],
            "sustain": ["sustain", "esg", "climate", "environmental", "development"],
            "math": ["math", "maths", "calculus", "mathematical", "linear", "algebra"]
        }
        
        # Build reverse index
        for course in self.courses:
            tags = course.get("tags", [])
            for subject, keywords in self.subject_keywords.items():
                if any(tag in keywords for tag in tags):
                    if subject not in self.keyword_index:
                        self.keyword_index[subject] = []
                    self.keyword_index[subject].append(course)
    
    def search_by_keyword(self, keyword: str) -> List[Dict]:
        """
        Search courses by keyword
        
        :param keyword: Subject keyword (eco, stat, fin, sustain, math)
        :return: List of matching courses
        """
        keyword = keyword.lower()
        
        # Direct subject match
        if keyword in self.keyword_index:
            return self.keyword_index[keyword]
        
        # Fuzzy match against course names and descriptions
        results = []
        for course in self.courses:
            course_name = course["name"].lower()
            description = course.get("description", "").lower()
            
            if (keyword in course_name or 
                keyword in description or
                any(keyword in tag for tag in course.get("tags", []))):
                results.append(course)
        
        # Sort by relevance (exact matches first)
        results.sort(key=lambda x: (
            keyword in x["name"].lower(),
            keyword in x.get("description", "").lower()
        ), reverse=True)
        
        return results[:10]  # Limit to top 10 results
    
    def get_course_by_code(self, code: str) -> Optional[Dict]:
        """
        Get course by course code
        
        :param code: Course code (e.g., "ECO302")
        :return: Course dictionary or None
        """
        code = code.upper()
        for course in self.courses:
            if course["code"].upper() == code:
                return course
        return None
    
    def get_prerequisites(self, course_code: str) -> List[str]:
        """
        Get prerequisites for a course
        
        :param course_code: Course code
        :return: List of prerequisite course codes
        """
        course = self.get_course_by_code(course_code)
        if course and "prerequisites" in course:
            return course["prerequisites"]
        return []
    
    def check_prerequisites_met(self, course_code: str, completed_courses: List[str]) -> bool:
        """
        Check if prerequisites are met for a course
        
        :param course_code: Course code to check
        :param completed_courses: List of completed course codes
        :return: True if all prerequisites are met
        """
        prerequisites = self.get_prerequisites(course_code)
        return all(prereq in completed_courses for prereq in prerequisites)