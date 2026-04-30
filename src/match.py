def calculate_match(resume_skills, jd_skills):
    """计算关键词精确匹配分，并找出重合与缺失的技能"""
    if not jd_skills:
        return 0, resume_skills, []

    resume_set = set(resume_skills)
    jd_set = set(jd_skills)

    matched_skills = sorted(list(resume_set & jd_set))  # 都会的
    missing_skills = sorted(list(jd_set - resume_set))  # JD要但你没有的

    # 评分公式：命中数量 / JD总要求数量
    score = len(matched_skills) / len(jd_skills) * 100
    return round(score, 2), matched_skills, missing_skills


def calculate_semantic_enhanced_match(
    jd_skills,
    exact_matched_skills,
    potential_matches,
    semantic_weight=0.6
):
    """
    计算语义增强匹配分。

    设计思想：
    1. 关键词精确命中：算 1 分
    2. 语义潜在匹配：算 0.6 分
    3. 最终分数仍由白盒规则计算，不让模型直接给分

    例子：
    JD 要求 5 个技能
    精确命中 Python、Git = 2 分
    语义匹配 Pandas = 0.6 分
    最终 = 2.6 / 5 * 100 = 52 分
    """
    if not jd_skills:
        return {
            "final_score": 0,
            "exact_score": 0,
            "semantic_bonus": 0,
            "exact_hit_count": 0,
            "semantic_hit_count": 0,
            "weighted_hit_count": 0,
            "total_required_count": 0,
        }

    jd_set = {skill.lower() for skill in jd_skills}
    exact_set = {skill.lower() for skill in exact_matched_skills}

    semantic_set = set()
    for item in potential_matches:
        skill = item["skill"].lower()

        # 只统计 JD 里要求过、且没有被精确命中的技能
        if skill in jd_set and skill not in exact_set:
            semantic_set.add(skill)

    exact_hit_count = len(exact_set)
    semantic_hit_count = len(semantic_set)

    weighted_hit_count = exact_hit_count + semantic_hit_count * semantic_weight
    total_required_count = len(jd_set)

    final_score = weighted_hit_count / total_required_count * 100
    exact_score = exact_hit_count / total_required_count * 100
    semantic_bonus = final_score - exact_score

    return {
        "final_score": round(final_score, 2),
        "exact_score": round(exact_score, 2),
        "semantic_bonus": round(semantic_bonus, 2),
        "exact_hit_count": exact_hit_count,
        "semantic_hit_count": semantic_hit_count,
        "weighted_hit_count": round(weighted_hit_count, 2),
        "total_required_count": total_required_count,
    }


def generate_suggestions(missing_skills):
    """根据缺失技能生成业务建议"""
    if not missing_skills:
        return ["🎉 技能点匹配良好！建议继续优化简历中项目的量化指标，例如准确率、数据规模、处理效率或业务结果。"]

    suggestions = []
    for skill in missing_skills:
        skill_lower = skill.lower()

        if skill_lower in ["sql", "mysql", "redis"]:
            suggestions.append(f"🔴 岗位需要 **{skill.upper()}**：建议补充数据库相关经历，或者去刷几道基础查询题防身。")
        elif skill_lower in ["rag", "langchain", "llm", "大模型"]:
            suggestions.append(f"🔥 岗位看重 **{skill.upper()}**：建议把你了解的大模型调用逻辑写进项目经历。")
        elif skill_lower in ["pytorch", "tensorflow", "cv", "深度学习"]:
            suggestions.append(
                f"🧠 岗位需要 **{skill.upper()}**：建议把你做过的相关课程实验，比如基于 YOLO 的目标检测，包装进简历。"
            )
        else:
            suggestions.append(f"💡 岗位要求 **{skill.upper()}**：建议在简历中补充相关的学习经历或工具使用场景。")

    return suggestions