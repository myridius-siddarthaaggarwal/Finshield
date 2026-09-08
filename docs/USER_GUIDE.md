# 📖 FinShield — User Guide & Presentation Manual

> **Target Audience**: Business Users, Hackathon Presenters, Judges, Risk Officers  
> **Application URL**: `http://localhost:5173` (Frontend) | `http://localhost:8000` (Backend API)  

---

## 🎭 Persona Fast-Switcher (Top Navigation)

In the top right of the application header, you will find the **Persona Switcher Dropdown**. You can dynamically switch between pre-seeded users during a presentation to demonstrate different perspectives:

| Persona Role | User Name | Title / Focus |
| :--- | :--- | :--- |
| **🔍 Lead Analyst** | **Rahul Mehta** / **Priya Chandran** | Senior FCRM Analysts (Overrides & Sandbox) |
| **👤 Product Submitter** | **Priya Sharma** / **Vikram Singh** | Business Product Managers |
| **🏛️ Risk Committee (CRO)** | **Sunita Rao** | Chief Risk Officer (Overall Risk Exposure) |
| **🏛️ Risk Committee (CCO)** | **James Lee** | Chief Compliance Officer (Regulatory Frameworks) |
| **🏛️ Risk Committee (Legal)** | **Anita Patel** | Head of Regulatory Legal (Statutory Liability) |
| **⚙️ Platform Admin** | **System Administrator** | Governance & Architecture Configuration |

---

## 🚶 End-to-End User Workflows

### 1. Submitter Flow: Creating a New Intake
1. Click **"New Intake"** in the top navigation bar or the **"Submit New Intake"** button on the dashboard.
2. Enter the **Proposal Title** (e.g., `QuickAccount — Instant Digital Account Opening`).
3. Select the **Banking Division** (`Consumer Banking`, `Payments`, `Commercial Banking`, `Wealth Management`, or `FCRM / Compliance`).
4. Select the **Change Type** (`New Product Launch`, `New Feature Launch`, `New Vendor Onboarding`, or `Process Change — INTERNAL`).
5. Enter **Target Geographies** (e.g. `United Kingdom, Nigeria`).
   > 💡 **Notice the live screening preview**: As soon as you type `Nigeria` or `UAE`, the system immediately displays a warning badge: *FATF Increased Monitoring Corridor detected. Enhanced Due Diligence (EDD) will be required.*
6. Click **"Run FinShield Assessment"**.
7. Watch the animated multi-stage orchestrator:
   - **Step 1**: Deterministic Sanctions & FATF Screening
   - **Step 2**: AI Document & Spec Extraction
   - **Step 3**: Multi-Dimension Risk Scoring & Traceability Logging
8. The newly created case opens automatically in the workbench!

---

### 2. FCRM Analyst Flow: Risk Breakdown & Overrides
1. Open any case from the dashboard (e.g., **Case 1: QuickAccount**).
2. Review the **4 Risk Dimension Cards**:
   - **Money Laundering Risk** (Weight: 35%) — e.g. *FATF Recommendation 10*.
   - **Terrorist Financing Risk** (Weight: 20%) — e.g. *FATF Recommendation 6*.
   - **Fraud Risk** (Weight: 25%) — e.g. *FCA Consumer Duty 2023*.
   - **Regulatory Compliance Risk** (Weight: 20%) — e.g. *FCA 2026 Supervisory Letter*.
3. Note the **AI Reasoning Confidence** on each card (e.g. 89%).
4. **Apply a Human Override**:
   - Click **"Override Score"** on the Fraud Risk card.
   - Adjust the score slider (e.g., from `8.5` down to `7.8`).
   - Enter a mandatory written regulatory reason:  
     `"Product team confirmed device fingerprinting will be deployed from launch — reduces synthetic identity risk."`
   - Click **"Commit Override"**.
   - Notice how the overall inherent score and residual risk are **deterministically recalculated** and logged into the immutable audit trail!
5. **Run the What-If Control Simulation Sandbox**:
   - Scroll down to the sandbox.
   - Toggle candidate controls (e.g., `£500/day limit for 90 days` + `Real-Time Transaction Monitoring`).
   - Watch the residual risk score drop in real-time with visual percentage reduction calculations.
6. Click **"Submit to Risk Committee"** to escalate the proposal.

---

### 3. Risk Committee Flow: 3-Member Governance & Sealing
1. Switch to the **"Risk Committee Governance"** tab.
2. Review the **3 Independent Voting Cards**:
   - **Sunita Rao (CRO)**: Focuses on institutional capital & aggregate risk exposure.
   - **James Lee (CCO)**: Focuses on regulatory obligations & supervisory warning letters.
   - **Anita Patel (Legal Counsel)**: Focuses on CASP licensing, MiCA statutory liability, and Consumer Duty.
3. Record votes for each member with their respective governance rationale.
4. Review the **Mandated Approval Conditions Checklist** (e.g. 8 conditions for Case 1).
5. Click **"Finalize & Lock Decision"**:
   - Select `APPROVED WITH CONDITIONS`, `APPROVED`, `DEFERRED`, or `REJECTED`.
   - Click **"Seal & Lock Decision"**.
   - The decision is stamped, the time saved is calculated (e.g., 93.0% time saved vs 18 days), and the audit trail is permanently locked.

---

### 4. Traceability & Audit Verification
1. Open the **"Traceability & Audit Logs"** tab on any case.
2. View the **Deterministic Traceability Chain**:
   - Input 1: Digital onboarding (+2.8)
   - Input 2: 60-second verification (+2.1)
   - Input 3: Broad retail exposure (+1.9)
   - Input 4: No initial transaction monitoring (+2.4)
   - Control: Basic KYC (-0.7)
   - Analyst Override: 8.5 &rarr; 7.8 (Rahul Mehta)
   - *Every single decimal point is accounted for!*
3. View the **Immutable ACID Audit Trail** list showing timestamped events for submissions, auto-screening, AI scoring, analyst overrides, and committee votes.

---

## 📊 Evaluation & Engineering Judgement Hub

Navigate to the **"Evaluation & Judgement Hub"** in the top navigation to present to evaluators:

1. **Executive Impact Matrix**:
   - Visual comparison: Traditional FCRM (18 days, 47 emails, $3.8B fines) vs FinShield (1.1 days, 93.8% time saved).
2. **AI vs Deterministic Decision Matrix**:
   - Clear justification of why deterministic code is used for FSM, Audit logging, RBAC, Sanctions lookup, Weighted math, and Confidence gating.
3. **Model Evaluation Benchmark**:
   - Comparing AI model scores against expert ground truth across all 7 benchmark cases (85.7% accuracy).
4. **Token Telemetry & Cost Optimization**:
   - Demonstrating $0.041 per complete assessment and −44% token savings via JSON schema enforcement and prompt optimization.
