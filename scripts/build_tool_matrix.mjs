import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const OUT = path.join(ROOT, "assets", "downloads");
const PREVIEWS = "/tmp/alkem_tool_matrix_previews";
const NAVY = "#073647";
const TEAL = "#0F766E";
const CYAN = "#0891B2";
const INDIGO = "#4F46E5";
const ORANGE = "#C2410C";
const PALE = "#F7FBFD";
const LINE = "#D8E7EF";
const WHITE = "#FFFFFF";
const MINT = "#ECFDF5";
const AMBER = "#FFF7ED";
const MUTED = "#475569";

function parseCsv(text) {
  const rows = [];
  let row = [];
  let field = "";
  let quoted = false;
  for (let i = 0; i < text.length; i += 1) {
    const char = text[i];
    if (quoted) {
      if (char === '"' && text[i + 1] === '"') {
        field += '"';
        i += 1;
      } else if (char === '"') {
        quoted = false;
      } else {
        field += char;
      }
    } else if (char === '"') {
      quoted = true;
    } else if (char === ",") {
      row.push(field);
      field = "";
    } else if (char === "\n") {
      row.push(field.replace(/\r$/, ""));
      rows.push(row);
      row = [];
      field = "";
    } else {
      field += char;
    }
  }
  if (field || row.length) {
    row.push(field);
    rows.push(row);
  }
  return rows.filter((item) => item.some((value) => value !== ""));
}

function columnName(index) {
  let name = "";
  let number = index + 1;
  while (number > 0) {
    const rem = (number - 1) % 26;
    name = String.fromCharCode(65 + rem) + name;
    number = Math.floor((number - 1) / 26);
  }
  return name;
}

function styleTitle(sheet, range) {
  sheet.getRange(range).format = {
    fill: NAVY,
    font: { bold: true, color: WHITE, size: 20 },
    verticalAlignment: "center",
  };
  sheet.getRange(range).format.rowHeight = 34;
}

function styleHeader(range, fill = TEAL) {
  range.format = {
    fill,
    font: { bold: true, color: WHITE },
    borders: { preset: "all", style: "thin", color: LINE },
    verticalAlignment: "center",
    wrapText: true,
  };
}

function styleBody(range) {
  range.format = {
    borders: { preset: "all", style: "thin", color: LINE },
    verticalAlignment: "top",
    wrapText: true,
  };
}

function addTitle(sheet, title, subtitle, lastColumn) {
  sheet.mergeCells(`A1:${lastColumn}1`);
  sheet.getRange("A1").values = [[title]];
  styleTitle(sheet, `A1:${lastColumn}1`);
  sheet.mergeCells(`A2:${lastColumn}2`);
  sheet.getRange("A2").values = [[subtitle]];
  sheet.getRange(`A2:${lastColumn}2`).format = {
    fill: PALE,
    font: { color: MUTED, italic: true },
    wrapText: true,
  };
  sheet.getRange(`A2:${lastColumn}2`).format.rowHeight = 32;
  sheet.showGridLines = false;
}

function listValues(value) {
  return Array.isArray(value) ? value.join("; ") : String(value ?? "");
}

