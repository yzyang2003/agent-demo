"""营养方案推荐工具 - 根据体重和目标生成营养计划"""

DISCLAIMER = "营养方案仅供参考，具体请咨询专业营养师"

# 目标对应的热量和宏量营养素配置（每公斤体重）
GOAL_CONFIG = {
    "增肌": {
        "cal_per_kg": 38,  # 增肌期热量
        "protein_per_kg": 2.0,
        "fat_ratio": 0.25,  # 脂肪占总热量比例
    },
    "减脂": {
        "cal_per_kg": 28,  # 减脂期热量
        "protein_per_kg": 2.2,
        "fat_ratio": 0.25,
    },
    "维持": {
        "cal_per_kg": 33,  # 维持期热量
        "protein_per_kg": 1.6,
        "fat_ratio": 0.28,
    },
}

SUPPORTED_GOALS = list(GOAL_CONFIG.keys())

# 各目标的示例餐食
MEAL_PLANS = {
    "增肌": [
        {"meal": "早餐", "time": "7:00-8:00", "foods": "燕麦+鸡蛋3个+全麦面包+牛奶", "cal_ratio": 0.25},
        {"meal": "午餐", "time": "12:00-13:00", "foods": "米饭+鸡胸肉200g+西兰花+橄榄油拌菜", "cal_ratio": 0.30},
        {"meal": "加餐", "time": "15:00-16:00", "foods": "香蕉+坚果一把+酸奶", "cal_ratio": 0.15},
        {"meal": "晚餐", "time": "18:00-19:00", "foods": "红薯+三文鱼150g+蔬菜沙拉", "cal_ratio": 0.25},
        {"meal": "训练后", "time": "训练后30分钟", "foods": "蛋白粉+香蕉", "cal_ratio": 0.05},
    ],
    "减脂": [
        {"meal": "早餐", "time": "7:00-8:00", "foods": "鸡蛋2个+全麦面包1片+黄瓜", "cal_ratio": 0.25},
        {"meal": "午餐", "time": "12:00-13:00", "foods": "糙米饭少量+鸡胸肉150g+大量蔬菜", "cal_ratio": 0.35},
        {"meal": "加餐", "time": "15:00-16:00", "foods": "苹果1个或酸奶", "cal_ratio": 0.10},
        {"meal": "晚餐", "time": "18:00-19:00", "foods": "虾100g+豆腐+蔬菜汤", "cal_ratio": 0.30},
    ],
    "维持": [
        {"meal": "早餐", "time": "7:00-8:00", "foods": "燕麦粥+鸡蛋2个+水果", "cal_ratio": 0.25},
        {"meal": "午餐", "time": "12:00-13:00", "foods": "米饭+牛肉150g+蔬菜", "cal_ratio": 0.35},
        {"meal": "加餐", "time": "15:00-16:00", "foods": "坚果+酸奶", "cal_ratio": 0.10},
        {"meal": "晚餐", "time": "18:00-19:00", "foods": "面条+鸡蛋+蔬菜", "cal_ratio": 0.30},
    ],
}

TIPS = {
    "增肌": "增肌期注意训练后30分钟内补充蛋白质，每天分4-5餐进食，保证充足睡眠",
    "减脂": "减脂期不要过度节食，保持适度热量缺口（300-500千卡），多喝水，少油少盐",
    "维持": "维持期保持三餐规律，注意营养均衡，适量运动保持体能",
}


def get_nutrition_plan(weight_kg: float, goal: str) -> dict:
    """
    根据体重和目标生成营养方案

    Args:
        weight_kg: 体重（公斤）
        goal: 目标，支持：增肌、减脂、维持

    Returns:
        包含每日热量、宏量营养素和餐食计划的字典
    """
    if not isinstance(weight_kg, (int, float)) or weight_kg <= 0:
        return {"error": "请输入有效的体重（公斤）"}
    if weight_kg > 300:
        return {"error": "体重数据不合理，请检查输入"}

    if not goal or not isinstance(goal, str):
        return {"error": f"请输入目标，支持：{'、'.join(SUPPORTED_GOALS)}"}

    goal = goal.strip()
    if goal not in GOAL_CONFIG:
        return {"error": f"不支持的目标「{goal}」，支持：{'、'.join(SUPPORTED_GOALS)}"}

    config = GOAL_CONFIG[goal]

    # 计算每日热量和宏量营养素
    daily_calories = round(config["cal_per_kg"] * weight_kg)
    protein_g = round(config["protein_per_kg"] * weight_kg)
    fat_calories = daily_calories * config["fat_ratio"]
    fat_g = round(fat_calories / 9)
    remaining_calories = daily_calories - (protein_g * 4) - fat_g * 9
    carbs_g = round(remaining_calories / 4)

    # 生成餐食计划
    meals = MEAL_PLANS[goal]
    meal_plan = []
    for meal in meals:
        meal_cal = round(daily_calories * meal["cal_ratio"])
        meal_plan.append({
            "meal": meal["meal"],
            "time": meal["time"],
            "foods": meal["foods"],
            "approx_calories": f"约{meal_cal}千卡",
        })

    return {
        "weight": f"{weight_kg}公斤",
        "goal": goal,
        "daily_calories": f"约{daily_calories}千卡",
        "protein_g": f"约{protein_g}克",
        "carbs_g": f"约{carbs_g}克",
        "fat_g": f"约{fat_g}克",
        "meal_plan": meal_plan,
        "tips": TIPS[goal],
        "disclaimer": DISCLAIMER,
    }


# 工具描述信息（用于Agent工具调用）
TOOL_DESCRIPTION = {
    "name": "get_nutrition_plan",
    "description": "根据体重和目标生成个性化营养方案，包含每日热量、宏量营养素和餐食建议",
    "parameters": {
        "type": "object",
        "properties": {
            "weight_kg": {
                "type": "number",
                "description": "体重，单位：公斤，如70"
            },
            "goal": {
                "type": "string",
                "description": "目标：增肌、减脂、维持"
            }
        },
        "required": ["weight_kg", "goal"]
    }
}
