from __future__ import annotations

import csv
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
MEDICAL = ROOT / "assets" / "medical"
VERIFIED = "2026-07-28"

P1 = "Patient Understanding and Engagement"
P2 = "Clinical Workflow and Decision Support"
P3 = "Pharma, Research and Professional Productivity"
P4 = "Responsible AI, Governance and Implementation"

COMMON_VERIFY = [
    "Compare every fact against the supplied source record",
    "Keep missing information and uncertainty visible",
    "Check that no medicine, dose, date, diagnosis, result, or citation was invented",
    "Record the qualified human's accept, edit, reject, or escalate decision",
]


def workflow(
    workflow_id: str,
    title: str,
    icon: str,
    pillar: str,
    roles: list[str],
    task: str,
    input_type: str,
    output_type: str,
    risk: str,
    sensitivity: str,
    languages: list[str],
    tools: list[str],
    dataset: str,
    case_context: str,
    prompt_task: str,
    expected_output: str,
    reviewer: str,
    prohibited: str,
    time_minutes: int = 12,
) -> dict:
    return {
        "workflow_id": workflow_id,
        "title": title,
        "icon": icon,
        "pillar": pillar,
        "roles": roles,
        "task": task,
        "input_type": input_type,
        "output_type": output_type,
        "risk_level": risk,
        "data_sensitivity": sensitivity,
        "languages": languages,
        "primary_tool": tools[0],
        "alternative_tools": tools[1:],
        "dataset": dataset,
        "case_context": case_context,
        "prompt_template": (
            "ROLE\nYou are a drafting assistant supporting a qualified {reviewer}. You do not replace "
            "professional judgement.\n\nINPUT\n{record}\n\nTASK\n"
            + prompt_task
            + "\n\nCONSTRAINTS\nUse only the supplied synthetic record. Mark missing information and "
            "uncertainty. Do not invent facts, doses, dates, diagnoses, results, or references. Do not "
            "take autonomous clinical, regulatory, safety, or publication decisions.\n\nOUTPUT\n"
            + expected_output
            + "\n\nVERIFY\nEnd with a source-fidelity checklist and an accept / edit / reject / escalate "
            "decision box for the qualified reviewer."
        ),
        "expected_output": expected_output,
        "verification": COMMON_VERIFY,
        "prohibited_actions": prohibited,
        "human_reviewer": reviewer,
        "time_minutes": time_minutes,
        "last_verified": VERIFIED,
    }


