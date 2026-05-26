"""签证信息查询工具 - 提供各国签证政策和要求信息"""


def check_visa(country: str) -> dict:
    """
    查询中国公民前往指定国家的签证信息
    
    Args:
        country: 目标国家名称
        
    Returns:
        包含签证要求、所需材料、办理时间等信息的字典
    """
    # 参数验证
    if not country or not isinstance(country, str):
        return {"error": "请输入有效的国家名称"}
    
    # 签证信息数据库（模拟数据）
    visa_data = {
        "日本": {
            "visa_required": True,
            "visa_type": "旅游签证（单次/三年多次/五年多次）",
            "duration": "单次最长15天，多次每次最长30天",
            "requirements": [
                "有效期6个月以上的护照",
                "签证申请表",
                "2寸白底照片2张",
                "在职证明或营业执照复印件",
                "银行流水（近6个月，余额10万以上）",
                "机票和酒店预订单",
                "行程单"
            ],
            "processing_time": "5-7个工作日",
            "fee": "约200-400元（单次），约400-800元（多次）",
            "notes": "三年多次签证需首次访问冲绳或东北三县；五年多次无地区限制但要求更高收入证明"
        },
        "韩国": {
            "visa_required": True,
            "visa_type": "旅游签证（单次/五年多次）",
            "duration": "单次最长90天，多次每次最长90天",
            "requirements": [
                "有效期6个月以上的护照",
                "签证申请表",
                "2寸白底照片1张",
                "身份证复印件",
                "在职证明或学生证明",
                "银行流水（近6个月）",
                "机票和酒店预订单"
            ],
            "processing_time": "5-7个工作日",
            "fee": "约300-500元",
            "notes": "北京、上海等户籍可简化材料；持有OECD签证记录可申请多次"
        },
        "泰国": {
            "visa_required": False,
            "visa_type": "免签/落地签",
            "duration": "免签30天，落地签15天",
            "requirements": [
                "有效期6个月以上的护照",
                "往返机票行程单",
                "酒店预订确认",
                "落地签需携带10000泰铢现金（约2000元人民币）"
            ],
            "processing_time": "免签即时，落地签约30分钟",
            "fee": "免签免费，落地签2000泰铢（约400元）",
            "notes": "2024年起对中国游客实施免签政策；建议提前购买旅游保险"
        },
        "新加坡": {
            "visa_required": True,
            "visa_type": "电子签证（eVisa）",
            "duration": "最长35天，可停留30天",
            "requirements": [
                "有效期6个月以上的护照",
                "电子签证申请表",
                "2寸白底照片电子版",
                "在职证明",
                "银行流水（近3个月）",
                "机票和酒店预订单"
            ],
            "processing_time": "1-3个工作日",
            "fee": "约300元",
            "notes": "可通过指定旅行社代为申请；部分情况可能被要求面签"
        },
        "美国": {
            "visa_required": True,
            "visa_type": "B1/B2旅游商务签证",
            "duration": "有效期10年，每次停留最长6个月",
            "requirements": [
                "有效期6个月以上的护照",
                "DS-160在线申请表",
                "2寸白底照片",
                "签证费缴纳证明",
                "面签预约确认",
                "在职证明和收入证明",
                "房产证或车辆登记证（非必需但有帮助）",
                "行程计划"
            ],
            "processing_time": "面签后3-5个工作日",
            "fee": "约1120元（160美元）",
            "notes": "需要到美国使领馆面签；建议提前2-3个月预约；有拒签风险"
        },
        "英国": {
            "visa_required": True,
            "visa_type": "标准访客签证",
            "duration": "有效期2年/5年/10年，每次停留最长180天",
            "requirements": [
                "有效期6个月以上的护照",
                "在线申请表",
                "2寸白底照片",
                "在职证明和准假证明",
                "银行流水（近6个月）",
                "机票和酒店预订单",
                "行程计划",
                "户口本复印件"
            ],
            "processing_time": "15-20个工作日",
            "fee": "约900元（100英镑，6个月）",
            "notes": "需要到签证中心录指纹；建议提前1个月申请"
        },
        "法国": {
            "visa_required": True,
            "visa_type": "申根签证（短期旅游）",
            "duration": "最长90天",
            "requirements": [
                "有效期6个月以上的护照",
                "签证申请表",
                "2寸白底照片",
                "机票预订单",
                "酒店预订确认",
                "旅行保险（保额30万人民币以上）",
                "在职证明和营业执照",
                "银行流水（近6个月，余额5万以上）",
                "行程单"
            ],
            "processing_time": "5-10个工作日",
            "fee": "约600元（80欧元）",
            "notes": "申根签证可访问26个申根国家；建议向主要目的地国申请"
        },
        "澳大利亚": {
            "visa_required": True,
            "visa_type": "访客签证（600类别）",
            "duration": "有效期1年，每次停留最长90天",
            "requirements": [
                "有效期6个月以上的护照",
                "在线申请表",
                "2寸白底照片",
                "在职证明和准假信",
                "银行流水（近6个月）",
                "机票和酒店预订单",
                "户口本复印件",
                "房产证或车辆登记证"
            ],
            "processing_time": "10-15个工作日",
            "fee": "约750元（150澳元）",
            "notes": "可通过ImmiAccount在线申请；可能被要求体检"
        },
        "马来西亚": {
            "visa_required": False,
            "visa_type": "免签/eVISA电子签证",
            "duration": "免签30天",
            "requirements": [
                "有效期6个月以上的护照",
                "往返机票",
                "酒店预订确认",
                "足够旅费证明"
            ],
            "processing_time": "免签即时，eVISA约2个工作日",
            "fee": "免签免费，eVISA约160元",
            "notes": "2024年起对中国游客实施30天免签；入境时可能被要求出示返程机票"
        },
        "越南": {
            "visa_required": False,
            "visa_type": "免签/电子签证",
            "duration": "免签45天，电子签证90天",
            "requirements": [
                "有效期6个月以上的护照",
                "往返机票",
                "酒店预订确认",
                "电子签证需上传照片和护照信息页"
            ],
            "processing_time": "免签即时，电子签证约3个工作日",
            "fee": "免签免费，电子签证约160元",
            "notes": "2023年起对中国游客实施45天免签；电子签证可多次入境"
        }
    }
    
    # 查找国家信息
    country_key = country.strip()
    if country_key in visa_data:
        info = visa_data[country_key]
        return {
            "country": country_key,
            "visa_required": info["visa_required"],
            "visa_type": info["visa_type"],
            "duration": info["duration"],
            "requirements": info["requirements"],
            "processing_time": info["processing_time"],
            "fee": info["fee"],
            "notes": info["notes"]
        }
    
    # 未知国家返回通用建议
    return {
        "country": country,
        "visa_required": None,
        "visa_type": "请咨询当地使领馆",
        "duration": "请咨询当地使领馆",
        "requirements": [
            "建议准备有效期6个月以上的护照",
            "准备2寸白底照片",
            "准备在职证明和银行流水",
            "准备机票和酒店预订单"
        ],
        "processing_time": "请咨询当地使领馆",
        "fee": "请咨询当地使领馆",
        "notes": f"关于{country}的签证政策，请咨询中国驻该国使领馆或访问外交部领事服务网获取最新信息"
    }


# 工具描述信息（用于Agent工具调用）
TOOL_DESCRIPTION = {
    "name": "check_visa",
    "description": "查询中国公民前往指定国家的签证信息，包括是否需要签证、签证类型、所需材料、办理时间和费用",
    "parameters": {
        "type": "object",
        "properties": {
            "country": {
                "type": "string",
                "description": "目标国家名称，如：日本、韩国、泰国、美国、英国"
            }
        },
        "required": ["country"]
    }
}
