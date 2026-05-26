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
            result = tool_func(query)
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
