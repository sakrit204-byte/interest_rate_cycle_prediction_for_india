const pptxgen = require("pptxgenjs");
const path = require("path");
const { applyTheme } = require("C:/Users/ACER/.claude/skills/synced/11ee3d9a-0528-437e-a2ff-3bd523a17804_e7fd4a16-4b00-422d-b074-e244d9894933/pptx/scripts/apply_theme.js");

const ROOT = "C:/Users/ACER/Desktop/macroeconomics";
const OUT = process.env.DECK_OUT || path.join(ROOT, "reports", "presentation", "ratecycle_india_nepal.pptx");
const FIG = (f) => path.join(ROOT, "reports", "figures", f);

const HEX = {
  ink: "1B1F2A", navy: "1F2D4A", white: "FFFFFF", paper: "F4F5F7",
  india: "EB6834", nepal: "2A78D6", green: "1BAF7A", muted: "8A8F98", line: "D9DCE1", red: "C8432B",
};
const THEME = {
  name: "RateCycle", headFontFace: "Cambria", bodyFontFace: "Calibri",
  colors: {
    dk1: HEX.ink, lt1: HEX.white, dk2: HEX.navy, lt2: HEX.paper,
    accent1: HEX.india, accent2: HEX.nepal, accent3: HEX.green, accent4: HEX.muted, accent5: HEX.red, accent6: "F2B134",
    hlink: HEX.nepal, folHlink: HEX.navy,
  },
};

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9"; // 10 x 5.625 in
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "Will India enter a new rate cycle, and how does it reach Nepal?";
pres.author = "sakrit204-byte";
const C = pres.SchemeColor;

pres.defineSlideMaster({
  title: "TITLE_DARK",
  background: { color: C.text2 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 1.5, w: 8.8, h: 1.2, fontFace: THEME.headFontFace,
      fontSize: 40, bold: true, color: C.background1, valign: "bottom", align: "left", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.6, y: 2.85, w: 8.8, h: 1.6, fontSize: 18,
      color: "CADCFC", valign: "top", margin: 0 }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: C.background1 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.5, y: 0.3, w: 9.0, h: 0.75, fontFace: THEME.headFontFace,
      fontSize: 26, bold: true, color: C.text2, valign: "middle", align: "left", margin: 0 }, text: "" } },
    { text: { text: "RateCycle India Nepal", options: { x: 0.5, y: 5.25, w: 4, h: 0.25, fontSize: 9, color: C.accent4, margin: 0 } } },
  ],
  slideNumber: { x: 9.0, y: 5.25, w: 0.5, h: 0.25, fontSize: 9, color: C.accent4, align: "right", margin: 0 },
});

const base = { fontFace: THEME.bodyFontFace, color: C.text1, margin: 0, isTextBox: true };
const txt = (s, t, o) => s.addText(t, { ...base, ...o });
const axis = () => ({
  catAxisLabelColor: HEX.ink, valAxisLabelColor: HEX.muted, catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt",
  dataLabelFontFace: "+mn-lt", titleFontFace: "+mn-lt", legendFontFace: "+mn-lt",
  catAxisLabelFontSize: 11, valAxisLabelFontSize: 10, dataLabelFontSize: 11, dataLabelColor: HEX.ink,
  valGridLine: { color: HEX.line, size: 0.5 }, catGridLine: { style: "none" },
  catAxisLineShow: false, valAxisLineShow: false,
});
let n = 0;
const content = (title, section) => {
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: section });
  s.addText(title, { placeholder: "title" });
  n += 1;
  return s;
};
const card = (s, x, y, w, h, name, fill = C.background2) =>
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, fill: { color: fill }, line: { type: "none" }, rectRadius: 0.08, objectName: name });
const dot = (s, x, y, label, color, name) => {
  s.addShape(pres.shapes.OVAL, { x, y, w: 0.42, h: 0.42, fill: { color }, line: { type: "none" }, objectName: name });
  txt(s, label, { x, y, w: 0.42, h: 0.42, fontSize: 13, bold: true, color: C.background1, align: "center", valign: "middle" });
};

// ---------- data
const D = JSON.parse(require("fs").readFileSync(path.join(__dirname, "deck_data.json"), "utf8"));
const signed = (v, dp = 2) => (v < 0 ? `minus ${Math.abs(v).toFixed(dp)}` : v.toFixed(dp));
const MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const span = (c) => (c.first_move.slice(0, 4) === c.last_move.slice(0, 4) ? c.first_move.slice(0, 4) : `${c.first_move.slice(0, 4)} to ${c.last_move.slice(0, 4)}`);
const shortDate = (iso) => `${MON[Number(iso.slice(5, 7)) - 1]} ${iso.slice(2, 4)}`;
const head = (t) => ({ text: t, options: { bold: true, color: C.background1, fill: { color: C.text2 }, align: "center" } });
const cell = (t, o = {}) => ({ text: t, options: { align: "center", ...o } });

// ---------- 1 Title
pres.addSection({ title: "Opening" });
let s = pres.addSlide({ masterName: "TITLE_DARK", sectionTitle: "Opening" });
s.addText("Will India enter a new rate cycle, and how does it reach Nepal?", { placeholder: "title", fontSize: 32 });
s.addText([
  { text: "RBI policy cycles, and Nepal's interest rates under the peg of 1.6 Nepali rupees to the Indian rupee", options: { breakLine: true } },
  { text: " ", options: { breakLine: true, fontSize: 10 } },
  { text: "RateCycle India Nepal  |  Macroeconomics project  |  October 2026", options: { fontSize: 13, color: "9FB3D1" } },
], { placeholder: "body" });
s.addNotes("Two questions. First, is India entering a new interest rate cycle, and how far will it go? Second, because Nepal's rupee is pegged to India's at 1.6, how does India's cycle carry over into Nepal's prices and interest rates?");

// ---------- 2 Answers up front
s = content("The answers", "Opening");
const stats = [
  ["Yes", C.accent1, 44, "India entered a hiking cycle on 7 October 2026, repo 5.25 to 5.50. Our model gives a second hike in December a 0.56 chance."],
  ["5.75 to 6.00", C.accent1, 28, "Most likely end by April 2027: 5.75, or 6.00 if oil stays above 110 dollars. A short cycle like 2013 and 2018."],
  ["0.6", C.accent2, 44, "Points the NRB moved its policy corridor per point of RBI move, in each of the three RBI cycles since 2019."],
];
stats.forEach(([v, col, size, label], i) => {
  const x = 0.5 + i * 3.07;
  card(s, x, 1.3, 2.85, 2.55, `stat${i}`);
  txt(s, v, { x: x + 0.25, y: 1.5, w: 2.4, h: 0.95, fontSize: size, bold: true, color: col, fontFace: THEME.headFontFace, valign: "bottom" });
  txt(s, label, { x: x + 0.25, y: 2.55, w: 2.4, h: 1.25, fontSize: 12.5, valign: "top" });
});
txt(s, "Through the peg, Nepal's prices and policy rate are derived from India's cycle; remittance liquidity decides how much reaches Nepal's market rate.",
  { x: 0.5, y: 4.1, w: 9.0, h: 0.9, fontSize: 14, color: C.text2, italic: true });
