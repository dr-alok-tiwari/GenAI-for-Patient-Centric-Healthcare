import fs from "node:fs/promises";
import path from "node:path";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const OUT = path.join(ROOT, "assets", "downloads");
const SLIDES = path.join(ROOT, "assets", "slides");
const XRAY = path.join(ROOT, "assets", "medical", "synthetic_chest_xray.png");
const RX = path.join(ROOT, "assets", "medical", "synthetic_prescription_01.png");

const C = {
  navy: "#073647",
  navy2: "#0b4f60",
  teal: "#0f766e",
  cyan: "#0891b2",
  indigo: "#4f46e5",
  orange: "#c2410c",
  ink: "#0f172a",
  muted: "#475569",
  pale: "#f7fbfd",
  line: "#d8e7ef",
  white: "#ffffff",
  mint: "#ecfdf5",
  blue: "#eff6ff",
  amber: "#fff7ed",
  rose: "#fff1f2",
};

async function writeBlob(filePath, blob) {
  await fs.writeFile(filePath, new Uint8Array(await blob.arrayBuffer()));
}

function addText(slide, text, left, top, width, height, size, color = C.ink, bold = false, name = undefined) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    name,
    position: { left, top, width, height },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  shape.text = text;
  shape.text.style = { fontSize: size, color, bold };
  return shape;
}

function addCard(slide, { left, top, width, height, fill = C.white, line = C.line, radius = "rounded-2xl", shadow = "shadow-sm", name }) {
  return slide.shapes.add({
    geometry: "roundRect",
    name,
    position: { left, top, width, height },
    fill,
    line: { style: "solid", fill: line, width: 1 },
    borderRadius: radius,
    shadow,
  });
}

function addPill(slide, text, left, top, width, fill, color) {
  const pill = slide.shapes.add({
    geometry: "roundRect",
    position: { left, top, width, height: 32 },
    fill,
    line: { style: "solid", fill, width: 1 },
    borderRadius: "rounded-full",
  });
  pill.text = text;
  pill.text.style = { fontSize: 12, bold: true, color };
  return pill;
}

function chrome(slide, number, section, title, subtitle = "") {
  slide.background.fill = C.pale;
  slide.shapes.add({
    geometry: "rect",
    position: { left: 0, top: 0, width: 1280, height: 14 },
    fill: C.teal,
    line: { style: "solid", fill: C.teal, width: 0 },
  });
  addText(slide, "ALKEM  |  AI MASTERCLASS", 64, 32, 360, 24, 13, C.navy, true, "brand-lockup");
  addText(slide, section.toUpperCase(), 64, 76, 430, 24, 12, C.teal, true, "section-label");
  addText(slide, title, 64, 108, 1060, 62, 36, C.navy, true, "slide-title");
  if (subtitle) addText(slide, subtitle, 64, 176, 1060, 50, 18, C.muted, false, "slide-subtitle");
  addText(slide, String(number).padStart(2, "0"), 1180, 656, 40, 24, 12, C.muted, true, "slide-number");
  addText(slide, "GenAI for Patient-Centric Healthcare", 64, 656, 360, 24, 11, C.muted, false, "footer-title");
}

function notes(slide, content, sources = []) {
  const lines = [content, "", "Sources / verification links:", ...sources.map((source) => `- ${source}`)];
  slide.speakerNotes.textFrame.setText(lines);
  slide.speakerNotes.setVisible(true);
}

async function addImage(slide, filePath, alt, position, fit = "cover") {
  const bytes = await fs.readFile(filePath);
  const blob = bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
  slide.images.add({
    blob,
    contentType: "image/png",
    alt,
    fit,
    position,
    geometry: "roundRect",
    borderRadius: "rounded-2xl",
  });
}

const meta = [];
function register(number, title, chapter, summary, cue, note, badges = [], related_labs = []) {
  meta.push({
    number,
    image: `page-${String(number).padStart(2, "0")}.png`,
    title,
    chapter,
    summary,
    cue,
    notes: note,
    badges,
    related_labs,
  });
}

