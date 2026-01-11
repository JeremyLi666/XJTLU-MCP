def summarize_plan(plan: dict) -> str:
    return (
        f"Recommended courses: {plan['recommended_courses']}\n"
        f"Workload score: {plan['workload_score']}\n"
        f"Risk level: {plan['risk_level']}"
    )