async function main() {
  await fs.mkdir(OUT, { recursive: true });
  await fs.mkdir(PREVIEWS, { recursive: true });
  const toolRows = parseCsv(await fs.readFile(path.join(ROOT, "data", "tool_comparison_matrix.csv"), "utf8"));
  const headers = toolRows[0];
  const tools = toolRows.slice(1);
  const workflows = JSON.parse(await fs.readFile(path.join(ROOT, "data", "workflow_catalog.json"), "utf8"));
  const labs = [
    ["1", "Prescription extraction and explanation", "Patient Understanding and Engagement", "prescription_cases.csv", "ChatGPT", "Clinician or pharmacist"],
    ["2", "Medical-image observation boundary", "Clinical Workflow and Decision Support", "imaging_cases.csv", "ChatGPT", "Radiologist or treating clinician"],
    ["3", "Discharge plan and multilingual teach-back", "Patient Understanding and Engagement", "discharge_summaries.csv", "ChatGPT / Gemini / DeepL", "Treating clinician plus fluent-language reviewer"],
    ["4", "Differential and red-flag checklist", "Clinical Workflow and Decision Support", "clinical_reasoning_cases.csv", "OpenEvidence / Pathway / ChatGPT", "Qualified treating clinician"],
    ["5", "Pharmacovigilance intake", "Pharma, Research and Professional Productivity", "adverse_event_reports.csv", "ChatGPT / Claude / Gemini", "PV professional or safety physician"],
    ["6", "Evidence search and citation verification", "Pharma, Research and Professional Productivity", "research_questions.csv", "PubMed / Elicit / Consensus", "Researcher or medical reviewer"],
  ];
  const sources = [
    ["WHO AI ethics", "https://www.who.int/publications/i/item/9789240029200", "Ethics and governance for AI in health", "2026-07-28"],
    ["NIST AI RMF", "https://www.nist.gov/itl/ai-risk-management-framework", "Voluntary AI risk-management framework and GenAI profile", "2026-07-28"],
    ["FDA AI-enabled devices", "https://www.fda.gov/medical-devices/software-medical-device-samd/artificial-intelligence-enabled-medical-devices", "AI-enabled medical-device context", "2026-07-28"],
    ["FDA CDS FAQ", "https://www.fda.gov/medical-devices/software-medical-device-samd/clinical-decision-support-software-frequently-asked-questions-faqs", "Clinical decision support regulatory FAQ", "2026-07-28"],
    ["ChatGPT image limitations", "https://help.openai.com/articles/8400551-chatgpt-image-inputs-faq", "Product image-input limitations, including specialised medical images", "2026-07-28"],
    ["India DPDP Act", "https://www.meity.gov.in/static/uploads/2024/06/2bf1f0e9f04e6fb4f8fef35e82c42aa5.pdf", "Official legislation source", "2026-07-28"],
    ["India DPDP Rules", "https://www.meity.gov.in/documents/act-and-policies/digital-personal-data-protection-rules-2025-gDOxUjMtQWa", "Official rules source", "2026-07-28"],
  ];

  const wb = Workbook.create();
  const overview = wb.worksheets.add("Overview");
  const toolSheet = wb.worksheets.add("Tool Matrix");
  const workflowSheet = wb.worksheets.add("Workflow Catalog");
  const coverageSheet = wb.worksheets.add("Dropdown Coverage");
  const labsSheet = wb.worksheets.add("Lab Matrix");
  const pilotSheet = wb.worksheets.add("Pilot Canvas");
  const sourcesSheet = wb.worksheets.add("Source Register");

  addTitle(overview, "ALKEM AI MASTERCLASS — HEALTHCARE TOOL MATRIX", "Workflow-first comparison, dropdown coverage, labs, pilot canvas, and source register. Product details can change; verify on official sites.", "H");
  overview.getRange("A4:B9").values = [
    ["Metric", "Value"],
    ["Verified tools", null],
    ["Complete workflows", null],
    ["Covered pillars", null],
    ["Medical/pharma labs", null],
    ["Visible-option gaps", null],
  ];
  styleHeader(overview.getRange("A4:B4"));
  styleBody(overview.getRange("A5:B9"));
  overview.getRange("B5").formulas = [["=COUNTA('Tool Matrix'!A4:A32)"]];
  overview.getRange("B6").formulas = [["=COUNTA('Workflow Catalog'!A4:A27)"]];
  overview.getRange("B7").formulas = [["=COUNTA(D5:D8)"]];
  overview.getRange("B8").formulas = [["=COUNTA('Lab Matrix'!A4:A9)"]];
  overview.getRange("B9").formulas = [["=COUNTIF('Dropdown Coverage'!D4:D200,\"GAP\")"]];
  overview.getRange("D4:E8").values = [
    ["Pillar", "Workflows"],
    ["Patient engagement", workflows.filter((x) => x.pillar.startsWith("Patient")).length],
    ["Clinical workflow", workflows.filter((x) => x.pillar.startsWith("Clinical")).length],
    ["Pharma & research", workflows.filter((x) => x.pillar.startsWith("Pharma")).length],
    ["Responsible AI", workflows.filter((x) => x.pillar.startsWith("Responsible")).length],
  ];
  styleHeader(overview.getRange("D4:E4"), INDIGO);
  styleBody(overview.getRange("D5:E8"));
  const chart = overview.charts.add("bar", overview.getRange("D4:E8"));
  chart.title = "Complete workflows by pillar";
  chart.hasLegend = false;
  chart.setPosition("D10", "H25");
  overview.getRange("A11:B16").values = [
    ["Selection check", "Question"],
    ["Data fit", "Can the account/workflow process the intended data?"],
    ["Capability", "Does the tool support the input/output with known limitations?"],
    ["Evidence", "Can claims and citations be opened and verified?"],
    ["Human fit", "Who reviews, escalates, monitors, and stops the workflow?"],
    ["Price/access", "Was current India pricing, region, login, and eligibility rechecked?"],
  ];
  styleHeader(overview.getRange("A11:B11"), CYAN);
  styleBody(overview.getRange("A12:B16"));
  overview.getRange("A1:H25").format.autofitRows();
  overview.getRange("A:A").format.columnWidth = 22;
  overview.getRange("B:B").format.columnWidth = 48;
  overview.getRange("D:D").format.columnWidth = 24;
  overview.getRange("E:E").format.columnWidth = 14;

  const toolLastColumn = columnName(headers.length - 1);
  addTitle(toolSheet, "VERIFIED TOOL MATRIX", `${tools.length} tools linked to complete medical, pharma, research, and governance workflows. Pricing/access notes are deliberately non-numeric because plans change.`, toolLastColumn);
  toolSheet.getRange(`A3:${toolLastColumn}${tools.length + 3}`).values = [headers, ...tools];
  styleHeader(toolSheet.getRange(`A3:${toolLastColumn}3`));
  styleBody(toolSheet.getRange(`A4:${toolLastColumn}${tools.length + 3}`));
  toolSheet.tables.add(`A3:${toolLastColumn}${tools.length + 3}`, true, "ToolMatrixTable");
  toolSheet.freezePanes.freezeRows(3);
  toolSheet.getRange(`A:${toolLastColumn}`).format.columnWidth = 18;
  toolSheet.getRange("A:A").format.columnWidth = 19;
  toolSheet.getRange("B:B").format.columnWidth = 8;
  toolSheet.getRange("D:D").format.columnWidth = 22;
  toolSheet.getRange("F:F").format.columnWidth = 32;
  toolSheet.getRange(`A1:${toolLastColumn}${tools.length + 3}`).format.autofitRows();

  const workflowHeaders = [
    "Workflow ID", "Title", "Pillar", "Roles", "Task", "Input", "Output", "Risk",
    "Languages", "Primary tool", "Alternatives", "Dataset", "Human reviewer",
    "Prohibited actions", "Verification", "Verified",
  ];
  const workflowValues = workflows.map((item) => [
    item.workflow_id, item.title, item.pillar, listValues(item.roles), item.task,
    item.input_type, item.output_type, item.risk_level, listValues(item.languages),
    item.primary_tool, listValues(item.alternative_tools), item.dataset, item.human_reviewer,
    item.prohibited_actions, listValues(item.verification), item.last_verified,
  ]);
  addTitle(workflowSheet, "COMPLETE WORKFLOW CATALOG", "Every row contains the full route from professional need to tool, dataset, output, verification, prohibited actions, and reviewer.", "P");
  workflowSheet.getRange(`A3:P${workflowValues.length + 3}`).values = [workflowHeaders, ...workflowValues];
  styleHeader(workflowSheet.getRange("A3:P3"), INDIGO);
  styleBody(workflowSheet.getRange(`A4:P${workflowValues.length + 3}`));
  workflowSheet.tables.add(`A3:P${workflowValues.length + 3}`, true, "WorkflowCatalogTable");
  workflowSheet.freezePanes.freezeRows(3);
  workflowSheet.getRange("A:P").format.columnWidth = 22;
  workflowSheet.getRange("B:B").format.columnWidth = 34;
  workflowSheet.getRange("N:O").format.columnWidth = 48;
  workflowSheet.getRange(`A1:P${workflowValues.length + 3}`).format.autofitRows();

  const fields = [
    ["Pillar", "pillar"], ["Role", "roles"], ["Task", "task"], ["Input", "input_type"],
    ["Output", "output_type"], ["Language", "languages"], ["Risk", "risk_level"],
  ];
  const coverageRows = [];
  for (const [label, field] of fields) {
    const options = [...new Set(workflows.flatMap((item) => Array.isArray(item[field]) ? item[field] : [item[field]]))].sort();
    for (const option of options) {
      const count = workflows.filter((item) => (Array.isArray(item[field]) ? item[field] : [item[field]]).includes(option)).length;
      coverageRows.push([label, option, count, count > 0 ? "COVERED" : "GAP"]);
    }
  }
  addTitle(coverageSheet, "DROPDOWN COVERAGE", "Every visible option is derived from one or more complete workflow records; unsupported intersections are removed by cascading selectors.", "D");
  coverageSheet.getRange(`A3:D${coverageRows.length + 3}`).values = [["Selector", "Visible option", "Complete workflows", "Status"], ...coverageRows];
  styleHeader(coverageSheet.getRange("A3:D3"), CYAN);
  styleBody(coverageSheet.getRange(`A4:D${coverageRows.length + 3}`));
  coverageSheet.tables.add(`A3:D${coverageRows.length + 3}`, true, "DropdownCoverageTable");
  coverageSheet.freezePanes.freezeRows(3);
  coverageSheet.getRange("A:A").format.columnWidth = 16;
  coverageSheet.getRange("B:B").format.columnWidth = 52;
  coverageSheet.getRange("C:D").format.columnWidth = 20;
  coverageSheet.getRange(`D4:D${coverageRows.length + 3}`).conditionalFormats.add("containsText", {
    text: "COVERED",
    format: { fill: MINT, font: { color: TEAL, bold: true } },
  });
  coverageSheet.getRange(`D4:D${coverageRows.length + 3}`).conditionalFormats.add("containsText", {
    text: "GAP",
    format: { fill: "#FFF1F2", font: { color: "#BE123C", bold: true } },
  });

  addTitle(labsSheet, "SIX-LAB DELIVERY MATRIX", "Each exercise uses the same 3–6–4–2 rhythm: orient, run, verify, decide.", "F");
  labsSheet.getRange("A3:F9").values = [["Lab", "Exercise", "Pillar", "Dataset", "Tool route", "Qualified reviewer"], ...labs];
  styleHeader(labsSheet.getRange("A3:F3"), ORANGE);
  styleBody(labsSheet.getRange("A4:F9"));
  labsSheet.tables.add("A3:F9", true, "LabMatrixTable");
  labsSheet.freezePanes.freezeRows(3);
  labsSheet.getRange("A:A").format.columnWidth = 10;
  labsSheet.getRange("B:C").format.columnWidth = 38;
  labsSheet.getRange("D:F").format.columnWidth = 32;
  labsSheet.getRange("A1:F9").format.autofitRows();

  addTitle(pilotSheet, "30-DAY RESPONSIBLE PILOT CANVAS", "Edit the pale cells. Keep the pilot bounded, measurable, reversible, monitored, and human-owned.", "D");
  pilotSheet.getRange("A4:B15").values = [
    ["Canvas", "Team decision"],
    ["Pillar", ""],
    ["Pain point and bounded task", ""],
    ["Accountable owner", ""],
    ["Allowed / prohibited data", ""],
    ["Users and qualified reviewer", ""],
    ["Baseline and success measure", ""],
    ["Monitoring and audit evidence", ""],
    ["Incident / escalation route", ""],
    ["Stop and rollback rule", ""],
    ["Decision", ""],
    ["Review date", ""],
  ];
  styleHeader(pilotSheet.getRange("A4:B4"));
  styleBody(pilotSheet.getRange("A5:B15"));
  pilotSheet.getRange("B5:B15").format.fill = AMBER;
  pilotSheet.getRange("B5").dataValidation = { rule: { type: "list", values: [
    "Patient Understanding and Engagement",
    "Clinical Workflow and Decision Support",
    "Pharma, Research and Professional Productivity",
    "Responsible AI, Governance and Implementation",
  ] } };
  pilotSheet.getRange("B14").dataValidation = { rule: { type: "list", values: ["Proceed", "Revise", "Do not proceed", "Escalate"] } };
  pilotSheet.getRange("A:A").format.columnWidth = 34;
  pilotSheet.getRange("B:B").format.columnWidth = 78;
  pilotSheet.getRange("A4:B15").format.rowHeight = 34;
  pilotSheet.getRange("A18:D22").values = [
    ["Readiness check", "Yes", "No", "Evidence / owner"],
    ["Data boundary approved", "", "", ""],
    ["Reviewer and escalation named", "", "", ""],
    ["Baseline and monitoring defined", "", "", ""],
    ["Stop rule agreed before launch", "", "", ""],
  ];
  styleHeader(pilotSheet.getRange("A18:D18"), INDIGO);
  styleBody(pilotSheet.getRange("A19:D22"));
  pilotSheet.getRange("B19:C22").dataValidation = { rule: { type: "list", values: ["Yes", "No"] } };
  pilotSheet.getRange("D:D").format.columnWidth = 48;

  addTitle(sourcesSheet, "SOURCE REGISTER", "Primary or official sources used for the deck, workbooks, and safety boundaries. Recheck before each delivery.", "D");
  sourcesSheet.getRange(`A3:D${sources.length + 3}`).values = [["Source", "Official URL", "Use", "Verified"], ...sources];
  styleHeader(sourcesSheet.getRange("A3:D3"), INDIGO);
  styleBody(sourcesSheet.getRange(`A4:D${sources.length + 3}`));
  sourcesSheet.tables.add(`A3:D${sources.length + 3}`, true, "SourceRegisterTable");
  sourcesSheet.getRange("A:A").format.columnWidth = 28;
  sourcesSheet.getRange("B:B").format.columnWidth = 80;
  sourcesSheet.getRange("C:C").format.columnWidth = 52;
  sourcesSheet.getRange("D:D").format.columnWidth = 16;
  sourcesSheet.getRange(`A1:D${sources.length + 3}`).format.autofitRows();
  sourcesSheet.freezePanes.freezeRows(3);

  wb.comments.setSelf({ displayName: "Alkem AI Masterclass" });
  wb.comments.addThread({ cell: overview.getRange("A1") }, "Workbook generated from the repository's verified workflow catalogue on 2026-07-28.");
  const inspection = await wb.inspect({ kind: "workbook,sheet,table,formula", maxChars: 8000, tableMaxRows: 4, tableMaxCols: 6 });
  await fs.writeFile(path.join(PREVIEWS, "workbook-inspect.ndjson"), inspection.ndjson);
  for (const sheet of wb.worksheets.items) {
    const preview = await wb.render({ sheetName: sheet.name, autoCrop: "all", scale: 1, format: "png" });
    await fs.writeFile(path.join(PREVIEWS, `${sheet.name.replaceAll(" ", "_")}.png`), new Uint8Array(await preview.arrayBuffer()));
  }
  const xlsx = await SpreadsheetFile.exportXlsx(wb);
  await xlsx.save(path.join(OUT, "Alkem_AI_Masterclass_Healthcare_Tool_Matrix.xlsx"));
  console.log(`Created workbook with ${wb.worksheets.items.length} sheets.`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
