import re

_US_ID = re.compile(r"US-\d+")


def parse_story_ids(story_field: str | None) -> list[str]:
    if not story_field:
        return []
    return _US_ID.findall(story_field)


def extract_user_story(spec_md: str, story_id: str) -> str | None:
    """Extrae una historia de usuario completa desde docs/SPEC.md."""
    marker = f"### {story_id} —"
    start = spec_md.find(marker)
    if start == -1:
        return None

    rest = spec_md[start + len(marker) :]
    next_us = rest.find("\n### US-")
    next_h2 = rest.find("\n## ")
    candidates = [index for index in (next_us, next_h2) if index != -1]
    end = start + len(marker) + (min(candidates) if candidates else len(rest))
    return spec_md[start:end].strip()


def extract_user_stories(spec_md: str, story_ids: list[str]) -> str:
    blocks: list[str] = []
    for story_id in story_ids:
        block = extract_user_story(spec_md, story_id)
        if block:
            blocks.append(block)
    return "\n\n---\n\n".join(blocks)
