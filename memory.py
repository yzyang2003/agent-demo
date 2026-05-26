"""
MemoryManager - 对话记忆管理器
实现对话摘要和主题追踪功能
"""

from typing import Optional


class MemoryManager:
    """对话记忆管理器，支持自动摘要和主题追踪"""

    # 主题关键词映射
    TOPIC_KEYWORDS = {
        "减脂": "健身",
        "增肌": "健身",
        "减肥": "健身",
        "健身": "健身",
        "运动": "健身",
        "跑步": "健身",
        "旅游": "旅游",
        "旅行": "旅游",
        "景点": "旅游",
        "酒店": "旅游",
        "机票": "旅游",
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

    def add_message(self, role: str, content: str) -> None:
        """
        添加消息到历史记录

        Args:
            role: 消息角色 ("user" 或 "assistant")
            content: 消息内容
        """
        self._messages.append({"role": role, "content": content})

        # 从用户消息中提取主题
        if role == "user":
            self._extract_topics(content)

        # 当消息超过10条时自动摘要
        if len(self._messages) > 10:
            self._summarize()

    def get_context_messages(self) -> list[dict[str, str]]:
        """
        获取用于LLM上下文的消息列表

        Returns:
            消息列表，可能包含摘要消息
        """
        if self._summary:
            # 返回摘要 + 最近6条消息
            summary_msg = {"role": "system", "content": f"对话摘要：{self._summary}"}
            recent_messages = self._messages[-6:]
            return [summary_msg] + recent_messages
        else:
            return self._messages.copy()

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

    def _extract_topics(self, content: str) -> None:
        """
        从用户消息中提取主题

        Args:
            content: 用户消息内容
        """
        for keyword, topic in self.TOPIC_KEYWORDS.items():
            if keyword in content and topic not in self._topics:
                self._topics.append(topic)

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
