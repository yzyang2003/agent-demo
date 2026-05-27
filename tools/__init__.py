"""工具模块 - 提供各种实用工具函数"""

from .weather import get_weather, TOOL_DESCRIPTION as WEATHER_TOOL_DESC
from .bmi import calculate_bmi, TOOL_DESCRIPTION as BMI_TOOL_DESC
from .itinerary import plan_itinerary, TOOL_DESCRIPTION as ITINERARY_TOOL_DESC
from .visa import check_visa, TOOL_DESCRIPTION as VISA_TOOL_DESC
from .calorie import estimate_calorie, TOOL_DESCRIPTION as CALORIE_TOOL_DESC
from .workout import generate_workout, TOOL_DESCRIPTION as WORKOUT_TOOL_DESC
from .nutrition import get_nutrition_plan, TOOL_DESCRIPTION as NUTRITION_TOOL_DESC


# 工具注册表 - 统一管理所有可用工具
TOOLS = {
    "get_weather": {
        "function": get_weather,
        "description": WEATHER_TOOL_DESC,
        "keywords": ["天气", "气温", "下雨", "温度", "weather"],
        "patterns": [r"(.{2,4})(?:的)?天气", r"天气(?:怎么样|如何|好吗)"],
        "scene": "tourism"
    },
    "plan_itinerary": {
        "function": plan_itinerary,
        "description": ITINERARY_TOOL_DESC,
        "keywords": ["行程", "旅游计划", "几天", "天行程", "玩几天", "路线", "攻略"],
        "patterns": [r"(.{2,4})(?:\d+天|\d+日)(?:行程|游|玩)", r"(?:去|到)(.{2,4})(?:旅游|玩)"],
        "scene": "tourism"
    },
    "check_visa": {
        "function": check_visa,
        "description": VISA_TOOL_DESC,
        "keywords": ["签证", "出国", "出境", "护照"],
        "patterns": [r"(.{2,4})(?:签证|入境)"],
        "scene": "tourism"
    },
    "calculate_bmi": {
        "function": calculate_bmi,
        "description": BMI_TOOL_DESC,
        "keywords": ["bmi", "BMI", "体重指数", "身体质量指数", "胖", "瘦"],
        "patterns": [r"(?:身高|体重).*?(?:身高|体重)", r"(?:bmi|BMI)"],
        "scene": "fitness"
    },
    "estimate_calorie": {
        "function": estimate_calorie,
        "description": CALORIE_TOOL_DESC,
        "keywords": ["卡路里", "热量", "千卡", "食物热量", "多少卡", "卡"],
        "patterns": [r"(.{2,6})(?:的)?(?:热量|卡路里)", r"(?:多少|含)(?:热量|卡)"],
        "scene": "fitness"
    },
    "generate_workout": {
        "function": generate_workout,
        "description": WORKOUT_TOOL_DESC,
        "keywords": ["训练计划", "健身计划", "怎么练", "训练安排", "锻炼", "训练"],
        "patterns": [r"(?:制定|生成|给).*(?:训练|锻炼)", r"(?:训练|锻炼)(?:计划|方案)"],
        "scene": "fitness"
    },
    "get_nutrition_plan": {
        "function": get_nutrition_plan,
        "description": NUTRITION_TOOL_DESC,
        "keywords": ["营养", "饮食", "吃什么", "食谱", "膳食", "蛋白质", "每天吃", "吃多少", "餐食", "一天吃"],
        "patterns": [r"(?:制定|生成|给).*(?:饮食|营养|餐)", r"(?:饮食|营养|餐食)(?:方案|计划)"],
        "scene": "fitness"
    }
}


def _fuzzy_match(message: str, keywords: list[str], threshold: int = 2) -> bool:
    """
    简单的模糊匹配 - 检查关键词是否部分匹配
    
    Args:
        message: 用户消息
        keywords: 关键词列表
        threshold: 最小匹配长度
        
    Returns:
        是否匹配
    """
    message_lower = message.lower()
    
    for keyword in keywords:
        keyword_lower = keyword.lower()
        # 完全匹配
        if keyword_lower in message_lower:
            return True
        # 部分匹配（关键词长度 >= threshold）
        if len(keyword) >= threshold:
            # 检查关键词的每个字符是否都在消息中出现（顺序）
            idx = 0
            for char in message_lower:
                if idx < len(keyword_lower) and char == keyword_lower[idx]:
                    idx += 1
            if idx == len(keyword_lower):
                return True
    
    return False


def detect_tool(message: str, scene: str = None) -> tuple:
    """
    检测用户消息是否需要调用工具
    
    Args:
        message: 用户输入的消息
        scene: 当前场景（tourism/fitness），为None时不限制场景
        
    Returns:
        (tool_name, tool_function) 或 (None, None)
    """
    import re
    
    message_lower = message.lower()
    
    for tool_name, tool_info in TOOLS.items():
        if scene and tool_info["scene"] != scene:
            continue
        
        # 1. 精确关键词匹配
        for keyword in tool_info["keywords"]:
            if keyword in message_lower:
                return tool_name, tool_info["function"]
        
        # 2. 正则模式匹配
        patterns = tool_info.get("patterns", [])
        for pattern in patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return tool_name, tool_info["function"]
        
        # 3. 模糊匹配（仅对长度 >= 3 的关键词）
        if _fuzzy_match(message, tool_info["keywords"]):
            return tool_name, tool_info["function"]
    
    return None, None
