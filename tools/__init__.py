"""工具模块 - 提供各种实用工具函数"""

from .weather import get_weather, TOOL_DESCRIPTION as WEATHER_TOOL_DESC
from .bmi import calculate_bmi, TOOL_DESCRIPTION as BMI_TOOL_DESC


# 工具注册表 - 统一管理所有可用工具
TOOLS = {
    "get_weather": {
        "function": get_weather,
        "description": WEATHER_TOOL_DESC,
        "keywords": ["天气", "气温", "下雨", "温度", "weather"],
        "scene": "tourism"  # 旅游场景
    },
    "calculate_bmi": {
        "function": calculate_bmi,
        "description": BMI_TOOL_DESC,
        "keywords": ["bmi", "BMI", "体重指数", "身体质量指数", "胖", "瘦", "体重"],
        "scene": "fitness"  # 健身场景
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
