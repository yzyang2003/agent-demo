"""
AI Agent Demo - Streamlit 主应用

支持两种业务场景：
- 🏖️ 旅游助手：基于长沙旅游知识库的 RAG 问答
- 💪 健身顾问：基于健身知识库的 RAG 问答，支持 BMI 计算

启动方式：
    streamlit run app.py
"""

import os
import re

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from rag import build_prompt, search
from tools import detect_tool
from memory import MemoryManager
from agent import AgentEngine
from prompts import build_system_prompt, build_cot_prompt

# ---------------------------------------------------------------------------
# 环境变量（兼容本地 .env 和 Streamlit Cloud secrets）
# ---------------------------------------------------------------------------
load_dotenv()


def _get_config(key: str, default: str) -> str:
    """优先从 st.secrets 读取，其次从环境变量读取。"""
    try:
        return st.secrets[key]
    except (KeyError, FileNotFoundError):
        return os.getenv(key, default)


API_BASE_URL = _get_config("API_BASE_URL", "https://api.xiaomimimo.com/v1")
API_KEY = _get_config("API_KEY", "")
MODEL_NAME = _get_config("MODEL_NAME", "xiaomi-token-plan-cn/mimo-v2.5-pro")

# ---------------------------------------------------------------------------
# 场景配置
# ---------------------------------------------------------------------------
SCENES = {
    "tourism": {
        "label": "🏖️ 旅游助手",
        "knowledge_file": "tourism.txt",
    },
    "fitness": {
        "label": "💪 健身顾问",
        "knowledge_file": "fitness.txt",
    },
}

# ---------------------------------------------------------------------------
# 场景主题配置
# ---------------------------------------------------------------------------
SCENE_THEMES = {
    "tourism": {
        "primary": "#1E88E5",
        "accent": "#64B5F6",
        "light": "#E3F2FD",
        "border": "#90CAF9",
        "gradient": "linear-gradient(180deg, #0D47A1 0%, #1565C0 40%, #1E88E5 100%)",
        "header": "🏖️ 向上国际旅行社 · 旅游助手",
        "description": (
            "向上国际旅行社 AI 智能助手，为您提供长沙及全国旅游景点推荐、"
            "行程规划、签证办理、天气查询等一站式旅游咨询服务。"
        ),
        "tools": ["🌤️ 天气查询", "📋 行程规划", "🛂 签证查询", "📚 旅游知识问答"],
        "company": "湖南向上国际旅行社",
        "slogan": "让旅行更简单",
    },
    "fitness": {
        "primary": "#43A047",
        "accent": "#81C784",
        "light": "#E8F5E9",
        "border": "#A5D6A7",
        "gradient": "linear-gradient(180deg, #1B5E20 0%, #2E7D32 40%, #43A047 100%)",
        "header": "💪 健萌 WEGYMER · 健身顾问",
        "description": (
            "健萌 WEGYMER AI 健身顾问，为您提供 BMI 计算、个性化训练计划、"
            "营养方案、热量估算等专业健身指导服务。"
        ),
        "tools": ["📊 BMI 计算", "💪 训练计划", "🥗 营养方案", "🍎 热量估算", "📚 健身知识问答"],
        "company": "健萌 WEGYMER",
        "slogan": "科学健身，快乐生活",
    },
}


# ---------------------------------------------------------------------------
# 工具参数提取
# ---------------------------------------------------------------------------
def _extract_city(message: str) -> str:
    """从用户消息中提取城市名称。"""
    # 优先匹配常见城市名
    known_cities = ["长沙", "北京", "上海", "广州", "深圳", "成都", "杭州", "西安", "重庆", "武汉"]
    for city in known_cities:
        if city in message:
            return city
    # 尝试正则：XX的天气 / XX天气
    match = re.search(r"([\u4e00-\u9fa5]{2,4})(?:的)?天气", message)
    if match:
        return match.group(1)
    return "长沙"  # 默认