s.addNotes("India: the new cycle has already started; the question now is how long it runs. Nepal: the peg carries India's prices across the border, and the NRB has answered every RBI cycle since 2019 with six tenths of the RBI's move.");

// ---------- 4 RBI cycles since 2001 (placed after the process slide)
const cyclesSlide = () => {
  pres.addSection({ title: "India" });
  s = content("India's rate cycles since 2001", "India");
  s.addChart(pres.charts.LINE, [{ name: "RBI repo rate, percent", labels: D.repo.labels.map((l) => l.slice(0, 4)), values: D.repo.values }], {
    x: 0.4, y: 1.1, w: 5.5, h: 3.95, ...axis(), chartColors: [HEX.india], lineSize: 2, lineDataSymbol: "none",
    catAxisLabelFrequency: 48, catAxisLabelFontSize: 10, valAxisMinVal: 3, valAxisMaxVal: 10, valAxisMajorUnit: 1,
    valAxisLabelFormatCode: "0", showLegend: false,
    showTitle: true, title: "RBI repo rate, percent, month end, 2001 to October 2026", titleFontSize: 11, titleColor: HEX.ink,
  });
  const hikes = D.cycles.filter((c) => c.direction === "hike" && c.first_move >= "2005");
  const rows = [[head("Hiking cycle"), head("Hikes"), head("Total")]].concat(hikes.map((c) => [
    cell(span(c), { align: "left" }),
    cell(String(c.moves)), cell(`${Math.round(c.rbi_change * 100)} bp`),
  ]));
  rows[rows.length - 1] = [cell("2026, open", { align: "left", bold: true, color: C.accent1 }), cell("1 so far", { bold: true, color: C.accent1 }), cell("25 bp", { bold: true, color: C.accent1 })];
  s.addTable(rows, { x: 6.15, y: 1.2, w: 3.35, colW: [1.45, 0.9, 1.0], fontFace: THEME.bodyFontFace, fontSize: 11, color: C.text1,
    border: { type: "solid", pt: 0.5, color: HEX.line }, rowH: 0.29, margin: 0.04 });
  txt(s, "Long cycles (2005, 2010, 2022) answered broad inflation and strong demand. Short ones (2013, 2018) answered the rupee and oil. Today's trigger is oil and a weak rupee.",
    { x: 6.15, y: 3.4, w: 3.35, h: 1.6, fontSize: 11.5, valign: "top" });
  s.addNotes("A cycle is a run of moves in one direction. Since 2005 hiking cycles have had between 2 and 13 hikes. The 2013 cycle followed the taper tantrum and the rupee's fall; 2018 followed oil and the rupee. Source: reports/tables/rbi_decisions.csv and peg_cycles.csv.");
};
// ---------- 8 Outlook: will it continue
const outlookSlide = () => {
  s = content("Will the new cycle continue? A second hike is likely", "India");
  s.addTable([
    [head("Scenario"), head("Brent, $"), head("P(hike) Dec"), head("P(hike) Feb"), head("P(hike) Apr"), head("Expected repo, Apr")],
    [cell("Premium persists", { align: "left" }), cell("112"), cell("0.57"), cell("0.35"), cell("0.21"), cell("5.71")],
    [cell("Escalation in the Gulf", { align: "left" }), cell("135"), cell("0.56"), cell("0.56"), cell("0.26"), cell("5.81")],
    [cell("Easing tensions", { align: "left" }), cell("92"), cell("0.57"), cell("0.19"), cell("0.16"), cell("5.63")],
    [cell("AI bust, world slowdown", { align: "left" }), cell("90"), cell("0.55"), cell("0.16"), cell("0.10"), cell("5.57")],
    [cell("Stagflation", { align: "left" }), cell("125"), cell("0.55"), cell("0.45"), cell("0.20"), cell("5.74")],
  ], { x: 0.5, y: 1.2, w: 9.0, colW: [2.4, 1.0, 1.4, 1.4, 1.4, 1.4], fontFace: THEME.bodyFontFace, fontSize: 12, color: C.text1,
    border: { type: "solid", pt: 0.5, color: HEX.line }, rowH: 0.36, margin: 0.05 });
  const o = [
    ["December: decided already", C.accent1, "Inflation 5.5 percent and rising, a recent hike, strong industry: about 0.56 in every scenario."],
    ["February: oil decides", C.accent1, "Dear oil or a Gulf war keeps hiking; cheaper oil or a world slowdown ends the cycle."],
    ["How it is built", C.accent4, "Each scenario sets oil, inflation and growth inputs; the same frozen model scores them all."],
  ];
  o.forEach(([h, col, b], i) => {
    const x = 0.5 + i * 3.07;
    card(s, x, 3.55, 2.86, 1.55, `out${i}`);
    txt(s, [{ text: h, options: { bold: true, color: col, breakLine: true } }, { text: b }], { x: x + 0.15, y: 3.63, w: 2.6, h: 1.42, fontSize: 11, valign: "top" });
  });
  s.addNotes("Decision D050. The probit was refitted on all 146 known decisions and not otherwise changed. Oil enters through the RBI's own sensitivity: crude 10 percent above baseline adds about 0.3 points to inflation and takes about 0.2 off growth. The December probabilities are recorded and will be scored after the 2 to 4 December meeting.");
};

