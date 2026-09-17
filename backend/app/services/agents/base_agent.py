"""
FinShield Base Micro-Agent
Handles ultra-lean LLM invocation, token telemetry recording,
and graceful offline fallback.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Tuple
from app.core.config import settings
from app.services.llm_client import call_llm

logger = logging.getLogger(__name__)

class BaseMicroAgent:
    def __init__(self, agent_id: str, prompt_file_name: str, domain_name: str, weight: float):
        self.agent_id = agent_id
        self.prompt_file_name = prompt_file_name
        self.domain_name = domain_name
        self.weight = weight
        self.prompt_config = self._load_prompt()

    def _load_prompt(self) -> Dict[str, Any]:
        p_path = settings.PROMPTS_DIR / "micro_agents" / self.prompt_file_name
        if p_path.exists():
            with open(p_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    async def execute(self, user_content: str, fallback_data: Dict[str, Any]) -> Tuple[Dict[str, Any], int, int]:
        """
        Executes the micro-agent with strictly scoped input context.
        Uses Gemini Pro / Claude if configured, otherwise falls back gracefully.
        Returns (result_dict, input_tokens, output_tokens).
        """
        system_prompt = self.prompt_config.get("system_prompt", "")
        
        parsed_res, inp, outp = await call_llm(
            system_prompt=system_prompt,
            user_prompt=user_content,
            max_tokens=256,
            temperature=settings.LLM_TEMPERATURE,
            json_mode=True
        )

        if parsed_res is not None and isinstance(parsed_res, dict):
            return parsed_res, inp, outp

        # Graceful Domain Fallback
        # Measure estimated tokens saved via offline/cached execution
        est_input = len(system_prompt.split()) + len(user_content.split())
        est_output = 80
        return fallback_data, est_input, est_output

    def provide_peer_consultation(
        self, requesting_agent_id: str, context_summary: str, consultation_reason: str
    ) -> Dict[str, Any]:
        """
        Provides a targeted, one-shot peer consultation response to another agent.
        Single round-trip only; strictly prohibited from initiating further consultations.
        """
        advisories = {
            "agent_aml": f"AML Peer Advisory: High-velocity structuring across transit corridors compounds money laundering risk under FATF R.10. Recommend mandatory source of funds check for {context_summary}.",
            "agent_cft": f"CFT Peer Advisory: Corridor transit connects with FATF monitored jurisdictions. Enhanced asset freezing checks recommended under FATF R.6.",
            "agent_fraud": f"Fraud Peer Advisory: Irrevocable payment window creates elevated Authorized Push Payment (APP) scam exposure under UK PSR 2024 rules. Recommend mandatory Confirmation of Payee.",
            "agent_compliance": f"Compliance Peer Advisory: Product requires formal statutory verification (CASP / TPRM) before launch. Operating without license triggers regulatory blocker under MiCA."
        }
        
        return {
            "consulting_agent": self.agent_id,
            "domain": self.domain_name,
            "target_case_context": context_summary,
            "reason_for_consultation": consultation_reason,
            "peer_advisory": advisories.get(self.agent_id, f"Peer advisory from {self.domain_name}: Review risk mitigation controls."),
            "score_adjustment_delta": 0.4
        }
