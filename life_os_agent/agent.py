from __future__ import annotations
import os
from dotenv import load_dotenv
from .agents.orchestrator import build_orchestrator_agent

from google.adk.models.lite_llm import LiteLlm


load_dotenv()
DEFAULT_MODEL = os.getenv("LIFEOS_MODEL_NAME", "gemini-2.5-flash")
#DEFAULT_MODEL = LiteLlm(
#    model=os.getenv("LIFEOS_MODEL_NAME", "ollama_chat/llama3.1:8b")
#)

root_agent = build_orchestrator_agent(model=DEFAULT_MODEL)