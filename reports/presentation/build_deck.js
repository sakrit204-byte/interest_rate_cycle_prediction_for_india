// Builds reports/presentation/ratecycle_india_nepal.pptx from the committed tables and figures.
// Needs pptxgenjs 3.12.0 (npm install pptxgenjs@3.12.0 in any folder, then run with NODE_PATH set to its node_modules)
// and apply_theme.js from the pptx skill. Every number on the slides is copied from reports/tables.
const pptxgen = require("pptxgenjs");
const path = require("path");
const { applyTheme } = require("C:/Users/ACER/.claude/skills/synced/11ee3d9a-0528-437e-a2ff-3bd523a17804_e7fd4a16-4b00-422d-b074-e244d9894933/pptx/scripts/apply_theme.js");

const ROOT = "C:/Users/ACER/Desktop/macroeconomics";
const OUT = path.join(ROOT, "reports", "presentation", "ratecycle_india_nepal.pptx");
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
pres.title = "Pegged but not imported";
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

// 1 Title
pres.addSection({ title: "Opening" });
let s = pres.addSlide({ masterName: "TITLE_DARK", sectionTitle: "Opening" });
s.addText("Pegged but not imported", { placeholder: "title" });
s.addText([
  { text: "Predicting RBI and NRB policy, and how Indian monetary policy reaches Nepal under the 1.6 peg", options: { breakLine: true } },
  { text: " ", options: { breakLine: true, fontSize: 10 } },
  { text: "RateCycle India Nepal  |  Macroeconomics project  |  October 2026", options: { fontSize: 13, color: "9FB3D1" } },
], { placeholder: "body" });
s.addNotes("The project asks two questions: can the RBI's next decision be predicted from what it could see at the meeting, and does Indian monetary policy set Nepali interest rates under the peg. The short answer to the second is in the title.");

// 2 Answer up front
s = content("The answer in three numbers", "Opening");
const stats = [
  ["0.69", C.accent1, "Balanced accuracy predicting RBI cut, hold or hike on 31 unseen decisions, 2021 to 2026 (chance 0.33)"],
  ["minus 0.07", C.accent2, "Correlation of yearly changes in the RBI repo rate and Nepal's interbank rate, 2001 to 2026"],
  ["0.66", C.accent3, "Correlation of Nepal and India CPI inflation since 2013: the peg carries prices, not policy rates"],
];
stats.forEach(([v, col, label], i) => {
  const x = 0.5 + i * 3.07;
  card(s, x, 1.3, 2.85, 2.55, `stat${i}`);
  txt(s, v, { x: x + 0.25, y: 1.5, w: 2.4, h: 0.95, fontSize: v.length > 5 ? 28 : 44, bold: true, color: col, fontFace: THEME.headFontFace, valign: "bottom" });
  txt(s, label, { x: x + 0.25, y: 2.5, w: 2.4, h: 1.25, fontSize: 13, color: C.text1, valign: "top" });
});
txt(s, "The RBI follows a smooth, forecast led inflation rule. Nepal's interest rate is set by its own liquidity, which the peg creates when remittances are converted at the fixed rate. Public macro data run out of signal at turning points.",
  { x: 0.5, y: 4.1, w: 9.0, h: 0.9, fontSize: 14, color: C.text2, italic: true });
s.addNotes("Three results carry the talk. The India model works on data it never saw, but mostly because the RBI is predictable most of the time. Nepal's interest rates do not follow India's. Nepal's prices do.");

// 3 Process
pres.addSection({ title: "Method" });
s = content("A process built to avoid fooling ourselves", "Method");
const steps = [
  ["Collect", "RBI, MOSPI, IMF, BIS, FRED and about 430 NRB workbooks; zero cost, every download logged with a hash"],
  ["Point in time", "Each meeting sees only data published before it, with the true publication lags"],
  ["Declare first", "52 logged decisions: every model, feature and test fixed before it was run; configs frozen by SHA256"],
  ["Walk forward", "Refit at every decision on past data only, 2001 to October 2021; four month embargo for Nepal"],
  ["Blind test", "November 2021 to October 2026 kept unseen until the end; Nepal forecasts sealed for later scoring"],
];
steps.forEach(([h, b], i) => {
  const x = 0.5 + i * 1.84;
  card(s, x, 1.35, 1.7, 3.35, `step${i}`);
  dot(s, x + 0.2, 1.55, String(i + 1), i < 4 ? C.text2 : C.accent1, `stepdot${i}`);
  txt(s, h, { x: x + 0.2, y: 2.1, w: 1.35, h: 0.5, fontSize: 15, bold: true, color: C.text2 });
  txt(s, b, { x: x + 0.2, y: 2.6, w: 1.35, h: 2.0, fontSize: 12, valign: "top" });
});
txt(s, "Failures are kept on the record: news indices, geopolitical indices, random forests and extra liquidity drivers were tested and rejected.",
  { x: 0.5, y: 4.85, w: 9.0, h: 0.35, fontSize: 12, color: C.accent4, italic: true });
