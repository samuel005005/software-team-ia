from llm.llm_response import LLMResponse
from parsers.json_content import parse_json_content
from parsers.parser_error import ParserError
from review.review_result import ReviewResult

REVIEWER_AGENT_NAME = "Reviewer"


def _validate_score(score: Any) -> float:
    if isinstance(score, bool) or not isinstance(score, (int, float)):
        raise ParserError(
            "El campo 'score' es obligatorio y debe ser un número",
            agent_name=REVIEWER_AGENT_NAME,
        )

    normalized_score = float(score)
    if normalized_score < 0.0 or normalized_score > 1.0:
        raise ParserError(
            "El campo 'score' debe estar entre 0.0 y 1.0",
            agent_name=REVIEWER_AGENT_NAME,
        )
    return normalized_score


def parse(
    response: LLMResponse,
    *,
    reviewed_agent: str,
    objective: str = "",
) -> ReviewResult:
    data = parse_json_content(response.content)

    approved = data.get("approved")
    if not isinstance(approved, bool):
        raise ParserError(
            "El campo 'approved' es obligatorio y debe ser un booleano",
            agent_name=REVIEWER_AGENT_NAME,
        )

    score = _validate_score(data.get("score"))

    summary = data.get("summary")
    if not isinstance(summary, str) or not summary.strip():
        raise ParserError(
            "El campo 'summary' es obligatorio y debe ser un string no vacío",
            agent_name=REVIEWER_AGENT_NAME,
        )

    issues = data.get("issues", [])
    if not isinstance(issues, list) or not all(isinstance(item, str) for item in issues):
        raise ParserError(
            "El campo 'issues' debe ser una lista de strings",
            agent_name=REVIEWER_AGENT_NAME,
        )

    recommendations = data.get("recommendations", [])
    if not isinstance(recommendations, list) or not all(
        isinstance(item, str) for item in recommendations
    ):
        raise ParserError(
            "El campo 'recommendations' debe ser una lista de strings",
            agent_name=REVIEWER_AGENT_NAME,
        )

    return ReviewResult(
        reviewed_agent=reviewed_agent,
        approved=approved,
        score=score,
        summary=summary.strip(),
        issues=issues,
        recommendations=recommendations,
        metadata={
            "source": "reviewer_llm",
            "objective": objective,
            "provider": response.provider,
        },
    )
