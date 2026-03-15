"""Conversation orchestration for chat-first behavior."""

from __future__ import annotations

from dataclasses import dataclass

from openpcb.agent.models import AgentTaskType


@dataclass
class ConversationDecision:
    action_route: AgentTaskType | None
    requires_confirmation: bool
    confirmed: bool
    reply_style: str
    user_goal: str
    payload: str = ""
    clarification: str | None = None


def _contains_any(text: str, keywords: tuple[str, ...]) -> bool:
    return any(word in text for word in keywords)


def decide_action(user_text: str, has_project: bool) -> ConversationDecision:
    """Map free-form text to a runtime action route."""
    text = user_text.strip()
    lowered = text.lower()
    if not text:
        return ConversationDecision(
            action_route=None,
            requires_confirmation=False,
            confirmed=False,
            reply_style="summary_then_details",
            user_goal="empty_input",
            clarification="Please describe what you want to do, for example: design an STM32 board with USB and LED.",
        )

    plan_keywords = ("plan", "design", "architecture", "方案", "规划", "设计")
    build_keywords = ("build", "generate files", "export", "构建", "导出", "生成文件")
    check_keywords = ("check", "risk", "rule", "erc", "drc", "检查", "风险", "规则")
    edit_keywords = ("edit", "update", "add", "remove", "replace", "modify", "修改", "增加", "删除", "替换")
    explain_keywords = ("explain", "what happened", "summary", "解释", "说明")

    if _contains_any(lowered, explain_keywords):
        return ConversationDecision(
            action_route=None,
            requires_confirmation=False,
            confirmed=False,
            reply_style="summary_then_details",
            user_goal="explain",
            clarification="You can ask me to plan, build, check, or edit. Example: 'check power risks' or 'add one LED'.",
        )

    if _contains_any(lowered, build_keywords):
        return ConversationDecision(
            action_route=AgentTaskType.BUILD,
            requires_confirmation=True,
            confirmed=False,
            reply_style="summary_then_details",
            user_goal="build_project",
        )

    if _contains_any(lowered, check_keywords):
        return ConversationDecision(
            action_route=AgentTaskType.CHECK,
            requires_confirmation=False,
            confirmed=True,
            reply_style="summary_then_details",
            user_goal="check_project",
        )

    if _contains_any(lowered, edit_keywords):
        return ConversationDecision(
            action_route=AgentTaskType.EDIT,
            requires_confirmation=True,
            confirmed=False,
            reply_style="summary_then_details",
            user_goal="edit_project",
            payload=text,
        )

    if _contains_any(lowered, plan_keywords) or not has_project:
        return ConversationDecision(
            action_route=AgentTaskType.PLAN,
            requires_confirmation=False,
            confirmed=True,
            reply_style="summary_then_details",
            user_goal="plan_project",
            payload=text,
        )

    return ConversationDecision(
        action_route=None,
        requires_confirmation=False,
        confirmed=False,
        reply_style="summary_then_details",
        user_goal="clarify",
        clarification="I am not sure which action to run. Try: 'check risks', 'build outputs', or 'add one LED'.",
    )
