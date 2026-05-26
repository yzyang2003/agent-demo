"""训练计划生成工具 - 根据目标和时长生成训练计划"""

DISCLAIMER = "训练计划仅供参考，请根据自身情况调整，如有伤病请咨询医生"

# 按目标分类的动作库
EXERCISES = {
    "增肌": {
        "warmup": [
            {"name": "开合跳", "duration": "2分钟"},
            {"name": "动态拉伸", "duration": "3分钟"},
            {"name": "空杆热身", "duration": "3分钟"},
        ],
        "main": [
            {"name": "杠铃深蹲", "sets": 4, "reps": "8-12", "rest_seconds": 90, "target_muscles": "股四头肌、臀大肌"},
            {"name": "杠铃卧推", "sets": 4, "reps": "8-12", "rest_seconds": 90, "target_muscles": "胸大肌、三角肌前束、肱三头肌"},
            {"name": "杠铃划船", "sets": 4, "reps": "8-12", "rest_seconds": 90, "target_muscles": "背阔肌、斜方肌"},
            {"name": "肩推", "sets": 3, "reps": "8-12", "rest_seconds": 75, "target_muscles": "三角肌"},
            {"name": "二头弯举", "sets": 3, "reps": "10-15", "rest_seconds": 60, "target_muscles": "肱二头肌"},
            {"name": "三头下压", "sets": 3, "reps": "10-15", "rest_seconds": 60, "target_muscles": "肱三头肌"},
        ],
        "cooldown": [
            {"name": "静态拉伸全身", "duration": "5分钟"},
        ],
        "tips": "增肌期每组做到接近力竭，组间休息充分，注意补充蛋白质",
    },
    "减脂": {
        "warmup": [
            {"name": "慢跑", "duration": "3分钟"},
            {"name": "动态拉伸", "duration": "2分钟"},
        ],
        "main": [
            {"name": "波比跳", "sets": 4, "reps": "10", "rest_seconds": 45, "target_muscles": "全身"},
            {"name": "高抬腿", "sets": 3, "reps": "30秒", "rest_seconds": 30, "target_muscles": "股四头肌、核心"},
            {"name": "登山者", "sets": 4, "reps": "20", "rest_seconds": 45, "target_muscles": "核心、肩部"},
            {"name": "深蹲跳", "sets": 3, "reps": "15", "rest_seconds": 45, "target_muscles": "腿部、臀部"},
            {"name": "俯卧撑", "sets": 3, "reps": "15", "rest_seconds": 30, "target_muscles": "胸部、三头肌"},
            {"name": "平板支撑", "sets": 3, "reps": "45秒", "rest_seconds": 30, "target_muscles": "核心"},
        ],
        "cooldown": [
            {"name": "慢走放松", "duration": "2分钟"},
            {"name": "静态拉伸", "duration": "3分钟"},
        ],
        "tips": "减脂期控制组间休息时间，保持心率在燃脂区间，配合饮食控制效果更佳",
    },
    "塑形": {
        "warmup": [
            {"name": "跳绳", "duration": "3分钟"},
            {"name": "动态拉伸", "duration": "2分钟"},
        ],
        "main": [
            {"name": "哑铃深蹲", "sets": 3, "reps": "12-15", "rest_seconds": 60, "target_muscles": "臀腿"},
            {"name": "哑铃臀桥", "sets": 3, "reps": "15", "rest_seconds": 60, "target_muscles": "臀大肌"},
            {"name": "哑铃飞鸟", "sets": 3, "reps": "12", "rest_seconds": 60, "target_muscles": "胸大肌"},
            {"name": "侧平举", "sets": 3, "reps": "15", "rest_seconds": 45, "target_muscles": "三角肌中束"},
            {"name": "弹力带划船", "sets": 3, "reps": "15", "rest_seconds": 45, "target_muscles": "背部"},
            {"name": "卷腹", "sets": 3, "reps": "20", "rest_seconds": 30, "target_muscles": "腹直肌"},
        ],
        "cooldown": [
            {"name": "瑜伽拉伸", "duration": "5分钟"},
        ],
        "tips": "塑形期以中等重量、多次数为主，注重动作控制和肌肉感受",
    },
    "体能": {
        "warmup": [
            {"name": "慢跑", "duration": "5分钟"},
            {"name": "动态拉伸", "duration": "3分钟"},
        ],
        "main": [
            {"name": "跑步间歇训练", "sets": 5, "reps": "400米", "rest_seconds": 120, "target_muscles": "心肺"},
            {"name": "跳箱", "sets": 4, "reps": "10", "rest_seconds": 60, "target_muscles": "腿部爆发力"},
            {"name": "战绳", "sets": 4, "reps": "30秒", "rest_seconds": 60, "target_muscles": "上肢、核心"},
            {"name": "农夫行走", "sets": 3, "reps": "40米", "rest_seconds": 60, "target_muscles": "握力、核心"},
            {"name": "壶铃摆荡", "sets": 4, "reps": "15", "rest_seconds": 60, "target_muscles": "后链、心肺"},
        ],
        "cooldown": [
            {"name": "慢走", "duration": "3分钟"},
            {"name": "全身拉伸", "duration": "5分钟"},
        ],
        "tips": "体能训练注意循序渐进，保证动作质量，避免过度训练导致受伤",
    },
    "初学者": {
        "warmup": [
            {"name": "原地踏步", "duration": "3分钟"},
            {"name": "关节活动", "duration": "2分钟"},
        ],
        "main": [
            {"name": "徒手深蹲", "sets": 3, "reps": "10", "rest_seconds": 60, "target_muscles": "腿部"},
            {"name": "跪姿俯卧撑", "sets": 3, "reps": "8-10", "rest_seconds": 60, "target_muscles": "胸部"},
            {"name": "弹力带辅助引体", "sets": 3, "reps": "6-8", "rest_seconds": 90, "target_muscles": "背部"},
            {"name": "哑铃推举", "sets": 3, "reps": "10", "rest_seconds": 60, "target_muscles": "肩部"},
            {"name": "平板支撑", "sets": 3, "reps": "20-30秒", "rest_seconds": 45, "target_muscles": "核心"},
        ],
        "cooldown": [
            {"name": "全身拉伸", "duration": "5分钟"},
        ],
        "tips": "初学者先掌握正确动作模式，不要急于上重量，建议每周训练3次",
    },
}

