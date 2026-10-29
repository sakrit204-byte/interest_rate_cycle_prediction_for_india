// Builds the presentation from the committed tables and figures.
// Needs pptxgenjs 3.12.0 (npm install pptxgenjs@3.12.0 in any folder, then run with NODE_PATH set to its node_modules),
// apply_theme.js from the pptx skill, and deck_data.json beside this script (exported from reports/tables).
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
pres.title = "Will India enter a new rate cycle, and does Nepal follow?";
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
s.addText("Will India enter a new rate cycle, and does Nepal follow?", { placeholder: "title", fontSize: 34 });
s.addText([
  { text: "RBI policy cycles, and Nepal's interest rates under the peg of 1.6 Nepali rupees to the Indian rupee", options: { breakLine: true } },
  { text: " ", options: { breakLine: true, fontSize: 10 } },
  { text: "RateCycle India Nepal  |  Macroeconomics project  |  October 2026", options: { fontSize: 13, color: "9FB3D1" } },
], { placeholder: "body" });
s.addNotes("Two questions. First, is India entering a new interest rate cycle, and how far will it go? Second, because Nepal's rupee is pegged to India's at 1.6, do Nepal's interest rates follow India's cycles?");

// ---------- 2 Answers up front
s = content("The answers", "Opening");
const stats = [
  ["Yes", C.accent1, 44, "India entered a hiking cycle on 7 October 2026, repo 5.25 to 5.50. Our model gives a second hike in December a 0.56 chance."],
  ["5.75 to 6.00", C.accent1, 28, "Most likely end by April 2027: 5.75, or 6.00 if oil stays above 110 dollars. A short cycle like 2013 and 2018."],
  ["6 of 12", C.accent2, 44, "RBI cycles since 2001 in which Nepal's interbank rate moved the same way: a coin flip, despite the peg."],
];
stats.forEach(([v, col, size, label], i) => {
  const x = 0.5 + i * 3.07;
  card(s, x, 1.3, 2.85, 2.55, `stat${i}`);
  txt(s, v, { x: x + 0.25, y: 1.5, w: 2.4, h: 0.95, fontSize: size, bold: true, color: col, fontFace: THEME.headFontFace, valign: "bottom" });
  txt(s, label, { x: x + 0.25, y: 2.55, w: 2.4, h: 1.25, fontSize: 12.5, valign: "top" });
});
txt(s, "The peg ties Nepal's prices to India's, not its interest rates. Nepal's rate is set by its own liquidity, which the peg creates when remittances are converted at the fixed rate.",
  { x: 0.5, y: 4.1, w: 9.0, h: 0.9, fontSize: 14, color: C.text2, italic: true });
s.addNotes("India: the new cycle has already started; the question now is how long it runs. Nepal: the peg carries prices across the border, but Nepal's short term interest rates follow India's only half the time, no better than chance.");

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