// ---------- 9 Where the cycle ends
const endSlide = () => {
  s = content("Where the cycle ends: repo rate after April 2027", "India");
  const lv = ["5.25 or lower", "5.50", "5.75", "6.00", "6.25"];
  const pick = (k) => {
    const v = Object.fromEntries(D.paths.map((r) => [r.repo_after_april_2027.toFixed(2), r[k]]));
    return [v["4.75"] + v["5.00"] + v["5.25"], v["5.50"], v["5.75"], v["6.00"], v["6.25"]];
  };
  s.addChart(pres.charts.BAR, [
    { name: "Easing tensions", labels: lv, values: pick("de_escalation") },
    { name: "Premium persists", labels: lv, values: pick("premium_persists") },
    { name: "Escalation", labels: lv, values: pick("escalation") },
  ], {
    x: 0.4, y: 1.1, w: 6.0, h: 3.95, barDir: "col", barGrouping: "clustered", ...axis(), chartColors: ["9DB9DE", HEX.muted, HEX.india],
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.00", dataLabelFontSize: 9, valAxisMinVal: 0, valAxisMaxVal: 0.4,
    valAxisHidden: true, showLegend: true, legendPos: "b", legendFontSize: 10,
    showTitle: true, title: "Probability of each repo level after the April 2027 meeting", titleFontSize: 11, titleColor: HEX.ink,
  });
  card(s, 6.7, 1.2, 2.8, 3.8, "end-read");
  txt(s, [
    { text: "Most likely", options: { bold: true, color: C.accent1, breakLine: true } },
    { text: "One more hike, to 5.75, in December or February.", options: { breakLine: true } },
    { text: " ", options: { breakLine: true, fontSize: 6 } },
    { text: "6.00 or higher", options: { bold: true, color: C.accent1, breakLine: true } },
    { text: "0.48 if the Gulf escalates, 0.33 if oil stays near 112, 0.21 if tensions ease.", options: { breakLine: true } },
    { text: " ", options: { breakLine: true, fontSize: 6 } },
    { text: "Below today", options: { bold: true, color: C.accent2, breakLine: true } },
    { text: "Only an AI driven world slowdown makes it plausible (0.26)." },
  ], { x: 6.85, y: 1.35, w: 2.5, h: 3.55, fontSize: 12, valign: "top" });
  s.addNotes("Each meeting's probabilities are chained: every branch carries its own previous decision and repo level into the next meeting. Source: reports/tables/india_outlook_paths_20261028.csv.");
};

// ---------- Training process, seven slides, in the order of the dashboard pages
pres.addSection({ title: "How the models were trained" });
const tcard = (s, x, y, w, h, title, col, body, name, size = 11) => {
  card(s, x, y, w, h, name);
  txt(s, [{ text: title, options: { bold: true, color: col, breakLine: true } }, { text: body }],
    { x: x + 0.15, y: y + 0.1, w: w - 0.3, h: h - 0.18, fontSize: size, valign: "top" });
};
const page = (s, label) => txt(s, `Dashboard page: ${label}`, { x: 5.5, y: 5.25, w: 3.4, h: 0.25, fontSize: 9, color: C.accent4, italic: true, align: "right" });

// T1 pipeline
s = content("How the models were trained: seven steps", "How the models were trained");
const stages = [
  ["Collect", "1,015 source files from RBI, MOSPI, IMF, BIS, FRED and NRB, each logged with a hash", "Data explorer"],
  ["Choose variables", "64 candidates in a ledger; 25 used, each other one kept or dropped with a reason", "Variable ledger"],
  ["Features at the cutoff", "Only what was published before each decision or month", "Data explorer"],
  ["Targets", "India: cut, hold or hike. Nepal: moves over 0.5 point in 3 months", "Models"],
  ["Walk forward", "Refit at every decision on past outcomes only, up to October 2021", "Models"],
  ["Check the skill", "Permutation, stability, block accuracy, replication, ablations", "Models, stability"],
  ["Freeze and blind test", "Configuration hashed, then scored once on 2021 to 2026", "Blind backtest"],
];
s.addShape(pres.shapes.LINE, { x: 0.85, y: 1.56, w: 8.3, h: 0, line: { color: HEX.line, width: 2 }, objectName: "flowline" });
stages.forEach(([h, b, pg], i) => {
  const x = 0.5 + i * 1.3;
  dot(s, x + 0.14, 1.35, String(i + 1), i === 6 ? C.accent1 : C.text2, `tdot${i}`);
  txt(s, h, { x, y: 1.9, w: 1.22, h: 0.55, fontSize: 12, bold: true, color: C.text2, valign: "top" });
  txt(s, b, { x, y: 2.5, w: 1.22, h: 1.85, fontSize: 10.5, valign: "top" });
  txt(s, pg, { x, y: 3.85, w: 1.22, h: 0.45, fontSize: 9.5, italic: true, color: C.accent4, valign: "top" });
});
txt(s, "Every choice from step 2 onward was written into the decision log before it was run, and failures stay on the record.", { x: 0.5, y: 4.5, w: 9.0, h: 0.4, fontSize: 13, italic: true, color: C.text2 });
s.addNotes("The seven steps run in this order and each one feeds the next. The grey line under each step names the page of the Streamlit dashboard where it can be inspected. Every choice in steps 2 to 7 was written into the decision log before it was run.");

// T2 data and ledger
s = content("Steps 1 and 2: data, and a ledger of every variable", "How the models were trained");
const src = [
  ["RBI", "Policy statements, policy index, projections", "250"],
  ["MOSPI", "CPI, industrial production", "8"],
  ["IMF", "Nepal CPI, monetary surveys, interest rates", "7"],
  ["BIS", "Policy rates of India and the US", "2"],
  ["FRED", "Brent oil, rupee per dollar, VIX", "3"],
  ["NRB", "Macro tables, time series database", "744"],
  ["Caldara and Iacoviello", "Geopolitical risk index", "1"],
];
s.addTable([[head("Source"), head("What"), head("Files")]].concat(src.map(([a, b, c]) => [cell(a, { align: "left", bold: true }), cell(b, { align: "left" }), cell(c)])),
  { x: 0.5, y: 1.15, w: 5.1, colW: [1.35, 3.0, 0.75], fontFace: THEME.bodyFontFace, fontSize: 10.5, color: C.text1,
    border: { type: "solid", pt: 0.5, color: HEX.line }, rowH: 0.3, margin: 0.04 });
txt(s, "Files that failed or were incomplete are logged, not silently dropped: 1,015 of 1,177 downloads are usable.",
  { x: 0.5, y: 3.75, w: 5.1, h: 0.6, fontSize: 10.5, color: C.accent4, italic: true });
s.addChart(pres.charts.BAR, [{ name: "Variables", labels: ["Used in the models", "Candidate, not used", "Robustness only", "Pending data", "Excluded"], values: [25, 22, 8, 4, 5] }], {
  x: 5.85, y: 1.1, w: 3.65, h: 3.0, barDir: "bar", ...axis(), chartColors: [HEX.nepal, HEX.muted, HEX.muted, HEX.muted, HEX.muted],
  catAxisOrientation: "maxMin", showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0", valAxisHidden: true,
  showLegend: false, catAxisLabelFontSize: 10, valAxisMaxVal: 30,
  showTitle: true, title: "The variable ledger, 64 variables", titleFontSize: 11, titleColor: HEX.ink,
});
txt(s, "Each variable has a role, a source, a publication lag and a reason for its status, so nothing enters a model unexplained.",
  { x: 5.85, y: 4.2, w: 3.65, h: 0.85, fontSize: 11, valign: "top" });
page(s, "Data explorer, Variable ledger");
s.addNotes("The ledger is data/source_registry/variable_registry.csv. Used means core or in use; excluded includes one variable that was coded and then not used. Each download is in a manifest under data/source_registry/manifests with its address, time and SHA256 hash.");

