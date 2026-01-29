from __future__ import annotations

import os

from dotenv import load_dotenv

from .agents.orchestrator import build_orchestrator_agent

load_dotenv()
DEFAULT_MODEL = os.getenv("LIFEOS_MODEL_NAME", "gemini-2.5-flash")

root_agent = build_orchestrator_agent(model=DEFAULT_MODEL)