def build_workflows() -> list[dict]:
    all_patient_languages = [
        "English", "Hindi", "Marathi", "Bengali", "Tamil", "Telugu",
        "Kannada", "Malayalam",
    ]
    return [
        workflow(
            "P1-RX-01", "Prescription extraction and patient explanation", "💊", P1,
            ["Doctor", "Nurse", "Pharmacist", "Patient educator"], "Explain a prescription",
            "Prescription image", "Structured medicine table and teach-back script", "High",
            "Synthetic only", all_patient_languages,
            ["ChatGPT", "Google Gemini", "Microsoft Copilot"],
            "prescription_cases.csv",
            "A synthetic prescription must be transcribed faithfully, explained in plain language, and checked by a clinician or pharmacist.",
            "Transcribe only legible content. Separate exact extraction from plain-language explanation. Flag every ambiguous token as unreadable; never guess.",
            "Exact transcription table; plain-language explanation; ambiguity log; warning that the prescription itself remains authoritative; three teach-back questions.",
            "clinician or registered pharmacist",
            "No prescribing, substitution, interaction decision, adherence judgement, or reconstruction of unreadable content.",
        ),
        workflow(
            "P1-DC-02", "Discharge plan with teach-back", "🏠", P1,
            ["Doctor", "Nurse", "Patient educator"], "Simplify a discharge summary",
            "Clinical text", "One-page patient action plan", "Moderate", "Synthetic only",
            all_patient_languages,
            ["ChatGPT", "Claude", "Google Gemini", "Doximity Ask"],
            "discharge_summaries.csv",
            "A patient needs a clear home-care plan without any change to medicines, dates, red flags, or follow-up.",
            "Rewrite at approximately Grade 6 reading level. Preserve all clinical facts. Make urgent warning signs and follow-up actions prominent.",
            "What happened; exact medicine/action schedule; red flags; follow-up; three teach-back questions; missing-information list.",
            "treating clinician or discharge nurse",
            "No new clinical advice, dose change, diagnosis, or omission of escalation instructions.",
        ),
        workflow(
            "P1-LANG-03", "Multilingual counselling", "🌐", P1,
            ["Doctor", "Nurse", "Pharmacist", "Patient educator"], "Translate patient counselling",
            "Clinical text", "Bilingual counselling script", "Moderate", "Synthetic only",
            all_patient_languages,
            ["Google Gemini", "DeepL", "ChatGPT", "Microsoft Copilot"],
            "multilingual_counselling_cases.csv",
            "A patient prefers another language; medicine and test names must remain stable and the translation needs clinical review.",
            "Create aligned English and target-language sections. Keep medicine, product, and test names unchanged. Avoid idioms and cultural assumptions.",
            "Bilingual script; terminology cross-check; teach-back questions; items requiring fluent clinical review.",
            "clinician plus fluent-language reviewer",
            "No unreviewed translation for clinical action and no changes to source meaning.",
        ),
        workflow(
            "P1-EDU-04", "Patient education fact sheet", "🧾", P1,
            ["Doctor", "Medical affairs professional", "Patient educator"], "Create patient education",
            "Evidence facts", "Patient fact sheet", "Moderate", "Synthetic only",
            all_patient_languages,
            ["Canva", "ChatGPT", "Google Gemini"],
            "patient_education_facts.csv",
            "Approved source facts need to become an accessible education aid with clear action steps.",
            "Use only supplied facts; distinguish general information from advice; include a reading-level and accessibility review.",
            "Plain-language fact sheet; source-fact map; accessibility checklist; clinician approval box.",
            "medical reviewer and patient-education reviewer",
            "No promotional claim, unsupported benefit, personalised diagnosis, or treatment instruction.",
        ),
        workflow(
            "P1-JOURNEY-05", "Patient journey friction map", "🗺️", P1,
            ["Hospital leader", "Quality professional", "Patient educator"], "Map a patient journey",
            "Tabular data", "Journey map and improvement backlog", "Low", "Synthetic only",
            ["English"],
            ["Napkin AI", "Canva", "Gamma", "Julius AI"],
            "patient_journey_map.csv",
            "A service team wants to turn synthetic journey observations into testable improvements.",
            "Map stages, patient goals, friction, emotions, handoffs, and measurable opportunities without inferring protected attributes.",
            "Journey table; top three improvement hypotheses; owner; measure; fairness and access check.",
            "service owner with patient representative",
            "No demographic inference, automated prioritisation of care, or unsupported operational claim.",
        ),
        workflow(
            "P1-FEEDBACK-06", "Patient feedback action plan", "💬", P1,
            ["Hospital leader", "Quality professional"], "Analyse patient feedback",
            "Tabular data", "Service-recovery action card", "Low", "Synthetic only",
            ["English", "Hindi"],
            ["Julius AI", "ChatGPT", "Microsoft Copilot"],
            "patient_feedback.csv",
            "Patient comments need to become measurable service-recovery and process-improvement actions.",
            "Retain patient voice, cluster themes transparently, state limitations, and propose reversible tests with owners and measures.",
            "Theme summary; representative synthetic examples; immediate recovery action; long-term action; owner; metric.",
            "quality lead and service owner",
            "No inference of protected attributes or automatic complaint adjudication.",
        ),
        workflow(
            "P2-XRAY-01", "Structured medical-image observation", "🩻", P2,
            ["Doctor", "Radiologist", "Medical student"], "Review a medical image safely",
            "Medical image", "Observation checklist and escalation note", "High", "Synthetic only",
            ["English"],
            ["ChatGPT", "Google Gemini"],
            "imaging_cases.csv",
            "A fully synthetic chest radiograph is used to practise separating image-quality checks, observations, uncertainty, and escalation.",
            "Describe only visible, non-diagnostic observations. First assess image adequacy and limitations. Explicitly state that specialised medical-image interpretation requires a qualified clinician and validated tools.",
            "Image adequacy checklist; structured visible observations; uncertainty; cannot-assess list; escalation and human-review note.",
            "qualified radiologist or treating clinician",
            "No diagnosis, triage clearance, treatment recommendation, or claim that a general-purpose model can read specialised medical images reliably.",
        ),
        workflow(
            "P2-REASON-02", "Differential and red-flag checklist", "🩺", P2,
            ["Doctor", "Medical student"], "Structure clinical reasoning",
            "Clinical text", "Differential checklist", "High", "Synthetic only",
            ["English"],
            ["OpenEvidence", "Glass Health", "Pathway", "ChatGPT"],
            "clinical_reasoning_cases.csv",
            "A synthetic case may contain a serious symptom; the exercise must prevent anchoring and retain uncertainty.",
            "Separate common/likely, cannot-miss, supporting evidence, opposing evidence, missing history/examination, and urgent escalation triggers.",
            "Clinician-review differential checklist; cognitive-bias prompt; missing-data list; urgency triggers.",
            "qualified treating clinician",
            "No final diagnosis, treatment plan, prescription, or autonomous triage decision.",
        ),
        workflow(
            "P2-NOTE-03", "Clinical note structuring", "📝", P2,
            ["Doctor", "Nurse"], "Draft clinical documentation",
            "Clinical text", "Reviewable structured note", "Moderate", "Synthetic only",
            ["English"],
            ["Microsoft Copilot", "ChatGPT", "Claude"],
            "outpatient_cases.csv",
            "A synthetic encounter must be structured without hiding missing facts or adding a diagnosis.",
            "Organise the record into a reviewable note. Label direct facts, patient-reported facts, inference, and missing information.",
            "Structured note; missing-information panel; fidelity table; sign-off checklist.",
            "authoring clinician",
            "No autonomous coding, diagnosis, order, prescription, or insertion into a patient record without review.",
        ),
        workflow(
            "P2-HANDOFF-04", "Safe handoff brief", "🔄", P2,
            ["Doctor", "Nurse"], "Create a clinical handoff",
            "Clinical text", "SBAR handoff", "High", "Synthetic only",
            ["English"],
            ["ChatGPT", "Claude", "Microsoft Copilot"],
            "outpatient_cases.csv",
            "A care team needs a concise handoff that keeps uncertainty, red flags, and pending information visible.",
            "Draft an SBAR handoff using source facts only. Surface pending items, escalation triggers, and items requiring verbal confirmation.",
            "SBAR brief; pending-items list; closed-loop confirmation checklist.",
            "sending and receiving clinicians",
            "No removal of uncertainty, unverified assumption, or replacement for live escalation.",
        ),
        workflow(
            "P2-WORKFLOW-05", "Hospital workflow redesign", "🏥", P2,
            ["Hospital leader", "Quality professional"], "Improve a clinical workflow",
            "Process data", "Current/future-state workflow", "Moderate", "Synthetic only",
            ["English"],
            ["Napkin AI", "Gamma", "Julius AI", "Microsoft Copilot"],
            "hospital_workflows.csv",
            "A synthetic process has delay and rework; leaders need a future-state pilot with controls.",
            "Map current state, bottlenecks, failure modes, human decisions, future state, measures, and stop conditions.",
            "Current/future-state map; RACI; measures; risk controls; 30-day pilot.",
            "clinical process owner and quality lead",
            "No removal of safety checks or automatic redesign of staffing or clinical authority.",
        ),
        workflow(
            "P2-COMMS-06", "Referral or follow-up communication", "✉️", P2,
            ["Doctor", "Nurse"], "Improve professional communication",
            "Clinical text", "Clear professional message", "Moderate", "Synthetic only",
            ["English"],
            ["Grammarly", "ChatGPT", "Claude", "QuillBot"],
            "medical_communication_drafts.csv",
            "A clinical message needs improved clarity and empathy without changing facts or commitments.",
            "Edit for clarity, tone, and actionability while preserving every fact, date, dose, and commitment.",
            "Edited message; change log; unresolved ambiguity list; sender approval box.",
            "original author or responsible clinician",
            "No new promise, clinical claim, result, instruction, or recipient action.",
        ),
        workflow(
            "P3-PV-01", "Pharmacovigilance intake structuring", "⚠️", P3,
            ["Pharmacovigilance professional", "Medical affairs professional"], "Triage an adverse-event report",
            "Safety report", "PV intake package", "High", "Synthetic only",
            ["English"],
            ["ChatGPT", "Claude", "Google Gemini", "Julius AI"],
            "adverse_event_reports.csv",
            "A synthetic spontaneous report is incomplete; AI may structure intake but not decide causality or expectedness.",
            "Structure seriousness screening, chronology, minimum criteria, missing fields, and neutral follow-up questions.",
            "Neutral narrative; seriousness-screening rationale; missing fields; follow-up questions; escalation triggers.",
            "qualified pharmacovigilance or safety physician reviewer",
            "No causality, expectedness, reportability, coding, or submission decision.",
        ),
        workflow(
            "P3-MI-02", "Medical information response plan", "📨", P3,
            ["Medical affairs professional", "Doctor"], "Draft a medical information response",
            "Medical query", "Balanced response workflow", "High", "Synthetic only",
            ["English"],
            ["OpenEvidence", "PubMed", "ChatGPT", "Claude"],
            "pharma_medical_queries.csv",
            "An unsolicited healthcare-professional query needs a balanced, non-promotional, evidence-traceable response route.",
            "Classify the query; identify approved-source needs, search steps, MLR/PV escalation, and balanced response structure.",
            "Query classification; evidence plan; balanced outline; escalation and documentation checklist.",
            "medical information professional with MLR/PV routing",
            "No promotion, patient-specific treatment recommendation, fabricated citation, or bypass of approved review.",
        ),
        workflow(
            "P3-EVID-03", "Reproducible evidence search", "🔎", P3,
            ["Researcher", "Medical affairs professional", "Doctor"], "Search and verify evidence",
            "Research question", "Search protocol and evidence table", "Moderate", "Synthetic only",
            ["English"],
            ["PubMed", "Elicit", "Consensus", "Semantic Scholar", "SciSpace"],
            "research_questions.csv",
            "A team needs a rapid evidence scan whose search log and screening decisions remain reproducible.",
            "Create PICO/PECO, search concepts, inclusion/exclusion criteria, extraction columns, citation checks, and AI-use disclosure.",
            "Search protocol; screening log; evidence-table schema; citation-verification checklist; limitation note.",
            "qualified researcher or medical reviewer",
            "No invented paper, citation, evidence claim, or replacement for a systematic-review protocol.",
        ),
        workflow(
            "P3-SYNTH-04", "Evidence synthesis from supplied sources", "📚", P3,
            ["Researcher", "Medical affairs professional"], "Synthesize supplied evidence",
            "Research abstracts", "Source-linked synthesis", "Moderate", "Synthetic only",
            ["English"],
            ["NotebookLM", "Elicit", "SciSpace", "ChatGPT"],
            "research_abstracts_sample.csv",
            "Synthetic abstracts are used to practise source-grounded extraction; they are not citable clinical evidence.",
            "Extract study design, population, intervention/exposure, outcomes, limitations, and uncertainty. Link every statement to a supplied source ID.",
            "Evidence table; source-linked synthesis; conflict and gap log; interpretation boundary.",
            "qualified research or medical reviewer",
            "No treating recommendation, cross-source fact blending without attribution, or citation of synthetic abstracts.",
        ),
        workflow(
            "P3-MANUSCRIPT-05", "Manuscript claim and transparency review", "✍️", P3,
            ["Researcher", "Medical writer"], "Review a manuscript draft",
            "Manuscript text", "Claim-and-evidence edit log", "Moderate", "Synthetic only",
            ["English"],
            ["Paperpal", "Grammarly", "ChatGPT", "Claude"],
            "synthetic_manuscript_paragraphs.csv",
            "A synthetic draft includes overclaiming and missing disclosure; the team must preserve author accountability.",
            "Identify claims, qualifiers, unsupported inference, reporting gaps, and AI-disclosure needs. Suggest edits without inventing data.",
            "Tracked claim table; cautious rewrite; reporting checklist; author verification list.",
            "author and accountable scientific reviewer",
            "No authorship decision, invented data/citation, concealment of AI use, or approval for submission.",
        ),
        workflow(
            "P3-TRIAL-06", "Clinical-trial eligibility summary", "🧪", P3,
            ["Clinical research professional", "Doctor"], "Summarise trial eligibility",
            "Tabular data", "Pre-screen summary", "High", "Synthetic only",
            ["English"],
            ["ChatGPT", "Microsoft Copilot", "Julius AI"],
            "clinical_trial_candidates.csv",
            "Synthetic candidate fields may be summarised for manual pre-screening; enrolment stays investigator-owned.",
            "Map supplied fields to criteria, mark missing data, and produce questions for manual source verification.",
            "Criteria map; missing-data list; neutral pre-screen summary; investigator decision box.",
            "qualified investigator or delegated trial professional",
            "No eligibility, enrolment, consent, randomisation, or medical decision.",
        ),
        workflow(
            "P4-RISK-01", "AI use-case risk classification", "🛡️", P4,
            ["AI governance professional", "Hospital leader", "Medical affairs professional"], "Classify AI risk",
            "Governance scenario", "Risk-and-control card", "Moderate", "Synthetic only",
            ["English"],
            ["ChatGPT", "Microsoft Copilot", "Claude"],
            "ai_governance_policy_scenarios.csv",
            "A proposed AI use case must be classified by data, impact, autonomy, reach, and reversibility.",
            "Classify risks, identify accountable roles, minimum controls, monitoring, incident route, and stop conditions.",
            "Risk tier; rationale; control checklist; approval route; monitoring metric; stop condition.",
            "multidisciplinary AI governance group",
            "No automatic approval, legal conclusion, regulatory classification, or bypass of institutional policy.",
        ),
        workflow(
            "P4-PILOT-02", "Responsible 30-day pilot canvas", "🧭", P4,
            ["Hospital leader", "Quality professional", "AI governance professional"], "Design a responsible pilot",
            "Governance scenario", "Pilot canvas", "Moderate", "Synthetic only",
            ["English"],
            ["Gamma", "Microsoft Copilot", "ChatGPT"],
            "ai_governance_policy_scenarios.csv",
            "A low-risk use case needs a measurable, reversible pilot with named ownership.",
            "Define pain point, current baseline, data boundary, users, human review, success measure, monitoring, and stop condition.",
            "One-page pilot canvas; RACI; baseline and measures; review cadence; rollback plan.",
            "accountable business owner and governance approver",
            "No deployment, procurement, processing agreement, or approval decision.",
        ),
        workflow(
            "P4-PRIVACY-03", "Data-boundary and privacy review", "🔐", P4,
            ["Data privacy professional", "AI governance professional", "Hospital leader"], "Review data privacy",
            "Governance scenario", "Data-boundary checklist", "High", "Synthetic only",
            ["English"],
            ["Microsoft Copilot", "ChatGPT", "Claude"],
            "ai_governance_policy_scenarios.csv",
            "A workflow must specify allowed data, minimum necessary fields, account type, retention, access, and incident handling.",
            "Create a data-flow inventory and questions for privacy, security, legal, and clinical-safety review.",
            "Data-flow table; allowed/prohibited data; access/retention checklist; unresolved decisions.",
            "privacy, security, legal, and clinical-safety reviewers",
            "No legal advice, approval, transfer-impact decision, or processing of real personal data.",
        ),
        workflow(
            "P4-VENDOR-04", "AI vendor due-diligence brief", "📋", P4,
            ["Procurement professional", "AI governance professional", "Hospital leader"], "Assess an AI vendor",
            "Governance scenario", "Due-diligence questionnaire", "Moderate", "Synthetic only",
            ["English"],
            ["Microsoft Copilot", "ChatGPT", "Claude"],
            "ai_governance_policy_scenarios.csv",
            "A team needs consistent vendor questions on data use, security, performance, monitoring, and exit.",
            "Draft verifiable due-diligence questions and evidence requests; mark which responses require independent validation.",
            "Questionnaire; evidence-request list; red flags; owner; decision log template.",
            "procurement, privacy, security, legal, and clinical-safety team",
            "No vendor selection, contract approval, certification claim, or unsupported comparison.",
        ),
        workflow(
            "P4-MONITOR-05", "Post-pilot monitoring plan", "📈", P4,
            ["AI governance professional", "Quality professional", "Hospital leader"], "Monitor an AI workflow",
            "Governance scenario", "Monitoring and incident plan", "High", "Synthetic only",
            ["English"],
            ["Julius AI", "Microsoft Copilot", "ChatGPT"],
            "ai_governance_policy_scenarios.csv",
            "An approved pilot needs fidelity, safety, fairness, usage, override, and incident monitoring.",
            "Define metrics, thresholds, sampling, subgroup/language checks, audit evidence, incident route, and stop rules.",
            "Monitoring table; thresholds; review cadence; incident workflow; rollback trigger.",
            "accountable owner with safety, quality, and governance reviewers",
            "No unattended monitoring decision, silent model change, or automated continuation after threshold breach.",
        ),
        workflow(
            "P4-CONFERENCE-06", "Multidisciplinary case conference", "🗣️", P4,
            ["Doctor", "Medical affairs professional", "AI governance professional", "Hospital leader"], "Debate an AI implementation",
            "Case scenario", "Decision record", "Moderate", "Synthetic only",
            ["English"],
            ["ChatGPT", "Gamma", "Napkin AI"],
            "case_conference_scenarios.csv",
            "A cross-functional group must debate benefits, harms, evidence, accountability, and stop conditions.",
            "Generate stakeholder questions, competing perspectives, unresolved evidence needs, and a documented decision route.",
            "Stakeholder map; benefits/harms table; unresolved questions; accept/edit/reject/escalate record.",
            "multidisciplinary governance chair",
            "No fabricated consensus, suppression of dissent, or final institutional approval.",
        ),
    ]