// T3 features and targets
s = content("Steps 3 and 4: features at the cutoff, and targets", "How the models were trained");
const lab = (x) => cell(x, { align: "left", bold: true, color: C.text2 });
const l = (x) => cell(x, { align: "left" });
s.addTable([
  [head(""), head("India"), head("Nepal")],
  [lab("One row per"), l("RBI decision: 146 since 2001, inter meeting moves included"), l("Month, from the mid 1990s")],
  [lab("Target"), l("Cut, hold or hike"), l("Does the published interbank rate rise, or fall, by more than 0.5 point over the next three months?")],
  [lab("What is known"), l("Data published at least 7 days before the decision (1 and 30 days as checks)"), l("Interbank and corridor rates lagged one month, monetary data two months, as published")],
  [lab("Inputs"), l("Previous decision; revision to the RBI's inflation projection; inflation and projected inflation minus the anchor; industrial growth minus its five year mean; rupee move over three months"),
                  l("Interbank level and momentum; distance to the corridor floor and ceiling; NRB and RBI rate changes; reserves to deposits; NRB foreign asset growth; government deposits at the NRB; credit minus deposit growth; calendar effect")],
  [lab("Fixed in advance"), l("Nominal anchor by regime: 5 percent from 2001, 8 in 2014, 6 in 2015, 5 in 2016, then the 4 percent target"), l("The 0.5 point band, set before the classes were counted")],
], { x: 0.5, y: 1.15, w: 9.0, colW: [1.5, 3.75, 3.75], fontFace: THEME.bodyFontFace, fontSize: 10.5, color: C.text1,
  border: { type: "solid", pt: 0.5, color: HEX.line }, margin: 0.06 });
txt(s, "The rule is enforced in code: features are joined on publication dates, and a test fails if any input is dated after its cutoff. RBI projections were hand coded from 223 policy statements and count only from the day they were published.", { x: 0.5, y: 4.3, w: 9.0, h: 0.7, fontSize: 12, italic: true, color: C.text2 });
page(s, "Data explorer, Models");
s.addNotes("The point in time rule is enforced in code: features are joined on publication dates, and tests fail if any value is dated after its cutoff. RBI projections were hand coded from the policy statements and count only from the day they were published.");

// T4 walk forward
s = content("Step 5: walk forward training, never looking ahead", "How the models were trained");
const rowsWF = [[0, 2.4], [0, 3.0], [0, 3.6]];
rowsWF.forEach(([x0, tr], i) => {
  const y = 1.35 + i * 0.55;
  txt(s, `Origin ${i + 1}`, { x: 0.5, y, w: 0.9, h: 0.35, fontSize: 10.5, color: C.accent4, valign: "middle" });
  s.addShape(pres.shapes.RECTANGLE, { x: 1.45, y: y + 0.05, w: tr, h: 0.25, fill: { color: C.accent2 }, line: { type: "none" }, objectName: `wftr${i}` });
  s.addShape(pres.shapes.RECTANGLE, { x: 1.45 + tr, y: y + 0.05, w: 0.5, h: 0.25, fill: { color: "D9DCE1" }, line: { type: "none" }, objectName: `wfemb${i}` });
  s.addShape(pres.shapes.OVAL, { x: 1.45 + tr + 0.52, y: y + 0.04, w: 0.27, h: 0.27, fill: { color: C.accent1 }, line: { type: "none" }, objectName: `wfte${i}` });
});
txt(s, [
  { text: "Train", options: { color: C.accent2, bold: true } }, { text: "  on public outcomes    " },
  { text: "Gap", options: { color: C.accent4, bold: true } }, { text: "  Nepal labels not yet known    " },
  { text: "Predict", options: { color: C.accent1, bold: true } }, { text: "  the next one" },
], { x: 0.5, y: 3.05, w: 6.0, h: 0.3, fontSize: 10 });
tcard(s, 0.5, 3.5, 2.9, 1.6, "Expanding window", C.accent2, "India from the 41st decision (January 2010); Nepal after 60 months. Rolling and recency weighted windows were tried for Nepal and did not do better overall.", "t4a", 10.5);
tcard(s, 3.55, 3.5, 2.9, 1.6, "Refit every time", C.accent2, "Scaling, coefficients and the calendar effect are estimated inside each window only, so no future mean leaks in.", "t4b", 10.5);
tcard(s, 6.6, 3.5, 2.9, 1.6, "Tuning without peeking", C.accent2, "Penalty strength picked by an inner walk forward on the last 15 training decisions, choosing the simplest within one standard error.", "t4c", 10.5);
tcard(s, 6.6, 1.25, 2.9, 1.95, "Benchmarks, same rules", C.accent4, "Majority class, persistence (repeat the last decision) and simple rules are scored on exactly the same origins.", "t4d", 10.5);
page(s, "Models");
s.addNotes("The Nepal gap, or embargo, equals the three month horizon plus the publication lag, so a training label is never one that would still be unknown at the forecast origin. The random forest used fixed shallow settings so that it could not be tuned to the test period.");

// T5 generations
s = content("Step 5: three generations of the India model", "How the models were trained");
s.addChart(pres.charts.BAR, [{
  name: "Balanced accuracy",
  labels: ["Majority class", "Persistence", "Gen 1: probit, 10 inputs", "Gen 1: Taylor rule probit", "Gen 1: random forest", "Gen 2: with RBI projections", "Gen 3: gaps from the anchor"],
  values: [0.359, 0.532, 0.442, 0.520, 0.551, 0.588, 0.639],
}], {
  x: 0.4, y: 1.1, w: 5.6, h: 3.95, barDir: "bar", ...axis(), catAxisOrientation: "maxMin",
  chartColors: [HEX.muted, HEX.muted, "BFC4CC", "BFC4CC", "BFC4CC", "F4B08E", HEX.india],
  showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.00", valAxisHidden: true, valAxisMinVal: 0, valAxisMaxVal: 0.8,
  showLegend: false, catAxisLabelFontSize: 10,
  showTitle: true, title: "Walk forward balanced accuracy, training years", titleFontSize: 11, titleColor: HEX.ink,
});
tcard(s, 6.3, 1.2, 3.2, 1.2, "Gen 1: realized data", C.accent4, "Inflation and growth as published. Complex versions overfitted, which led us to the RBI's own forecasts.", "t5a", 10.5);
tcard(s, 6.3, 2.5, 3.2, 1.2, "Gen 2: the RBI's own forecast", C.accent1, "Adding its inflation projection and its revision: the RBI reacts to news in its forecast.", "t5b", 10.5);
tcard(s, 6.3, 3.8, 3.2, 1.25, "Gen 3: distance to the anchor", C.accent1, "Inflation measured against the anchor of each regime. Six inputs. Chosen as the primary model.", "t5c", 10.5);
page(s, "Models");
s.addNotes("Generation 1 was scored on 80 decisions, generations 2 and 3 on 75, because RBI projections start later. Nepal went the same way: a policy style model (0.35) gave way to a liquidity model (0.42) and then to the two yes or no questions (0.64 for rises, 0.73 for falls in the training years). Every step up was declared before it was run, and the failures stay in the record.");