s.addNotes("The main threat in forecasting work is choosing a model after seeing how it scores. Every choice here was written into the decision log before it was run, the configuration is frozen by hash, and five years of decisions were kept unseen until the final test.");

// 4 India reaction function
pres.addSection({ title: "India" });
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

// 5 India blind
s = content("India on unseen years: beats chance, ties persistence", "India");
s.addChart(pres.charts.BAR, [{
  name: "Balanced accuracy", labels: ["Majority class", "Persistence", "Random forest", "Taylor rule probit", "Economic probit"],
  values: [0.333, 0.555, 0.491, 0.641, 0.693],
}], {
  x: 0.4, y: 1.15, w: 5.6, h: 3.9, barDir: "col", ...axis(), chartColors: [HEX.muted, HEX.muted, HEX.muted, HEX.muted, HEX.india],
  showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.00", valAxisMinVal: 0, valAxisMaxVal: 0.8,
  valAxisHidden: true, showLegend: false, catAxisLabelFontSize: 10,
  showTitle: true, title: "Balanced accuracy, 31 decisions, November 2021 to October 2026", titleFontSize: 11, titleColor: HEX.ink,
});
card(s, 6.3, 1.25, 3.2, 3.7, "blind-read");
txt(s, [
  { text: "Beats always predicting hold", options: { bold: true, color: C.accent3, breakLine: true } },
  { text: "Diebold Mariano on log loss, p 0.002.", options: { breakLine: true } },
  { text: " ", options: { breakLine: true, fontSize: 6 } },
  { text: "Does not clearly beat persistence", options: { bold: true, color: C.accent5, breakLine: true } },
  { text: "Same accuracy, 0.77; log loss difference p 0.51; confidence band 0.49 to 0.86.", options: { breakLine: true } },
  { text: " ", options: { breakLine: true, fontSize: 6 } },
  { text: "Late at turning points", options: { bold: true, color: C.accent5, breakLine: true } },
  { text: "One meeting late in 2022 and 2025; gave the October 2026 hike only 0.09." },
], { x: 6.5, y: 1.4, w: 2.85, h: 3.45, fontSize: 12, valign: "top" });
s.addNotes("Balanced accuracy averages the hit rate over cut, hold and hike, so always predicting hold scores 0.33. The model reaches 0.69, but its plain accuracy equals the persistence rule. Its gain is that it sometimes calls a change correctly where persistence never does.");

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

