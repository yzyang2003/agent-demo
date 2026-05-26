"""热量估算工具 - 估算食物的热量和营养成分"""

# 常见食物营养数据（每100g）：(热量kcal, 蛋白质g, 碳水g, 脂肪g)
FOOD_DATA = {
    "鸡胸肉": (165, 31, 0, 3.6),
    "牛肉": (250, 26, 0, 15),
    "鸡蛋": (155, 13, 1.1, 11),
    "米饭": (130, 2.7, 28, 0.3),
    "面条": (138, 4.5, 25, 2.1),
    "红薯": (86, 1.6, 20, 0.1),
    "西兰花": (34, 2.8, 7, 0.4),
    "苹果": (52, 0.3, 14, 0.2),
    "香蕉": (89, 1.1, 23, 0.3),
    "牛奶": (42, 3.4, 5, 1),
    "酸奶": (59, 10, 3.6, 0.7),
    "豆腐": (76, 8, 1.9, 4.8),
    "虾": (99, 24, 0.2, 0.3),
    "三文鱼": (208, 20, 0, 13),
    "燕麦": (389, 17, 66, 7),
    "全麦面包": (247, 13, 41, 3.4),
    "坚果": (607, 15, 22, 54),
    "橄榄油": (884, 0, 0, 100),
    "番茄": (18, 0.9, 3.9, 0.2),
    "黄瓜": (15, 0.7, 3.6, 0.1),
    "猪肉": (242, 27, 0, 14),
    "羊肉": (250, 26, 0, 16),
    "土豆": (77, 2, 17, 0.1),
    "玉米": (86, 3.2, 19, 1.2),
    "胡萝卜": (41, 0.9, 10, 0.2),
}

# 别名映射
FOOD_ALIASES = {
    "鸡肉": "鸡胸肉",
    "牛排": "牛肉",
    "蛋": "鸡蛋",
    "饭": "米饭",
    "面": "面条",
    "地瓜": "红薯",
    "花椰菜": "西兰花",
    "酸奶酪": "酸奶",
    "豆花": "豆腐",
    "大虾": "虾",
    "三文鱼刺身": "三文鱼",
    "麦片": "燕麦",
    "面包": "全麦面包",
    "果仁": "坚果",
    "西红柿": "番茄",
    "青瓜": "黄瓜",
}

DISCLAIMER = "热量数据仅供参考，实际数值可能因品牌和烹饪方式而异"


def _parse_portion(portion: str) -> float:
    """解析份量字符串，返回克数"""
    portion = portion.strip().lower()
    if "g" in portion:
        try:
            return float(portion.replace("g", "").strip())
        except ValueError:
            return 100
    if "kg" in portion:
        try:
            return float(portion.replace("kg", "").strip()) * 1000
        except ValueError:
            return 100
    if "斤" in portion:
        try:
            return float(portion.replace("斤", "").strip()) * 500
        except ValueError:
            return 100
    if "两" in portion:
        try:
            return float(portion.replace("两", "").strip()) * 50
        except ValueError:
            return 100
    try:
        return float(portion)
    except ValueError:
        return 100


def estimate_calorie(food: str, portion: str = "100g") -> dict:
    """
    估算食物的热量和营养成分

    Args:
        food: 食物名称，如"鸡胸肉"
        portion: 份量，默认"100g"，支持"g"、"kg"、"斤"、"两"

    Returns:
        包含热量、蛋白质、碳水、脂肪等信息的字典
    """
    if not food or not isinstance(food, str):
        return {"error": "请输入有效的食物名称"}

    food = food.strip()
    grams = _parse_portion(portion)
    if grams <= 0:
        return {"error": "份量必须大于0"}

    # 查找食物数据
    key = FOOD_ALIASES.get(food, food)
    if key in FOOD_DATA:
        cal, protein, carbs, fat = FOOD_DATA[key]
        ratio = grams / 100
        notes = f"{food}的常见营养数据（每100g）"
    else:
        # 未知食物返回估算值
        cal, protein, carbs, fat = 100, 5, 15, 3
        ratio = grams / 100
        notes = f"未找到「{food}」的精确数据，以上为粗略估算，请以实际包装标注为准"

    return {
        "food": food,
        "portion": f"{grams}g",
        "calories": f"约{round(cal * ratio, 1)}千卡",
        "protein": f"约{round(protein * ratio, 1)}克",
        "carbs": f"约{round(carbs * ratio, 1)}克",
        "fat": f"约{round(fat * ratio, 1)}克",
        "notes": notes,
        "disclaimer": DISCLAIMER,
    }


# 工具描述信息（用于Agent工具调用）
TOOL_DESCRIPTION = {
    "name": "estimate_calorie",
    "description": "估算食物的热量和营养成分，支持20多种常见食物",
    "parameters": {
        "type": "object",
        "properties": {
            "food": {
                "type": "string",
                "description": "食物名称，如鸡胸肉、牛肉、米饭"
            },
            "portion": {
                "type": "string",
                "description": "份量，默认100g，支持如200g、1斤等格式"
            }
        },
        "required": ["food"]
    }
}