def build_prescriptions() -> None:
    MEDICAL.mkdir(parents=True, exist_ok=True)
    rows = [
        ["RX-SYN-001", "Aarav Mehta", "Metformin 500 mg", "One tablet with evening meal", "30 days", "Review in 4 weeks", "Fully synthetic; education only", "synthetic_prescription_01.png"],
        ["RX-SYN-002", "Nisha Rao", "Amlodipine 5 mg", "One tablet every morning", "30 days", "Check blood pressure log in 2 weeks", "Fully synthetic; education only", "synthetic_prescription_02.png"],
        ["RX-SYN-003", "Kabir Shah", "Amoxicillin 500 mg", "One capsule three times daily", "5 days", "Seek help for rash or breathing difficulty", "Fully synthetic; education only", "synthetic_prescription_03.png"],
        ["RX-SYN-004", "Meera Iyer", "Pantoprazole 40 mg", "One tablet before breakfast", "14 days", "Review if symptoms persist", "Fully synthetic; education only", "synthetic_prescription_04.png"],
        ["RX-SYN-005", "Rohan Das", "Salbutamol inhaler 100 mcg", "Two puffs as directed in the supplied plan", "As needed per plan", "Urgent help for severe breathlessness", "Fully synthetic; education only", "synthetic_prescription_05.png"],
        ["RX-SYN-006", "Tara Singh", "Levothyroxine 50 mcg", "One tablet on an empty stomach each morning", "30 days", "TSH review as documented by clinician", "Fully synthetic; education only", "synthetic_prescription_06.png"],
    ]
    path = DATA / "prescription_cases.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["prescription_id", "synthetic_patient", "medicine", "instructions", "duration", "follow_up_or_warning", "source_status", "image_file"])
        writer.writerows(rows)

    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    font_path = next((item for item in font_paths if Path(item).exists()), None)
    normal = ImageFont.truetype(font_path, 28) if font_path else ImageFont.load_default()
    small = ImageFont.truetype(font_path, 21) if font_path else ImageFont.load_default()
    bold_path = font_path.replace(".ttf", "-Bold.ttf") if font_path else None
    bold = ImageFont.truetype(bold_path, 34) if bold_path and Path(bold_path).exists() else normal

    for rx_id, patient, medicine, instructions, duration, follow_up, _, image_file in rows:
        image = Image.new("RGB", (1200, 1550), "#f8fafc")
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((70, 60, 1130, 1460), radius=28, fill="white", outline="#b9cbd7", width=4)
        draw.rectangle((70, 60, 1130, 230), fill="#073647")
        draw.text((110, 105), "ALKEM AI MASTERCLASS", font=bold, fill="white")
        draw.text((110, 162), "SYNTHETIC PRESCRIPTION • NOT FOR CLINICAL USE", font=small, fill="#a5f3fc")
        draw.text((110, 290), "Dr. Ananya Kulkarni  •  Demonstration Clinic", font=normal, fill="#073647")
        draw.text((110, 340), f"Prescription ID: {rx_id}", font=small, fill="#475569")
        draw.line((110, 395, 1090, 395), fill="#d8e7ef", width=3)
        draw.text((110, 440), f"Synthetic patient: {patient}", font=normal, fill="#0f172a")
        draw.text((110, 540), "Rx", font=bold, fill="#0f766e")
        draw.text((185, 550), medicine, font=bold, fill="#0f172a")
        draw.text((185, 625), instructions, font=normal, fill="#0f172a")
        draw.text((185, 685), f"Duration: {duration}", font=normal, fill="#0f172a")
        draw.rounded_rectangle((110, 805, 1090, 1010), radius=20, fill="#eff6ff", outline="#bfdbfe", width=3)
        draw.text((145, 845), "Follow-up / warning from source", font=normal, fill="#1e3a8a")
        words = follow_up.split()
        lines, current = [], ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if draw.textlength(candidate, font=normal) > 820:
                lines.append(current)
                current = word
            else:
                current = candidate
        lines.append(current)
        for index, line in enumerate(lines):
            draw.text((145, 910 + index * 44), line, font=normal, fill="#0f172a")
        draw.text((110, 1140), "SIGNATURE", font=small, fill="#64748b")
        draw.line((110, 1240, 560, 1240), fill="#94a3b8", width=2)
        draw.text((110, 1300), "This image and every name/value on it are fully synthetic.", font=small, fill="#b45309")
        draw.text((110, 1340), "Use only to practise extraction, explanation, and human verification.", font=small, fill="#b45309")
        image.save(MEDICAL / image_file, quality=95)