// 7 Nepal forecasting
pres.addSection({ title: "Nepal" });
s = content("Nepal: rises can be forecast, falls cannot", "Nepal");
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
const head = (t) => ({ text: t, options: { bold: true, color: C.background1, fill: { color: C.text2 }, align: "center" } });
const cell = (t, strong) => ({ text: t, options: { align: "center", bold: !!strong } });
s.addTable([
  [head("Months after the RBI move"), head("Interbank rate"), head("91 day T bill"), head("CPI inflation")],
  [cell("0"), cell("minus 0.39 (p 0.28)"), cell("minus 0.21 (p 0.48)"), cell("0.12 (p 0.59)")],
  [cell("3"), cell("minus 0.59 (p 0.41)"), cell("minus 0.38 (p 0.50)"), cell("0.15 (p 0.81)")],
  [cell("6"), cell("minus 0.72 (p 0.33)"), cell("minus 0.70 (p 0.32)"), cell("0.10 (p 0.88)")],
  [cell("12"), cell("minus 1.57 (p 0.05)", true), cell("minus 0.43 (p 0.44)"), cell("0.04 (p 0.95)")],
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

// 11 Outlook
pres.addSection({ title: "Outlook and limits" });
s = content("Outlook to April 2027, same India model", "Outlook and limits");
const oh = (t) => ({ text: t, options: { bold: true, color: C.background1, fill: { color: C.text2 }, align: "center" } });
const oc = (t) => ({ text: t, options: { align: "center" } });
s.addTable([
  [oh("Scenario"), oh("Brent, $"), oh("P(hike) Dec"), oh("P(hike) Feb"), oh("P(hike) Apr"), oh("Expected repo, Apr")],
  ["Premium persists", oc("112"), oc("0.57"), oc("0.35"), oc("0.21"), oc("5.71")],
  ["Escalation in the Gulf", oc("135"), oc("0.56"), oc("0.56"), oc("0.26"), oc("5.81")],
  ["Easing tensions", oc("92"), oc("0.57"), oc("0.19"), oc("0.16"), oc("5.63")],
  ["AI bust, world slowdown", oc("90"), oc("0.55"), oc("0.16"), oc("0.10"), oc("5.57")],
  ["Stagflation", oc("125"), oc("0.55"), oc("0.45"), oc("0.20"), oc("5.74")],
], { x: 0.5, y: 1.2, w: 9.0, colW: [2.4, 1.0, 1.4, 1.4, 1.4, 1.4], fontFace: THEME.bodyFontFace, fontSize: 12, color: C.text1,
  border: { type: "solid", pt: 0.5, color: HEX.line }, rowH: 0.36, margin: 0.05 });
txt(s, [
  { text: "Repo 5.50 after the 7 October 2026 hike. ", options: { bold: true } },
  { text: "December is set mostly by what is already known, so every scenario gives a second hike about 0.56. From February the paths split on oil and world demand. Scenarios are assumptions fed into the model's own inputs, not model output; the December call is recorded and will be scored after the 2 to 4 December meeting. The model tends to call the end of a cycle early, and it gives cuts some weight that the RBI has ruled out." },
], { x: 0.5, y: 3.55, w: 9.0, h: 1.5, fontSize: 12, valign: "top" });
s.addNotes("Decision D050. The ordered probit was refitted on all 146 known decisions and not otherwise changed. Oil enters through the RBI's own sensitivity: crude 10 percent above baseline raises inflation by about 0.3 points and lowers growth by about 0.2. Nepal: the frozen model's latest sealed forecast gives a rise 0.29 and a fall 0.24.");

// 12 Limits
s = content("Limits and what is still open", "Outlook and limits");
const lim = [
  ["Not yet done", C.accent5, ["Robustness checks: other cutoffs, the 2015 inflation measure switch, Nepal deadbands, a VAR", "Citations to verify: neutral real rate, Patel committee date, 2016 corridor start", "Corridor analysis is descriptive; a causal regression is next"]],
  ["Waiting for data", C.accent1, ["Three sealed Nepal forecasts, August to October 2026: NRB data end at mid July", "The December 2026 RBI call"]],
  ["Design limits", C.accent4, ["No market data (bond yields, swaps), the main signal at turning points", "Latest vintage series for some inputs, not what was known at the time", "Few RBI cycles: wide confidence bands"]],
];
lim.forEach(([h, col, items], i) => {
  const x = 0.5 + i * 3.07;
  card(s, x, 1.2, 2.86, 3.85, `lim${i}`);
  txt(s, h, { x: x + 0.18, y: 1.33, w: 2.5, h: 0.4, fontSize: 15, bold: true, color: col });
  txt(s, items.map((t, j) => ({ text: t, options: { bullet: { indent: 14 }, breakLine: j < items.length - 1, paraSpaceAfter: 6 } })),
    { x: x + 0.18, y: 1.8, w: 2.55, h: 3.15, fontSize: 11.5, valign: "top" });
});
s.addNotes("Two of our own earlier claims were corrected during the project and the corrections are logged: the fiscal explanation of the Nepal floor (D049) and the two year inflation effect, which came from an error in the IMF CPI file (D052).");

// 13 Conclusion
s = pres.addSlide({ masterName: "TITLE_DARK", sectionTitle: "Outlook and limits" });
s.addText("Conclusion", { placeholder: "title" });
s.addText([
  { text: "The RBI is a smooth, forecast led inflation targeter: predictable most of the time, hard to call at turning points from public macro data.", options: { bullet: { indent: 18 }, breakLine: true, paraSpaceAfter: 8 } },
  { text: "The peg carries India's prices into Nepal, not India's policy rate; capital controls keep the NRB's short rate its own.", options: { bullet: { indent: 18 }, breakLine: true, paraSpaceAfter: 8 } },
  { text: "Nepal's rate is a liquidity price: remittances bought at the peg hold it on the NRB floor, so the NRB's real instrument is the floor and its absorption.", options: { bullet: { indent: 18 } } },
], { placeholder: "body", fontSize: 16, color: "E3EBF7", y: 2.85, h: 2.3 });
s.addNotes("Code, data manifests and the decision log are in the project repository; every number in this deck comes from a committed table.");

pres.writeFile({ fileName: OUT }).then(async () => {
  await applyTheme(OUT, THEME);
  console.log("written", OUT, "content slides", n);
});
