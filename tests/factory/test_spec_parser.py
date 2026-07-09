from factory.spec_parser import extract_user_story, extract_user_stories, parse_story_ids

SAMPLE_SPEC = """
## Historias

### US-004 — Consultar barberos y disponibilidad

**Como** cliente, **quiero** ver barberos y horarios, **para** reservar.

**Criterios de aceptación:**
- [ ] Veo barberos que ofrecen el servicio elegido.
- [ ] Veo slots disponibles por fecha.

**Prioridad:** MVP

---

### US-005 — Reservar cita

**Como** cliente, **quiero** reservar, **para** asegurar mi turno.

**Prioridad:** MVP
"""


def test_parse_story_ids() -> None:
    assert parse_story_ids("US-004, US-005") == ["US-004", "US-005"]
    assert parse_story_ids(None) == []


def test_extract_user_story() -> None:
    block = extract_user_story(SAMPLE_SPEC, "US-004")
    assert block is not None
    assert "Consultar barberos" in block
    assert "Veo barberos que ofrecen el servicio" in block
    assert "US-005" not in block


def test_extract_user_stories_multiple() -> None:
    text = extract_user_stories(SAMPLE_SPEC, ["US-004", "US-005"])
    assert "US-004" in text
    assert "US-005" in text