// T6 skill checks
s = content("Step 6: is the skill real, and is it stable?", "How the models were trained");
s.addTable([
  [head("Check"), head("Question it answers"), head("Result")],
  [cell("Permutation test", { align: "left", bold: true }), cell("Could shuffled history score as well?", { align: "left" }), cell("Generation 2: 0.59 against 0.47 for the top 5 percent of 96 shifts; p 0.01", { align: "left" })],
  [cell("Coefficient stability", { align: "left", bold: true }), cell("Does each effect keep its sign as the window grows?", { align: "left" }), cell("All 6 India inputs in at least 81 percent of 75 windows; all 8 Nepal inputs in at least 82 percent of 157", { align: "left" })],
  [cell("Accuracy by period", { align: "left", bold: true }), cell("Is the gain spread over time, not one lucky spell?", { align: "left" }), cell("India beats persistence in 3 of 4 three year blocks; Nepal in 3 of 5", { align: "left" })],
  [cell("Benchmarks", { align: "left", bold: true }), cell("Does it beat simple rules on unseen years?", { align: "left" }), cell("Balanced accuracy 0.69, against 0.55 for persistence and 0.33 for chance", { align: "left" })],
  [cell("Ablations", { align: "left", bold: true }), cell("Do news, geopolitical or election indices help?", { align: "left" }), cell("None improved the model; all rejected", { align: "left" })],
  [cell("Replication", { align: "left", bold: true }), cell("Does a rebuild from raw files give the same output?", { align: "left" }), cell("Identical file hashes", { align: "left" })],
], { x: 0.5, y: 1.15, w: 9.0, colW: [1.9, 3.3, 3.8], fontFace: THEME.bodyFontFace, fontSize: 10.5, color: C.text1,
  border: { type: "solid", pt: 0.5, color: HEX.line }, rowH: 0.48, margin: 0.05 });
page(s, "Models, stability and replication");
s.addNotes("The permutation test shifts the decision labels in time while keeping their order, which keeps the persistence of policy but breaks the link to the inputs. A coefficient counts as learned only if its sign holds in at least 80 percent of windows, a rule set before the check (D031).");

// T7 freeze and blind
s = content("Step 7: freeze, then test once on unseen years", "How the models were trained");
const fz = [
  ["Freeze", C.text2, "Models, inputs and benchmarks written into a configuration and hashed with SHA256. The scoring script refuses to run if the hash changes."],
  ["Blind test", C.accent1, "Scored once on November 2021 to October 2026: 31 RBI decisions and 57 Nepal months, still refitting at each origin on outcomes public by then."],
  ["Seal", C.accent2, "Nepal forecasts whose outcomes are not yet public are stored now and scored when the NRB publishes."],
  ["Use", C.accent3, "For the outlook the same model is refitted on all 146 decisions, with nothing added."],
];
fz.forEach(([h, col, b], i) => {
  const x = 0.5 + i * 2.3;
  card(s, x, 1.3, 2.1, 2.75, `fz${i}`);
  dot(s, x + 0.15, 1.45, String(i + 1), col, `fzd${i}`);
  txt(s, h, { x: x + 0.15, y: 1.95, w: 1.8, h: 0.4, fontSize: 14, bold: true, color: col });
  txt(s, b, { x: x + 0.15, y: 2.35, w: 1.8, h: 1.65, fontSize: 10.5, valign: "top" });
  if (i < 3) s.addShape(pres.shapes.CHEVRON, { x: x + 2.13, y: 2.55, w: 0.14, h: 0.3, fill: { color: C.accent4 }, line: { type: "none" }, objectName: `fza${i}` });
});
txt(s, "Result: India 0.69 balanced accuracy on the blind years, against 0.55 for persistence.",
  { x: 0.5, y: 4.3, w: 9.0, h: 0.6, fontSize: 13, italic: true, color: C.text2 });
page(s, "Blind backtest");
s.addNotes("Results after the freeze that came from designs chosen later, such as the Nepal yes or no questions, are labelled post hoc rather than blind.");
// ---------- model against reality, and Nepal as derived from India's cycle
const M = JSON.parse(require("fs").readFileSync(path.join(__dirname, "deck_model_vs_actual.json"), "utf8"));
const year = (l) => l.slice(0, 4);
const minus = '0.0;"minus "0.0';
const sideCards = (s, items, key, x = 6.3, w = 3.2, top = 1.2, step = 1.27, h = 1.15) => items.forEach(([hd, col, b], i) => {
  card(s, x, top + i * step, w, h, `${key}${i}`);
  txt(s, [{ text: hd, options: { bold: true, color: col, breakLine: true } }, { text: b }], { x: x + 0.15, y: top + 0.08 + i * step, w: w - 0.25, h: h - 0.13, fontSize: 11, valign: "top" });
});
// actual moves as bars at plus or minus 1, the model's lean P(up) minus P(down) as a line
const leanChart = (s, labels, y, lean, upName, downName, title, freq) => s.addChart([
  { type: pres.charts.BAR, data: [
    { name: upName, labels, values: y.map((v) => (v === 1 ? 1 : 0)) },
    { name: downName, labels, values: y.map((v) => (v === -1 ? -1 : 0)) },
  ], options: { barDir: "col", barGrouping: "stacked", barGapWidthPct: 20, chartColors: ["F4B08E", "9DB9DE"] } },
  { type: pres.charts.LINE, data: [{ name: "Model lean, P(up) minus P(down)", labels, values: lean }],
    options: { chartColors: [HEX.navy], lineSize: 2, lineDataSymbol: "none" } },
], {
  x: 0.4, y: 1.1, w: 5.75, h: 3.95, ...axis(), catAxisLabelFrequency: freq, catAxisLabelFontSize: 10, catAxisLabelPos: "low",
  valAxisMinVal: -1, valAxisMaxVal: 1, valAxisMajorUnit: 0.5, valAxisLabelFormatCode: minus,
  showLegend: true, legendPos: "b", legendFontSize: 9.5, showTitle: true, title, titleFontSize: 11, titleColor: HEX.ink,
});

