import json
import os
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from app.core.config import settings
from app.MCP.message import MCPMessage
from app.MCP.protocol import ProtocolStatus, ProtocolRules
from app.services.course_service import CourseService
from app.services.ai_service import AIService
from app.services.planning_service import PlanningService
from app.core.logger import get_logger

logger = get_logger(__name__)

class AcademicDispatcher:
    """
    MCP架构中的核心调度器 - 负责学术请求的意图识别、路由和协调
    
    设计原则：
    1. 无状态：每次请求携带完整上下文
    2. 意图驱动：基于关键词识别用户真实需求
    3. 数据隔离：Context层（课程数据）与Model层（AI推理）严格分离
    4. 协议标准化：统一消息格式确保模块间兼容性
    5. 容错设计：自动降级和错误处理
    """
    
    # 意图关键词映射
    INTENT_KEYWORDS = {
        "course_explanation": ["explain", "what is", "about", "describe", "introduction", "tell me", "overview"],
        "semester_planning": ["plan", "recommend", "suggest", "build", "design", "roadmap", "schedule", "timetable"],
        "career_alignment": ["career", "job", "future", "hku", "kcl", "target", "path", "direction"],
        "prerequisite_check": ["prerequisite", "before", "need to take", "require", "must take", "pre-req"],
        "workload_assessment": ["workload", "difficult", "hard", "time", "balance", "manage", "hours", "effort"]
    }
    
    # 学科关键词映射
    SUBJECT_KEYWORDS = {
        "eco": ["eco", "economics", "micro", "macro", "economic", "econ"],
        "stat": ["stat", "econometrics", "data", "statistics", "quantitative", "regression", "metrics"],
        "fin": ["fin", "finance", "monetary", "financial", "banking", "investment", "wealth"],
        "sustain": ["sustain", "esg", "climate", "environmental", "development", "green", "social"],
        "math": ["math", "maths", "calculus", "mathematical", "linear", "algebra", "probability"]
    }
    
    # 学科专业解释映射
    SUBJECT_EXPLANATIONS = {
        "fin": (
            "Finance-focused courses in XJTLU's Economics programme provide rigorous training in quantitative asset "
            "management, risk modeling, and monetary policy analysis. These courses build essential competencies in "
            "financial engineering and portfolio optimization directly applicable to systematic wealth management strategies."
        ),
        "stat": (
            "The econometrics sequence (ECO205 → ECO214 → ECO302) provides progressive mastery of statistical methods "
            "for economic analysis. These courses develop your ability to validate financial models using real market "
            "data — a critical skill for evidence-based decision making in quantitative finance roles."
        ),
        "eco": (
            "Core economics courses establish fundamental principles of resource allocation, market dynamics, and "
            "policy evaluation. This theoretical foundation is essential for advanced specialization in finance or "
            "policy analysis, providing the analytical framework required for strategic decision-making."
        ),
        "sustain": (
            "Sustainability courses integrate environmental, social, and governance (ESG) factors into economic analysis. "
            "These courses prepare students for the rapidly growing sustainable finance sector, where traditional financial "
            "acumen is combined with impact assessment capabilities."
        )
    }
    
    def __init__(self):
        """初始化所有依赖服务"""
        self.course_service = CourseService()
        self.ai_service = AIService()
        self.planning_service = PlanningService()
        self._load_course_database()
        logger.info("AcademicDispatcher initialized successfully")
    
    def _load_course_database(self):
 
        try:
            with open(os.path.join(settings.MOCK_DATA_PATH, "xjtlu_economics_courses.json"), "r", encoding="utf-8") as f:
                self.course_db = json.load(f)
            logger.info(f"Loaded {len(self.course_db)} courses from database")
        except Exception as e:
            logger.error(f"Failed to load course database: {str(e)}")
            self.course_db = []
    
    def dispatch(self, query: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        主调度函数 - MCP架构的核心入口
        
        处理流程：
        1. 标准化输入
        2. 意图识别 (Protocol层)
        3. 关键词提取 (Context层)
        4. 服务路由 (Model层)
        5. 响应生成 (Model+Context融合)
        
        :param query: 用户原始查询
        :param user_context: 用户画像上下文
        :return: 结构化响应
        """
        try:
            # 1. 标准化输入
            normalized_query = query.lower().strip()
            logger.info(f"Processing query: '{normalized_query}'")
            
            # 2. 意图识别
            intent = self._detect_intent(normalized_query)
            logger.info(f"Detected intent: {intent}")
            
            # 3. 关键词提取
            subject_keywords = self._extract_subject_keywords(normalized_query)
            logger.info(f"Extracted subject keywords: {subject_keywords}")
            
            # 4. 路由决策
            if intent == "course_explanation" and subject_keywords:
                return self._handle_course_explanation(subject_keywords, user_context, normalized_query)
            elif intent == "semester_planning":
                return self._handle_semester_planning(user_context, normalized_query)
            elif intent == "career_alignment":
                return self._handle_career_alignment(subject_keywords, user_context, normalized_query)
            elif intent == "prerequisite_check" and subject_keywords:
                return self._handle_prerequisite_check(subject_keywords, user_context)
            elif intent == "workload_assessment":
                return self._handle_workload_assessment(user_context)
            else:
                return self._handle_general_query(normalized_query, user_context)
                
        except Exception as e:
            logger.error(f"Dispatch error: {str(e)}", exc_info=True)
            return {
                "type": "error",
                "message": "I encountered an error processing your request. Please try rephrasing your question.",
                "original_query": query,
                "error_details": str(e) if settings.APP_ENV == "development" else None
            }
    
    def _detect_intent(self, query: str) -> str:
        """意图识别引擎 - 基于关键词匹配"""
        for intent, keywords in self.INTENT_KEYWORDS.items():
            if any(keyword in query for keyword in keywords):
                return intent
        return "general_query"
    
    def _extract_subject_keywords(self, query: str) -> List[str]:
        """提取学科关键词（支持多关键词）"""
        found_keywords = []
        for subject, keywords in self.SUBJECT_KEYWORDS.items():
            if any(keyword in query for keyword in keywords):
                found_keywords.append(subject)
        return found_keywords
    
    def _handle_course_explanation(self, subjects: List[str], user_context: Dict[str, Any], original_query: str) -> Dict[str, Any]:
        """
        处理课程解释请求
        
        特色：
        - 基于西浦真实课程体系（非硬编码特定课程）
        - 动态匹配关键词（eco/stat/fin）
        - 结合用户目标生成个性化解释
        - 自动降级到预定义解释（如果AI服务不可用）
        """
        try:
            # 1. 获取相关课程（使用课程服务）
            relevant_courses = []
            for subject in subjects:
                courses = self.course_service.search_by_keyword(subject)
                relevant_courses.extend(courses[:3])  # 每个关键词取前3门
            
            # 2. 去重（根据课程代码）
            unique_courses = []
            seen_codes = set()
            for course in relevant_courses:
                if course["code"] not in seen_codes:
                    seen_codes.add(course["code"])
                    unique_courses.append(course)
            relevant_courses = unique_courses[:5]  # 限制最多5门课程
            
            # 3. 生成AI解释（使用AI服务）
            explanation = self.ai_service.generate_course_explanation(
                subjects=subjects,
                courses=relevant_courses,
                user_profile=user_context,
                original_query=original_query
            )
            
            # 4. 构建结构化响应
            response = {
                "type": "course_explanation",
                "subjects": subjects,
                "matched_courses": [
                    {
                        "code": course["code"],
                        "name": course["name"],
                        "credits": course["credits"],
                        "description": course.get("description", "")[:100] + "...",
                        "semester": course.get("semester", "N/A"),
                        "prerequisites": course.get("prerequisites", []),
                        "career_paths": course.get("career_paths", [])
                    } for course in relevant_courses
                ],
                "explanation": explanation,
                "relevance_score": round(0.85 + 0.05 * len(subjects), 2),
                "academic_year": user_context.get("academic_year", "2025-2026"),
                "target_program": user_context.get("target_program", "graduate studies")
            }
            
            logger.info(f"Generated course explanation for subjects: {subjects}")
            return response
            
        except Exception as e:
            logger.warning(f"Falling back to default explanation due to error: {str(e)}")
            # 降级到预定义解释
            default_explanation = " ".join([
                self.SUBJECT_EXPLANATIONS.get(subject, 
                    f"Courses in {subject} provide valuable analytical training for economics students.")
                for subject in subjects
            ])
            
            return {
                "type": "course_explanation",
                "subjects": subjects,
                "explanation": default_explanation,
                "note": "This is a simplified explanation due to system limitations. Full AI analysis would provide more personalized insights.",
                "fallback_mode": True
            }
    
    def _handle_semester_planning(self, user_context: Dict[str, Any], original_query: str) -> Dict[str, Any]:
        """处理学期规划请求"""
        try:
            # 1. 获取规划建议
            plan = self.planning_service.generate_semester_plan(user_context)
            
            # 2. 生成专业建议
            advice = self.ai_service.generate_planning_advice(
                plan=plan,
                user_profile=user_context,
                original_query=original_query
            )
            
            response = {
                "type": "semester_plan",
                "recommended_courses": plan["courses"],
                "total_credits": plan["total_credits"],
                "workload_assessment": plan["workload_level"],
                "strategic_advice": advice,
                "gap_analysis": plan.get("gap_analysis", []),
                "career_alignment": plan.get("career_alignment_score", 0.0),
                "academic_year": user_context.get("academic_year", "2025-2026"),
                "semester": user_context.get("current_semester", "Fall")
            }
            
            logger.info(f"Generated semester plan with {len(plan['courses'])} courses")
            return response
            
        except Exception as e:
            logger.error(f"Planning error: {str(e)}")
            return {
                "type": "error",
                "message": "Could not generate semester plan due to system constraints.",
                "suggestion": "Try asking about specific subject areas instead."
            }
    
    def _handle_career_alignment(self, subjects: List[str], user_context: Dict[str, Any], original_query: str) -> Dict[str, Any]:
        """处理职业路径对齐分析"""
        try:
            career_goal = user_context.get("target_program", "graduate studies")
            background = user_context.get("major", "Economics")
            
            analysis = self.ai_service.analyze_career_alignment(
                subjects=subjects,
                career_goal=career_goal,
                academic_background=background,
                original_query=original_query
            )
            
            response = {
                "type": "career_alignment",
                "career_goal": career_goal,
                "relevant_subjects": subjects,
                "competency_gap": analysis["gap"],
                "recommended_pathway": analysis["pathway"],
                "hku_alignment_score": analysis["alignment_score"],
                "key_modules": analysis["key_modules"],
                "industry_outlook": analysis["industry_outlook"]
            }
            
            logger.info(f"Generated career alignment analysis for {career_goal}")
            return response
            
        except Exception as e:
            logger.warning(f"Career analysis fallback: {str(e)}")
            # 降级到通用职业建议
            return {
                "type": "career_alignment",
                "career_goal": career_goal,
                "message": f"Based on XJTLU Economics curriculum, courses in {', '.join(subjects)} provide strong foundation for {career_goal}.",
                "note": "For personalized career advice, consider booking an appointment with XJTLU Career Hub.",
                "fallback_mode": True
            }
    
    def _handle_prerequisite_check(self, subjects: List[str], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """处理先决条件检查"""
        try:
            completed_courses = user_context.get("completed_courses", [])
            all_prereqs_satisfied = True
            missing_prerequisites = []
            
            relevant_courses = []
            for subject in subjects:
                courses = self.course_service.search_by_keyword(subject)
                relevant_courses.extend(courses[:2])  # 每个关键词取前2门
            
            for course in relevant_courses:
                course_code = course["code"]
                prereqs = course.get("prerequisites", [])
                missing = [p for p in prereqs if p not in completed_courses]
                
                if missing:
                    all_prereqs_satisfied = False
                    missing_prerequisites.append({
                        "course": course_code,
                        "missing_prerequisites": missing
                    })
            
            response = {
                "type": "prerequisite_check",
                "subjects": subjects,
                "all_prereqs_satisfied": all_prereqs_satisfied,
                "missing_prerequisites": missing_prerequisites,
                "completed_courses": completed_courses
            }
            
            logger.info(f"Prerequisite check completed for {len(relevant_courses)} courses")
            return response
            
        except Exception as e:
            logger.error(f"Prerequisite check error: {str(e)}")
            return {
                "type": "error",
                "message": "Could not check prerequisites due to system error.",
                "suggestion": "Please verify course prerequisites manually in XJTLU Learning Mall."
            }
    
    def _handle_workload_assessment(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """处理工作量评估"""
        try:
            # 简单的工作量评估逻辑
            completed_courses = user_context.get("completed_courses", [])
            total_credits = sum(5 for _ in completed_courses)  # 假设每门课5学分
            
            # 基于学分的简单评估
            if total_credits < 60:
                workload_level = "beginner"
                assessment = "You're building your foundation. Current workload is manageable for most students."
            elif total_credits < 120:
                workload_level = "intermediate"
                assessment = "You have substantial coursework experience. Consider balancing technical and theoretical courses."
            else:
                workload_level = "advanced"
                assessment = "You have significant academic experience. Focus on specialization courses that align with career goals."
            
            response = {
                "type": "workload_assessment",
                "workload_level": workload_level,
                "assessment": assessment,
                "total_completed_credits": total_credits,
                "recommendation": "For optimal learning, maintain 15-20 credits per semester with balanced difficulty levels."
            }
            
            logger.info(f"Workload assessment: {workload_level} level")
            return response
            
        except Exception as e:
            logger.error(f"Workload assessment error: {str(e)}")
            return {
                "type": "error",
                "message": "Could not assess workload due to incomplete academic record.",
                "suggestion": "Please ensure your completed courses are correctly recorded."
            }
    
    def _handle_general_query(self, query: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """处理通用查询"""
        fallback_response = {
            "type": "general_response",
            "message": "I specialize in academic planning for XJTLU Economics students. Try asking about specific subject areas like:",
            "suggestions": [
                "Explain courses related to 'fin' for HKU MFWM preparation",
                "Plan my semester with 'eco' and 'stat' courses",
                "How do 'sustain' courses align with family wealth management careers?",
                "Check prerequisites for advanced econometrics courses",
                "Assess my current academic workload"
            ],
            "available_subjects": list(self.SUBJECT_KEYWORDS.keys()),
            "academic_year": user_context.get("academic_year", "2025-2026")
        }
        
        return fallback_response