def _extract_bmi_params(message: str) -> tuple[float | None, float | None]:
    """从用户消息中提取体重(kg)和身高(m)。"""
    numbers = re.findall(r"\d+\.?\d*", message)
    weight, height = None, None
    if len(numbers) >= 2:
        # 启发式：大于 100 的是体重（kg），小于 3 的是身高（m）
        nums = [float(n) for n in numbers]
        for n in nums:
            if n > 100 and weight is None:
                weight = n
            elif 0.5 < n < 3 and height is None:
                height = n
        if weight is None or height is None:
            # 回退：第一个当体重，第二个当身高
            weight = weight or nums[0]
            height = height or nums[1]
    elif len(numbers) == 1:
        weight = float(numbers[0])
    return weight, height


def _extract_itinerary_params(message: str) -> tuple[str | None, int | None]:
    """从用户消息中提取目的地和天数。"""
    # 提取天数
    days = None
    day_match = re.search(r"(\d+)\s*天", message)
    if day_match:
        days = int(day_match.group(1))

    # 提取目的地
    known_destinations = [
        "三亚", "北京", "上海", "广州", "深圳", "成都", "杭州", "西安", "重庆", "武汉",
        "长沙", "南京", "苏州", "厦门", "青岛", "大连", "桂林", "昆明", "大理", "丽江",
    ]
    destination = None
    for city in known_destinations:
        if city in message:
            destination = city
            break

    # 尝试正则：去XX / XX旅游 / XX行程
    if not destination:
        match = re.search(r"(?:去|到)([\u4e00-\u9fa5]{2,4})(?:旅游|玩|行程)", message)
        if match:
            destination = match.group(1)

    return destination, days


def _extract_country(message: str) -> str | None:
    """从用户消息中提取国家名称。"""
    known_countries = [
        "日本", "韩国", "泰国", "新加坡", "马来西亚", "越南", "印度尼西亚",
        "美国", "英国", "法国", "德国", "意大利", "西班牙", "澳大利亚",
        "加拿大", "新西兰", "俄罗斯", "巴西", "印度", "菲律宾",
    ]
    for country in known_countries:
        if country in message:
            return country

    # 尝试正则：去XX / XX签证 / 去XX需要
    match = re.search(r"(?:去|到)([\u4e00-\u9fa5]{2,4})(?:签证|需要|要)", message)
    if match:
        return match.group(1)

    match = re.search(r"([\u4e00-\u9fa5]{2,4})(?:签证)", message)
    if match:
        return match.group(1)

    return None


def _extract_calorie_params(message: str) -> tuple[str | None, str]:
    """从用户消息中提取食物名称和份量。"""
    known_foods = [
        "鸡胸肉", "牛肉", "鸡蛋", "米饭", "面条", "红薯", "西兰花", "苹果", "香蕉",
        "牛奶", "酸奶", "豆腐", "虾", "三文鱼", "燕麦", "全麦面包", "坚果", "番茄",
        "黄瓜", "猪肉", "羊肉", "土豆", "玉米", "胡萝卜", "牛排", "蛋", "饭", "面",
    ]

    food = None
    for f in known_foods:
        if f in message:
            food = f
            break

    # 尝试正则：XX的热量 / XX多少卡
    if not food:
        match = re.search(r"([\u4e00-\u9fa5]{2,6})(?:的)?(?:热量|卡路里|多少卡)", message)
        if match:
            food = match.group(1)

    # 提取份量
    portion = "100g"
    portion_match = re.search(r"(\d+\.?\d*)\s*(g|kg|斤|两)", message)
    if portion_match:
        portion = portion_match.group(0)
    else:
        # 尝试匹配：一份、一个、一碗等
        simple_match = re.search(r"(一|二|三|四|五|\d+)\s*(个|份|碗|盘|块)", message)
        if simple_match:
            count_map = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5}
            count_str = simple_match.group(1)
            count = count_map.get(count_str, int(count_str) if count_str.isdigit() else 1)
            unit_map = {"个": 100, "份": 150, "碗": 200, "盘": 200, "块": 50}
            grams = count * unit_map.get(simple_match.group(2), 100)
            portion = f"{grams}g"

    return food, portion


def _extract_workout_params(message: str) -> tuple[str | None, int]:
    """从用户消息中提取训练目标和时长。"""
    goals = ["增肌", "减脂", "塑形", "体能", "初学者"]
    goal = None
    for g in goals:
        if g in message:
            goal = g
            break

    # 尝试模糊匹配
    if not goal:
        if any(kw in message for kw in ["长肌肉", "变壮", "力量"]):
            goal = "增肌"
        elif any(kw in message for kw in ["减肥", "瘦身", "脂肪"]):
            goal = "减脂"
        elif any(kw in message for kw in ["新手", "入门", "开始健身"]):
            goal = "初学者"

    # 提取时长
    duration = 60  # 默认60分钟
    duration_match = re.search(r"(\d+)\s*(?:分钟|min)", message)
    if duration_match:
        duration = int(duration_match.group(1))

    return goal, duration


