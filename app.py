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
        "system_prompt": (
            "你是「长沙旅游助手」，一位热情、专业的长沙本地旅游顾问。\n"
            "你的职责是：\n"
            "1. 根据知识库中的资料，为用户推荐长沙的景点、美食和文化体验。\n"
            "2. 帮助用户规划行程路线，提供实用的交通和住宿建议。\n"
            "3. 回答关于长沙历史、文化、天气等方面的问题。\n"
            "4. 如果用户询问天气信息，请结合天气工具的结果给出出行建议。\n\n"
            "请用亲切、活泼的语气回答，适当使用 emoji 让回复更生动。"
        ),
    },
    "fitness": {
        "label": "💪 健身顾问",
        "knowledge_file": "fitness.txt",
        "system_prompt": (
            "你是「健身顾问」，一位专业、负责的健身教练和营养师。\n"
            "你的职责是：\n"
            "1. 根据知识库中的资料，为用户解答健身、运动和营养方面的问题。\n"
            "2. 帮助用户制定合理的训练计划和饮食方案。\n"
            "3. 解答关于增肌、减脂、体态矫正等方面的问题。\n"
            "4. 如果用户询问 BMI 相关信息，请结合 BMI 工具的结果给出专业建议。\n\n"
            "请用专业但易懂的语气回答，注意安全提醒。"
        ),
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

st.title("🤖 AI Agent Demo")

# ---------------------------------------------------------------------------
# 侧边栏：场景选择
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ 设置")

    scene_key = st.radio(
        "选择业务场景",
        options=list(SCENES.keys()),
        format_func=lambda k: SCENES[k]["label"],
        key="scene_radio",
    )

    st.divider()
    st.caption("💡 切换场景将清空对话历史")

    # API 状态
    if not API_KEY:
        st.warning("⚠️ 未检测到 API_KEY，请在 .env 文件中配置")
    else:
        st.success(f"✅ 模型：{MODEL_NAME}")

# ---------------------------------------------------------------------------
# 会话状态初始化
# ---------------------------------------------------------------------------
if "scene" not in st.session_state:
    st.session_state.scene = scene_key
    st.session_state.messages = [{"role": "system", "content": SCENES[scene_key]["system_prompt"]}]

# 场景切换检测：清空对话历史
if scene_key != st.session_state.scene:
    st.session_state.scene = scene_key
    st.session_state.messages = [{"role": "system", "content": SCENES[scene_key]["system_prompt"]}]
    st.rerun()

# 当前场景配置
current_scene = SCENES[st.session_state.scene]

# ---------------------------------------------------------------------------
# 显示历史消息（跳过 system prompt）
# ---------------------------------------------------------------------------
for msg in st.session_state.messages:
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

    # 1. 显示用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. 处理逻辑
    with st.chat_message("assistant"):
        internal_steps = {}  # 收集内部步骤信息

        # 2a. 工具检测
        tool_name, tool_func = detect_tool(prompt, scene=st.session_state.scene)
        tool_result = None
        if tool_name and tool_func:
            tool_result = _call_tool(tool_name, tool_func, prompt)
            internal_steps["工具调用"] = f"**{tool_name}**\n\n{tool_result or '参数不足，未调用'}"

        # 2b. RAG 检索
        chunks = search(prompt, current_scene["knowledge_file"], top_k=3)
        if chunks:
            internal_steps["RAG 检索"] = "\n\n".join(
                f"📄 片段 {i+1}：{c[:200]}..." if len(c) > 200 else f"📄 片段 {i+1}：{c}"
                for i, c in enumerate(chunks)
            )
        else:
            internal_steps["RAG 检索"] = "未检索到相关内容"

        # 2c. 构建 Prompt
        rag_prompt = build_prompt(prompt, chunks)

        # 如果有工具结果，附加到 prompt
        if tool_result:
            rag_prompt += f"\n\n工具调用结果：\n{tool_result}\n\n请结合以上工具结果回答用户问题。"

        internal_steps["最终 Prompt"] = rag_prompt

        # 2d. 构建消息列表（排除 system，用场景 prompt 替代）
        messages_for_api = [
            {"role": "system", "content": current_scene["system_prompt"]},
            # 添加历史对话（跳过 system）
            *[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
                if m["role"] != "system"
            ],
            # 当前用户问题用 RAG 增强后的 prompt
            {"role": "user", "content": rag_prompt},
        ]

        # 2e. 流式调用 LLM
        try:
            response = _stream_chat(messages_for_api)
            full_response = st.write_stream(
                (chunk.choices[0].delta.content or "" for chunk in response if chunk.choices[0].delta.content)
            )
        except Exception as exc:
            full_response = f"❌ API 调用失败：{exc}"
            st.error(full_response)

        # 2f. 显示内部步骤
        with st.expander("🔍 内部步骤"):
            for step_name, step_content in internal_steps.items():
                st.subheader(step_name)
                if step_name == "RAG 检索" and isinstance(step_content, type(iter([]))):
                    # step_content 是生成器，需要消费
                    step_content = "\n\n".join(list(step_content))
                st.text(step_content if isinstance(step_content, str) else str(step_content))

        # 3. 保存助手回复
        st.session_state.messages.append({"role": "assistant", "content": full_response})