const repoModelSlide = () => {
  s = content("Model against reality: the repo rate", "India");
  s.addChart(pres.charts.LINE, [
    { name: "Actual repo after the decision", labels: M.rule.labels.map(year), values: M.rule.actual },
    { name: "Rate our model prescribed before the decision", labels: M.rule.labels.map(year), values: M.rule.model },
  ], {
    x: 0.4, y: 1.1, w: 5.75, h: 3.95, ...axis(), chartColors: [HEX.ink, HEX.india], lineSize: 2, lineDataSymbol: "circle", lineDataSymbolSize: 4,
    catAxisLabelFrequency: 14, catAxisLabelFontSize: 10, valAxisMinVal: 2, valAxisMaxVal: 9, valAxisMajorUnit: 1, valAxisLabelFormatCode: "0",
    showLegend: true, legendPos: "b", legendFontSize: 10,
    showTitle: true, title: "RBI repo rate at each of 106 decisions, 2010 to October 2026, percent", titleFontSize: 11, titleColor: HEX.ink,
  });
  sideCards(s, [
    ["Set before each meeting", C.accent1, "Refitted at every decision on past data only, then compared with what the RBI did."],
    ["Close on unseen years", C.accent3, "From November 2021 the prescribed rate was within 0.14 point of the actual repo on average."],
    ["Turns captured", C.accent1, "It rises through the 2022 hiking cycle, flattens in 2023 and falls with the 2025 cuts."],
  ], "rm");
  s.addNotes("The prescribed rate is the estimated policy rule of the suggestion engine: the partial adjustment rule refitted in real time at every decision on inflation gap, projection gap and growth gap. Mean absolute distance from the actual repo: 0.14 point on the 31 blind decisions, 0.19 on the 75 training decisions. Source: reports/tables/suggestions_train.csv, suggestions_blind.csv, figure backtest_blind.png.");
};

const decisionModelSlide = () => {
  s = content("Model against reality: hikes and cuts", "India");
  leanChart(s, M.lean.labels.map(year), M.lean.y, M.lean.lean, "Actual hike", "Actual cut",
    "Model lean before each RBI decision, against the decision taken", 14);
  sideCards(s, [
    ["Right direction", C.accent1, "The model leaned the right way before 32 of the 42 actual moves, 76 percent."],
    ["Unseen years", C.accent3, "Balanced accuracy 0.69 on November 2021 to October 2026, against 0.33 for chance."],
    ["Cycles, not single moves", C.accent1, "The lean builds through each cycle: up in 2010 to 2011 and 2022, down in 2012, 2015, 2019 and 2025."],
  ], "dm");
  s.addNotes("Lean is the probability of a hike minus the probability of a cut from the economic ordered probit, refitted at every decision with only data published before it. Bars mark the decision the RBI actually took. Sources: reports/tables/walk_forward_train_econ_predictions.csv and blind_india_predictions.csv.");
};

const transmissionSlide = () => {
  pres.addSection({ title: "Nepal, derived from India's cycle" });
  s = content("How India's rate cycle reaches Nepal", "Nepal, derived from India's cycle");
  card(s, 0.5, 2.15, 1.9, 1.5, "tr-rbi", C.text2);
  txt(s, [{ text: "RBI moves the repo", options: { bold: true, breakLine: true, fontSize: 14 } }, { text: "the driver", options: { fontSize: 11 } }],
    { x: 0.62, y: 2.25, w: 1.66, h: 1.3, color: C.background1, align: "center", valign: "middle" });
  s.addShape(pres.shapes.CHEVRON, { x: 2.5, y: 2.72, w: 0.2, h: 0.36, fill: { color: C.accent4 }, line: { type: "none" }, objectName: "tr-a1" });
  card(s, 2.8, 2.15, 1.9, 1.5, "tr-peg", C.accent1);
  txt(s, [{ text: "Peg at 1.6", options: { bold: true, breakLine: true, fontSize: 14 } }, { text: "Indian rupee moves are Nepali rupee moves", options: { fontSize: 11 } }],
    { x: 2.92, y: 2.25, w: 1.66, h: 1.3, color: C.background1, align: "center", valign: "middle" });
  s.addShape(pres.shapes.CHEVRON, { x: 4.8, y: 2.72, w: 0.2, h: 0.36, fill: { color: C.accent4 }, line: { type: "none" }, objectName: "tr-a2" });
  sideCards(s, [
    ["1  Prices: strong", C.accent1, "Two thirds of imports come from India at a fixed rupee price. Inflation correlation 0.88 since 2021."],
    ["2  NRB policy corridor: 0.6", C.accent2, "The NRB moved its corridor 0.6 point per RBI point in each of the three cycles since 2019."],
    ["3  Market rate: through liquidity", C.accent3, "Remittances bought at the peg add reserves and set how much of the move reaches the interbank rate."],
  ], "tr", 5.15, 4.35, 1.15, 1.32, 1.18);
  s.addNotes("Nepal's interest rates and prices are treated here as outcomes of India's cycle. Capital controls resolve the impossible trinity: the peg holds, and the NRB keeps room over its own rate, so India's move arrives through prices, through the NRB's own response, and through liquidity. Sources: peg_channels.csv and peg_cycles.csv, decisions D052 and D053.");
};

const pricesSlide = () => {
  s = content("Channel 1: India's inflation becomes Nepal's", "Nepal, derived from India's cycle");
  s.addChart(pres.charts.LINE, [
    { name: "India CPI inflation", labels: M.prices.labels.map(year), values: M.prices.india },
    { name: "Nepal CPI inflation", labels: M.prices.labels.map(year), values: M.prices.nepal },
  ], {
    x: 0.4, y: 1.1, w: 5.75, h: 3.95, ...axis(), chartColors: [HEX.india, HEX.nepal], lineSize: 2, lineDataSymbol: "none",
    catAxisLabelFrequency: 24, catAxisLabelFontSize: 10, valAxisMinVal: 0, valAxisMaxVal: 12, valAxisMajorUnit: 2, valAxisLabelFormatCode: "0",
    showLegend: true, legendPos: "b", legendFontSize: 10,
    showTitle: true, title: "Consumer price inflation over 12 months, percent, 2013 to 2026", titleFontSize: 11, titleColor: HEX.ink,
  });
  sideCards(s, [
    ["Correlation 0.88", C.accent1, "Since November 2021, the years of India's last full hiking and cutting cycles. 0.66 since 2013."],
    ["Why", C.accent1, "A fixed rupee price makes India's goods, fuel and food prices Nepal's import prices."],
    ["For the new cycle", C.accent2, "An RBI hike that cools India's inflation cools Nepal's too, without the NRB moving."],
  ], "pr");
  s.addNotes("Monthly CPI inflation on both sides; Nepal's series ends in March 2026 and twelve months in 2006 and 2007 that repeated the year before in the IMF file are left missing. Source: reports/tables/peg_channels.csv, decision D052.");
};

