"""BMI计算工具 - 计算身体质量指数并给出健康建议"""


def calculate_bmi(weight: float, height: float) -> dict:
    """
    计算BMI值并给出健康建议
    
    Args:
        weight: 体重（公斤）
        height: 身高（米）
        
    Returns:
        包含BMI值、分类和建议的字典
    """
    # 参数验证
    if weight <= 0 or weight > 500:
        return {"error": "体重数据不合理，请输入有效的体重（公斤）"}
    if height <= 0 or height > 3:
        return {"error": "身高数据不合理，请输入有效的身高（米），如1.75"}
    
    # 计算BMI
    bmi = weight / (height ** 2)
    bmi = round(bmi, 2)
    
    # 判断BMI分类并给出建议
    if bmi < 18.5:
        category = "体重过轻"
        advice = "您的体重偏低，建议：\n1. 适当增加热量摄入，每天多吃300-500千卡\n2. 增加蛋白质摄入，每公斤体重1.6-2克\n3. 进行力量训练，增加肌肉量\n4. 规律作息，保证充足睡眠"
        health_risk = "营养不良、免疫力下降、骨质疏松风险增加"
    elif bmi < 24:
        category = "体重正常"
        advice = "您的体重在健康范围内，建议：\n1. 保持当前的饮食和运动习惯\n2. 每周进行3-5次运动\n3. 均衡饮食，多吃蔬果\n4. 定期体检，保持健康"
        health_risk = "低风险，继续保持"
    elif bmi < 28:
        category = "体重偏重"
        advice = "您的体重偏重，建议：\n1. 适当减少热量摄入，每天减少300-500千卡\n2. 增加有氧运动，如跑步、游泳，每周3-5次\n3. 减少高糖、高脂食物的摄入\n4. 控制晚餐份量，避免夜宵"
        health_risk = "心血管疾病、糖尿病风险增加"
    else:
        category = "肥胖"
        advice = "您的体重已达到肥胖标准，建议：\n1. 咨询医生或营养师，制定科学的减重计划\n2. 逐步减少热量摄入，不要节食\n3. 从低强度运动开始，逐渐增加运动量\n4. 定期监测血压、血糖、血脂"
        health_risk = "心血管疾病、糖尿病、关节疾病风险显著增加"
    
    # 理想体重范围（BMI 18.5-24）
    height_cm = height * 100
    ideal_weight_min = round(18.5 * (height ** 2), 1)
    ideal_weight_max = round(24 * (height ** 2), 1)
    
    return {
        "bmi": bmi,
        "category": category,
        "weight": weight,
        "height": height,
        "ideal_weight_range": f"{ideal_weight_min} - {ideal_weight_max} 公斤",
        "health_risk": health_risk,
        "advice": advice
    }


# 工具描述信息（用于Agent工具调用）
TOOL_DESCRIPTION = {
    "name": "calculate_bmi",
    "description": "计算BMI（身体质量指数）并给出健康建议，需要输入体重和身高",
    "parameters": {
        "type": "object",
        "properties": {
            "weight": {
                "type": "number",
                "description": "体重，单位：公斤，如70"
            },
            "height": {
                "type": "number",
                "description": "身高，单位：米，如1.75"
            }
        },
        "required": ["weight", "height"]
    }
}
