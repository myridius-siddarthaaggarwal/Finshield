"""
FinShield Comprehensive Database Initialization & Benchmark Data Seeder
Seeds all 13 Users, 7 Realistic Benchmark Cases, Dimension Scores, Overrides,
Controls, Committee Votes, Immutable Audit Histories, and Token Logs.
"""

from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.db.session import engine, Base, SessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.case import (
    RiskCase, RiskDimensionScore, CaseControl, CommitteeVote,
    DecisionCondition, AuditEvent, TokenLog
)


def seed_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()
    try:
        # 1. SEED USERS
        default_pw = get_password_hash("finshield2026")

        users = [
            # Submitters
            User(email="priya.sharma@bank.com", hashed_password=default_pw, full_name="Priya Sharma", role=UserRole.SUBMITTER, division="Consumer Banking", title="Product Manager, Retail Banking"),
            User(email="arun.kumar@bank.com", hashed_password=default_pw, full_name="Arun Kumar", role=UserRole.SUBMITTER, division="Payments", title="Product Manager, Digital Payments"),
            User(email="vikram.singh@bank.com", hashed_password=default_pw, full_name="Vikram Singh", role=UserRole.SUBMITTER, division="Payments", title="Product Manager, Digital Assets"),
            User(email="meera.nair@bank.com", hashed_password=default_pw, full_name="Meera Nair", role=UserRole.SUBMITTER, division="Commercial Banking", title="Relationship Manager, Trade Finance"),
            User(email="rajesh.kapoor@bank.com", hashed_password=default_pw, full_name="Rajesh Kapoor", role=UserRole.SUBMITTER, division="Wealth Management", title="Head of Private Banking"),
            User(email="neha.gupta@bank.com", hashed_password=default_pw, full_name="Neha Gupta", role=UserRole.SUBMITTER, division="Consumer Banking", title="Product Manager, Retail Lending"),
            User(email="deepa.sharma@bank.com", hashed_password=default_pw, full_name="Deepa Sharma", role=UserRole.SUBMITTER, division="FCRM / Compliance", title="Head of Financial Crime Operations"),
            
            # Analysts
            User(email="rahul.mehta@bank.com", hashed_password=default_pw, full_name="Rahul Mehta", role=UserRole.ANALYST, division="FCRM / Compliance", title="Senior FCRM Risk Analyst"),
            User(email="priya.chandran@bank.com", hashed_password=default_pw, full_name="Priya Chandran", role=UserRole.ANALYST, division="FCRM / Compliance", title="Lead Compliance & AML Analyst"),
            
            # Risk Committee
            User(email="sunita.rao@bank.com", hashed_password=default_pw, full_name="Sunita Rao", role=UserRole.COMMITTEE_MEMBER, division="Executive Risk", title="Chief Risk Officer (CRO)"),
            User(email="james.lee@bank.com", hashed_password=default_pw, full_name="James Lee", role=UserRole.COMMITTEE_MEMBER, division="Executive Compliance", title="Chief Compliance Officer (CCO)"),
            User(email="anita.patel@bank.com", hashed_password=default_pw, full_name="Anita Patel", role=UserRole.COMMITTEE_MEMBER, division="Legal Counsel", title="Head of Financial Regulatory Legal"),
            
            # Admin
            User(email="admin@bank.com", hashed_password=default_pw, full_name="System Administrator", role=UserRole.ADMIN, division="Technology", title="FCRM Platform Architect")
        ]
        db.add_all(users)
        db.commit()

        # Helper map for submitter IDs
        user_map = {u.email: u.id for u in db.query(User).all()}

        # ----------------------------------------------------
        # CASE 1: QuickAccount (Consumer Banking)
        # ----------------------------------------------------
        c1 = RiskCase(
            case_number=1,
            title="QuickAccount — Instant Digital Account Opening",
            division="Consumer Banking",
            change_type="New Product Launch",
            submitter_id=user_map["priya.sharma@bank.com"],
            submitter_name="Priya Sharma",
            submitter_role="Product Manager, Retail Banking",
            what_requester_wants="Launch instant digital account opening. Customers verified in 60 seconds with no branch visit needed and no manual checks at onboarding. Open to ALL retail customers across domestic UK market.",
            target_geographies=["United Kingdom"],
            target_customers="All retail consumer applicants",
            verification_speed="Instant (60 seconds automated)",
            transaction_limits_desc="Unlimited standard current account privileges",
            real_world_context="Monzo fined £21.1M by FCA in 2026. Customer base grew tenfold but financial crime controls failed to keep pace with growth. System catches onboarding high-risk mule accounts before launch.",
            status="APPROVED_WITH_CONDITIONS",
            inherent_risk_score=8.4,
            inherent_risk_tier="CRITICAL",
            residual_risk_score=7.8,
            residual_risk_tier="CRITICAL",
            final_analyst_score=7.8,
            ai_confidence_overall=0.87,
            analyst_recommendation="APPROVE_WITH_CONDITIONS",
            final_outcome="APPROVED_WITH_CONDITIONS",
            committee_vote_result="3-0 Unanimous",
            time_taken_hours=26.0,
            old_process_days=18,
            time_saved_pct=93.0,
            is_audit_locked=True,
            created_at=datetime.now(timezone.utc) - timedelta(days=2),
            locked_at=datetime.now(timezone.utc) - timedelta(days=1)
        )
        db.add(c1)
        db.flush()

        # Dimension Scores Case 1
        db.add_all([
            RiskDimensionScore(
                case_id=c1.id, dimension_key="money_laundering", dimension_name="Money Laundering Risk", weight=0.35,
                ai_score=9.2, analyst_override_score=None, final_score=9.2, confidence=0.89,
                framework_citation="FATF Recommendation 10 (Customer Due Diligence)",
                reasoning="High volume onboarding with 60-second verification provides ideal vector for opening mule accounts without face-to-face or enhanced due diligence.",
                traceability_factors=["New digital onboarding (+2.8)", "60s instant verification (+2.1)", "Broad retail exposure (+1.9)", "No initial txn monitoring (+2.4)", "Basic KYC applied (-0.7)"]
            ),
            RiskDimensionScore(
                case_id=c1.id, dimension_key="terrorist_financing", dimension_name="Terrorist Financing Risk", weight=0.20,
                ai_score=8.0, analyst_override_score=None, final_score=8.0, confidence=0.82,
                framework_citation="FATF Recommendation 6 (Targeted Financial Sanctions)",
                reasoning="Rapid frictionless onboarding without automated fuzzy name screening allows sanctioned individuals or proxies to open accounts undetected.",
                traceability_factors=["Automated non-face-to-face onboarding (+3.2)", "Sanctions lookup buffer gap (+2.5)", "Basic KYC (-0.7)"]
            ),
            RiskDimensionScore(
                case_id=c1.id, dimension_key="fraud", dimension_name="Fraud Risk", weight=0.25,
                ai_score=8.5, analyst_override_score=7.8, final_score=7.8, confidence=0.91,
                framework_citation="FCA Consumer Duty 2023 / MLR 2017 Regulation 28",
                reasoning="60-second automated check exposes product to synthetic identity fraud rings. [Analyst Override applied: Device fingerprinting reduces risk to 7.8].",
                traceability_factors=["Synthetic identity vulnerability (+4.0)", "No manual review fallback (+2.5)", "Device fingerprinting confirmed (-1.2)"]
            ),
            RiskDimensionScore(
                case_id=c1.id, dimension_key="compliance", dimension_name="Regulatory & Compliance Risk", weight=0.20,
                ai_score=8.0, analyst_override_score=None, final_score=8.0, confidence=0.87,
                framework_citation="FCA 2026 Supervisory Letter on Fast Onboarding",
                reasoning="FCA explicitly warned retail banks in 2026 that rapid onboarding without risk-based controls constitutes a direct regulatory breach.",
                traceability_factors=["FCA 2026 warning alignment (+4.5)", "Lack of risk-based segmentation (+3.5)"]
            )
        ])

        # Controls Case 1
        db.add_all([
            CaseControl(case_id=c1.id, control_id="CTRL-KYC-BASIC", name="Basic KYC at signup", effectiveness=0.15, is_active=True, control_type="EXISTING", rationale="One-time onboarding check, lacks ongoing transaction monitoring."),
            CaseControl(case_id=c1.id, control_id="CTRL-KYC-RISK", name="Risk-Based KYC for flagged profiles", effectiveness=0.65, is_active=True, control_type="MANDATED_BY_COMMITTEE", rationale="Mandatory enhanced due diligence for high-risk flags."),
            CaseControl(case_id=c1.id, control_id="CTRL-TXN-LIMITS", name="£500/day limit for first 90 days", effectiveness=0.55, is_active=True, control_type="MANDATED_BY_COMMITTEE", rationale="Restricts cash muling capacity during probationary period."),
            CaseControl(case_id=c1.id, control_id="CTRL-TXN-MONITORING", name="Real-time transaction monitoring from Day 1", effectiveness=0.60, is_active=True, control_type="MANDATED_BY_COMMITTEE", rationale="Detects sudden velocity spikes immediately upon launch."),
            CaseControl(case_id=c1.id, control_id="CTRL-DEV-FINGERPRINT", name="Device & Network Fingerprinting", effectiveness=0.50, is_active=True, control_type="ADDED_BY_ANALYST", rationale="Confirmed with product team to mitigate synthetic identity fraud.")
        ])

        # Committee Votes Case 1
        db.add_all([
            CommitteeVote(case_id=c1.id, member_name="Sunita Rao", member_role="CRO", vote="APPROVE_WITH_CONDITIONS", rationale="Controls proposed are necessary and sufficient if implemented before launch. KYC gap is primary concern."),
            CommitteeVote(case_id=c1.id, member_name="James Lee", member_role="CCO", vote="APPROVE_WITH_CONDITIONS", rationale="Agree. Transaction limits for 90 days critical. Monthly monitoring report to FCRM mandatory."),
            CommitteeVote(case_id=c1.id, member_name="Anita Patel", member_role="Legal Counsel", vote="APPROVE_WITH_CONDITIONS", rationale="FCA 2026 supervisory letter makes clear enhanced CDD is mandatory. Legal confirms compliance plan.")
        ])

        # Conditions Case 1
        db.add_all([
            DecisionCondition(case_id=c1.id, condition_text="Risk-based KYC — enhanced for flagged profiles", is_mandatory=True, is_met=True),
            DecisionCondition(case_id=c1.id, condition_text="Transaction limit: £500/day for first 90 days", is_mandatory=True, is_met=True),
            DecisionCondition(case_id=c1.id, condition_text="Real-time transaction monitoring live from Day 1", is_mandatory=True, is_met=True),
            DecisionCondition(case_id=c1.id, condition_text="Device fingerprinting mandatory at launch", is_mandatory=True, is_met=True),
            DecisionCondition(case_id=c1.id, condition_text="Manual review for accounts flagged by AI screener", is_mandatory=True, is_met=True),
            DecisionCondition(case_id=c1.id, condition_text="Monthly AML report submitted to FCRM team", is_mandatory=True, is_met=False),
            DecisionCondition(case_id=c1.id, condition_text="Quarterly control effectiveness review scheduled", is_mandatory=True, is_met=False),
            DecisionCondition(case_id=c1.id, condition_text="FCA Consumer Duty compliance confirmed in writing", is_mandatory=True, is_met=True)
        ])

        # Audit Events Case 1
        db.add_all([
            AuditEvent(case_id=c1.id, event_type="SUBMISSION", actor_name="Priya Sharma", actor_role="Submitter", description="QuickAccount proposal submitted for FCRM assessment.", created_at=datetime.now(timezone.utc) - timedelta(hours=26)),
            AuditEvent(case_id=c1.id, event_type="AUTO_SCREENING", actor_name="FinShield Engine", actor_role="System", description="Auto sanctions & FATF geography screening completed: Clear (Domestic UK).", created_at=datetime.now(timezone.utc) - timedelta(hours=25, minutes=58)),
            AuditEvent(case_id=c1.id, event_type="AI_SCORING", actor_name="Claude Sonnet (v1.2.0)", actor_role="AI", description="AI parsed proposal and generated Inherent Risk score: 8.4 (CRITICAL). Confidence: 87%.", created_at=datetime.now(timezone.utc) - timedelta(hours=25, minutes=50)),
            AuditEvent(case_id=c1.id, event_type="ANALYST_OVERRIDE", actor_name="Rahul Mehta", actor_role="Senior Analyst", description="Analyst override applied on Fraud Risk: 8.5 -> 7.8. Reason: Product team confirmed device fingerprinting will be live at launch.", created_at=datetime.now(timezone.utc) - timedelta(hours=20)),
            AuditEvent(case_id=c1.id, event_type="COMMITTEE_VOTE", actor_name="Risk Committee", actor_role="Committee", description="Risk Committee voted 3-0 Unanimous: APPROVED WITH CONDITIONS.", created_at=datetime.now(timezone.utc) - timedelta(hours=2)),
            AuditEvent(case_id=c1.id, event_type="AUDIT_LOCK", actor_name="FinShield Engine", actor_role="System", description="Decision recorded and immutable audit trail locked.", created_at=datetime.now(timezone.utc) - timedelta(hours=2))
        ])

        # Token Log Case 1
        db.add_all([
            TokenLog(case_id=c1.id, step_name="document_parsing", input_tokens=850, output_tokens=353, total_tokens=1203, estimated_cost_usd=0.012, saved_tokens=650),
            TokenLog(case_id=c1.id, step_name="risk_scoring", input_tokens=520, output_tokens=327, total_tokens=847, estimated_cost_usd=0.008, saved_tokens=420),
            TokenLog(case_id=c1.id, step_name="draft_generation", input_tokens=1250, output_tokens=884, total_tokens=2134, estimated_cost_usd=0.021, saved_tokens=1600)
        ])

        # ----------------------------------------------------
        # CASE 2: PayAnywhere (Payments)
        # ----------------------------------------------------
        c2 = RiskCase(
            case_number=2,
            title="PayAnywhere — Real Time Faster Payments",
            division="Payments",
            change_type="New Feature Launch",
            submitter_id=user_map["arun.kumar@bank.com"],
            submitter_name="Arun Kumar",
            submitter_role="Product Manager, Digital Payments",
            what_requester_wants="Launch real time faster payments feature. Money sent in 10 seconds — irreversible. Available 24/7 including weekends. No transaction limits at launch. Open to all existing customers across Domestic + EU.",
            target_geographies=["United Kingdom", "European Union"],
            target_customers="All retail and business payment users",
            verification_speed="Instant transfer (10 seconds execution)",
            transaction_limits_desc="No limit at launch",
            real_world_context="Nationwide fined £44M by FCA in December 2025 for failing to implement anti-fraud controls on faster payments, exposing customers to APP fraud. APP fraud cost UK customers £460M in 2025.",
            status="APPROVED_WITH_CONDITIONS",
            inherent_risk_score=8.3,
            inherent_risk_tier="CRITICAL",
            residual_risk_score=8.3,
            residual_risk_tier="CRITICAL",
            final_analyst_score=8.3,
            ai_confidence_overall=0.88,
            analyst_recommendation="APPROVE_WITH_CONDITIONS",
            final_outcome="APPROVED_WITH_CONDITIONS",
            committee_vote_result="3-0 Unanimous",
            time_taken_hours=25.0,
            old_process_days=18,
            time_saved_pct=94.0,
            is_audit_locked=True,
            created_at=datetime.now(timezone.utc) - timedelta(days=2),
            locked_at=datetime.now(timezone.utc) - timedelta(days=1)
        )
        db.add(c2)
        db.flush()

        db.add_all([
            RiskDimensionScore(case_id=c2.id, dimension_key="money_laundering", dimension_name="Money Laundering Risk", weight=0.35, ai_score=8.0, analyst_override_score=None, final_score=8.0, confidence=0.85, framework_citation="FATF R.16 (Wire Transfers)", reasoning="No limits with 24/7 instant settlement enables structuring and smurfing without human intervention window.", traceability_factors=["24/7 instant settlement (+3.0)", "No transaction limits (+2.8)", "Cross-border EU corridor (+1.5)"]),
            RiskDimensionScore(case_id=c2.id, dimension_key="terrorist_financing", dimension_name="Terrorist Financing Risk", weight=0.20, ai_score=7.0, analyst_override_score=None, final_score=7.0, confidence=0.78, framework_citation="FATF R.16 + R.6", reasoning="Instant cross-border transfers risk funding illicit actors before post-event monitoring alerts trigger.", traceability_factors=["Irreversible transfer (+2.5)", "Cross-border EU reach (+2.0)"]),
            RiskDimensionScore(case_id=c2.id, dimension_key="fraud", dimension_name="Fraud Risk", weight=0.25, ai_score=9.5, analyst_override_score=None, final_score=9.5, confidence=0.95, framework_citation="PSR APP Fraud Rules 2024", reasoning="Irreversible 10s payments are the primary target for APP social engineering scams. Nationwide paid £44M for identical vulnerability.", traceability_factors=["10s irreversibility (+4.5)", "No payee delay (+2.5)", "No Confirmation of Payee (+2.5)"]),
            RiskDimensionScore(case_id=c2.id, dimension_key="compliance", dimension_name="Regulatory & Compliance Risk", weight=0.20, ai_score=8.5, analyst_override_score=None, final_score=8.5, confidence=0.88, framework_citation="NACHA 2026 + PSR Reimbursement Rules", reasoning="Mandates fraud prevention controls and 50:50 APP reimbursement liability for instant payment providers.", traceability_factors=["Missing PSR policy (+4.0)", "NACHA 2026 mandate gap (+3.5)"])
        ])

        db.add_all([
            CaseControl(case_id=c2.id, control_id="CTRL-COP", name="Confirmation of Payee (CoP) mandatory", effectiveness=0.45, is_active=True, control_type="MANDATED_BY_COMMITTEE", rationale="Verifies beneficiary name before execution."),
            CaseControl(case_id=c2.id, control_id="CTRL-PAYEE-DELAY", name="10-second delay for first-time payees", effectiveness=0.40, is_active=True, control_type="MANDATED_BY_COMMITTEE", rationale="Allows scam intervention cooling-off."),
            CaseControl(case_id=c2.id, control_id="CTRL-TXN-LIMITS", name="Transaction limit: £500 per payment at launch", effectiveness=0.55, is_active=True, control_type="MANDATED_BY_COMMITTEE", rationale="Caps catastrophic single-event fraud loss."),
            CaseControl(case_id=c2.id, control_id="CTRL-TXN-MONITORING", name="Real-time fraud scoring on every payment", effectiveness=0.60, is_active=True, control_type="MANDATED_BY_COMMITTEE", rationale="Scores transaction payload in <50ms.")
        ])

        db.add_all([
            CommitteeVote(case_id=c2.id, member_name="Sunita Rao", member_role="CRO", vote="APPROVE_WITH_CONDITIONS", rationale="Fraud risk is the primary concern. Controls must be live BEFORE launch — not planned."),
            CommitteeVote(case_id=c2.id, member_name="James Lee", member_role="CCO", vote="APPROVE_WITH_CONDITIONS", rationale="APP reimbursement policy must be in place. PSR compliance is non-negotiable."),
            CommitteeVote(case_id=c2.id, member_name="Anita Patel", member_role="Legal Counsel", vote="APPROVE_WITH_CONDITIONS", rationale="NACHA 2026 compliance confirmation required in writing before go-live.")
        ])

        db.add_all([
            DecisionCondition(case_id=c2.id, condition_text="Transaction limit: £500 per payment at launch", is_mandatory=True, is_met=True),
            DecisionCondition(case_id=c2.id, condition_text="10 second delay for first-time payees", is_mandatory=True, is_met=True),
            DecisionCondition(case_id=c2.id, condition_text="Real-time fraud scoring on every payment", is_mandatory=True, is_met=True),
            DecisionCondition(case_id=c2.id, condition_text="Confirmation of Payee mandatory", is_mandatory=True, is_met=True),
            DecisionCondition(case_id=c2.id, condition_text="APP fraud reimbursement policy published", is_mandatory=True, is_met=True),
            DecisionCondition(case_id=c2.id, condition_text="NACHA 2026 compliance confirmed in writing", is_mandatory=True, is_met=True),
            DecisionCondition(case_id=c2.id, condition_text="24/7 fraud monitoring team in place", is_mandatory=True, is_met=True),
            DecisionCondition(case_id=c2.id, condition_text="90 day post-launch mandatory review", is_mandatory=True, is_met=False),
            DecisionCondition(case_id=c2.id, condition_text="Monthly fraud loss report to committee", is_mandatory=True, is_met=False)
        ])

        db.add(AuditEvent(case_id=c2.id, event_type="AUDIT_LOCK", actor_name="FinShield Engine", actor_role="System", description="PayAnywhere approved with 9 conditions. Full audit locked.", created_at=datetime.now(timezone.utc) - timedelta(hours=1)))

        # ----------------------------------------------------
        # CASE 3: CryptoConnect (Payments / Crypto) -> REJECTED
        # ----------------------------------------------------
        c3 = RiskCase(
            case_number=3,
            title="CryptoConnect — In-App Crypto Wallet with USDT",
            division="Payments",
            change_type="New Product Launch",
            submitter_id=user_map["vikram.singh@bank.com"],
            submitter_name="Vikram Singh",
            submitter_role="Product Manager, Digital Assets",
            what_requester_wants="Allow customers to buy Bitcoin, Ethereum and USDT stablecoin through bank app. Send crypto to ANY external unhosted wallet globally. No transaction limits at launch. No CASP license obtained yet. No travel rule compliance plan. No wallet address screening.",
            target_geographies=["United States", "European Union", "United Arab Emirates", "Southeast Asia"],
            target_customers="Retail & crypto investors",
            verification_speed="Instant unhosted wallet transfers",
            transaction_limits_desc="No limits proposed",
            real_world_context="OKX fined $504M by DOJ in 2025 for unlicensed money transmission and zero KYC. Coinbase Europe fined €21.46M. Illicit crypto flows hit $154B in 2025 with USDT representing 84% of illicit volume. FATF March 2026 report strictly mandates unhosted wallet screening.",
            status="REJECTED",
            inherent_risk_score=8.8,
            inherent_risk_tier="CRITICAL",
            residual_risk_score=8.8,
            residual_risk_tier="CRITICAL",
            final_analyst_score=8.8,
            ai_confidence_overall=0.92,
            analyst_recommendation="REJECT",
            final_outcome="REJECTED",
            committee_vote_result="3-0 Unanimous Rejection",
            time_taken_hours=24.0,
            old_process_days=20,
            time_saved_pct=95.0,
            rejection_or_deferral_notice="REJECTED: Fundamental regulatory prerequisites not met. (1) CASP Licence required under EU MiCA (6-12 month process); (2) FATF Travel Rule technical compliance missing; (3) USDT inclusion indefensible given 84% illicit volume. Resubmit once prerequisites are resolved.",
            is_audit_locked=True,
            created_at=datetime.now(timezone.utc) - timedelta(days=2),
            locked_at=datetime.now(timezone.utc) - timedelta(days=1)
        )
        db.add(c3)
        db.flush()

        db.add_all([
            RiskDimensionScore(case_id=c3.id, dimension_key="money_laundering", dimension_name="Money Laundering Risk", weight=0.35, ai_score=9.2, analyst_override_score=None, final_score=9.2, confidence=0.95, framework_citation="FATF R.15 + GENIUS Act 2025", reasoning="USDT accounts for 84% of illicit crypto volume. Unhosted wallet transfers are untraceable after leaving bank ledger.", traceability_factors=["USDT stablecoin integration (+3.5)", "Unhosted wallet transfers (+3.0)", "No transaction limits (+2.7)"]),
            RiskDimensionScore(case_id=c3.id, dimension_key="terrorist_financing", dimension_name="Terrorist Financing Risk", weight=0.20, ai_score=8.5, analyst_override_score=None, final_score=8.5, confidence=0.91, framework_citation="FATF R.15 + R.6 + March 2026 Report", reasoning="UAE and SE Asia corridors represent high TF transit risk. Absence of wallet screening enables sanctioned entities to transact.", traceability_factors=["Zero wallet address screening (+4.0)", "High-risk TF corridors (+3.5)", "OFAC crypto list unlinked (+1.0)"]),
            RiskDimensionScore(case_id=c3.id, dimension_key="fraud", dimension_name="Fraud Risk", weight=0.25, ai_score=8.0, analyst_override_score=None, final_score=8.0, confidence=0.88, framework_citation="FinCEN 2026 Virtual Asset Advisory", reasoning="Pig butchering scams and crypto investment fraud victimize bank customers. Irreversible transfers prevent fund recovery.", traceability_factors=["Pig butchering vulnerability (+4.0)", "Irreversible crypto transfer (+3.0)"]),
            RiskDimensionScore(case_id=c3.id, dimension_key="compliance", dimension_name="Regulatory & Compliance Risk", weight=0.20, ai_score=9.5, analyst_override_score=None, final_score=9.5, confidence=0.97, framework_citation="MiCA + GENIUS Act + FATF Travel Rule", reasoning="Operating without CASP licence in EU constitutes criminal liability for executive management, not merely a regulatory fine.", traceability_factors=["No CASP licence (+5.0)", "No Travel Rule compliance (+3.5)", "GENIUS Act stablecoin breach (+1.0)"])
        ])

        db.add_all([
            CommitteeVote(case_id=c3.id, member_name="Sunita Rao", member_role="CRO", vote="REJECT", rationale="Completely support rejection. Operating without CASP licence in EU = criminal liability. OKX paid $504M for this. We will not take that risk."),
            CommitteeVote(case_id=c3.id, member_name="James Lee", member_role="CCO", vote="REJECT", rationale="USDT inclusion is indefensible. 84% of illicit crypto volume. No conditions can make this safe. Remove USDT and return with CASP and travel rule."),
            CommitteeVote(case_id=c3.id, member_name="Anita Patel", member_role="Legal Counsel", vote="REJECT", rationale="Legal cannot support this in any form without CASP licence. Exposes bank to criminal prosecution. Hard no.")
        ])

        db.add(AuditEvent(case_id=c3.id, event_type="AUDIT_LOCK", actor_name="FinShield Engine", actor_role="System", description="CryptoConnect rejected by unanimous 3-0 committee vote. Resubmission criteria issued.", created_at=datetime.now(timezone.utc) - timedelta(hours=1)))

        # ----------------------------------------------------
        # CASE 4: TradeLink (Commercial Banking) -> DEFERRED
        # ----------------------------------------------------
        c4 = RiskCase(
            case_number=4,
            title="TradeLink — Vendor Onboarding in High Risk Jurisdictions",
            division="Commercial Banking",
            change_type="New Vendor Onboarding",
            submitter_id=user_map["meera.nair@bank.com"],
            submitter_name="Meera Nair",
            submitter_role="Relationship Manager, Trade Finance",
            what_requester_wants="Onboard 3 new payment processing vendors operating across Nigeria, UAE and Southeast Asia for trade finance payment services. No Enhanced Due Diligence (EDD) planned yet. Standard vendor onboarding used.",
            target_geographies=["Nigeria", "United Arab Emirates", "Southeast Asia"],
            target_customers="Corporate trade finance clients",
            verification_speed="Standard vendor onboarding",
            transaction_limits_desc="Corporate trade credit facilities",
            real_world_context="TD Bank fined $3 BILLION in 2024 for turning a blind eye to high-risk vendors and illicit trade flows. UAE Exchange House fined $54.5M in 2026. Singapore S$3B money laundering case linked to regional vendor networks.",
            status="DEFERRED",
            inherent_risk_score=7.8,
            inherent_risk_tier="HIGH",
            residual_risk_score=7.1,
            residual_risk_tier="HIGH",
            final_analyst_score=7.1,
            ai_confidence_overall=0.86,
            analyst_recommendation="DEFER",
            final_outcome="DEFERRED",
            committee_vote_result="3-0 Unanimous Deferral",
            rejection_or_deferral_notice="DEFERRED PENDING EDD: Relationship has clear business value but onboarding cannot proceed without Enhanced Due Diligence. Required: (1) UBO verification for all entities; (2) Source of business funds; (3) Regulatory license verification; (4) AML program audit; (5) Correspondent bank references; (6) Site inspection.",
            is_audit_locked=True,
            created_at=datetime.now(timezone.utc) - timedelta(days=2),
            locked_at=datetime.now(timezone.utc) - timedelta(days=1)
        )
        db.add(c4)
        db.flush()

        db.add_all([
            RiskDimensionScore(case_id=c4.id, dimension_key="money_laundering", dimension_name="Money Laundering Risk", weight=0.35, ai_score=8.5, analyst_override_score=None, final_score=8.5, confidence=0.88, framework_citation="FATF R.13 + FinCEN TBML Advisory", reasoning="Geographies on FATF monitoring lists. Third-party vendors create indirect exposure to trade-based money laundering schemes.", traceability_factors=["FATF Grey/Monitoring jurisdictions (+3.5)", "Trade-based money laundering exposure (+3.0)", "No vendor transaction limits (+2.0)"]),
            RiskDimensionScore(case_id=c4.id, dimension_key="terrorist_financing", dimension_name="Terrorist Financing Risk", weight=0.20, ai_score=7.5, analyst_override_score=6.8, final_score=6.8, confidence=0.79, framework_citation="FATF R.12 (Correspondent Banking)", reasoning="Nigeria and SE Asia have documented TF transit networks. [Analyst Override: Nigeria vendor holds valid CBN payment processor license].", traceability_factors=["Regional corridor TF risk (+3.5)", "CBN license mitigation (-0.7)"]),
            RiskDimensionScore(case_id=c4.id, dimension_key="fraud", dimension_name="Fraud Risk", weight=0.25, ai_score=7.0, analyst_override_score=None, final_score=7.0, confidence=0.82, framework_citation="OCC Third Party Risk 2023", reasoning="Vendor fraud risk — shell entities exploiting correspondent accounts to siphon institutional funds.", traceability_factors=["Vendor shell structure risk (+3.5)", "Standard onboarding only (+2.5)"]),
            RiskDimensionScore(case_id=c4.id, dimension_key="compliance", dimension_name="Regulatory & Compliance Risk", weight=0.20, ai_score=8.0, analyst_override_score=None, final_score=8.0, confidence=0.85, framework_citation="OCC TPRM + FinCEN + Basel AML", reasoning="Onboarding high-risk jurisdiction intermediaries without EDD constitutes an explicit OCC regulatory violation.", traceability_factors=["No EDD performed (+4.5)", "OCC TPRM mandate breach (+3.5)"])
        ])

        db.add_all([
            CommitteeVote(case_id=c4.id, member_name="Sunita Rao", member_role="CRO", vote="DEFER", rationale="Clear defer. EDD is mandatory. TD Bank paid $3B for this type of oversight. Come back when EDD is complete."),
            CommitteeVote(case_id=c4.id, member_name="James Lee", member_role="CCO", vote="DEFER", rationale="Agree. Nigeria and UAE need extra scrutiny given 2026 fine context. EDD is non-negotiable."),
            CommitteeVote(case_id=c4.id, member_name="Anita Patel", member_role="Legal Counsel", vote="DEFER", rationale="OCC expects risk-based EDD. Not optional. Defer with clear resubmission criteria.")
        ])

        # ----------------------------------------------------
        # CASE 5: WealthGlobal (Wealth Management)
        # ----------------------------------------------------
        c5 = RiskCase(
            case_number=5,
            title="WealthGlobal — Offshore Investment for HNI Clients",
            division="Wealth Management",
            change_type="New Product + New Geography",
            submitter_id=user_map["rajesh.kapoor@bank.com"],
            submitter_name="Rajesh Kapoor",
            submitter_role="Head of Private Banking",
            what_requester_wants="Launch offshore investment product for High Net Worth Individual (HNI) clients. Minimum investment: $1 million. Structures: Holding companies in Cayman Islands and Jersey. Target clients: Middle East and Asian HNIs.",
            target_geographies=["Cayman Islands", "Jersey", "United Arab Emirates", "Singapore"],
            target_customers="High Net Worth Individuals ($1M+ liquidity)",
            verification_speed="Private banking bespoke onboarding",
            transaction_limits_desc="$1M minimum ticket size",
            real_world_context="Credit Suisse paid $511M settlement in 2025 for facilitating offshore tax evasion and complex shell structures. FinCEN Investment Adviser AML Rule effective Jan 1, 2026 requires formal AML and SAR filing.",
            status="APPROVED_WITH_CONDITIONS",
            inherent_risk_score=6.6,
            inherent_risk_tier="MEDIUM",
            residual_risk_score=5.4,
            residual_risk_tier="MEDIUM",
            final_analyst_score=5.4,
            ai_confidence_overall=0.89,
            analyst_recommendation="APPROVE_WITH_CONDITIONS",
            final_outcome="APPROVED_WITH_CONDITIONS",
            committee_vote_result="3-0 Unanimous",
            is_audit_locked=True,
            created_at=datetime.now(timezone.utc) - timedelta(days=2),
            locked_at=datetime.now(timezone.utc) - timedelta(days=1)
        )
        db.add(c5)
        db.flush()

        db.add_all([
            RiskDimensionScore(case_id=c5.id, dimension_key="money_laundering", dimension_name="Money Laundering Risk", weight=0.35, ai_score=7.5, analyst_override_score=None, final_score=7.5, confidence=0.83, framework_citation="FATF R.22 + JMLSG Part 2", reasoning="Offshore holding companies in Cayman/Jersey represent classic layering vehicles. HNI large ticket volumes amplify laundering exposure.", traceability_factors=["Cayman/Jersey secrecy jurisdiction (+2.5)", "Complex holding structures (+2.5)", "High ticket size (+1.5)"]),
            RiskDimensionScore(case_id=c5.id, dimension_key="terrorist_financing", dimension_name="Terrorist Financing Risk", weight=0.20, ai_score=6.0, analyst_override_score=5.0, final_score=5.0, confidence=0.76, framework_citation="FATF R.12 (PEPs)", reasoning="Middle East HNI client base includes potential PEPs. [Analyst Override: Pre-screened client base with full EDD before onboarding].", traceability_factors=["Middle East PEP exposure (+3.0)", "Existing EDD mitigation (-1.0)"]),
            RiskDimensionScore(case_id=c5.id, dimension_key="fraud", dimension_name="Fraud Risk", weight=0.25, ai_score=5.0, analyst_override_score=4.5, final_score=4.5, confidence=0.88, framework_citation="Internal Private Banking Policy", reasoning="Established HNI clients with personal relationship manager verification. Low retail fraud typology match.", traceability_factors=["High touch verification (-0.5)", "$1M threshold barriers (-0.5)"]),
            RiskDimensionScore(case_id=c5.id, dimension_key="compliance", dimension_name="Regulatory & Compliance Risk", weight=0.20, ai_score=8.0, analyst_override_score=None, final_score=8.0, confidence=0.92, framework_citation="FinCEN Investment Adviser Rule Jan 2026", reasoning="New FinCEN 2026 rule requires formal AML program and mandatory SAR filing for investment advisers offering offshore accounts.", traceability_factors=["FinCEN 2026 SAR obligation (+4.0)", "OECD CRS reporting requirements (+3.0)"])
        ])

        db.add_all([
            CommitteeVote(case_id=c5.id, member_name="Sunita Rao", member_role="CRO", vote="APPROVE_WITH_CONDITIONS", rationale="Medium risk is acceptable for wealth management with right controls. Credit Suisse is the warning — our controls must exceed theirs."),
            CommitteeVote(case_id=c5.id, member_name="James Lee", member_role="CCO", vote="APPROVE_WITH_CONDITIONS", rationale="FinCEN 2026 compliance is priority. SAR program must be in place before launch."),
            CommitteeVote(case_id=c5.id, member_name="Anita Patel", member_role="Legal Counsel", vote="APPROVE_WITH_CONDITIONS", rationale="OECD CRS reporting confirmed. Legal supports with documented conditions.")
        ])

        db.add_all([
            DecisionCondition(case_id=c5.id, condition_text="Enhanced Due Diligence for ALL new clients", is_mandatory=True, is_met=True),
            DecisionCondition(case_id=c5.id, condition_text="PEP screening mandatory — no exceptions", is_mandatory=True, is_met=True),
            DecisionCondition(case_id=c5.id, condition_text="Source of wealth documented for every client", is_mandatory=True, is_met=True),
            DecisionCondition(case_id=c5.id, condition_text="FinCEN SAR program implemented before launch", is_mandatory=True, is_met=True),
            DecisionCondition(case_id=c5.id, condition_text="Annual review of ALL offshore structures", is_mandatory=True, is_met=False),
            DecisionCondition(case_id=c5.id, condition_text="No clients from sanctioned jurisdictions", is_mandatory=True, is_met=True),
            DecisionCondition(case_id=c5.id, condition_text="OECD CRS reporting confirmed", is_mandatory=True, is_met=True),
            DecisionCondition(case_id=c5.id, condition_text="Relationship manager sign-off per client", is_mandatory=True, is_met=True),
            DecisionCondition(case_id=c5.id, condition_text="$5M cap per client for first 12 months", is_mandatory=True, is_met=True),
            DecisionCondition(case_id=c5.id, condition_text="Quarterly risk review with FCRM", is_mandatory=True, is_met=False)
        ])

        # ----------------------------------------------------
        # CASE 6: GreenHome (Consumer Banking) -> APPROVED CLEAN
        # ----------------------------------------------------
        c6 = RiskCase(
            case_number=6,
            title="GreenHome — Sustainable Mortgage Product",
            division="Consumer Banking",
            change_type="New Product Launch",
            submitter_id=user_map["neha.gupta@bank.com"],
            submitter_name="Neha Gupta",
            submitter_role="Product Manager, Retail Lending",
            what_requester_wants="Launch green mortgage product offering discounted interest rates for energy-efficient residential home purchases. Open strictly to existing verified UK customers.",
            target_geographies=["United Kingdom"],
            target_customers="Existing verified mortgage applicants",
            verification_speed="Standard mortgage underwriting (3-5 days)",
            transaction_limits_desc="Secured against UK property valuation",
            real_world_context="Demonstrates proportionate risk-based triage under FATF Recommendation 1. Demonstrates that AI and workbench fast-tracks low-risk proposals in 5 hours without unnecessary friction.",
            status="APPROVED",
            inherent_risk_score=2.5,
            inherent_risk_tier="LOW",
            residual_risk_score=1.8,
            residual_risk_tier="LOW",
            final_analyst_score=2.5,
            ai_confidence_overall=0.95,
            analyst_recommendation="APPROVE",
            final_outcome="APPROVED",
            committee_vote_result="3-0 Unanimous",
            time_taken_hours=5.0,
            old_process_days=15,
            time_saved_pct=96.0,
            is_audit_locked=True,
            created_at=datetime.now(timezone.utc) - timedelta(days=2),
            locked_at=datetime.now(timezone.utc) - timedelta(days=1)
        )
        db.add(c6)
        db.flush()

        db.add_all([
            RiskDimensionScore(case_id=c6.id, dimension_key="money_laundering", dimension_name="Money Laundering Risk", weight=0.35, ai_score=2.5, analyst_override_score=None, final_score=2.5, confidence=0.94, framework_citation="FATF R.1 (Risk-Based Approach)", reasoning="Secured lending against domestic UK property. Existing verified customers with established KYC histories.", traceability_factors=["Secured collateral property (-2.0)", "Existing customer base (-2.0)"]),
            RiskDimensionScore(case_id=c6.id, dimension_key="terrorist_financing", dimension_name="Terrorist Financing Risk", weight=0.20, ai_score=2.0, analyst_override_score=None, final_score=2.0, confidence=0.96, framework_citation="FATF R.1 (Low Risk Factors)", reasoning="Domestic residential property purchase. Very low TF typology match.", traceability_factors=["Domestic residential property (-3.0)"]),
            RiskDimensionScore(case_id=c6.id, dimension_key="fraud", dimension_name="Fraud Risk", weight=0.25, ai_score=3.0, analyst_override_score=None, final_score=3.0, confidence=0.92, framework_citation="FCA MCOB Mortgage Rules", reasoning="Independent property surveyor valuation and solicitor conveyancing verification in place.", traceability_factors=["Independent valuation check (-2.0)"]),
            RiskDimensionScore(case_id=c6.id, dimension_key="compliance", dimension_name="Regulatory & Compliance Risk", weight=0.20, ai_score=2.5, analyst_override_score=None, final_score=2.5, confidence=0.95, framework_citation="FCA MCOB + MLR 2017", reasoning="Standard mortgage regulatory framework applies. No new novel regulatory obligations triggered.", traceability_factors=["Standard regulatory regime (-2.5)"])
        ])

        db.add_all([
            CommitteeVote(case_id=c6.id, member_name="Sunita Rao", member_role="CRO", vote="APPROVE", rationale="Clean case. AI correctly identified this as low risk. Approve with no conditions."),
            CommitteeVote(case_id=c6.id, member_name="James Lee", member_role="CCO", vote="APPROVE", rationale="Agreed. This is what fast-track approval looks like. Standard controls sufficient."),
            CommitteeVote(case_id=c6.id, member_name="Anita Patel", member_role="Legal Counsel", vote="APPROVE", rationale="No new legal obligations. Standard mortgage framework applies. Approve.")
        ])

        # ----------------------------------------------------
        # CASE 7: AlertSmart (FCRM / Compliance) -> THE META CASE
        # ----------------------------------------------------
        c7 = RiskCase(
            case_number=7,
            title="AlertSmart — AI-Powered AML Alert Triage Process Change",
            division="FCRM / Compliance",
            change_type="Process Change — INTERNAL",
            submitter_id=user_map["deepa.sharma@bank.com"],
            submitter_name="Deepa Sharma",
            submitter_role="Head of Financial Crime Operations",
            what_requester_wants="Internal FCRM Operations process change: replace 100% manual review of transaction monitoring alerts with AI-powered triage. AI auto-closes low-risk alerts (~70% volume); human analysts review only medium and high risk alerts. Estimated 60% analyst time savings.",
            target_geographies=["United Kingdom", "Global Operations"],
            target_customers="Internal AML surveillance operations",
            verification_speed="Real-time alert classification",
            transaction_limits_desc="Internal alert disposition workflow",
            real_world_context="THE META CASE: The FCRM team uses the Risk Workbench to assess a change TO ITS OWN operations! FinCEN 2026 AI in AML Advisory permits AI triage only with human oversight; FCA 2026 Model Risk requires independent model validation, explainability, and rollback capability.",
            status="APPROVED_WITH_CONDITIONS",
            inherent_risk_score=6.0,
            inherent_risk_tier="MEDIUM",
            residual_risk_score=4.8,
            residual_risk_tier="MEDIUM",
            final_analyst_score=4.8,
            ai_confidence_overall=0.88,
            analyst_recommendation="APPROVE_WITH_CONDITIONS",
            final_outcome="APPROVED_WITH_CONDITIONS",
            committee_vote_result="3-0 Unanimous",
            is_audit_locked=True,
            created_at=datetime.now(timezone.utc) - timedelta(days=2),
            locked_at=datetime.now(timezone.utc) - timedelta(days=1)
        )
        db.add(c7)
        db.flush()

        db.add_all([
            RiskDimensionScore(case_id=c7.id, dimension_key="money_laundering", dimension_name="Money Laundering Risk", weight=0.35, ai_score=6.5, analyst_override_score=None, final_score=6.5, confidence=0.82, framework_citation="FATF R.3 + FinCEN 2026 AI Advisory", reasoning="False negatives in AI auto-closure could allow genuine money laundering alerts to go undetected and unreported.", traceability_factors=["Potential false negative closure (+3.5)", "Surveillance backlog reduction (-1.0)"]),
            RiskDimensionScore(case_id=c7.id, dimension_key="terrorist_financing", dimension_name="Terrorist Financing Risk", weight=0.20, ai_score=6.0, analyst_override_score=None, final_score=6.0, confidence=0.78, framework_citation="FATF R.3 (Detection Obligation)", reasoning="TF alerts incorrectly categorized as low risk carry severe regulatory and societal repercussions.", traceability_factors=["TF false negative severity (+3.0)"]),
            RiskDimensionScore(case_id=c7.id, dimension_key="fraud", dimension_name="Fraud Risk", weight=0.25, ai_score=4.5, analyst_override_score=3.8, final_score=3.8, confidence=0.74, framework_citation="FCA Model Risk Guidance", reasoning="Model adversarial manipulation risk. [Analyst Override: Trained on historical fraud patterns; reduces 40% analyst fatigue omissions].", traceability_factors=["Fatigue omission reduction (-1.2)", "Model adversarial vulnerability (+0.5)"]),
            RiskDimensionScore(case_id=c7.id, dimension_key="compliance", dimension_name="Regulatory & Compliance Risk", weight=0.20, ai_score=7.0, analyst_override_score=6.2, final_score=6.2, confidence=0.88, framework_citation="OCC Model Risk + FCA 2026 AI Framework", reasoning="High-risk AI in compliance operations requires formal validation, explainability, and governance. [Analyst Override: External validation already commissioned].", traceability_factors=["OCC MRM high-risk classification (+4.0)", "Independent audit scheduled (-1.0)"])
        ])

        db.add_all([
            CommitteeVote(case_id=c7.id, member_name="Sunita Rao", member_role="CRO", vote="APPROVE_WITH_CONDITIONS", rationale="This is smart. We cannot manually review all alerts effectively anyway — volume is too high. AI triage with human sampling is the right approach."),
            CommitteeVote(case_id=c7.id, member_name="James Lee", member_role="CCO", vote="APPROVE_WITH_CONDITIONS", rationale="FinCEN 2026 advisory supports this approach. Independent model validation is the key condition. Must happen before go-live."),
            CommitteeVote(case_id=c7.id, member_name="Anita Patel", member_role="Legal Counsel", vote="APPROVE_WITH_CONDITIONS", rationale="OCC model risk guidance followed. Legal confirms conditions cover all regulatory requirements. Approve.")
        ])

        db.add_all([
            DecisionCondition(case_id=c7.id, condition_text="Independent model validation before launch", is_mandatory=True, is_met=True),
            DecisionCondition(case_id=c7.id, condition_text="Human sampling: 10% of auto-closed alerts reviewed monthly", is_mandatory=True, is_met=True),
            DecisionCondition(case_id=c7.id, condition_text="False negative rate monitored: < 0.1% threshold", is_mandatory=True, is_met=True),
            DecisionCondition(case_id=c7.id, condition_text="Quarterly model performance report to committee", is_mandatory=True, is_met=False),
            DecisionCondition(case_id=c7.id, condition_text="Full audit trail of every AI triage decision", is_mandatory=True, is_met=True),
            DecisionCondition(case_id=c7.id, condition_text="Override capability for any analyst — always active", is_mandatory=True, is_met=True),
            DecisionCondition(case_id=c7.id, condition_text="Escalation path for borderline cases defined", is_mandatory=True, is_met=True),
            DecisionCondition(case_id=c7.id, condition_text="Annual model revalidation scheduled", is_mandatory=True, is_met=False),
            DecisionCondition(case_id=c7.id, condition_text="Explainability report for every auto-close decision", is_mandatory=True, is_met=True),
            DecisionCondition(case_id=c7.id, condition_text="Emergency rollback plan if performance degrades", is_mandatory=True, is_met=True)
        ])

        db.commit()
        print("[FinShield DB] Successfully seeded 13 users, 7 comprehensive benchmark cases, dimensions, controls, votes, conditions, audit trails, and token telemetry.")

    except Exception as e:
        db.rollback()
        print(f"[FinShield DB Error] Seeding failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
