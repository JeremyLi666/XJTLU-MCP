import os
import requests
import json
from typing import Dict, Any, List, Optional
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

class AIService:
    """
    AI Service Layer - Handles all interactions with AI models
    
    This service encapsulates the complexity of AI model interactions,
    providing a clean interface for the rest of the application.
    Supports both real API calls and professional mock responses.
    """
    
    def __init__(self):
        """Initialize AI service with configuration"""
        self.use_mock = settings.USE_MOCK_AI
        self.api_key = settings.DEEPSEEK_API_KEY
        self.api_url = settings.DEEPSEEK_API_URL
        self.model = settings.DEEPSEEK_MODEL
        
        # Validate configuration
        if not self.use_mock and not self.api_key:
            logger.warning("DeepSeek API key not configured. Falling back to mock mode.")
            self.use_mock = True
    
    def generate_course_explanation(self, subjects: List[str], courses: List[Dict], 
                                   user_profile: Dict[str, Any], original_query: str) -> str:
        """
        Generate professional course explanation
        
        :param subjects: List of subject keywords (e.g., ["fin", "stat"])
        :param courses: List of matched course dictionaries
        :param user_profile: User academic profile and goals
        :param original_query: Original user query for context
        :return: Professional explanation text
        """
        if self.use_mock:
            return self._mock_course_explanation(subjects, courses, user_profile, original_query)
        
        try:
            prompt = self._build_course_prompt(subjects, courses, user_profile, original_query)
            return self._call_deepseek_api(prompt)
        except Exception as e:
            logger.error(f"DeepSeek API error: {str(e)}")
            return self._mock_course_explanation(subjects, courses, user_profile, original_query)
    
    def generate_planning_advice(self, plan: Dict[str, Any], user_profile: Dict[str, Any], 
                                original_query: str) -> str:
        """Generate professional semester planning advice"""
        if self.use_mock:
            return self._mock_planning_advice(plan, user_profile, original_query)
        
        try:
            prompt = self._build_planning_prompt(plan, user_profile, original_query)
            return self._call_deepseek_api(prompt)
        except Exception as e:
            logger.error(f"DeepSeek API error in planning: {str(e)}")
            return self._mock_planning_advice(plan, user_profile, original_query)
    
    def analyze_career_alignment(self, subjects: List[str], career_goal: str, 
                                 academic_background: str, original_query: str) -> Dict[str, Any]:
        """Analyze career alignment for course subjects"""
        if self.use_mock:
            return self._mock_career_alignment(subjects, career_goal, academic_background, original_query)
        
        try:
            prompt = self._build_career_prompt(subjects, career_goal, academic_background, original_query)
            response = self._call_deepseek_api(prompt)
            
            # Try to parse JSON response
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                logger.warning("Failed to parse career alignment JSON response")
                return self._mock_career_alignment(subjects, career_goal, academic_background, original_query)
                
        except Exception as e:
            logger.error(f"DeepSeek API error in career analysis: {str(e)}")
            return self._mock_career_alignment(subjects, career_goal, academic_background, original_query)
    
    def _build_course_prompt(self, subjects: List[str], courses: List[Dict], 
                           user_profile: Dict[str, Any], original_query: str) -> str:
        """构建专业课程解释提示词"""
        course_summaries = []
        for course in courses:
            summary = (
                f"- {course['code']}: {course['name']} ({course['credits']} credits)\n"
                f"  Focus: {course.get('description', 'Comprehensive academic course')[:100]}...\n"
                f"  Career paths: {', '.join(course.get('career_paths', ['Academic Development']))}"
            )
            course_summaries.append(summary)
        
        return f"""
        You are an expert academic advisor at Xi'an Jiaotong-Liverpool University (XJTLU) 
        specializing in the Economics programme. You help students understand course content 
        and make informed academic decisions.

        STUDENT PROFILE:
        - Major: {user_profile.get('major', 'Economics')}
        - Current year: {user_profile.get('academic_year', '2025-2026')}
        - Career goal: {user_profile.get('target_program', 'graduate studies')}
        - Completed courses: {', '.join(user_profile.get('completed_courses', ['Introductory courses']))}

        USER QUERY: "{original_query}"

        RELEVANT COURSES (based on subject keywords: {', '.join(subjects)}):
        {chr(10).join(course_summaries)}

        INSTRUCTIONS:
        1. Provide a professional, concise explanation (120-150 words) of how these courses relate to the student's career goals
        2. Focus on practical skills and career relevance rather than theoretical details
        3. If the career goal is HKU MFWM (Master of Family Wealth Management), emphasize quantitative skills, risk management, and portfolio optimization
        4. Maintain an encouraging but realistic tone
        5. Do not mention specific instructors or unpublished curriculum changes
        6. Format the response in clear, readable paragraphs without markdown

        RESPONSE:
        """
    
    def _build_planning_prompt(self, plan: Dict[str, Any], user_profile: Dict[str, Any], 
                             original_query: str) -> str:
        """构建学期规划提示词"""
        course_list = []
        for course in plan.get("courses", []):
            course_list.append(f"- {course.get('code', '')}: {course.get('name', '')} ({course.get('credits', 0)} credits)")
        
        return f"""
        You are an academic planning specialist at XJTLU Economics department.

        STUDENT PROFILE:
        - Major: {user_profile.get('major', 'Economics')}
        - Academic year: {user_profile.get('academic_year', '2025-2026')}
        - Target program: {user_profile.get('target_program', 'graduate studies')}
        - Completed courses: {', '.join(user_profile.get('completed_courses', []))}

        PROPOSED SEMESTER PLAN:
        Total credits: {plan.get('total_credits', 0)}
        Workload level: {plan.get('workload_level', 'moderate')}
        Courses:
        {chr(10).join(course_list)}

        USER QUERY: "{original_query}"

        INSTRUCTIONS:
        1. Provide strategic advice (100-120 words) on this semester plan's alignment with career goals
        2. Highlight 1-2 key strengths and 1 potential concern (if any)
        3. For HKU MFWM preparation, emphasize quantitative course sequences and practical applications
        4. Suggest one concrete next step (e.g., "Consider adding a project-based course" or "Connect with Career Hub for internship opportunities")
        5. Maintain professional, encouraging tone
        6. Do not use bullet points or markdown formatting

        RESPONSE:
        """
    
    def _build_career_prompt(self, subjects: List[str], career_goal: str, 
                           academic_background: str, original_query: str) -> str:
        """构建职业分析提示词"""
        return f"""
        You are a career development specialist at XJTLU with expertise in economics and finance pathways.

        REQUEST ANALYSIS:
        Subject areas: {', '.join(subjects)}
        Career goal: {career_goal}
        Academic background: {academic_background}
        User query: "{original_query}"

        INSTRUCTIONS:
        1. Analyze how courses in these subject areas prepare students for the specified career goal
        2. Identify 1-2 competency gaps that need addressing
        3. Recommend a specific academic pathway (course sequence) for optimal preparation
        4. Provide industry outlook for this career path (1-2 sentences)
        5. If career goal is HKU MFWM, emphasize family office dynamics, intergenerational wealth transfer, and behavioral finance aspects
        6. Respond in JSON format with these exact keys:
           {{
             "gap": "Brief description of competency gaps",
             "pathway": "Recommended course sequence",
             "alignment_score": 0.85,
             "key_modules": ["List", "of", "essential", "courses"],
             "industry_outlook": "Current industry trends and outlook"
           }}
        7. Keep values concise and actionable

        RESPONSE (JSON only):
        """
    
    def _call_deepseek_api(self, prompt: str) -> str:
        """调用 DeepSeek API"""
        if not self.api_key:
            raise ValueError("DeepSeek API key not configured")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 500
        }
        
        logger.info(f"Calling DeepSeek API with prompt length: {len(prompt)}")
        
        response = requests.post(
            self.api_url,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        response.raise_for_status()
        result = response.json()
        
        if "choices" not in result or not result["choices"]:
            raise ValueError("Invalid API response format")
        
        content = result["choices"][0]["message"]["content"].strip()
        logger.info(f"Received DeepSeek response (length: {len(content)})")
        return content
    
    def _mock_course_explanation(self, subjects: List[str], courses: List[Dict], 
                               user_profile: Dict[str, Any], original_query: str) -> str:
        """高质量mock课程解释 - 基于西浦经济学课程体系"""
        target = user_profile.get("target_program", "graduate studies")
        subject_explanations = []
        
        for subject in subjects:
            if subject == "fin" and "HKU MFWM" in target:
                subject_explanations.append(
                    f"Finance courses in XJTLU's Economics programme provide rigorous training in quantitative asset management and risk modeling. "
                    f"For HKU MFWM preparation, these courses build essential competencies in financial engineering, portfolio optimization, and behavioral finance principles. "
                    f"The curriculum emphasizes both theoretical foundations and practical implementation through case studies of Asian wealth management practices."
                )
            elif subject == "stat" and "HKU MFWM" in target:
                subject_explanations.append(
                    f"The econometrics sequence (ECO205 → ECO214 → ECO302) develops your ability to analyze financial data and validate investment models. "
                    f"For family wealth management careers, these statistical skills are critical for evidence-based decision making and risk assessment. "
                    f"XJTLU's approach integrates Python programming throughout, ensuring you can implement quantitative strategies in professional environments."
                )
            elif subject == "sustain" and "HKU MFWM" in target:
                subject_explanations.append(
                    f"Sustainability courses (ECO307, ECO311) address the growing importance of ESG factors in wealth preservation and legacy planning. "
                    f"HKU MFWM graduates increasingly work with clients who prioritize impact alongside returns. These courses provide frameworks for integrating environmental, social, and governance considerations into portfolio construction."
                )
            else:
                subject_explanations.append(
                    f"Courses in {subject} provide valuable analytical training that develops critical thinking and quantitative reasoning skills essential for economics graduates."
                )
        
        # 结合课程信息
        course_references = []
        for course in courses[:3]:  # 最多参考3门课程
            relevance = "directly relevant" if any(tag in ["fin", "stat"] for tag in course.get("tags", [])) else "supportive"
            course_references.append(f"{course['name']} ({course['code']}) is {relevance} for your goals")
        
        if course_references:
            course_sentence = ". ".join(course_references) + "."
        else:
            course_sentence = "These subject areas align with XJTLU's Economics curriculum design."
        
        return " ".join(subject_explanations) + " " + course_sentence
    
    def _mock_planning_advice(self, plan: Dict[str, Any], user_profile: Dict[str, Any], 
                            original_query: str) -> str:
        """高质量mock规划建议"""
        target = user_profile.get("target_program", "graduate studies")
        total_credits = plan.get("total_credits", 0)
        course_count = len(plan.get("courses", []))
        
        if "HKU MFWM" in target:
            return (
                f"This semester plan provides strong preparation for HKU's Family Wealth Management program. "
                f"The combination of quantitative courses (econometrics, mathematical finance) and applied finance modules "
                f"builds the analytical foundation required for systematic wealth management. With {total_credits} credits across {course_count} courses, "
                f"the workload is well-balanced for sustained academic performance. Consider connecting with XJTLU's Career Hub to explore "
                f"summer internships at private banks or family offices to complement this academic preparation."
            )
        else:
            return (
                f"This balanced semester plan effectively combines theoretical foundations with practical applications. "
                f"The {total_credits} credit load across {course_count} courses provides comprehensive coverage while maintaining manageable workload. "
                f"Focus on developing strong relationships with course instructors, as their mentorship and recommendation letters will be valuable for your future applications. "
                f"Consider joining the XJTLU Economics Society to connect with peers sharing similar career aspirations."
            )
    
    def _mock_career_alignment(self, subjects: List[str], career_goal: str, 
                             academic_background: str, original_query: str) -> Dict[str, Any]:
        """高质量mock职业分析"""
        if "HKU MFWM" in career_goal:
            return {
                "gap": "Practical experience in client relationship management and intergenerational wealth transfer case studies",
                "pathway": "ECO205 → ECO214 → ECO302 (Econometrics sequence) + FIN301 + ECO305 + ECO311",
                "alignment_score": 0.88,
                "key_modules": ["ECO302", "FIN301", "ECO305", "ECO311"],
                "industry_outlook": "Family wealth management in Asia is experiencing rapid growth with increasing demand for professionals who combine quantitative rigor with interpersonal skills. HKU MFWM graduates are highly sought after by private banks and multi-family offices across the Greater Bay Area."
            }
        else:
            return {
                "gap": "Specialized technical skills in data analysis or policy evaluation depending on career direction",
                "pathway": "Core Economics sequence + Statistics concentration + relevant electives",
                "alignment_score": 0.75,
                "key_modules": ["ECO213", "ECO216", "ECO205", "ECO214"],
                "industry_outlook": "Economics graduates have diverse career pathways in analysis, policy, and finance roles. Developing complementary quantitative skills significantly enhances employability across all sectors."
            }