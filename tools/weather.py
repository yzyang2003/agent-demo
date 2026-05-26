"""天气查询工具 - 提供城市天气信息查询功能"""

import random


def get_weather(city: str) -> dict:
    """
    获取城市天气信息
    
    Args:
        city: 城市名称
        
    Returns:
        包含天气信息的字典，包括温度、天气状况、湿度
    """
    # 基础天气数据（模拟数据，可接入真实天气API如和风天气、OpenWeatherMap）
    weather_data = {
        "长沙": {
            "temp": "28°C",
            "weather": "晴",
            "humidity": "65%",
            "wind": "南风3级",
            "aqi": "良",
            "tip": "适合外出游玩，注意防晒"
        },
        "北京": {
            "temp": "25°C",
            "weather": "多云",
            "humidity": "45%",
            "wind": "北风2级",
            "aqi": "轻度污染",
            "tip": "建议减少户外活动"
        },
        "上海": {
            "temp": "30°C",
            "weather": "阴",
            "humidity": "75%",
            "wind": "东风3级",
            "aqi": "优",
            "tip": "天气闷热，注意防暑"
        },
        "广州": {
            "temp": "32°C",
            "weather": "雷阵雨",
            "humidity": "85%",
            "wind": "南风2级",
            "aqi": "良",
            "tip": "有雨，出门记得带伞"
        },
        "深圳": {
            "temp": "31°C",
            "weather": "多云",
            "humidity": "80%",
            "wind": "西南风3级",
            "aqi": "优",
            "tip": "适合户外活动"
        },
        "成都": {
            "temp": "26°C",
            "weather": "阴",
            "humidity": "70%",
            "wind": "微风",
            "aqi": "良",
            "tip": "适合吃火锅的天气"
        },
    }
    
    # 如果城市在预设数据中，返回对应数据
    if city in weather_data:
        result = weather_data[city].copy()
        result["city"] = city
        return result
    
    # 否则返回模拟数据
    return {
        "city": city,
        "temp": f"{random.randint(20, 35)}°C",
        "weather": random.choice(["晴", "多云", "阴", "小雨"]),
        "humidity": f"{random.randint(40, 90)}%",
        "wind": "微风",
        "aqi": random.choice(["优", "良", "轻度污染"]),
        "tip": "天气信息仅供参考"
    }


# 工具描述信息（用于Agent工具调用）
TOOL_DESCRIPTION = {
    "name": "get_weather",
    "description": "查询指定城市的天气信息，包括温度、天气状况、湿度、风力等",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "要查询天气的城市名称，如：长沙、北京、上海"
            }
        },
        "required": ["city"]
    }
}
