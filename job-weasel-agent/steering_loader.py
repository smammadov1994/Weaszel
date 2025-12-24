from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class SteeringPrinciples:
    """
    Minimal, actionable steering extracted from the repo steering docs.
    We keep this intentionally short so it can be injected into prompts cheaply.
    """

    safety: str
    efficiency: str
    reliability: str
    prompting: str


def load_steering_principles() -> SteeringPrinciples:
    """
    Load a compact steering summary.

    We do NOT attempt to fully parse markdown into a knowledge graph—just keep a
    short, stable set of principles aligned with the steering docs in repo root.
    """
    # Defaults (safe even if docs missing)
    safety = (
        "- Ask for confirmation before irreversible actions (payments, submits, deletes).\n"
        "- If CAPTCHA or strong bot-wall: pause and ask user for intervention or switch site."
    )
    efficiency = (
        "- Prefer batching actions (navigate + filter + open) to reduce LLM round-trips.\n"
        "- Avoid deliberate UI delays (highlights/waits) unless needed for reliability."
    )
    reliability = (
        "- Verify preconditions (logged in? correct page?) before acting.\n"
        "- If stuck: try 2–3 alternative approaches, then switch site or ask user."
    )
    prompting = (
        "- Be concrete: specify site, filters, output fields.\n"
        "- Keep context concise; only include what’s needed for the next step."
    )

    # If repo has steering docs, lightly incorporate their presence (no heavy parsing).
    # This is intentionally conservative to avoid slowdowns and brittle parsing.
    root = os.path.abspath(".")
    candidates = [
        os.path.join(root, "STEERING-PROMPTING.md"),
        os.path.join(root, "STEERING-PERFORMANCE.md"),
        os.path.join(root, "STEERING-RESISTANCE.md"),
    ]
    existing = [p for p in candidates if os.path.exists(p)]
    if existing:
        prompting += "\n- Follow repo steering docs when available."

    return SteeringPrinciples(safety=safety, efficiency=efficiency, reliability=reliability, prompting=prompting)