def _extract_nutrition_params(message: str) -> tuple[float | None, str | None]:
    """从用户消息中提取体重和目标。"""
    # 提取体重
    weight = None
    weight_match = re.search(r"(\d+\.?\d*)\s*(?:kg|公斤|斤)", message)
    if weight_match:
        weight = float(weight_match.group(1))
        if "斤" in message:
            weight = weight / 2  # 斤转公斤

    # 如果没有明确体重，尝试从BMI参数中提取
    if not weight:
        numbers = re.findall(r"\d+\.?\d*", message)
        for n in numbers:
            num = float(n)
            if 30 < num < 200:  # 合理体重范围
                weight = num
                break

    # 提取目标
    goals = ["增肌", "减脂", "维持"]
    goal = None
    for g in goals:
        if g in message:
            goal = g
            break

    # 尝试模糊匹配
    if not goal:
        if any(kw in message for kw in ["长肌肉", "变壮", "增重"]):
            goal = "增肌"
        elif any(kw in message for kw in ["减肥", "瘦身", "减重"]):
            goal = "减脂"
        elif any(kw in message for kw in ["保持", "维持体重"]):
            goal = "维持"

    return weight, goal


# ---------------------------------------------------------------------------
# 工具调用
# ---------------------------------------------------------------------------
def _call_tool(tool_name: str, tool_func, message: str) -> str | None:
    """尝试调用工具并返回格式化结果。"""
    try:
        if tool_name == "get_weather":
            city = _extract_city(message)
            result = tool_func(city)
            return (
                f"🌤️ {result['city']}天气\n"
                f"温度：{result['temp']} | 天气：{result['weather']}\n"
                f"湿度：{result['humidity']} | 风力：{result['wind']}\n"
                f"空气质量：{result['aqi']}\n"
                f"💡 {result['tip']}"
            )

        if tool_name == "calculate_bmi":
            weight, height = _extract_bmi_params(message)
            if weight and height:
                result = tool_func(weight, height)
                if "error" in result:
                    return f"⚠️ {result['error']}"
                return (
                    f"📊 BMI 计算结果\n"
                    f"BMI：{result['bmi']}（{result['category']}）\n"
                    f"理想体重范围：{result['ideal_weight_range']}\n"
                    f"健康风险：{result['health_risk']}\n"
                    f"💡 建议：\n{result['advice']}"
                )
            return None  # 参数不足，让 LLM 处理

        if tool_name == "plan_itinerary":
            destination, days = _extract_itinerary_params(message)
            if destination and days:
                result = tool_func(destination, days)
                if "error" in result:
                    return f"⚠️ {result['error']}"
                # 格式化行程结果
                output = f"📋 {result.get('destination', destination)}{days}天行程规划\n"
                output += f"📅 最佳季节：{result.get('best_season', '全年')}\n"
                output += f"💰 预算参考：{result.get('budget', '待定')}\n\n"
                if "itinerary" in result:
                    for day_plan in result["itinerary"]:
                        output += f"--- Day {day_plan.get('day', '?')} ---\n"
                        output += f"🌅 上午：{day_plan.get('morning', '')}\n"
                        output += f"☀️ 下午：{day_plan.get('afternoon', '')}\n"
                        output += f"🌙 晚上：{day_plan.get('evening', '')}\n\n"
                if "food_highlights" in result:
                    output += f"🍜 美食推荐：{'、'.join(result['food_highlights'])}\n"
                if "tips" in result:
                    output += f"💡 小贴士：{result['tips']}\n"
                return output
            return None

        if tool_name == "check_visa":
            country = _extract_country(message)
            if country:
                result = tool_func(country)
                if "error" in result:
                    return f"⚠️ {result['error']}"
                output = f"🛂 {country}签证信息\n"
                output += f"是否需要签证：{'是' if result.get('visa_required') else '否'}\n"
                if result.get("visa_type"):
                    output += f"签证类型：{result['visa_type']}\n"
                if result.get("duration"):
                    output += f"停留时长：{result['duration']}\n"
                if result.get("requirements"):
                    output += f"所需材料：\n"
                    for req in result["requirements"]:
                        output += f"  • {req}\n"
                if result.get("processing_time"):
                    output += f"办理时间：{result['processing_time']}\n"
                if result.get("tips"):
                    output += f"💡 {result['tips']}\n"
                return output
            return None

        if tool_name == "estimate_calorie":
            food, portion = _extract_calorie_params(message)
            if food:
                result = tool_func(food, portion)
                if "error" in result:
                    return f"⚠️ {result['error']}"
                output = f"🍎 {result.get('food', food)}热量估算\n"
                output += f"📏 份量：{result.get('portion', portion)}\n"
                output += f"🔥 热量：{result.get('calories', '?')} kcal\n"
                output += f"🥩 蛋白质：{result.get('protein', '?')}g\n"
                output += f"🍚 碳水：{result.get('carbs', '?')}g\n"
                output += f"🧈 脂肪：{result.get('fat', '?')}g\n"
                if result.get("notes"):
                    output += f"📝 {result['notes']}\n"
                if result.get("disclaimer"):
                    output += f"⚠️ {result['disclaimer']}\n"
                return output
            return None

        if tool_name == "generate_workout":
            goal, duration = _extract_workout_params(message)
            if goal:
                result = tool_func(goal, duration)
                if "error" in result:
                    return f"⚠️ {result['error']}"
                output = f"💪 {goal}训练计划（{duration}分钟）\n\n"
                if "warmup" in result:
                    output += "🔥 热身：\n"
                    for ex in result["warmup"]:
                        output += f"  • {ex['name']} - {ex.get('duration', '')}\n"
                    output += "\n"
                if "main" in result:
                    output += "🏋️ 主训练：\n"
                    for ex in result["main"]:
                        output += f"  • {ex['name']} {ex['sets']}组×{ex['reps']}"
                        output += f"（休息{ex.get('rest_seconds', 60)}秒）"
                        output += f" - 目标：{ex.get('target_muscles', '')}\n"
                    output += "\n"
                if "cooldown" in result:
                    output += "🧘 放松：\n"
                    for ex in result["cooldown"]:
                        output += f"  • {ex['name']} - {ex.get('duration', '')}\n"
                    output += "\n"
                if "tips" in result:
                    output += f"💡 {result['tips']}\n"
                if "disclaimer" in result:
                    output += f"⚠️ {result['disclaimer']}\n"
                return output
            return None

        if tool_name == "get_nutrition_plan":
            weight, goal = _extract_nutrition_params(message)
            if weight and goal:
                result = tool_func(weight, goal)
                if "error" in result:
                    return f"⚠️ {result['error']}"
                output = f"🥗 {goal}营养方案（{weight}kg）\n\n"
                output += f"📊 每日热量：{result.get('daily_calories', '?')} kcal\n"
                output += f"🥩 蛋白质：{result.get('protein_g', '?')}g\n"
                output += f"🍚 碳水：{result.get('carbs_g', '?')}g\n"
                output += f"🧈 脂肪：{result.get('fat_g', '?')}g\n\n"
                if "meal_plan" in result:
                    output += "🍽️ 餐食计划：\n"
                    for meal in result["meal_plan"]:
                        output += f"  • {meal.get('meal', '')}（{meal.get('time', '')}）：{meal.get('foods', '')}\n"
                if "tips" in result:
                    output += f"\n💡 {result['tips']}\n"
                if "disclaimer" in result:
                    output += f"⚠️ {result['disclaimer']}\n"
                return output
            return None

    except Exception as exc:
        return f"⚠️ 工具调用失败：{exc}"

    return None