SUPPORTED_GOALS = list(EXERCISES.keys())


def generate_workout(goal: str, duration_minutes: int = 60) -> dict:
    """
    根据训练目标和时长生成训练计划

    Args:
        goal: 训练目标，支持：增肌、减脂、塑形、体能、初学者
        duration_minutes: 训练时长（分钟），默认60分钟

    Returns:
        包含完整训练计划的字典
    """
    if not goal or not isinstance(goal, str):
        return {"error": f"请输入训练目标，支持：{'、'.join(SUPPORTED_GOALS)}"}

    goal = goal.strip()
    if goal not in EXERCISES:
        return {"error": f"不支持的目标「{goal}」，支持：{'、'.join(SUPPORTED_GOALS)}"}

    if not isinstance(duration_minutes, (int, float)) or duration_minutes <= 0:
        return {"error": "训练时长必须为正数"}

    duration_minutes = int(duration_minutes)
    plan = EXERCISES[goal]

    # 根据时长调整动作数量
    exercises = plan["main"]
    if duration_minutes < 40:
        exercises = exercises[:3]
    elif duration_minutes < 50:
        exercises = exercises[:4]
    # >=50分钟用全部动作

    return {
        "goal": goal,
        "duration": f"{duration_minutes}分钟",
        "warmup": plan["warmup"],
        "workout_plan": exercises,
        "cooldown": plan["cooldown"],
        "tips": plan["tips"],
        "disclaimer": DISCLAIMER,
    }


# 工具描述信息（用于Agent工具调用）
TOOL_DESCRIPTION = {
    "name": "generate_workout",
    "description": "根据训练目标和时长生成个性化训练计划，支持增肌、减脂、塑形、体能、初学者",
    "parameters": {
        "type": "object",
        "properties": {
            "goal": {
                "type": "string",
                "description": "训练目标：增肌、减脂、塑形、体能、初学者"
            },
            "duration_minutes": {
                "type": "number",
                "description": "训练时长（分钟），默认60"
            }
        },
        "required": ["goal"]
    }
}
