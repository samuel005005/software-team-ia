from collections.abc import Callable

from context.agent_context import AgentContext
from llm.llm_request import LLMRequest

from . import analyst_prompt, architect_prompt, developer_prompt, qa_prompt

PromptBuilderFn = Callable[[AgentContext], LLMRequest]


class PromptBuilder:
    """Transforma AgentContext en LLMRequest delegando al template del agente."""

    _BUILDERS: dict[str, PromptBuilderFn] = {
        "Business Analyst": analyst_prompt.build,
        "Software Architect": architect_prompt.build,
        "Flutter Developer": developer_prompt.build,
        "QA Engineer": qa_prompt.build,
    }

    @classmethod
    def build(cls, context: AgentContext) -> LLMRequest:
        builder = cls._BUILDERS.get(context.agent_name)
        if builder is None:
            raise ValueError(
                f"No hay template de prompt para el agente: {context.agent_name}"
            )
        return builder(context)

    @staticmethod
    def for_analyst(context: AgentContext) -> LLMRequest:
        return analyst_prompt.build(context)

    @staticmethod
    def for_architect(context: AgentContext) -> LLMRequest:
        return architect_prompt.build(context)

    @staticmethod
    def for_developer(context: AgentContext) -> LLMRequest:
        return developer_prompt.build(context)

    @staticmethod
    def for_qa(context: AgentContext) -> LLMRequest:
        return qa_prompt.build(context)
