"""
FinShield Fraud & Push Payment Scams Specialist Micro-Agent
Laser-focused on fraud typologies, UK PSR APP Fraud mandatory reimbursement,
synthetic identities, and account takeover vectors.
"""

from typing import Dict, Any, Tuple
from app.services.agents.base_agent import BaseMicroAgent

class FraudSpecialistAgent(BaseMicroAgent):
    def __init__(self):
        super().__init__(
            agent_id="agent_fraud",
            prompt_file_name="fraud_agent_v1.0.json",
            domain_name="Fraud Risk",
            weight=0.25
        )

    async def evaluate_fraud(
        self,
        title: str,
        verification_speed: str,
        limits_desc: str,
        settlement_speed: str = "Instant"
    ) -> Tuple[Dict[str, Any], int, int]:
        """
        Token-Optimized Context: Passes strictly fraud & scam relevant parameters.
        """
        user_content = (
            f"Title: {title}\n"
            f"Verification: {verification_speed or 'Standard'}\n"
            f"Limits: {limits_desc or 'None'}\n"
            f"Settlement: {settlement_speed}"
        )

        t_lower = title.lower()

        # Calibrated domain fallback
        if "crypto" in t_lower or "usdt" in t_lower:
            fallback = {
                "score": 8.0, "confidence": 0.88,
                "framework_citation": "FinCEN 2026 Virtual Asset Fraud Advisory",
                "reasoning": "Pig butchering scams and crypto investment fraud victimize retail users with zero recall mechanisms.",
                "traceability_factors": ["Irreversible transfer (+3.5)", "Social engineering vulnerability (+3.5)"]
            }
        elif "mortgage" in t_lower or "green" in t_lower:
            fallback = {
                "score": 3.0, "confidence": 0.92,
                "framework_citation": "FCA MCOB Mortgage Conduct Rules",
                "reasoning": "Independent property valuation and solicitor conveyancing verification in place.",
                "traceability_factors": ["Independent valuation check (-2.0)"]
            }
        elif "faster" in t_lower or "pay" in t_lower or "p2p" in t_lower or "instant" in t_lower:
            fallback = {
                "score": 8.5, "confidence": 0.93,
                "framework_citation": "PSR APP Fraud Reimbursement 2024 / FCA Consumer Duty",
                "reasoning": "Irreversible instant execution creates extreme exposure to Authorised Push Payment (APP) scams with 50:50 firm liability.",
                "traceability_factors": ["Irrevocable execution (+3.5)", "No mandatory Confirmation of Payee (+3.0)"]
            }
        else:
            fallback = {
                "score": 8.0, "confidence": 0.89,
                "framework_citation": "FCA Consumer Duty 2023",
                "reasoning": "Social engineering and synthetic identity fraud vulnerabilities require preventative controls.",
                "traceability_factors": ["Synthetic identity risk (+3.0)", "No mandatory delay (+2.0)"]
            }

        return await self.execute(user_content, fallback)