const policySlide = () => {
  s = content("Channel 2: the NRB follows the RBI at 0.6", "Nepal, derived from India's cycle");
  s.addChart(pres.charts.LINE, [
    { name: "RBI repo rate", labels: M.policy.labels.map(year), values: M.policy.repo },
    { name: "NRB bank rate, corridor ceiling", labels: M.policy.labels.map(year), values: M.policy.bank },
  ], {
    x: 0.4, y: 1.1, w: 5.4, h: 3.95, ...axis(), chartColors: [HEX.india, HEX.nepal], lineSize: 2, lineDataSymbol: "none",
    catAxisLabelFrequency: 24, catAxisLabelFontSize: 10, valAxisMinVal: 3, valAxisMaxVal: 9, valAxisMajorUnit: 1, valAxisLabelFormatCode: "0",
    showLegend: true, legendPos: "b", legendFontSize: 10,
    showTitle: true, title: "Policy rates, percent, month end, 2016 to July 2026", titleFontSize: 11, titleColor: HEX.ink,
  });
  const cyc = D.cycles.filter((c) => c.complete === true && c.first_move >= "2019");
  s.addTable([[head("RBI cycle"), head("RBI"), head("NRB"), head("Ratio")]].concat(cyc.map((c) => [
    cell(`${c.direction === "hike" ? "Hike" : "Cut"} ${span(c)}`, { align: "left" }), cell(signed(c.rbi_change)),
    cell(signed(c.nrb_bank_rate_change)), cell((c.nrb_bank_rate_change / c.rbi_change).toFixed(1), { bold: true, color: C.accent2 }),
  ])), { x: 6.0, y: 1.2, w: 3.5, colW: [1.2, 0.85, 0.85, 0.6], fontFace: THEME.bodyFontFace, fontSize: 10, color: C.text1,
    border: { type: "solid", pt: 0.5, color: HEX.line }, rowH: 0.32, margin: 0.04 });
  txt(s, "In every RBI cycle since 2019 the NRB moved its corridor the same way, by six tenths of the RBI's move. The 91 day treasury bill followed in all three as well.",
    { x: 6.0, y: 2.6, w: 3.5, h: 1.3, fontSize: 11.5, valign: "top" });
  txt(s, "At this ratio, a cycle ending at 5.75 to 6.00 implies an NRB move of about 0.3 to 0.45 point.",
    { x: 6.0, y: 4.0, w: 3.5, h: 0.9, fontSize: 11.5, italic: true, color: C.text2, valign: "top" });
  s.addNotes("Change from the month before the RBI's first move to three months after its last. Over all twelve complete RBI cycles since 2001 the NRB bank rate moved the same way in 7, the 91 day treasury bill in 7 and the interbank rate in 6; the response became regular once the NRB corridor was in place. Treasury bill changes since 2019: minus 0.65, plus 2.08, minus 0.35. Source: reports/tables/peg_cycles.csv, decision D053.");
};

const nepalModelSlide = () => {
  s = content("Model against reality: Nepal's interbank rate", "Nepal, derived from India's cycle");
  const y = M.nepal.y.map((v) => (v === null ? 0 : v));
  leanChart(s, M.nepal.labels.map(year), y, M.nepal.lean, "Actual rise", "Actual fall",
    "Lean three months ahead against moves over 0.5 point", 36);
  sideCards(s, [
    ["India is an input", C.accent1, "The model reads the RBI's repo change of the last three months with Nepal's corridor and liquidity."],
    ["Training years", C.accent3, "Leaned the right way before 65 percent of rises and 73 percent of falls, 2008 to 2021."],
    ["2021 to 2026", C.accent3, "Quiet months called quiet 94 percent of the time; balanced accuracy for rises 0.67."],
  ], "nm");
  s.addNotes("Binary logistic model of decision D039, refitted at every origin with a four month gap so no training label was unknown at the origin. Lean is P(rise) minus P(fall). Results from November 2021 are labelled post hoc because the design was chosen afterwards. The last three months, August to October 2026, are sealed forecasts awaiting NRB data. Source: reports/tables/nepal_binary_predictions.csv.");
};

const nepalMeaningSlide = () => {
  s = content("What India's new cycle means for Nepal", "Nepal, derived from India's cycle");
  const m = [
    ["Prices first", C.accent1, "India's inflation is 5.5 percent and rising with oil and a weaker rupee. Through the peg this reaches Nepal's prices directly; an RBI hike that works in India works in Nepal."],
    ["NRB corridor next", C.accent2, "At the 0.6 response of the last three cycles, a cycle ending at 5.75 to 6.00 means an NRB move of about 0.3 to 0.45 point."],
    ["Market rate: liquidity decides", C.accent3, "The interbank rate sits on the NRB floor of 2.75 percent, held there by remittance reserves. It follows India once liquidity tightens."],
    ["The Gulf link", C.accent5, "Remittances, 29 percent of broad money a year, come largely from the Gulf. A Gulf war would raise India's oil bill and drain Nepal's liquidity together."],
  ];
  m.forEach(([h, col, b], i) => {
    const x = 0.5 + (i % 2) * 4.6, y = 1.2 + Math.floor(i / 2) * 1.95;
    card(s, x, y, 4.4, 1.8, `mean${i}`);
    txt(s, [{ text: h, options: { bold: true, color: col, fontSize: 14, breakLine: true } }, { text: b }], { x: x + 0.2, y: y + 0.13, w: 4.0, h: 1.6, fontSize: 12, valign: "top" });
  });
  s.addNotes("The NRB estimate applies the ratio of the last three cycles to the outlook range and is an implication, not a model forecast. The frozen Nepal model's sealed forecast for October 2026 is rise 0.29, fall 0.24.");
};