def enrich_tool_matrix(workflows: list[dict]) -> None:
    catalog_by_tool: dict[str, list[dict]] = {}
    for item in workflows:
        for tool in [item["primary_tool"], *item["alternative_tools"]]:
            catalog_by_tool.setdefault(tool, []).append(item)

    matrix_path = DATA / "tool_comparison_matrix.csv"
    with matrix_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        linked = catalog_by_tool.get(row["Tool"], [])
        if not linked:
            linked = [item for item in workflows if item["dataset"] == row["Dataset"]]
        if not linked:
            linked = [item for item in workflows if item["pillar"] == P4]
        row.update(
            {
                "Pillars": ";".join(sorted({item["pillar"] for item in linked})),
                "Roles": ";".join(sorted({role for item in linked for role in item["roles"]})),
                "Input modalities": ";".join(sorted({item["input_type"] for item in linked})),
                "Output types": ";".join(sorted({item["output_type"] for item in linked})),
                "Approx INR cost": "Free tier and/or paid plan; verify current India pricing",
                "Login requirement": "Account usually required; verify organisation and region eligibility",
                "Free tier": "Varies—confirm on official site",
                "Evidence capability": (
                    "Source discovery/grounding supported; open every source"
                    if row["Tool"] in {"Elicit", "Consensus", "Semantic Scholar", "PubMed", "SciSpace", "Connected Papers", "ResearchRabbit", "OpenEvidence", "Pathway", "Perplexity", "NotebookLM"}
                    else "Do not assume evidence grounding; verify against source material"
                ),
                "Human reviewer": ";".join(sorted({item["human_reviewer"] for item in linked})),
                "Verified source": row["Official URL"],
                "Verified on": VERIFIED,
            }
        )
    fields = list(rows[0])
    with matrix_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def extend_playbook(workflows: list[dict]) -> None:
    path = DATA / "tool_demo_playbook.json"
    rows = json.loads(path.read_text(encoding="utf-8"))
    by_tool: dict[str, list[dict]] = {}
    for item in workflows:
        for tool in [item["primary_tool"], *item["alternative_tools"]]:
            by_tool.setdefault(tool, []).append(item)
    for row in rows:
        linked = by_tool.get(row["Tool"]) or [
            item for item in workflows if item["dataset"] == row["Dataset"]
        ]
        if not linked:
            linked = [item for item in workflows if item["pillar"] == P4]
        row.update(
            {
                "Pillars": [item["pillar"] for item in linked],
                "Roles": sorted({role for item in linked for role in item["roles"]}),
                "Input types": sorted({item["input_type"] for item in linked}),
                "Workflow IDs": [item["workflow_id"] for item in linked],
                "Verified on": VERIFIED,
            }
        )
    path.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    csv_path = DATA / "tool_demo_playbook.csv"
    flat_rows = []
    for row in rows:
        flat = {}
        for key, value in row.items():
            flat[key] = ";".join(value) if isinstance(value, list) else value
        flat_rows.append(flat)
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(flat_rows[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(flat_rows)
    (ROOT / "assets" / "downloads" / "tool_demo_playbook.csv").write_bytes(csv_path.read_bytes())


def update_registry() -> None:
    path = DATA / "dataset_registry.json"
    registry = json.loads(path.read_text(encoding="utf-8"))
    registry["prescription_cases.csv"] = {
        "name": "Synthetic prescriptions",
        "icon": "💊",
        "domain": "Patient understanding",
        "description": "Fully synthetic prescription images and source values for extraction, explanation, ambiguity handling, and human verification.",
    }
    registry["imaging_cases.csv"] = {
        "name": "Synthetic medical images",
        "icon": "🩻",
        "domain": "Clinical workflow",
        "description": "Fully synthetic image cases for practising image-quality checks, structured observation, limitations, and escalation—not diagnosis.",
    }
    path.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (ROOT / "assets" / "downloads" / "dataset_catalog.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["Dataset", "Name", "Domain", "Rows", "Description"])
        for filename, meta in registry.items():
            with (DATA / filename).open(newline="", encoding="utf-8") as source:
                rows = max(0, sum(1 for _ in csv.reader(source)) - 1)
            writer.writerow(
                [filename, meta["name"], meta["domain"], rows, meta["description"]]
            )


def main() -> None:
    workflows = build_workflows()
    DATA.mkdir(exist_ok=True)
    MEDICAL.mkdir(parents=True, exist_ok=True)
    (DATA / "workflow_catalog.json").write_text(
        json.dumps(workflows, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    build_prescriptions()
    with (DATA / "imaging_cases.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["image_id", "modality", "body_region", "view", "image_file", "source_status", "training_goal", "reference_boundary"])
        writer.writerow([
            "IMG-SYN-001", "Synthetic radiograph", "Chest", "PA-style",
            "synthetic_chest_xray.png", "Fully AI-generated synthetic image",
            "Separate adequacy, visible observations, uncertainty, cannot-assess items, and human escalation.",
            "No diagnostic ground truth is asserted. A qualified clinician must interpret real medical images using approved workflows.",
        ])
    enrich_tool_matrix(workflows)
    extend_playbook(workflows)
    update_registry()
    (MEDICAL / "ATTRIBUTION.md").write_text(
        "# Medical training assets\n\n"
        "- `synthetic_chest_xray.png` was generated specifically for this workshop with OpenAI image generation on 2026-07-28. It is fully synthetic, contains no patient data, and has no diagnostic ground truth.\n"
        "- `synthetic_prescription_01.png` through `synthetic_prescription_06.png` are code-generated mock prescriptions containing fictional names and values drawn from `data/prescription_cases.csv`.\n"
        "- All assets are for education only. They are not clinical evidence and must not be used for diagnosis, prescribing, or patient care.\n",
        encoding="utf-8",
    )
    print(f"Built {len(workflows)} covered workflows, 6 prescription cases, and 1 imaging case.")


if __name__ == "__main__":
    main()