# ---------------------------------------------------------------------------
# LLM 调用
# ---------------------------------------------------------------------------
def _stream_chat(messages: list[dict]) -> str:
    """调用 OpenAI 兼容 API 并流式返回响应。"""
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        stream=True,
    )
    return response


# ---------------------------------------------------------------------------
# 页面配置
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Agent Demo",
    page_icon="🤖",
    layout="wide",
)

# ---------------------------------------------------------------------------
# 侧边栏：场景选择
# ---------------------------------------------------------------------------
with st.sidebar:
    # ---- 场景选择 ----
    scene_key = st.radio(
        "选择业务场景",
        options=list(SCENES.keys()),
        format_func=lambda k: SCENES[k]["label"],
        key="scene_radio",
    )

    theme = SCENE_THEMES[scene_key]

    # ---- 场景信息卡片 ----
    st.markdown(
        f"""
        <div style="
            background: {theme['gradient']};
            border-radius: 12px;
            padding: 16px 14px;
            margin-bottom: 12px;
            color: #fff;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        ">
            <div style="font-size:1.1em; font-weight:700; margin-bottom:6px;">
                {theme['header']}
            </div>
            <div style="font-size:0.82em; opacity:0.92; line-height:1.5;">
                {theme['description']}
            </div>
            <div style="
                margin-top:10px;
                font-size:0.78em;
                opacity:0.78;
                font-style:italic;
                text-align:right;
            ">
                — {theme['slogan']}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # ---- 可用工具 ----
    st.markdown("🔧 **可用工具**")
    for tool_name in theme["tools"]:
        st.markdown(f"&nbsp;&nbsp;• {tool_name}")

    st.divider()

    # ---- 清空对话按钮 ----
    if st.button("🗑️ 清空对话", use_container_width=True, key="clear_chat"):
        st.session_state.memory = MemoryManager()
        system_prompt = build_system_prompt(scene_key)
        st.session_state.memory.add_message("system", system_prompt)
        st.rerun()

    st.caption("💡 切换场景将自动清空对话历史")

    st.divider()

    # ---- 模型信息 ----
    st.markdown("⚙️ **系统信息**")
    if not API_KEY:
        st.warning("⚠️ 未检测到 API_KEY，请在 .env 文件中配置")
    else:
        st.caption(f"🤖 模型：`{MODEL_NAME}`")
    st.caption(f"🏢 {theme['company']}")

st.title(theme['header'])

# ---------------------------------------------------------------------------
# 会话状态初始化
# ---------------------------------------------------------------------------
if "scene" not in st.session_state:
    st.session_state.scene = scene_key
    st.session_state.memory = MemoryManager()
    # 使用 build_system_prompt 初始化系统消息
    system_prompt = build_system_prompt(scene_key)
    st.session_state.memory.add_message("system", system_prompt)

# 场景切换检测：清空对话历史
if scene_key != st.session_state.scene:
    st.session_state.scene = scene_key
    st.session_state.memory = MemoryManager()
    system_prompt = build_system_prompt(scene_key)
    st.session_state.memory.add_message("system", system_prompt)
    st.rerun()

# ---------------------------------------------------------------------------
# 场景主题 CSS 注入
# ---------------------------------------------------------------------------
_theme = SCENE_THEMES[scene_key]
st.markdown(
    f"""
    <style>
    /* ---- 页面标题颜色 ---- */
    h1 {{ color: {_theme['primary']}; }}

    /* ---- 助手消息左边框 ---- */
    div[data-testid="stChatMessage"] div[data-testid="stMarkdownContainer"]
        p:first-child {{
        border-left: 4px solid {_theme['primary']};
        padding-left: 10px;
    }}

    /* ---- 工具结果高亮框 ---- */
    .tool-box {{
        background: {_theme['light']};
        border: 1px solid {_theme['border']};
        border-radius: 8px;
        padding: 12px 14px;
        margin: 8px 0;
        font-size: 0.92em;
        line-height: 1.6;
    }}

    /* ---- 推理步骤 expander 美化 ---- */
    details[data-testid="stExpander"] summary {{
        font-weight: 600;
        color: {_theme['primary']};
    }}

    /* ---- 侧边栏按钮 ---- */
    div[data-testid="stSidebar"] div[data-testid="stButton"] button {{
        background-color: {_theme['primary']};
        color: #fff;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: opacity 0.2s;
    }}
    div[data-testid="stSidebar"] div[data-testid="stButton"] button:hover {{
        opacity: 0.88;
    }}
    div[data-testid="stSidebar"] div[data-testid="stButton"] button:active {{
        opacity: 0.75;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# 显示历史消息（跳过 system prompt）
# ---------------------------------------------------------------------------
for msg in st.session_state.memory.get_context_messages():
    if msg["role"] == "system":
        continue
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------------------------------------------------------------------
# 用户输入处理
# ---------------------------------------------------------------------------
if prompt := st.chat_input("请输入您的问题..."):
    # ---- 检查 API Key ----
    if not API_KEY:
        st.error("❌ 请先在 .env 文件中配置 API_KEY")
        st.stop()

    # 1. 显示用户消息并保存到记忆
    st.session_state.memory.add_message("user", prompt)
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. 处理逻辑
    with st.chat_message("assistant"):
        # 2a. 使用 AgentEngine 获取推理步骤和 RAG 上下文
        with st.spinner("🔍 正在检索知识库..."):
            agent_engine = AgentEngine()
            agent_response = agent_engine.process(prompt, st.session_state.scene)

        # 2b. 收集内部步骤（来自 AgentEngine）
        internal_steps = {}
        for step in agent_response.steps:
            internal_steps[step["name"]] = step["content"]

        # 2c. 使用 _call_tool 进行工具调用（支持参数提取）
        tool_name, tool_func = detect_tool(prompt, scene=st.session_state.scene)
        tool_result = None
        if tool_name and tool_func:
            with st.spinner("🔧 正在调用工具..."):
                tool_result = _call_tool(tool_name, tool_func, prompt)
            if tool_result:
                internal_steps["工具调用"] = f"**{tool_name}**\n\n{tool_result}"
            else:
                internal_steps["工具调用"] = f"**{tool_name}**\n\n参数不足，未调用"

        # 2d. RAG 检索结果（来自 AgentEngine）
        chunks = agent_response.context_chunks
        if chunks:
            internal_steps["RAG 检索"] = "\n\n".join(
                f"📄 片段 {i+1}：{c[:200]}..." if len(c) > 200 else f"📄 片段 {i+1}：{c}"
                for i, c in enumerate(chunks)
            )
        else:
            internal_steps["RAG 检索"] = "未检索到相关内容"

        # 2e. 使用 build_cot_prompt 构建 CoT 提示词
        context_text = "\n\n".join(chunks) if chunks else ""
        cot_prompt = build_cot_prompt(prompt, context_text)

        # 如果有工具结果，附加到 prompt
        if tool_result:
            cot_prompt += f"\n\n工具调用结果：\n{tool_result}\n\n请结合以上工具结果回答用户问题。"

        internal_steps["最终 Prompt"] = cot_prompt

        # 2f. 构建消息列表（使用 MemoryManager 管理历史）
        system_prompt = build_system_prompt(st.session_state.scene)
        messages_for_api = [
            {"role": "system", "content": system_prompt},
            # 使用 MemoryManager 获取上下文消息（跳过 system）
            *[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.memory.get_context_messages()
                if m["role"] != "system"
            ],
            # 当前用户问题用 CoT 增强后的 prompt
            {"role": "user", "content": cot_prompt},
        ]

        # 2g. 流式调用 LLM
        try:
            with st.spinner("🤖 AI 正在思考..."):
                response = _stream_chat(messages_for_api)
            full_response = st.write_stream(
                (chunk.choices[0].delta.content or "" for chunk in response if chunk.choices[0].delta.content)
            )
        except Exception as exc:
            full_response = f"❌ API 调用失败：{exc}"
            st.error(full_response)

        # 2h. 显示内部步骤（Agent 推理过程）
        with st.expander("🔍 Agent 推理步骤"):
            for step_name, step_content in internal_steps.items():
                st.subheader(step_name)
                if step_name == "RAG 检索" and isinstance(step_content, type(iter([]))):
                    # step_content 是生成器，需要消费
                    step_content = "\n\n".join(list(step_content))
                st.text(step_content if isinstance(step_content, str) else str(step_content))

        # 3. 保存助手回复到记忆
        st.session_state.memory.add_message("assistant", full_response)

# ---------------------------------------------------------------------------
# 页脚
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown(
    """
    <div style="text-align:center; padding:8px 0 16px; color:#999; font-size:0.82em;">
        Powered by <b>OpenCode</b> + <b>OMO Skills</b>
        &nbsp;|&nbsp;
        Built for 湖南向上国际旅行社 & 健萌 WEGYMER
    </div>
    """,
    unsafe_allow_html=True,
)