// ---------- assembly after the training section
cyclesSlide();
// 4 India reaction function
s = content("What the RBI reacts to", "India");
s.addChart(pres.charts.BAR, [{
  name: "Change in P(hike), points",
  labels: ["Previous decision was a hike", "RBI raised its inflation projection by 1 point", "Realized inflation 1 point above anchor", "Projected inflation 1 point above anchor", "Growth gap 1 point higher", "Rupee 1 percent weaker"],
  values: [24.5, 27.6, 2.5, -4.7, 0.2, -0.3],
}], {
  x: 0.4, y: 1.15, w: 5.9, h: 3.9, barDir: "bar", ...axis(), chartColors: [HEX.india, HEX.india, HEX.muted, HEX.muted, HEX.muted, HEX.muted],
  catAxisOrientation: "maxMin", catAxisLabelPos: "low", showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: '0.0;"minus "0.0', valAxisLabelFormatCode: '0;"minus "0', valAxisMinVal: -15, valAxisMaxVal: 35,
  valAxisHidden: true, showLegend: false, catAxisLabelFontSize: 10,
  showTitle: true, title: "Average change in the probability of a hike, points", titleFontSize: 11, titleColor: HEX.ink,
});
card(s, 6.6, 1.25, 2.9, 3.7, "india-read");
txt(s, [
  { text: "Smoothing", options: { bold: true, color: C.accent1, breakLine: true } },
  { text: "A hike was followed by another hike 71 percent of the time.", options: { breakLine: true } },
  { text: " ", options: { breakLine: true, fontSize: 6 } },
  { text: "Forecast led", options: { bold: true, color: C.accent1, breakLine: true } },
  { text: "The RBI's own projection revision matters most (p 0.003); realized inflation adds little.", options: { breakLine: true } },
  { text: " ", options: { breakLine: true, fontSize: 6 } },
  { text: "Not significant", options: { bold: true, color: C.accent4, breakLine: true } },
  { text: "Growth gap and the rupee, once inflation and the projection are known." },
], { x: 6.8, y: 1.4, w: 2.55, h: 3.45, fontSize: 12, valign: "top" });
s.addNotes("Ordered probit on 115 training decisions with six economic inputs. Bars are average marginal effects on the probability of a hike. Orange bars are significant at 1 percent. Inflation gaps are measured from the nominal anchor of each regime: the multiple indicator years, the Patel glide path and the 4 percent target.");

repoModelSlide(); decisionModelSlide();
// 6 Fit gap
s = content("Over and underfitting: the three stage check", "India");
s.addChart(pres.charts.BAR, [
  { name: "In sample", labels: ["India probit", "Nepal rise", "Nepal fall"], values: [0.598, 0.735, 0.751] },
  { name: "Walk forward, training years", labels: ["India probit", "Nepal rise", "Nepal fall"], values: [0.639, 0.640, 0.727] },
  { name: "Unseen 2021 to 2026", labels: ["India probit", "Nepal rise", "Nepal fall"], values: [0.693, 0.669, 0.530] },
], {
  x: 0.4, y: 1.15, w: 5.6, h: 3.9, barDir: "col", barGrouping: "clustered", ...axis(), chartColors: ["BFC4CC", HEX.muted, HEX.navy],
  showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.00", dataLabelFontSize: 9, valAxisMinVal: 0, valAxisMaxVal: 0.9,
  valAxisHidden: true, showLegend: true, legendPos: "b", legendFontSize: 10,
  showTitle: true, title: "Balanced accuracy at each stage", titleFontSize: 11, titleColor: HEX.ink,
});
const fits = [
  ["India: no overfitting", C.accent3, "Unseen score is higher than in sample: what the model learned carries over to new years."],
  ["Nepal rise: mild gap", C.accent3, "0.74 in sample, 0.64 to 0.67 out of sample, and it holds on unseen data."],
  ["Nepal fall: the floor", C.accent4, "0.73 in training. Since 2021 the rate has sat on the NRB floor, where a fall needs an NRB cut first."],
];
fits.forEach(([h, col, b], i) => {
  card(s, 6.3, 1.25 + i * 1.25, 3.2, 1.12, `fit${i}`);
  txt(s, [{ text: h, options: { bold: true, color: col, breakLine: true } }, { text: b }],
    { x: 6.45, y: 1.33 + i * 1.25, w: 2.95, h: 0.98, fontSize: 11.5, valign: "top" });
});
s.addNotes("An overfitted model scores much better on the data it was fitted to than on new data. None of the final models shows that pattern. Complex models did: the random forest fell to 0.49 on unseen data and a ten feature probit to 0.44 in training, which is why the small models were kept. Source: reports/tables/fit_gap.csv, decision D051.");

outlookSlide(); endSlide(); transmissionSlide(); pricesSlide(); policySlide();
// 10 Corridor regimes
s = content("Channel 3: liquidity decides the market rate", "Nepal, derived from India's cycle");
s.addImage({ path: FIG("nepal_liquidity_regimes.png"), x: 0.4, y: 1.05, w: 4.4, h: 3.96, altText: "Nepal interbank rate inside the NRB corridor with FX purchases, remittances, fiscal flows, credit and deposit growth, 2019 to 2026" });
const eps = [
  ["Floor, 2020 to 2021, 9 months", C.accent2, "Interbank 0.3 percent. Deposits grew 21 percent, credit 14; excess reserves 3.6 percent of deposits."],
  ["Ceiling, 2021 to 2022, 15 months", C.accent1, "Interbank 6.5 percent. Credit grew 20 percent, deposits 13; excess reserves fell to 0.35; NRB never net absorbing."],
  ["Floor, 2023 to 2026, 34 months", C.accent2, "Interbank 2.9 percent. Credit 6.5, deposits 13; remittances 29 percent of broad money a year; NRB absorbing in 94 percent of months."],
];
eps.forEach(([h, col, b], i) => {
  card(s, 5.05, 1.1 + i * 1.3, 4.45, 1.18, `ep${i}`);
  txt(s, [{ text: h, options: { bold: true, color: col, breakLine: true } }, { text: b }], { x: 5.2, y: 1.17 + i * 1.3, w: 4.2, h: 1.05, fontSize: 11, valign: "top" });
});
s.addNotes("Under the peg the NRB must buy the foreign currency that remittances bring in, and each purchase creates bank reserves. When deposits grow faster than credit, the surplus pushes the interbank rate to the floor of the corridor; when credit outruns deposits, it rises to the ceiling. Slow government spending did not cause the current floor: the fiscal injection was smaller during it. Decision D049.");

nepalModelSlide(); nepalMeaningSlide();
// ---------- Conclusion
pres.addSection({ title: "Close" });
s = pres.addSlide({ masterName: "TITLE_DARK", sectionTitle: "Close" });
s.addText("Conclusion", { placeholder: "title" });
s.addText([
  { text: "India has entered a new hiking cycle. A second hike is more likely than not; the cycle most likely ends at 5.75 to 6.00, and oil decides which.", options: { bullet: { indent: 18 }, breakLine: true, paraSpaceAfter: 8 } },
  { text: "Nepal's rates follow from India's cycle through the peg: prices move with India's (0.88 since 2021), and the NRB has moved its corridor 0.6 point per RBI point in every cycle since 2019.", options: { bullet: { indent: 18 }, breakLine: true, paraSpaceAfter: 8 } },
  { text: "Remittance liquidity sets how much reaches Nepal's market rate. Next test: the December RBI decision against our recorded 0.56.", options: { bullet: { indent: 18 } } },
], { placeholder: "body", fontSize: 15, color: "E3EBF7", y: 2.85, h: 2.4 });
s.addNotes("Code, data manifests and the decision log are in the project repository; every number in this deck comes from a committed table.");

pres.writeFile({ fileName: OUT }).then(async () => {
  await applyTheme(OUT, THEME);
  console.log("written", OUT, "content slides", n);
});