// ---------- 6 Can the model see a cycle coming
const turnSlide = () => {
  s = content("Can the model see a new cycle coming?", "India");
  s.addChart(pres.charts.LINE, [
    { name: "P(hike)", labels: D.blind.labels.map(shortDate), values: D.blind.hike },
    { name: "P(cut)", labels: D.blind.labels.map(shortDate), values: D.blind.cut },
  ], {
    x: 0.4, y: 1.1, w: 5.6, h: 3.95, ...axis(), chartColors: [HEX.india, HEX.nepal], lineSize: 2, lineDataSymbol: "circle", lineDataSymbolSize: 5,
    catAxisLabelFrequency: 4, catAxisLabelFontSize: 9, valAxisMinVal: 0, valAxisMaxVal: 1, valAxisMajorUnit: 0.25, valAxisLabelFormatCode: "0.00",
    showLegend: true, legendPos: "b", legendFontSize: 10,
    showTitle: true, title: "Probabilities before each decision, unseen 2021 to 2026", titleFontSize: 11, titleColor: HEX.ink,
  });
  const turns = [
    ["May 2022, first hike", C.accent1, "P(hike) rose from 0.17 to 0.45 at the first hike, then 0.84 at the next. One meeting late."],
    ["February 2025, first cut", C.accent2, "P(cut) only 0.14 at the first cut, 0.57 at the next. One meeting late."],
    ["October 2026, first hike", C.accent5, "P(hike) rose to 0.27 in August, then fell to 0.09 at the hike itself. Missed."],
  ];
  turns.forEach(([h, col, b], i) => {
    card(s, 6.3, 1.2 + i * 1.27, 3.2, 1.15, `turn${i}`);
    txt(s, [{ text: h, options: { bold: true, color: col, breakLine: true } }, { text: b }], { x: 6.45, y: 1.28 + i * 1.27, w: 2.95, h: 1.02, fontSize: 11.5, valign: "top" });
  });
  s.addNotes("Over the five unseen years the model's balanced accuracy is 0.69 against 0.33 for chance, but its plain accuracy, 0.77, equals simply repeating the last decision, and the gain over that is not significant (p 0.51). Its weakness is the start of a cycle: it reacts one meeting late, because it sees inflation data, not the RBI's words or market expectations.");
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
    ["Read with care", C.accent4, "Scenarios are our assumptions fed into the model's inputs. The model calls cycle ends early."],
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

// ---------- 10 Nepal through India's cycles
const nepalCyclesSlide = () => {
  pres.addSection({ title: "Nepal" });
  s = content("Nepal through India's cycles: a coin flip", "Nepal");
  const done = D.cycles.filter((c) => c.complete === true);
  const yes = (b) => (b === true ? cell("same way", { color: C.accent3, bold: true }) : cell("no", { color: C.accent4 }));
  const rows = [[head("RBI cycle"), head("RBI change"), head("Nepal interbank"), head("Followed?"), head("NRB bank rate"), head("Followed?")]].concat(done.map((c) => [
    cell(`${c.direction === "hike" ? "Hike" : "Cut"} ${span(c)}`, { align: "left" }),
    cell(signed(c.rbi_change)), cell(signed(c.interbank_change)), yes(c.interbank_same_direction),
    cell(signed(c.nrb_bank_rate_change)), yes(c.nrb_bank_rate_same_direction),
  ]));
  s.addTable(rows, { x: 0.5, y: 1.1, w: 6.2, colW: [1.45, 0.95, 1.15, 0.85, 1.0, 0.8], fontFace: THEME.bodyFontFace, fontSize: 9.5, color: C.text1,
    border: { type: "solid", pt: 0.5, color: HEX.line }, rowH: 0.29, margin: 0.03 });
  card(s, 6.95, 1.1, 2.55, 3.9, "nc-read");
  txt(s, [
    { text: "Market rate: 6 of 12", options: { bold: true, color: C.accent2, breakLine: true } },
    { text: "The interbank rate moved the RBI's way only half the time, in 2010 falling 10.7 points while India hiked.", options: { breakLine: true } },
    { text: " ", options: { breakLine: true, fontSize: 6 } },
    { text: "NRB policy rate: 7 of 12", options: { bold: true, color: C.accent2, breakLine: true } },
    { text: "The NRB often leans the same way, by less: plus 1.50 when India hiked 2.50 in 2022.", options: { breakLine: true } },
  ], { x: 7.1, y: 1.25, w: 2.3, h: 3.65, fontSize: 11.5, valign: "top" });
  s.addNotes("Change from the month before the RBI's first move to three months after its last, in percentage points. Same way means a move of more than 0.1 point in the RBI's direction. The NRB bank rate is the ceiling of the NRB corridor. Decision D053, reports/tables/peg_cycles.csv.");
};

// ---------- 14 What India's new cycle means for Nepal
const meaningSlide = () => {
  s = content("What India's new cycle means for Nepal", "Nepal");
  const m = [
    ["Interest rates: little", C.accent2, "Nepal's interbank rate has sat on the NRB floor of 2.75 percent for 34 months. It moves when the NRB moves the floor or liquidity dries up, not when the RBI hikes."],
    ["Prices: yes", C.accent1, "Every fall of the Indian rupee against the dollar is a fall of the Nepali rupee. Inflation in the two countries has moved together closely since 2021 (0.88)."],
    ["Remittances: the risk", C.accent5, "Remittances reach 29 percent of broad money a year, largely from the Gulf. A Gulf war could cut them and lift Nepal off the floor."],
    ["Watch the NRB", C.accent3, "The NRB's policy rate leaned with the RBI in 7 of 12 cycles. Our sealed Nepal forecast: rise 0.29, fall 0.24 by October."],
  ];
  m.forEach(([h, col, b], i) => {
    const x = 0.5 + (i % 2) * 4.6, y = 1.2 + Math.floor(i / 2) * 1.95;
    card(s, x, y, 4.4, 1.8, `mean${i}`);
    txt(s, [{ text: h, options: { bold: true, color: col, fontSize: 14, breakLine: true } }, { text: b }], { x: x + 0.2, y: y + 0.13, w: 4.0, h: 1.6, fontSize: 12, valign: "top" });
  });
  s.addNotes("The sealed forecast is from the frozen Nepal model at origin July 2026, three months ahead, recorded on 27 October before the outcome was public.");
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
tcard(s, 6.3, 1.2, 3.2, 1.2, "Gen 1: realized data", C.accent4, "Inflation and growth as published. Complex versions overfit; none clearly beat persistence.", "t5a", 10.5);
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
  [cell("Diebold Mariano", { align: "left", bold: true }), cell("Are probability scores better than the benchmark?", { align: "left" }), cell("Not significantly better than persistence (p 0.62 in training)", { align: "left", color: C.accent5 })],
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

turnSlide();
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
  ["India: no overfitting", C.accent3, "Unseen score is higher than in sample. If anything the model is too simple: it lags turning points."],
  ["Nepal rise: mild gap", C.accent3, "0.74 in sample, 0.64 to 0.67 out of sample, and it holds on unseen data."],
  ["Nepal fall: regime change", C.accent5, "Holds in training, fails after 2021 when the rate sat on the NRB floor and could not fall."],
];
fits.forEach(([h, col, b], i) => {
  card(s, 6.3, 1.25 + i * 1.25, 3.2, 1.12, `fit${i}`);
  txt(s, [{ text: h, options: { bold: true, color: col, breakLine: true } }, { text: b }],
    { x: 6.45, y: 1.33 + i * 1.25, w: 2.95, h: 0.98, fontSize: 11.5, valign: "top" });
});
s.addNotes("An overfitted model scores much better on the data it was fitted to than on new data. None of the final models shows that pattern. Complex models did: the random forest fell to 0.49 on unseen data and a ten feature probit to 0.44 in training, which is why the small models were kept. Source: reports/tables/fit_gap.csv, decision D051.");

outlookSlide(); endSlide(); nepalCyclesSlide();
// 8 Peg channels
s = content("What the peg carries: India's prices, not its policy rate", "Nepal");
s.addImage({ path: FIG("peg_channels.png"), x: 0.4, y: 1.1, w: 5.7, h: 3.99, altText: "Inflation in India and Nepal, and the RBI repo rate against Nepal's interbank and treasury bill rates, 2001 to 2026" });
s.addTable([
  [{ text: "Correlation", options: { bold: true, color: C.background1, fill: { color: C.text2 } } },
   { text: "Prices", options: { bold: true, color: C.background1, fill: { color: C.text2 }, align: "center" } },
   { text: "Rates", options: { bold: true, color: C.background1, fill: { color: C.text2 }, align: "center" } }],
  ["2001 to 2026", { text: "0.46", options: { align: "center" } }, { text: "minus 0.07", options: { align: "center" } }],
  ["Before corridor", { text: "0.32", options: { align: "center" } }, { text: "minus 0.20", options: { align: "center" } }],
  ["2016 to 2021", { text: "0.29", options: { align: "center" } }, { text: "0.45", options: { align: "center" } }],
  ["2021 to 2026", { text: "0.88", options: { align: "center" } }, { text: "0.18", options: { align: "center" } }],
], { x: 6.35, y: 1.2, w: 3.15, colW: [1.35, 0.8, 1.0], fontFace: THEME.bodyFontFace, fontSize: 11, color: C.text1,
  border: { type: "solid", pt: 0.5, color: HEX.line }, rowH: 0.3, margin: 0.04 });
txt(s, "Prices: inflation in the same month. Rates: 12 month changes in the RBI repo and Nepal's interbank rate. Nepal's rate averages 3.2 points below the repo. The impossible trinity is resolved by capital controls: the peg imports India's price level, while the NRB keeps its own short rate.",
  { x: 6.35, y: 2.9, w: 3.15, h: 2.15, fontSize: 11, valign: "top" });
s.addNotes("Descriptive comparison, decision D052. India's inflation is WPI before 2014 and CPI after; with CPI on both sides since 2013 the correlation is 0.66. The one period with a positive rate correlation, 2016 to 2021, contains a single cycle and the pandemic, a common shock. Building this chart exposed an error in the IMF CPI file for Nepal: twelve months in 2006 and 2007 repeated the year before. They are now left missing.");

// 9 Transmission LP
s = content("An RBI move leaves no significant trace on Nepal", "Nepal");
s.addTable([
  [head("Months after the RBI move"), head("Interbank rate"), head("91 day T bill"), head("CPI inflation")],
  [cell("0"), cell("minus 0.39 (p 0.28)"), cell("minus 0.21 (p 0.48)"), cell("0.12 (p 0.59)")],
  [cell("3"), cell("minus 0.59 (p 0.41)"), cell("minus 0.38 (p 0.50)"), cell("0.15 (p 0.81)")],
  [cell("6"), cell("minus 0.72 (p 0.33)"), cell("minus 0.70 (p 0.32)"), cell("0.10 (p 0.88)")],
  [cell("12"), cell("minus 1.57 (p 0.05)", { bold: true }), cell("minus 0.43 (p 0.44)"), cell("0.04 (p 0.95)")],
  [cell("24"), cell("minus 0.88 (p 0.22)"), cell("minus 0.25 (p 0.70)"), cell("0.87 (p 0.23)")],
], { x: 0.5, y: 1.2, w: 9.0, colW: [2.1, 2.3, 2.3, 2.3], fontFace: THEME.bodyFontFace, fontSize: 12, color: C.text1,
  border: { type: "solid", pt: 0.5, color: HEX.line }, rowH: 0.36, margin: 0.05 });
const lp = [
  ["No pass through", C.accent2, "If the peg carried India's policy rate, the interbank response would approach plus 1. At 12 months plus 1 is outside the band (minus 3.14 to 0.01)."],
  ["Wrong sign is timing", C.accent4, "Few RBI cycles, and they happened to meet Nepali liquidity cycles running the other way, as in 2010 and 2011."],
  ["Inflation: not measurable", C.accent5, "The two year CPI effect (0.87) is not significant once a data error is removed; an earlier 1.5 (p 0.04) was withdrawn."],
];
lp.forEach(([h, col, b], i) => {
  const x = 0.5 + i * 3.07;
  card(s, x, 3.55, 2.86, 1.55, `lp${i}`);
  txt(s, [{ text: h, options: { bold: true, color: col, breakLine: true } }, { text: b }], { x: x + 0.15, y: 3.63, w: 2.6, h: 1.42, fontSize: 11, valign: "top" });
});
s.addNotes("Local projections, August 2000 to October 2021, controlling for oil, US policy and Indian inflation, with Newey West errors. Coefficients are the cumulative response in percentage points to a 1 point change in the RBI repo rate. The forecasting test agrees: adding the RBI repo to the Nepal liquidity model does not improve it (Diebold Mariano p 0.40).");

// 10 Corridor regimes
s = content("What sets Nepal's rate: liquidity in the corridor", "Nepal");
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

meaningSlide();
// ---------- Limits
pres.addSection({ title: "Close" });
s = content("Limits and what is still open", "Close");
const lim = [
  ["Not yet done", C.accent5, ["Robustness checks: other cutoffs, the 2015 inflation measure switch, Nepal deadbands, a VAR", "Citations to verify: neutral real rate, Patel committee date, 2016 corridor start", "Nepal comparisons are descriptive; a causal test is next"]],
  ["Waiting for data", C.accent1, ["The December 2026 RBI decision, against our recorded 0.56", "Three sealed Nepal forecasts, August to October 2026: NRB data end at mid July"]],
  ["Design limits", C.accent4, ["No market data (bond yields, swaps), the main signal at the start of a cycle", "Latest vintage series for some inputs", "Only 12 complete RBI cycles: wide confidence bands"]],
];
lim.forEach(([h, col, items], i) => {
  const x = 0.5 + i * 3.07;
  card(s, x, 1.2, 2.86, 3.85, `lim${i}`);
  txt(s, h, { x: x + 0.18, y: 1.33, w: 2.5, h: 0.4, fontSize: 15, bold: true, color: col });
  txt(s, items.map((t, j) => ({ text: t, options: { bullet: { indent: 14 }, breakLine: j < items.length - 1, paraSpaceAfter: 6 } })),
    { x: x + 0.18, y: 1.8, w: 2.55, h: 3.15, fontSize: 11.5, valign: "top" });
});
s.addNotes("Two of our own earlier claims were corrected and logged: the fiscal explanation of the Nepal floor (D049) and a two year effect of RBI moves on Nepali inflation, which came from an error in the IMF CPI file (D052).");

// ---------- Conclusion
s = pres.addSlide({ masterName: "TITLE_DARK", sectionTitle: "Close" });
s.addText("Conclusion", { placeholder: "title" });
s.addText([
  { text: "India has entered a new hiking cycle. A second hike is more likely than not; the cycle most likely ends at 5.75 to 6.00, and oil decides which.", options: { bullet: { indent: 18 }, breakLine: true, paraSpaceAfter: 8 } },
  { text: "The peg carries India's prices into Nepal, not India's interest rates: Nepal's market rate followed the RBI in only 6 of 12 cycles.", options: { bullet: { indent: 18 }, breakLine: true, paraSpaceAfter: 8 } },
  { text: "Capital controls keep the NRB's rate its own. Remittances bought at the peg hold it on the NRB floor, so watch the NRB and the Gulf, not the RBI.", options: { bullet: { indent: 18 } } },
], { placeholder: "body", fontSize: 16, color: "E3EBF7", y: 2.85, h: 2.3 });
s.addNotes("Code, data manifests and the decision log are in the project repository; every number in this deck comes from a committed table.");
// 7 Nepal forecasting
pres.addSection({ title: "Appendix" });
s = content("Appendix: forecasting Nepal's rate direction", "Appendix");
s.addChart(pres.charts.BAR, [
  { name: "Model", labels: ["Rise over 0.5 point", "Fall over 0.5 point"], values: [0.669, 0.530] },
  { name: "Persistence", labels: ["Rise over 0.5 point", "Fall over 0.5 point"], values: [0.604, 0.651] },
], {
  x: 0.4, y: 1.15, w: 4.9, h: 3.9, barDir: "col", barGrouping: "clustered", ...axis(), chartColors: [HEX.nepal, HEX.muted],
  showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.00", valAxisMinVal: 0, valAxisMaxVal: 0.8,
  valAxisHidden: true, showLegend: true, legendPos: "b", legendFontSize: 10,
  showTitle: true, title: "Balanced accuracy, 57 months, 2021 to 2026", titleFontSize: 11, titleColor: HEX.ink,
});
card(s, 5.6, 1.25, 3.9, 3.7, "nepal-read");
txt(s, [
  { text: "Target", options: { bold: true, color: C.accent2, breakLine: true } },
  { text: "Will the interbank rate rise, or fall, by more than half a point in three months? Two yes or no questions, after the declared three way model failed (0.47 against persistence 0.43).", options: { breakLine: true } },
  { text: " ", options: { breakLine: true, fontSize: 6 } },
  { text: "Rises: forecastable", options: { bold: true, color: C.accent3, breakLine: true } },
  { text: "Liquidity tightening shows up in reserves and credit before the rate moves.", options: { breakLine: true } },
  { text: " ", options: { breakLine: true, fontSize: 6 } },
  { text: "Falls: not after 2021", options: { bold: true, color: C.accent5, breakLine: true } },
  { text: "At the floor the rate can only fall if the NRB cuts the floor. Results labelled post hoc; three sealed forecasts await data." },
], { x: 5.8, y: 1.4, w: 3.55, h: 3.45, fontSize: 11.5, valign: "top" });
s.addNotes("The Nepal target is the published interbank rate. The binary design was chosen on the training years only, so the 2021 to 2026 scores are labelled post hoc rather than blind. The sealed forecasts for August to October 2026 can be scored when the NRB publishes those months.");


pres.writeFile({ fileName: OUT }).then(async () => {
  await applyTheme(OUT, THEME);
  console.log("written", OUT, "content slides", n);
});
