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
        "scene": "tourism"  # 旅游场景
    },
    "plan_itinerary": {
        "function": plan_itinerary,
        "description": ITINERARY_TOOL_DESC,
        "keywords": ["行程", "旅游计划", "几天", "天行程", "玩几天", "路线"],
        "scene": "tourism"
    },
    "check_visa": {
        "function": check_visa,
        "description": VISA_TOOL_DESC,
        "keywords": ["签证", "出国", "出境", "护照"],
        "scene": "tourism"
    },
    "calculate_bmi": {
        "function": calculate_bmi,
        "description": BMI_TOOL_DESC,
        "keywords": ["bmi", "BMI", "体重指数", "身体质量指数", "胖", "瘦", "体重"],
        "scene": "fitness"  # 健身场景
    },
    "estimate_calorie": {
        "function": estimate_calorie,
        "description": CALORIE_TOOL_DESC,
        "keywords": ["卡路里", "热量", "千卡", "食物热量", "多少卡"],
        "scene": "fitness"
    },
    "generate_workout": {
        "function": generate_workout,
        "description": WORKOUT_TOOL_DESC,
        "keywords": ["训练计划", "健身计划", "怎么练", "训练安排", "锻炼"],
        "scene": "fitness"
    },
    "get_nutrition_plan": {
        "function": get_nutrition_plan,
        "description": NUTRITION_TOOL_DESC,
        "keywords": ["营养", "饮食", "吃什么", "食谱", "膳食", "蛋白质"],
        "scene": "fitness"
    }
}


def detect_tool(message: str, scene: str = None) -> tuple:
    """
    检测用户消息是否需要调用工具
    
    Args:
        message: 用户输入的消息
        scene: 当前场景（tourism/fitness），为None时不限制场景
        
    Returns:
        (tool_name, tool_function) 或 (None, None)
    """
    message_lower = message.lower()
    
    for tool_name, tool_info in TOOLS.items():
        # 如果指定了场景，只检测该场景的工具
        if scene and tool_info["scene"] != scene:
            continue
        
        # 检查关键词匹配
        for keyword in tool_info["keywords"]:
            if keyword in message_lower:
                return tool_name, tool_info["function"]
    
    return None, None