async function main() {
  await fs.mkdir(OUT, { recursive: true });
  await fs.mkdir(SLIDES, { recursive: true });
  const deck = Presentation.create({ slideSize: { width: 1280, height: 720 } });

  {
    const s = deck.slides.add();
    s.background.fill = C.navy;
    s.shapes.add({
      geometry: "ellipse",
      position: { left: 924, top: 0, width: 356, height: 338 },
      fill: "#0b6170",
      line: { style: "solid", fill: "#0b6170", width: 0 },
    });
    s.shapes.add({
      geometry: "ellipse",
      position: { left: 1010, top: 360, width: 270, height: 360 },
      fill: "#075664",
      line: { style: "solid", fill: "#075664", width: 0 },
    });
    addPill(s, "ALKEM  |  AI MASTERCLASS", 70, 62, 264, "#0b5260", "#a5f3fc");
    addText(s, "GenAI for\nPatient-Centric\nHealthcare", 70, 150, 710, 260, 54, C.white, true, "title");
    addText(s, "Practical, responsible workflows for doctors and pharma professionals", 74, 432, 650, 72, 23, "#d7f9ff", false, "subtitle");
    addPill(s, "60 MIN THEORY", 74, 548, 154, "#0f766e", C.white);
    addPill(s, "90 MIN HANDS-ON", 244, 548, 180, "#0891b2", C.white);
    addPill(s, "SYNTHETIC DATA", 440, 548, 174, "#4f46e5", C.white);
    addText(s, "Four pillars • medical-specific demos • qualified human decisions", 74, 620, 700, 28, 15, "#b9e9ef", false);
    const labels = [
      ["🤝", "Patient engagement", C.cyan],
      ["🩺", "Clinical workflow", C.teal],
      ["🔬", "Pharma & research", C.indigo],
      ["🛡️", "Responsible AI", C.orange],
    ];
    labels.forEach(([icon, label, color], index) => {
      const top = 126 + index * 116;
      addCard(s, { left: 840, top, width: 332, height: 92, fill: C.white, line: C.white, shadow: "shadow-lg" });
      addText(s, icon, 864, top + 22, 48, 48, 26, color, true);
      addText(s, label, 924, top + 29, 220, 34, 18, C.navy, true);
    });
    notes(s, "Open by asking participants to name one task they would improve—not one tool they want to use. Set the contract: synthetic data, bounded tasks, source checks, and qualified human authority.");
    register(1, "GenAI for Patient-Centric Healthcare", "Opening", "Alkem AI Masterclass title and programme promise.", "Ask for one workflow pain point from the room.", "Establish scope and safety contract.", ["60 + 90 min", "Four pillars"], []);
  }

  {
    const s = deck.slides.add();
    chrome(s, 2, "Opening", "The learning contract", "Useful output is not the goal. Verified, accountable workflow improvement is.");
    const items = [
      ["1", "Use approved data", "Synthetic, public, or institution-approved de-identified inputs only.", C.cyan],
      ["2", "Bound the task", "Draft, extract, structure, compare, or explain—never silently decide.", C.teal],
      ["3", "Verify the source", "Check every consequential fact, citation, ambiguity, and omission.", C.indigo],
      ["4", "Keep human authority", "Record accept, edit, reject, or escalate—and who owns it.", C.orange],
    ];
    items.forEach(([num, title, body, color], index) => {
      const left = 64 + (index % 2) * 576;
      const top = 258 + Math.floor(index / 2) * 176;
      addCard(s, { left, top, width: 540, height: 148, fill: C.white });
      addPill(s, num, left + 24, top + 24, 42, color, C.white);
      addText(s, title, left + 86, top + 24, 414, 34, 21, C.navy, true);
      addText(s, body, left + 86, top + 68, 414, 58, 16, C.muted, false);
    });
    notes(s, "Use a prescription example: fluency cannot compensate for one wrong strength. Explain that approval, data handling, and review requirements come from the organisation and the intended use—not from the model's confidence.", [
      "https://www.who.int/publications/i/item/9789240029200",
      "https://www.nist.gov/itl/ai-risk-management-framework",
    ]);
    register(2, "The learning contract", "Opening", "Four rules: approved data, bounded task, source verification, and human authority.", "Have participants repeat the four rules in one sentence.", "Use a prescription error example to make the contract concrete.", ["Synthetic data", "Human authority"], []);
  }

  {
    const s = deck.slides.add();
    chrome(s, 3, "Programme map", "Four pillars—from patient need to responsible implementation");
    const pillars = [
      ["01", "Patient Understanding\nand Engagement", "Explain • translate • teach back", C.cyan, C.blue],
      ["02", "Clinical Workflow\nand Decision Support", "Structure • observe • escalate", C.teal, C.mint],
      ["03", "Pharma, Research and\nProfessional Productivity", "Search • extract • document", C.indigo, "#eef2ff"],
      ["04", "Responsible AI, Governance\nand Implementation", "Classify • control • monitor", C.orange, C.amber],
    ];
    pillars.forEach(([num, title, verbs, color, fill], index) => {
      const left = 64 + index * 286;
      addCard(s, { left, top: 240, width: 260, height: 334, fill, line: color, shadow: "shadow-md" });
      addPill(s, num, left + 22, 264, 56, color, C.white);
      addText(s, title, left + 22, 330, 214, 104, 22, C.navy, true);
      addText(s, verbs, left + 22, 454, 214, 54, 16, C.muted, false);
      addText(s, "Human decision\nat the end", left + 22, 522, 214, 52, 14, color, true);
    });
    notes(s, "The four pillars are a programme structure, not a maturity score. A workflow may span pillars; the selection engine maps roles and tasks to complete supported workflows.");
    register(3, "Four pillars", "Programme map", "A concise architecture for patient, clinical, pharma/research, and governance use cases.", "Ask participants to stand or raise a hand for their primary pillar.", "Show how workflows can span pillars.", ["4 pillars", "24 workflows"], []);
  }

  {
    const s = deck.slides.add();
    chrome(s, 4, "Pillar 1", "Prescription extraction: separate reading from explaining", "A synthetic image, an exact source table, and a clinician/pharmacist decision.");
    await addImage(s, RX, "Fully synthetic prescription generated for the workshop", { left: 64, top: 240, width: 380, height: 366 }, "contain");
    const steps = [
      ["1", "Extract", "Transcribe legible fields exactly."],
      ["2", "Flag", "Mark ambiguity [UNREADABLE]; never guess."],
      ["3", "Explain", "Use plain language without adding advice."],
      ["4", "Verify", "Compare field-by-field; record human decision."],
    ];
    steps.forEach(([num, title, body], index) => {
      const top = 242 + index * 86;
      addPill(s, num, 488, top, 42, index < 2 ? C.cyan : C.teal, C.white);
      addText(s, title, 548, top - 2, 190, 28, 19, C.navy, true);
      addText(s, body, 548, top + 30, 350, 42, 15, C.muted);
    });
    addCard(s, { left: 922, top: 242, width: 294, height: 344, fill: C.amber, line: "#fdba74" });
    addText(s, "Never let the model", 948, 270, 242, 30, 19, C.orange, true);
    addText(s, "• reconstruct unclear text\n• infer the indication\n• prescribe or substitute\n• assess interactions autonomously\n• overrule the source prescription", 948, 320, 230, 176, 16, C.ink);
    addText(s, "Owner: clinician or pharmacist", 948, 528, 230, 34, 15, C.orange, true);
    notes(s, "Run the synthetic prescription demo. Keep the facilitator reference hidden until participants have extracted the fields. Score exactness, ambiguity handling, and scope—not elegance.");
    register(4, "Prescription extraction", "Pillar 1", "A safe separation of extraction, explanation, and human verification.", "Hide reference values until after extraction.", "Use the synthetic prescription image; never ask participants to use real patient documents.", ["Synthetic prescription", "No guessing"], [1]);
  }

  {
    const s = deck.slides.add();
    chrome(s, 5, "Pillar 1", "From discharge summary to patient action plan", "Preserve the medicine, date, warning, and follow-up—change only clarity.");
    const leftCard = addCard(s, { left: 64, top: 240, width: 470, height: 340, fill: C.white });
    addPill(s, "CLINICIAN SOURCE", 90, 266, 158, C.navy, C.white);
    addText(s, "“Continue medication as listed. Review as advised. Return if symptoms worsen.”", 92, 328, 386, 100, 22, C.ink, true);
    addText(s, "What is missing for a patient?\n• exact action\n• urgency threshold\n• timing\n• comprehension check", 92, 448, 386, 106, 16, C.muted);
    s.shapes.add({ geometry: "rightArrow", position: { left: 562, top: 362, width: 92, height: 72 }, fill: C.teal, line: { style: "solid", fill: C.teal, width: 1 } });
    addCard(s, { left: 684, top: 240, width: 532, height: 340, fill: C.mint, line: "#a7f3d0" });
    addPill(s, "PATIENT ACTION PLAN", 712, 266, 176, C.teal, C.white);
    addText(s, "1. What happened—in plain words\n2. Exact medicine/action schedule\n3. Warning signs and urgent route\n4. Follow-up: who, when, where\n5. Three teach-back questions", 714, 324, 446, 184, 21, C.ink, true);
    addText(s, "Bilingual drafts require fluent clinical review.", 714, 526, 446, 32, 15, C.teal, true);
    notes(s, "Ask: what must never change when simplifying? Elicit medicine, dose, duration, dates, red flags, follow-up, and uncertainty. For translation, preserve medicine/test names and require a fluent clinical reviewer.");
    register(5, "Patient action plan", "Pillar 1", "Plain-language discharge and teach-back without changing clinical meaning.", "Ask what must never change during simplification.", "Connect clarity to teach-back and translation review.", ["Teach-back", "Multilingual review"], [3]);
  }

  {
    const s = deck.slides.add();
    chrome(s, 6, "Pillar 2", "Medical images: demonstrate the boundary, not a diagnosis", "General-purpose image models are not a substitute for qualified interpretation or validated medical-device workflows.");
    await addImage(s, XRAY, "Fully AI-generated synthetic chest radiograph with no diagnostic ground truth", { left: 64, top: 238, width: 446, height: 388 }, "contain");
    addPill(s, "FULLY SYNTHETIC • NO GROUND TRUTH", 88, 254, 282, C.orange, C.white);
    const good = addCard(s, { left: 548, top: 238, width: 304, height: 352, fill: C.mint, line: "#a7f3d0" });
    addText(s, "Practise", 574, 266, 230, 34, 21, C.teal, true);
    addText(s, "✓ image adequacy\n✓ neutral visible observations\n✓ cannot-assess items\n✓ uncertainty\n✓ human escalation", 574, 322, 230, 190, 18, C.ink);
    const bad = addCard(s, { left: 884, top: 238, width: 332, height: 352, fill: C.rose, line: "#fecdd3" });
    addText(s, "Do not claim", 910, 266, 250, 34, 21, "#9f1239", true);
    addText(s, "✕ diagnosis\n✕ emergency clearance\n✕ treatment advice\n✕ “normal” or “safe” verdict\n✕ validated performance", 910, 322, 250, 190, 18, C.ink);
    notes(s, "Do not ask the model for a diagnosis. The demonstration is about image adequacy, descriptive observation, uncertainty, and escalation. Explicitly mention the product limitation on specialised medical images.", [
      "https://help.openai.com/articles/8400551-chatgpt-image-inputs-faq",
      "https://www.fda.gov/medical-devices/software-medical-device-samd/artificial-intelligence-enabled-medical-devices",
    ]);
    register(6, "Medical-image boundary", "Pillar 2", "A non-diagnostic observation workflow with limitations and escalation.", "Model the boundary by refusing to provide a diagnosis.", "Use only the synthetic radiograph and product limitation source.", ["No diagnosis", "Qualified interpretation"], [2]);
  }

  {
    const s = deck.slides.add();
    chrome(s, 7, "Pillar 2", "Clinical reasoning: use AI to reduce omission, not own the decision");
    const items = [
      ["COMMON", "Common / likely", "Keep prevalence and presentation in view.", C.blue, C.cyan],
      ["CAN'T MISS", "Cannot-miss", "Separate severity from probability.", C.rose, "#be123c"],
      ["MISSING", "History / exam gaps", "Make absent information visible.", C.amber, C.orange],
      ["ESCALATE", "Urgency triggers", "Define when human action cannot wait.", C.mint, C.teal],
    ];
    items.forEach(([pill, title, body, fill, color], index) => {
      const left = 64 + (index % 2) * 574;
      const top = 230 + Math.floor(index / 2) * 176;
      addCard(s, { left, top, width: 540, height: 148, fill, line: color });
      addPill(s, pill, left + 24, top + 22, 110, color, C.white);
      addText(s, title, left + 154, top + 18, 340, 36, 20, C.navy, true);
      addText(s, body, left + 154, top + 64, 340, 52, 16, C.muted);
    });
    addCard(s, { left: 64, top: 594, width: 1114, height: 44, fill: C.navy, line: C.navy, radius: "rounded-full" });
    addText(s, "Always ask: What evidence supports this? What opposes it? What would change urgency?", 92, 604, 1058, 24, 16, C.white, true);
    notes(s, "Run a cognitive forcing pause after the model response: What did it omit? Where could anchoring or automation bias occur? What new data would change urgency? Diagnosis and treatment remain clinician-owned.");
    register(7, "Clinical reasoning", "Pillar 2", "Common, cannot-miss, missing data, and escalation kept separate.", "Pause for a cognitive-bias check.", "Judge the checklist against the case, not its fluency.", ["No final diagnosis", "Red flags"], [4]);
  }

  {
    const s = deck.slides.add();
    chrome(s, 8, "Pillar 3", "Two lanes: safety intake and evidence verification", "Both gain speed from structure. Neither delegates qualified judgement.");
    addCard(s, { left: 64, top: 236, width: 540, height: 354, fill: C.amber, line: "#fdba74" });
    addPill(s, "PHARMACOVIGILANCE", 92, 264, 190, C.orange, C.white);
    addText(s, "AI may help", 92, 320, 210, 30, 20, C.navy, true);
    addText(s, "• structure chronology\n• screen seriousness fields\n• identify missing data\n• draft neutral follow-up", 92, 364, 236, 150, 17, C.ink);
    addText(s, "Never decide causality, expectedness,\ncoding, or reportability.", 330, 364, 230, 106, 17, C.orange, true);
    addCard(s, { left: 638, top: 236, width: 540, height: 354, fill: C.blue, line: "#93c5fd" });
    addPill(s, "EVIDENCE", 666, 264, 112, C.indigo, C.white);
    addText(s, "AI may help", 666, 320, 210, 30, 20, C.navy, true);
    addText(s, "• form PICO/PECO\n• expand search concepts\n• extract supplied sources\n• map evidence gaps", 666, 364, 236, 150, 17, C.ink);
    addText(s, "Never invent a citation.\nOpen and verify every source.", 904, 364, 230, 88, 17, C.indigo, true);
    addText(s, "Human-owned: safety decisions • screening log • source checks • interpretation • disclosure", 92, 612, 1046, 28, 16, C.navy, true);
    notes(s, "Contrast the two lanes. In PV, qualified reviewers own causality, expectedness, coding, and reporting. In evidence work, the team owns the reproducible search, screening decisions, source opening, extraction checks, and interpretation.");
    register(8, "PV and evidence", "Pillar 3", "A side-by-side boundary for safety intake and evidence work.", "Ask which decisions cannot be delegated in each lane.", "Demonstrate neutral intake and citation opening.", ["PV review", "Open every source"], [5, 6]);
  }

  {
    const s = deck.slides.add();
    chrome(s, 9, "Pillar 4", "Risk follows data × impact × autonomy × reach", "Use the highest-risk dimension to set minimum controls and a stop condition.");
    const axes = [
      ["DATA", "Synthetic → identifiable / highly sensitive", C.cyan],
      ["IMPACT", "Communication → influences care", C.teal],
      ["AUTONOMY", "Draft → default → autonomous action", C.indigo],
      ["REACH", "Sandbox → patient / population scale", C.orange],
    ];
    axes.forEach(([label, desc, color], index) => {
      const top = 230 + index * 86;
      addPill(s, label, 64, top, 104, color, C.white);
      addText(s, desc, 190, top - 1, 480, 34, 18, C.ink, true);
      s.shapes.add({ geometry: "line", position: { left: 676, top: top + 17, width: 208, height: 0 }, fill: "none", line: { style: "solid", fill: color, width: 6 } });
      addText(s, "LOWER", 676, top + 28, 70, 20, 10, C.muted, true);
      addText(s, "HIGHER", 826, top + 28, 70, 20, 10, C.muted, true);
    });
    addCard(s, { left: 930, top: 230, width: 286, height: 342, fill: C.white, line: C.orange });
    addText(s, "Minimum decision record", 956, 260, 234, 58, 21, C.navy, true);
    addText(s, "• accountable owner\n• allowed data\n• human review\n• monitoring metric\n• incident route\n• stop / rollback rule", 956, 334, 226, 190, 17, C.ink);
    notes(s, "Use the governance workbench in the app. The score is a discussion aid, not legal or regulatory advice. High or critical use cases need multidisciplinary review and may need validated or regulated pathways.", [
      "https://www.nist.gov/itl/ai-risk-management-framework",
      "https://www.who.int/publications/i/item/9789240029200",
      "https://www.meity.gov.in/documents/act-and-policies/digital-personal-data-protection-rules-2025-gDOxUjMtQWa",
    ]);
    register(9, "Risk and controls", "Pillar 4", "A practical four-axis screen for data, impact, autonomy, and reach.", "Classify one audience use case live.", "Treat the result as governance input, not legal advice.", ["Risk tier", "Stop condition"], []);
  }

  {
    const s = deck.slides.add();
    chrome(s, 10, "Tool selection", "Choose the workflow first; let supported options cascade", "The app offers only intersections backed by a complete prompt, dataset, output, verification, and reviewer.");
    const labels = ["Pillar", "Role", "Task", "Input", "Language", "Workflow"];
    labels.forEach((label, index) => {
      const left = 64 + index * 185;
      addCard(s, { left, top: 272, width: 158, height: 88, fill: index === 5 ? C.mint : C.white, line: index === 5 ? C.teal : C.line });
      addText(s, String(index + 1), left + 18, 288, 30, 28, 16, index === 5 ? C.teal : C.cyan, true);
      addText(s, label, left + 18, 324, 122, 24, 17, C.navy, true);
      if (index < labels.length - 1) {
        s.shapes.add({ geometry: "rightArrow", position: { left: left + 158, top: 302, width: 28, height: 28 }, fill: C.teal, line: { style: "solid", fill: C.teal, width: 0 } });
      }
    });
    const questions = [
      ["Data fit", "Can this account and workflow process the intended data?"],
      ["Capability", "Does the tool support the input and output—and with what limitations?"],
      ["Evidence", "Can claims and citations be opened, traced, and checked?"],
      ["Human fit", "Who reviews, what gets escalated, and what stops the workflow?"],
    ];
    questions.forEach(([title, body], index) => {
      const left = 64 + (index % 2) * 576;
      const top = 414 + Math.floor(index / 2) * 102;
      addPill(s, title.toUpperCase(), left, top, 132, index % 2 === 0 ? C.cyan : C.indigo, C.white);
      addText(s, body, left + 150, top - 4, 390, 54, 15, C.muted, false);
    });
    notes(s, "Demonstrate the Prompt Studio. Every option is derived from workflows remaining after previous selections. An unmatched free-text search returns a labelled closest verified alternative; it never fabricates a new workflow.");
    register(10, "Workflow-first tool selection", "Tool selection", "Cascading selectors guarantee complete, supported routes.", "Show a role/task/language combination in Prompt Studio.", "Explain that unsupported intersections are removed before selection.", ["100% visible-option coverage", "Verified alternatives"], []);
  }

  {
    const s = deck.slides.add();
    chrome(s, 11, "Hands-on", "90 minutes: six medical and pharma exercises", "For every lab: 3 min orient • 6 min run • 4 min verify • 2 min decide.");
    const labs = [
      ["01", "Prescription extraction", "Exactness • ambiguity • explain", C.cyan],
      ["02", "Image observation", "Adequacy • boundary • escalate", C.teal],
      ["03", "Discharge + language", "Meaning • teach-back • review", C.indigo],
      ["04", "Differential + red flags", "Omission • bias • urgency", C.orange],
      ["05", "PV intake", "Neutrality • missingness • route", "#be123c"],
      ["06", "Evidence verification", "Search log • source checks", "#0369a1"],
    ];
    labs.forEach(([num, title, body, color], index) => {
      const left = 64 + (index % 3) * 380;
      const top = 240 + Math.floor(index / 3) * 172;
      addCard(s, { left, top, width: 350, height: 144, fill: C.white, line: color });
      addPill(s, num, left + 22, top + 22, 54, color, C.white);
      addText(s, title, left + 94, top + 20, 230, 34, 19, C.navy, true);
      addText(s, body, left + 94, top + 64, 230, 48, 15, C.muted);
    });
    addCard(s, { left: 64, top: 598, width: 1110, height: 44, fill: C.navy, line: C.navy, radius: "rounded-full" });
    addText(s, "Decision record for every output: ACCEPT • EDIT • REJECT • ESCALATE", 192, 607, 860, 26, 17, C.white, true);
    notes(s, "Assign teams and tools before starting. Do not require any participant to upload real patient or company-confidential data. Have an offline fallback for every live tool demonstration.");
    register(11, "Six hands-on labs", "Hands-on", "The six 15-minute medical and pharma labs.", "Assign tools and cases before the clock starts.", "Use the 3-6-4-2 timing and require a decision record.", ["6 × 15 min", "Accept/edit/reject/escalate"], [1, 2, 3, 4, 5, 6]);
  }

  {
    const s = deck.slides.add();
    chrome(s, 12, "Close", "Your 30-day responsible pilot", "Start with a reversible workflow, a measurable outcome, and a stop rule.");
    const steps = [
      ["PAIN POINT", "One bounded task worth improving"],
      ["OWNER", "One accountable person or team"],
      ["DATA", "Allowed, prohibited, and minimum necessary"],
      ["MEASURE", "Baseline, target, and quality/safety metric"],
      ["REVIEW", "Human checks, escalation, and audit evidence"],
      ["STOP", "Threshold that pauses or rolls back the pilot"],
    ];
    steps.forEach(([title, body], index) => {
      const left = 64 + (index % 3) * 380;
      const top = 232 + Math.floor(index / 3) * 158;
      addCard(s, { left, top, width: 350, height: 130, fill: index === 5 ? C.amber : C.white, line: index === 5 ? C.orange : C.line });
      addPill(s, title, left + 22, top + 20, 112, index === 5 ? C.orange : C.teal, C.white);
      addText(s, body, left + 22, top + 66, 304, 46, 16, C.ink, true);
    });
    addText(s, "The model drafts. The source constrains. The qualified human decides.", 150, 574, 980, 44, 28, C.navy, true);
    addPill(s, "TAKE THE WORKBOOK + APP + VERIFIED TOOL MATRIX", 364, 634, 550, C.navy, C.white);
    notes(s, "Close with each team naming one pilot and one stop condition. Direct participants to the workbook, facilitator handbook, app, dataset kit, and verified tool matrix.");
    register(12, "30-day responsible pilot", "Close", "A six-part pilot canvas and the final accountability message.", "Ask every team for one success measure and one stop rule.", "End with a written implementation commitment.", ["Reversible pilot", "Named owner"], []);
  }

  for (const [index, slide] of deck.slides.items.entries()) {
    const stem = `page-${String(index + 1).padStart(2, "0")}`;
    const png = await deck.export({ slide, format: "png", scale: 1 });
    await writeBlob(path.join(SLIDES, `${stem}.png`), png);
    const layout = await slide.export({ format: "layout" });
    await fs.writeFile(path.join(SLIDES, `${stem}.layout.json`), await layout.text());
  }
  await writeBlob(path.join(SLIDES, "deck-montage.webp"), await deck.export({ format: "webp", montage: true, scale: 1 }));
  await fs.writeFile(path.join(SLIDES, "slides_meta.json"), JSON.stringify(meta, null, 2) + "\n");
  const pptx = await PresentationFile.exportPptx(deck);
  await pptx.save(path.join(OUT, "Alkem_AI_Masterclass_Healthcare.pptx"));
  console.log(`Created ${deck.slides.items.length} editable slides.`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
