"""
Agent 引擎模块 - 多步推理流程编排

提供 AgentEngine 类，编排以下推理步骤：
1. 意图分析 (intent analysis)
2. 工具选择 (tool selection)
3. 工具执行 (tool execution)
4. 知识检索 (knowledge retrieval)
5. 总结 (summary)

不直接调用 LLM，仅负责编排和记录步骤。LLM 调用由 app.py 处理。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from tools import TOOLS, detect_tool

# NOTE: `from rag import search` is intentionally deferred to
# _retrieve_knowledge() to avoid triggering heavy ML model loading
# (sentence_transformers, torch) at import time.


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------
@dataclass
class AgentResponse:
    """Agent 引擎的处理结果。"""

    answer: str = ""
    """最终答案（由 app.py 调用 LLM 填充）。"""

    steps: list[dict] = field(default_factory=list)
    """推理步骤列表，每个元素包含 "name" 和 "content"。"""

    tool_calls: list[dict] = field(default_factory=list)
    """工具调用记录，每个元素包含 "tool_name"、"input"、"output"。"""

    context_chunks: list[str] = field(default_factory=list)
    """RAG 检索到的知识片段。"""


# ---------------------------------------------------------------------------
# Scene → knowledge file mapping
# ---------------------------------------------------------------------------
SCENE_KNOWLEDGE: dict[str, str] = {
    "tourism": "tourism.txt",
    "fitness": "fitness.txt",
}


# ---------------------------------------------------------------------------
# 参数提取函数（从用户查询中提取工具所需参数）
# ---------------------------------------------------------------------------
def _extract_itinerary_params(message: str) -> tuple[str | None, int | None]:
    """提取目的地和天数。"""
    days = None
    day_match = re.search(r"(\d+)\s*天", message)
    if day_match:
        days = int(day_match.group(1))

    known_destinations = [
        "三亚", "北京", "上海", "广州", "深圳", "成都", "杭州", "西安", "重庆", "武汉",
        "长沙", "南京", "苏州", "厦门", "青岛", "大连", "桂林", "昆明", "大理", "丽江",
        "张家界", "凤凰古城", "衡山", "韶山",
    ]
    destination = None
    for city in known_destinations:
        if city in message:
            destination = city
            break
    if not destination:
        match = re.search(r"(?:去|到)([\u4e00-\u9fa5]{2,4})(?:旅游|玩|行程)", message)
        if match:
            destination = match.group(1)
    return destination, days


def _extract_country(message: str) -> str | None:
    """提取国家名称。"""
    known_countries = [
        "日本", "韩国", "泰国", "新加坡", "马来西亚", "越南",
        "美国", "英国", "法国", "德国", "澳大利亚", "加拿大",
    ]
    for country in known_countries:
        if country in message:
            return country
    match = re.search(r"([\u4e00-\u9fa5]{2,4})(?:签证)", message)
    if match:
        return match.group(1)
    return None


def _extract_city(message: str) -> str:
    """提取城市名称。"""
    known_cities = ["长沙", "北京", "上海", "广州", "深圳", "成都", "杭州", "西安", "重庆", "武汉"]
    for city in known_cities:
        if city in message:
            return city
    match = re.search(r"([\u4e00-\u9fa5]{2,4})(?:的)?天气", message)
    if match:
        return match.group(1)
    return "长沙"


def _extract_bmi_params(message: str) -> tuple[float | None, float | None]:
    """提取体重(kg)和身高(m)。"""
    numbers = re.findall(r"\d+\.?\d*", message)
    weight, height = None, None
    if len(numbers) >= 2:
        nums = [float(n) for n in numbers]
        for n in nums:
            if n > 100 and weight is None:
                weight = n
            elif 0.5 < n < 3 and height is None:
                height = n
        if weight is None or height is None:
            weight = weight or nums[0]
            height = height or nums[1]
    elif len(numbers) == 1:
        weight = float(numbers[0])
    return weight, height


def _extract_calorie_params(message: str) -> tuple[str | None, str]:
    """提取食物名称和份量。"""
    known_foods = [
        "鸡胸肉", "牛肉", "鸡蛋", "米饭", "面条", "红薯", "西兰花", "苹果", "香蕉",
        "牛奶", "酸奶", "豆腐", "虾", "三文鱼", "燕麦", "坚果", "番茄", "黄瓜",
    ]
    food = None
    for f in known_foods:
        if f in message:
            food = f
            break
    if not food:
        match = re.search(r"([\u4e00-\u9fa5]{2,6})(?:的)?(?:热量|卡路里|多少卡)", message)
        if match:
            food = match.group(1)
    portion = "100g"
    portion_match = re.search(r"(\d+\.?\d*)\s*(g|kg|斤|两)", message)
    if portion_match:
        portion = portion_match.group(0)
    return food, portion


def _extract_workout_params(message: str) -> tuple[str | None, int]:
    """提取训练目标和时长。"""
    goals = ["增肌", "减脂", "塑形", "体能", "初学者"]
    goal = None
    for g in goals:
        if g in message:
            goal = g
            break
    if not goal:
        if any(kw in message for kw in ["长肌肉", "变壮", "力量"]):
            goal = "增肌"
        elif any(kw in message for kw in ["减肥", "瘦身", "脂肪"]):
            goal = "减脂"
        elif any(kw in message for kw in ["新手", "入门"]):
            goal = "初学者"
    duration = 60
    duration_match = re.search(r"(\d+)\s*(?:分钟|min)", message)
    if duration_match:
        duration = int(duration_match.group(1))
    return goal, duration


def _extract_nutrition_params(message: str) -> tuple[float | None, str | None]:
    """提取体重和目标。"""
    weight = None
    weight_match = re.search(r"(\d+\.?\d*)\s*(?:kg|公斤|斤)", message)
    if weight_match:
        weight = float(weight_match.group(1))
        if "斤" in message:
            weight = weight / 2
    if not weight:
        numbers = re.findall(r"\d+\.?\d*", message)
        for n in numbers:
            num = float(n)
            if 30 < num < 200:
                weight = num
                break
    goals = ["增肌", "减脂", "维持"]
    goal = None
    for g in goals:
        if g in message:
            goal = g
            break
    if not goal:
        if any(kw in message for kw in ["长肌肉", "变壮", "增重"]):
            goal = "增肌"
        elif any(kw in message for kw in ["减肥", "瘦身", "减重"]):
            goal = "减脂"
        elif any(kw in message for kw in ["保持", "维持"]):
            goal = "维持"
    return weight, goal


# ---------------------------------------------------------------------------
# Agent Engine
# ---------------------------------------------------------------------------
class AgentEngine:
    """多步推理 Agent 引擎。

    编排意图分析 → 工具选择 → 工具执行 → 知识检索 → 总结的完整流程，
    每一步记录到 steps 中供 UI 可视化。
    """

    def process(self, query: str, scene: str) -> AgentResponse:
        """处理用户查询，返回带完整推理步骤的响应。

        Args:
            query: 用户输入的问题。
            scene: 当前业务场景 (tourism / fitness)。

        Returns:
            包含推理步骤、工具调用记录和 RAG 上下文的 AgentResponse。
        """
        response = AgentResponse()

        # Step 1: 意图分析
        intent = self._analyze_intent(query, scene, response)

        # Step 2: 工具选择
        tool_name, tool_func = self._select_tool(query, scene, intent, response)

        # Step 3: 工具执行
        tool_output = self._execute_tool(query, tool_name, tool_func, response)

        # Step 4: 知识检索
        context_chunks = self._retrieve_knowledge(query, scene, response)

        # Step 5: 总结
        self._build_summary(query, scene, intent, tool_name, tool_output, context_chunks, response)

        return response

    # ------------------------------------------------------------------
    # Internal steps
    # ------------------------------------------------------------------

    def _analyze_intent(
        self, query: str, scene: str, response: AgentResponse
    ) -> dict:
        """Step 1: 分析用户意图。"""
        tool_keywords: list[str] = []
        for tool_info in TOOLS.values():
            if scene and tool_info["scene"] != scene:
                continue
            tool_keywords.extend(tool_info["keywords"])

        query_lower = query.lower()
        has_tool_intent = any(kw in query_lower for kw in tool_keywords)

        if has_tool_intent:
            intent_type = "tool_call"
        elif len(query) > 5:
            intent_type = "knowledge_question"
        else:
            intent_type = "general_chat"

        intent = {
            "type": intent_type,
            "keywords": [kw for kw in tool_keywords if kw in query_lower],
        }

        response.steps.append({
            "name": "意图分析",
            "content": (
                f"检测到意图类型：{intent_type}，"
                f"匹配关键词：{intent['keywords'] or '无'}"
            ),
        })
        return intent

    def _select_tool(
        self,
        query: str,
        scene: str,
        intent: dict,
        response: AgentResponse,
    ) -> tuple[str | None, object | None]:
        """Step 2: 选择合适的工具。"""
        tool_name, tool_func = None, None

        if intent["type"] == "tool_call":
            tool_name, tool_func = detect_tool(query, scene=scene)

        if tool_name:
            response.steps.append({
                "name": "工具选择",
                "content": f"已选择工具：{tool_name}",
            })
        else:
            response.steps.append({
                "name": "工具选择",
                "content": "未找到匹配工具，跳过工具调用",
            })

        return tool_name, tool_func

    def _execute_tool(
        self,
        query: str,
        tool_name: str | None,
        tool_func: object | None,
        response: AgentResponse,
    ) -> str | None:
        """Step 3: 执行选定的工具。"""
        if not tool_name or not tool_func:
            response.steps.append({
                "name": "工具执行",
                "content": "无工具需要执行",
            })
            return None

        try:
            result = self._call_tool_with_params(query, tool_name, tool_func)
            output = str(result)
        except Exception as exc:
            output = f"工具调用失败：{exc}"

        response.tool_calls.append({
            "tool_name": tool_name,
            "input": query,
            "output": output,
        })
        response.steps.append({
            "name": "工具执行",
            "content": f"工具 {tool_name} 返回结果：{output[:200]}",
        })
        return output

    def _call_tool_with_params(self, query: str, tool_name: str, tool_func) -> dict | None:
        """根据工具名称提取参数并调用工具。"""
        if tool_name == "get_weather":
            city = _extract_city(query)
            return tool_func(city)

        if tool_name == "calculate_bmi":
            weight, height = _extract_bmi_params(query)
            if weight and height:
                return tool_func(weight, height)
            return None

        if tool_name == "plan_itinerary":
            destination, days = _extract_itinerary_params(query)
            if destination and days:
                return tool_func(destination, days)
            return None

        if tool_name == "check_visa":
            country = _extract_country(query)
            if country:
                return tool_func(country)
            return None

        if tool_name == "estimate_calorie":
            food, portion = _extract_calorie_params(query)
            if food:
                return tool_func(food, portion)
            return None

        if tool_name == "generate_workout":
            goal, duration = _extract_workout_params(query)
            if goal:
                return tool_func(goal, duration)
            return None

        if tool_name == "get_nutrition_plan":
            weight, goal = _extract_nutrition_params(query)
            if weight and goal:
                return tool_func(weight, goal)
            return None

        # 未知工具，尝试直接调用
        return tool_func(query)

    def _retrieve_knowledge(
        self, query: str, scene: str, response: AgentResponse
    ) -> list[str]:
        """Step 4: RAG 知识检索。"""
        from rag import search  # lazy import to avoid heavy ML loading at module level

        knowledge_file = SCENE_KNOWLEDGE.get(scene, "tourism.txt")
        chunks = search(query, knowledge_file, top_k=3)

        if chunks:
            preview = " | ".join(c[:50] + "..." for c in chunks[:3])
            response.steps.append({
                "name": "知识检索",
                "content": f"检索到 {len(chunks)} 个相关片段：{preview}",
            })
        else:
            response.steps.append({
                "name": "知识检索",
                "content": "未检索到相关内容",
            })

        response.context_chunks = chunks
        return chunks

    def _build_summary(
        self,
        query: str,
        scene: str,
        intent: dict,
        tool_name: str | None,
        tool_output: str | None,
        context_chunks: list[str],
        response: AgentResponse,
    ) -> None:
        """Step 5: 汇总所有信息。"""
        parts: list[str] = []
        parts.append(f"用户问题：{query}")
        parts.append(f"场景：{scene}")
        parts.append(f"意图类型：{intent['type']}")

        if tool_name and tool_output:
            parts.append(f"工具 {tool_name} 结果：{tool_output[:200]}")

        if context_chunks:
            parts.append(f"RAG 上下文片段数：{len(context_chunks)}")
        else:
            parts.append("无 RAG 上下文")

        response.steps.append({
            "name": "总结",
            "content": "；".join(parts),
        })
