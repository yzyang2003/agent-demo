"""
MemoryManager - 对话记忆管理器
实现对话摘要、主题追踪和实体提取功能
"""

import re
from typing import Optional


class MemoryManager:
    """对话记忆管理器，支持自动摘要、主题追踪和实体提取"""

    # 主题关键词映射
    TOPIC_KEYWORDS = {
        "减脂": "健身",
        "增肌": "健身",
        "减肥": "健身",
        "健身": "健身",
        "运动": "健身",
        "跑步": "健身",
        "体重": "健身",
        "身高": "健身",
        "bmi": "健身",
        "BMI": "健身",
        "训练": "健身",
        "营养": "健身",
        "热量": "健身",
        "卡路里": "健身",
        "旅游": "旅游",
        "旅行": "旅游",
        "景点": "旅游",
        "酒店": "旅游",
        "机票": "旅游",
        "行程": "旅游",
        "签证": "签证",
        "护照": "签证",
        "美食": "美食",
        "餐厅": "美食",
        "小吃": "美食",
        "住宿": "住宿",
        "民宿": "住宿",
        "交通": "交通",
        "地铁": "交通",
        "公交": "交通",
        "打车": "交通",
        "购物": "购物",
        "免税店": "购物",
        "退税": "购物",
        "预算": "预算",
        "花费": "预算",
        "便宜": "预算",
    }

    def __init__(self):
        """初始化记忆管理器"""
        self._messages: list[dict[str, str]] = []
        self._summary: Optional[str] = None
        self._topics: list[str] = []
        self._entities: dict[str, str] = {}  # 存储提取的实体

    def add_message(self, role: str, content: str) -> None:
        """
        添加消息到历史记录

        Args:
            role: 消息角色 ("user" 或 "assistant")
            content: 消息内容
        """
        self._messages.append({"role": role, "content": content})

        # 从用户消息中提取主题和实体
        if role == "user":
            self._extract_topics(content)
            self._extract_entities(content)

        # 当消息超过10条时自动摘要
        if len(self._messages) > 10:
            self._summarize()

    def get_context_messages(self) -> list[dict[str, str]]:
        """
        获取用于LLM上下文的消息列表

        Returns:
            消息列表，可能包含摘要消息
        """
        result = []

        # 如果有摘要，添加摘要消息
        if self._summary:
            result.append({"role": "system", "content": f"对话摘要：{self._summary}"})

        # 如果有实体数据，添加实体摘要
        if self._entities:
            entity_summary = "用户已提供的数据：" + "，".join(
                f"{k}={v}" for k, v in self._entities.items()
            )
            result.append({"role": "system", "content": entity_summary})

        # 添加最近的消息
        recent_messages = self._messages[-6:] if self._summary else self._messages
        result.extend(recent_messages)

        return result

    def get_summary(self) -> Optional[str]:
        """
        获取对话摘要

        Returns:
            摘要字符串，如果还没有摘要则返回None
        """
        return self._summary

    def get_topics(self) -> list[str]:
        """
        获取用户关注的主题

        Returns:
            主题列表
        """
        return self._topics.copy()

    def get_entities(self) -> dict[str, str]:
        """
        获取提取的实体数据

        Returns:
            实体字典
        """
        return self._entities.copy()

    def _extract_topics(self, content: str) -> None:
        """
        从用户消息中提取主题

        Args:
            content: 用户消息内容
        """
        for keyword, topic in self.TOPIC_KEYWORDS.items():
            if keyword in content and topic not in self._topics:
                self._topics.append(topic)

    def _extract_entities(self, content: str) -> None:
        """
        从用户消息中提取实体数据（体重、身高等）

        Args:
            content: 用户消息内容
        """
        # 提取体重
        weight_match = re.search(r"(\d+\.?\d*)\s*(?:kg|公斤|斤)", content)
        if weight_match:
            weight = float(weight_match.group(1))
            if "斤" in content:
                weight = weight / 2
            self._entities["体重"] = f"{weight}kg"

        # 提取身高
        height_match = re.search(r"(\d+\.?\d*)\s*(?:米|m|cm|厘米)", content)
        if height_match:
            height = float(height_match.group(1))
            if height > 100:  # 可能是厘米
                height = height / 100
            self._entities["身高"] = f"{height}m"

        # 提取BMI值
        bmi_match = re.search(r"bmi[是为：:]*\s*(\d+\.?\d*)", content.lower())
        if bmi_match:
            self._entities["BMI"] = bmi_match.group(1)

        # 提取训练目标
        goals = ["增肌", "减脂", "塑形", "体能"]
        for goal in goals:
            if goal in content:
                self._entities["训练目标"] = goal
                break

    def _summarize(self) -> None:
        """对早期消息进行摘要，保留最近6条消息"""
        # 提取需要摘要的早期消息
        messages_to_summarize = self._messages[:-6]

        # 简单摘要：提取关键信息
        summary_parts = []

        # 收集用户的主要问题
        user_questions = []
        for msg in messages_to_summarize:
            if msg["role"] == "user":
                user_questions.append(msg["content"][:50])  # 取前50字符

        if user_questions:
            summary_parts.append(f"用户询问了{len(user_questions)}个问题")

        # 收集主题
        if self._topics:
            summary_parts.append(f"主要话题：{'、'.join(self._topics)}")

        # 收集实体数据
        if self._entities:
            entity_info = "，".join(f"{k}={v}" for k, v in self._entities.items())
            summary_parts.append(f"用户数据：{entity_info}")

        # 生成摘要
        if summary_parts:
            new_summary = "；".join(summary_parts)

            # 如果已有摘要，合并
            if self._summary:
                self._summary = f"{self._summary}；{new_summary}"
            else:
                self._summary = new_summary

        # 只保留最近6条消息
        self._messages = self._messages[-6:]


# 便捷函数：创建MemoryManager实例
def create_memory_manager() -> MemoryManager:
    """创建并返回MemoryManager实例"""
    return MemoryManager()
