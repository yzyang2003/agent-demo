"""优化的提示词模板模块。

提供 Chain-of-Thought (CoT) 和 Few-shot 提示模板，
用于旅游助手和健身顾问两个场景。
"""


# ---------------------------------------------------------------------------
# 场景角色定义
# ---------------------------------------------------------------------------
_SCENE_ROLES = {
    "tourism": {
        "role": (
            "你是「向上国际旅行社」的资深旅游顾问，专注于长沙本地旅游服务。"
        ),
        "responsibilities": (
            "你的职责：\n"
            "1. 根据参考资料为用户推荐长沙景点、美食和文化体验。\n"
            "2. 帮助用户规划行程路线，提供交通和住宿建议。\n"
            "3. 回答关于长沙历史、文化、天气等问题。\n"
            "4. 结合天气工具结果给出出行建议。"
        ),
        "style": "请用亲切、活泼的语气回答，适当使用 emoji 让回复更生动。",
    },
    "fitness": {
        "role": (
            "你是「健萌 WEGYMER」的专业健身教练兼营养师。"
        ),
        "responsibilities": (
            "你的职责：\n"
            "1. 根据参考资料为用户解答健身、运动和营养问题。\n"
            "2. 帮助用户制定训练计划和饮食方案。\n"
            "3. 解答增肌、减脂、体态矫正等问题。\n"
            "4. 结合 BMI 工具结果给出专业建议。"
        ),
        "style": "请用专业但易懂的语气回答，注意安全提醒。",
    },
}


# ---------------------------------------------------------------------------
# Few-shot 默认示例
# ---------------------------------------------------------------------------
_DEFAULT_EXAMPLES = {
    "tourism": [
        {
            "q": "长沙有什么好吃的？",
            "a": "长沙美食可多啦！推荐你试试：\n"
                "- 臭豆腐：坡子街的黑色经典最正宗\n"
                "- 糖油粑粑：金黄酥脆，甜而不腻\n"
                "- 口味虾：文和友的招牌，麻辣鲜香\n"
                "建议晚上去坡子街逛逛，边走边吃超满足！",
        },
        {
            "q": "两天时间怎么玩长沙？",
            "a": "两天长沙行程推荐：\n"
                "Day 1：橘子洲头 → 岳麓山 → 太平街\n"
                "Day 2：湖南省博物馆 → 坡子街 → 黄兴路步行街\n\n"
                "小贴士：橘子洲头建议坐地铁2号线，岳麓山穿舒适的鞋子哦！",
        },
    ],
    "fitness": [
        {
            "q": "新手怎么开始健身？",
            "a": "新手健身建议：\n"
                "1. 先做体能评估，了解自身基础\n"
                "2. 每周3次，每次45-60分钟\n"
                "3. 从复合动作开始：深蹲、硬拉、卧推\n"
                "4. 注意热身和拉伸，避免受伤\n\n"
                "建议找个教练带几节课，掌握正确动作模式。",
        },
        {
            "q": "减脂期饮食怎么安排？",
            "a": "减脂饮食要点：\n"
                "- 每日热量缺口300-500大卡\n"
                "- 蛋白质：每公斤体重1.6-2克\n"
                "- 碳水：选择粗粮，训练前后适当补充\n"
                "- 脂肪：坚果、牛油果、橄榄油\n\n"
                "别节食！合理饮食+运动才是长久之计。",
        },
    ],
}


# ---------------------------------------------------------------------------
# 公开接口
# ---------------------------------------------------------------------------
def build_system_prompt(scene: str, context: str = "") -> str:
    """构建系统提示词。

    Args:
        scene: 场景标识，'tourism' 或 'fitness'。
        context: 可选的额外上下文信息。

    Returns:
        系统提示词字符串。
    """
    cfg = _SCENE_ROLES.get(scene)
    if cfg is None:
        raise ValueError(f"未知场景: {scene}，支持: {list(_SCENE_ROLES.keys())}")

    parts = [cfg["role"], cfg["responsibilities"], cfg["style"]]

    if context:
        parts.append(f"\n参考资料：\n{context}")

    return "\n\n".join(parts)


def build_cot_prompt(query: str, context: str) -> str:
    """构建 Chain-of-Thought 提示词。

    引导模型按步骤思考，先分析问题、再查找资料、最后综合回答。

    Args:
        query: 用户问题。
        context: 检索到的参考资料。

    Returns:
        CoT 格式的提示词。
    """
    template = (
        "请按以下步骤思考并回答用户问题：\n\n"
        "1. 首先分析用户的问题，明确核心需求。\n"
        "2. 然后从参考资料中查找相关信息。\n"
        "3. 综合分析后给出结构化的回答。\n\n"
        "参考资料：\n"
        "{{context}}\n\n"
        "用户问题：\n"
        "{{query}}\n\n"
        "请按上述步骤逐步思考，最后给出完整回答："
    )
    return template.replace("{{context}}", context).replace("{{query}}", query)


def build_few_shot_prompt(
    query: str,
    context: str,
    examples: list | None = None,
    scene: str = "tourism",
) -> str:
    """构建 Few-shot 提示词。

    通过示例展示期望的回答格式和风格。

    Args:
        query: 用户问题。
        context: 检索到的参考资料。
        examples: 自定义示例列表，每项含 'q' 和 'a' 键。
                  若为 None 则使用场景默认示例。
        scene: 场景标识，用于选择默认示例。

    Returns:
        Few-shot 格式的提示词。
    """
    if examples is None:
        examples = _DEFAULT_EXAMPLES.get(scene, _DEFAULT_EXAMPLES["tourism"])

    example_block = "\n\n".join(
        f"用户：{ex['q']}\n助手：{ex['a']}" for ex in examples
    )

    template = (
        "请参考以下问答示例的格式和风格来回答用户问题。\n\n"
        "--- 示例 ---\n"
        "{examples}\n"
        "--- 示例结束 ---\n\n"
        "参考资料：\n"
        "{{context}}\n\n"
        "用户问题：\n"
        "{{query}}\n\n"
        "请参照示例格式回答："
    )
    return (
        template
        .replace("{examples}", example_block)
        .replace("{{context}}", context)
        .replace("{{query}}", query)
    )
