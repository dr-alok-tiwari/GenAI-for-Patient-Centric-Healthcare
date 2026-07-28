from __future__ import annotations

BRAND = {
    "organisation": "Alkem",
    "programme": "AI Masterclass",
    "title": "GenAI for Patient-Centric Healthcare",
    "subtitle": "Practical, responsible workflows for doctors and pharma professionals",
    "lockup": "ALKEM  |  AI MASTERCLASS",
}

PILLARS = [
    {
        "name": "Patient Understanding and Engagement",
        "short": "Patient engagement",
        "icon": "🤝",
        "colour": "#0891b2",
        "promise": "Make trusted health information clearer, more inclusive and more actionable.",
        "examples": "Prescription explanation • discharge teach-back • multilingual counselling",
    },
    {
        "name": "Clinical Workflow and Decision Support",
        "short": "Clinical workflow",
        "icon": "🩺",
        "colour": "#0f766e",
        "promise": "Structure information and surface missingness while qualified clinicians retain decisions.",
        "examples": "Image observation • red-flag checklist • documentation support",
    },
    {
        "name": "Pharma, Research and Professional Productivity",
        "short": "Pharma & research",
        "icon": "🔬",
        "colour": "#4f46e5",
        "promise": "Accelerate evidence, medical-affairs and pharmacovigilance preparation with traceability.",
        "examples": "PV intake • evidence search • medical information response",
    },
    {
        "name": "Responsible AI, Governance and Implementation",
        "short": "Responsible AI",
        "icon": "🛡️",
        "colour": "#c2410c",
        "promise": "Match controls to data, impact and autonomy—and define who can stop the workflow.",
        "examples": "Risk tiering • pilot canvas • human review and escalation",
    },
]

PILLAR_NAMES = [item["name"] for item in PILLARS]

SAFETY_ACKNOWLEDGEMENT = (
    "I confirm that I will use only synthetic, public, or institution-approved de-identified "
    "data; I will not use the output as a diagnosis, prescription, or autonomous clinical decision; "
    "and a qualified human will verify every consequential output."
)

SOURCE_URLS = {
    "WHO AI ethics": "https://www.who.int/publications/i/item/9789240029200",
    "NIST AI RMF": "https://www.nist.gov/itl/ai-risk-management-framework",
    "FDA AI-enabled devices": (
        "https://www.fda.gov/medical-devices/software-medical-device-samd/"
        "artificial-intelligence-enabled-medical-devices"
    ),
    "FDA clinical decision support FAQ": (
        "https://www.fda.gov/medical-devices/software-medical-device-samd/"
        "clinical-decision-support-software-frequently-asked-questions-faqs"
    ),
    "ChatGPT image-input limitations": "https://help.openai.com/articles/8400551-chatgpt-image-inputs-faq",
    "India Digital Personal Data Protection Act": (
        "https://www.meity.gov.in/static/uploads/2024/06/"
        "2bf1f0e9f04e6fb4f8fef35e82c42aa5.pdf"
    ),
    "India Digital Personal Data Protection Rules": (
        "https://www.meity.gov.in/documents/act-and-policies/"
        "digital-personal-data-protection-rules-2025-gDOxUjMtQWa"
    ),
}
