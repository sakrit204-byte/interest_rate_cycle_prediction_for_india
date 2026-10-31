# Presenter guide: RateCycle India Nepal

A plain language companion for presenting the slides and the Streamlit dashboard. Every number here comes from a committed table in `reports/tables`. Read Part 1 first: it is the whole story in two minutes. Parts 2 and 3 explain every concept you may be asked about. Parts 4 and 5 walk through every dashboard page and every slide. Part 6 prepares you for hard questions.

## Part 1: The story in two minutes

**Question 1: Is India entering a new interest rate cycle?** Yes. On 7 October 2026 the Reserve Bank of India (RBI) raised its policy rate, the repo rate, from 5.25 to 5.50 percent. That is the first hike since 2023. Our model gives a second hike in December a 56 percent chance. The most likely end point is 5.75 percent by April 2027, or 6.00 if oil stays above about 110 dollars a barrel.

**Question 2: Because Nepal's rupee is fixed to India's at 1.6, does India's cycle reach Nepal?** Yes, but not the way the textbook says.

* **Prices follow India strongly.** Nepal buys about two thirds of its imports from India at a fixed rupee price, so Indian inflation becomes Nepali inflation (correlation 0.88 since 2021).
* **Nepal's market interest rate does not follow India.** It moved the same way as the RBI in only 6 of 12 RBI cycles since 2001, a coin flip.
* **The NRB's own policy rate does follow India since 2016.** Since the Nepal Rastra Bank (NRB) set up its interest rate corridor in 2016, it moves its rate about 0.5 point for every 1 point the RBI moves. Before 2016 it did not respond at all. This passed a statistical test we declared before running it (p 0.007).

**Looking two years ahead:** the model sees a short cycle, peaking near 5.75 by April 2027, then a slow easing back towards 5.25 by late 2028 as the oil shock drops out of inflation, with the NRB's rate rising to about 6.0 and drifting back. This part rests on declared assumptions, so present it as a conditional outlook.

**The one sentence takeaway:** the peg imports India's prices directly, and India's interest rate reaches Nepal only through the NRB's own decisions, at about half strength, while remittance money keeps Nepal's market rate on its own path.

## Part 2: The economics, in plain words

### Interest rates and central banks

* **Policy rate (repo rate).** The rate at which the central bank lends overnight money to commercial banks. When it goes up, banks pay more for money, so they charge more on loans, people and firms borrow and spend less, and inflation cools. When it goes down, the opposite.
* **Rate cycle.** Central banks rarely move once. They move in runs: several hikes in a row (a hiking cycle), then a pause, then several cuts (a cutting cycle). India has had 13 such runs since 2001.
* **Why the RBI hikes.** Mainly to fight inflation. Since 2016 India has a legal inflation target of 4 percent (with a band of 2 to 6). Before that the target was looser. We call each period's target the **nominal anchor**.
* **Why the RBI is hiking now.** Oil prices are high because of tension in the Gulf, the rupee is weak against the dollar, and inflation is about 5.5 percent and rising. A weaker rupee and dearer oil both push Indian prices up.
* **Inflation projection.** The RBI publishes its own forecast of inflation at every meeting. Our strongest finding about India is that the RBI reacts to changes in its own forecast more than to past inflation. It is **forecast led**: it acts before inflation arrives.
* **Smoothing (inertia).** Central banks move in small steps, usually 0.25 point, and rarely reverse suddenly. So the best single clue to the next decision is the last decision. After a hike, another hike followed 71 percent of the time.

### Rules for setting the rate

* **Textbook Taylor rule.** A recipe proposed by the economist John Taylor in 1993: rate equals a neutral real rate (1.5 percent in our project) plus inflation, plus half of the gap between inflation and the target, plus half of the output gap (how hot the economy runs; we use industrial production growth). It says what a central bank "should" do by theory. It matches the RBI's actual decisions only about a third of the time because it ignores smoothing and forecasts.
* **Estimated rule.** The same idea, but with weights learned from what the RBI actually did, plus smoothing and the RBI's own forecast. It describes how the RBI really behaves: it closes only about 3 to 13 percent of the gap to its neutral rate at each meeting.
* **The economic lesson from comparing them.** The RBI follows the spirit of the Taylor rule (it raises rates when inflation and growth run hot) but it smooths heavily and acts on its forecasts.

### The peg and Nepal

* **Peg.** Nepal fixes its rupee at 1.6 Nepali rupees per Indian rupee and has done so since 1993. The NRB promises to buy and sell Indian rupees at that price.
* **Impossible trinity (also called the trilemma).** A country cannot have all three at once: a fixed exchange rate, free movement of money across the border, and its own interest rate policy. It must give up one. The textbook expects a pegged country to give up its own interest rate and copy the anchor country's rate.
* **How Nepal escapes it: capital controls.** Nepali banks and investors cannot freely move money into Indian money markets to chase a higher rate. So Nepal keeps the peg and still has its own interest rate. That is why our coin flip result is not a failure: it is the impossible trinity working through capital controls.
* **Remittances and liquidity.** Nepali workers abroad, mostly in the Gulf and Malaysia, send home money equal to about 29 percent of broad money each year. The NRB must buy that foreign currency at the peg and pay out rupees. Those rupees land in banks as reserves. When banks hold more reserves than they can lend, they lend to each other very cheaply, and the interbank rate falls.
* **Interbank rate.** The rate at which Nepali banks lend to each other overnight. It is Nepal's market interest rate and our Nepal target.
* **NRB interest rate corridor (since 2016).** The NRB sets a floor (the deposit rate it pays banks, now 2.75 percent) and a ceiling (the bank rate at which it lends to banks, now 5.75). The interbank rate moves inside that corridor. With plenty of remittance money it sits on the floor, as it has for 34 months since late 2023. When credit grows faster than deposits, it rises toward the ceiling, as in 2021 to 2022.
* **91 day treasury bill.** A three month government bond. Its yield is another short Nepali interest rate.
* **Transmission.** How a change in one country's policy rate shows up in another country's rates and prices. We find three channels from India to Nepal: prices (strong), the NRB's policy corridor (about half strength since 2016), and the market rate (only through liquidity, a coin flip).

## Part 3: The statistics, in plain words

### How the models were trained

* **Point in time data.** At each past decision, the model sees only data that had already been published by that day. Indian inflation for a month comes out about two weeks after the month ends, so it is used only from then. This stops the model from "seeing the future".
* **Walk forward validation.** Train on decisions 1 to 40, predict decision 41. Then train on 1 to 41, predict 42. And so on. Every prediction is for a meeting the model had not seen. Like a student taking each exam only after studying the earlier chapters.
* **Embargo (gap) for Nepal.** A Nepal label (did the rate rise over the next three months?) is only known three months later plus a publication lag, so recent months are left out of training until their answer would really have been known.
* **Declared before running.** Every model, input and benchmark was written into the decision log (`docs/decision_log.md`) before it was run. Failures stay in the record. This prevents trying many models and showing only the lucky one.
* **Blind test.** November 2021 to October 2026 was kept sealed. The final model settings were frozen and fingerprinted with a SHA256 hash (a digital fingerprint that changes if a single character changes), and only then was the sealed period scored, once.
* **Sealed forecasts.** Nepal forecasts for August to October 2026 are stored now and will be scored when the NRB publishes those months.

### The models

* **Ordered probit (India).** A model for outcomes that have a natural order: cut, hold, hike. It turns the inputs into three probabilities that add up to 1, such as cut 0.05, hold 0.39, hike 0.56.
* **Logistic regression (Nepal).** A model for yes or no questions: will the interbank rate rise by more than half a point in three months? A second one asks about a fall. It gives a probability for each.
* **Random forest.** A flexible machine learning model made of many decision trees. We tried it as a comparison. It did worse on unseen years (0.49), a sign that flexible models overfit a small sample like 146 decisions.
* **Local projection.** A regression that asks: after the RBI moves its rate by 1 point, how much do Nepali variables change 0, 3, 6, 12 and 24 months later, holding oil prices, US rates and Indian inflation fixed?
* **Policy response test (decisions D055 and D056).** A regression asking: when the RBI's rate changes, how much does the NRB's rate change three months later, before and after the 2016 corridor?

### How the models are scored

* **Accuracy.** The share of decisions called exactly right. Misleading on its own, because the RBI holds most of the time: a model that always says "hold" looks good.
* **Balanced accuracy.** The average of the hit rates for cuts, holds and hikes separately, so each kind of decision counts equally. Pure guessing scores 0.33 with three outcomes and 0.5 with two.
* **Benchmarks.** Our model must beat simple rules scored on exactly the same decisions:
  * **Majority class:** always predict the most common outcome (hold).
  * **Persistence:** predict whatever the RBI did last time. Hard to beat, because of smoothing.
  * **Chance:** guessing.
* **Log loss and Brier score.** These grade the probabilities, not just the final call. A model that said 0.9 for the right answer scores better than one that said 0.4. Lower is better for both.
* **Confidence interval (95 percent).** The range where the true value probably lies. A wide interval means few observations.
* **p value.** The chance of seeing a result at least this strong if there were really no effect. Below 0.05 is the usual line for "significant". Our NRB result has p 0.007, so less than 1 in 100.
* **Diebold Mariano test.** Checks whether one model's forecast errors are really smaller than another's, or just smaller by luck.
* **Permutation test.** Shifts the decision history in time 96 ways so the inputs no longer line up with the right decisions, and scores the model each time. If the real model beats almost all shifted versions, its skill is real. Ours beat the top 5 percent (p 0.01).
* **Block bootstrap.** Resamples chunks of history many times to build confidence intervals that respect the fact that months next to each other are related.
* **Newey West errors.** A correction for confidence intervals when monthly observations overlap and are related to each other over time.
* **Overfitting and underfitting.** Overfitting means the model memorised the training data and fails on new data, like a student who memorised last year's answers. Underfitting means it is too simple to learn anything. We check by comparing three scores: on the data it was fitted to, in the walk forward test, and on unseen years. The India model scores 0.60, 0.64 and 0.69: it does better on new data, so it is not overfitted.
* **Coefficient stability.** Each input's effect must keep the same sign (positive or negative) in at least 80 percent of refits. All 6 India inputs and all 7 Nepal liquidity inputs pass.
* **Replication.** Rebuilding everything from the raw files gives byte identical output files.

## Part 4: The Streamlit dashboard, page by page

Start it with `streamlit run app/main.py` and open http://localhost:8501. Each page carries a coloured label: **observed** (raw data), **estimated** (a statistical estimate), **predicted** (model output), **simulated** (scenario under your assumptions).

### Page 1: Overview

* **Four numbers at the top (blind test, November 2021 to October 2026).**
  * *RBI decisions called correctly, 77 percent:* the India model's exact hit rate on 31 unseen decisions.
  * *Balanced accuracy, India, 0.69:* plus 0.14 over persistence (0.55). Chance is 0.33.
  * *Balanced accuracy, Nepal, 0.47:* the older three way Nepal model (down, flat, up), plus 0.03 over persistence. Say: Nepal's rate is hard to forecast because it is set by liquidity, which led us to the yes or no Nepal model shown later.
  * *Textbook Taylor rule hit rate, 35 percent:* the theory rule matches the RBI only about a third of the time. It is shown as a reference, not a forecaster.
* **What we found.** Four headline findings. Read them out as your summary.
* **Research questions and status.** The six questions the project set out to answer and where each stands.

### Page 2: Data explorer

* **India: policy rates chart.** The RBI repo rate (black steps) and the US Federal Reserve rate. Point out the cycles: hikes 2010 to 2011, the 2020 pandemic cut to 4 percent, hikes 2022 to 2023 to 6.5, cuts in 2025, and the new hike in October 2026. The US line shows the global backdrop: when the US hikes, money leaves emerging markets and pressures the rupee.
* **India: inflation chart.** Consumer price inflation (CPI) and wholesale price inflation (WPI). The RBI targets CPI. WPI moves more with oil and commodity prices.
* **India: industrial production (IIP) chart.** Our measure of how hot the economy runs. The huge swings in 2020 to 2021 are base effects: growth looks enormous compared with the collapsed pandemic months a year earlier.
* **Nepal: interbank rate chart.** The raw interbank rate and a seasonally adjusted version (with the usual monthly pattern removed). Point out how it jumps between near zero and the ceiling: liquidity regimes.
* **Nepal: liquidity drivers chart.** Banks' reserves at the NRB as a share of deposits, growth in the NRB's foreign assets (remittance dollars it bought), and government deposits at the NRB. More reserves and foreign assets mean more cash in banks and a lower interbank rate. When the government collects taxes and does not spend, the money sits at the NRB and drains banks, so the rate rises.

### Page 3: Variable ledger

* **Main table.** All 64 variables we considered, with role, source, publication lag, status and the reason. Filter by country or status, or search.
* **Count by status table.** How many are used in models, candidates not used, robustness checks only, pending data, or excluded.
* **What to say:** nothing enters a model without a written reason, and nothing is silently dropped.

### Page 4: Political events

* **Events chart.** 98 dated events (elections, budgets, government changes, governor appointments) for each country, each with a source. Hover for the description.
* **Table.** The event date, the announcement date and the source link. Features use the announcement date, because that is when markets and central banks learn about an event.
* **Do events improve forecasts? (H2) table.** Compares the model with and without political events. The p values (0.57 for India, 0.31 for Nepal) say events add nothing significant.
* **Economic reading:** elections and politics affect central banks through inflation, budgets and liquidity, which the models already measure. Once those are in, events add nothing extra.

### Page 5: Models (training period), three tabs

**Tab India (RBI)**

* **Reaction function bar chart.** How much each input changes the probability of a hike, in percentage points:
  * previous decision was a hike: plus 24.5 points (smoothing);
  * the RBI raised its own inflation projection by 1 point: plus 27.6 points (forecast led);
  * realised inflation 1 point above the anchor: plus 2.5 points;
  * projected inflation above the anchor: minus 4.7. This looks odd but makes sense: the RBI's projection already assumes its own planned policy, so a high projection partly reflects hikes it has already planned;
  * growth gap and rupee: near zero, not significant.
  * Blue bars are significant (p below 0.10), grey are not.
* **Three model generations tables.** The scores of each generation on the training period:
  * Generation 1 used published inflation and growth; the complex versions overfitted.
  * Generation 2 added the RBI's own inflation projections, hand coded from 223 policy statements.
  * Generation 3 measured inflation as the gap from each regime's target. Balanced accuracy rose from 0.44 to 0.59 to 0.64; persistence was 0.56.
* **Permutation test table.** Real model balanced accuracy 0.59 against 0.47 for the best 5 percent of 96 shuffled histories: p 0.01, the skill is real.
* **Diebold Mariano table.** Compares the model's probability errors with each benchmark. Against always "hold" the model is clearly better. Against persistence the difference is small: be ready to say that persistence is a very strong benchmark for a smoothing central bank, and that our gain comes from calling the direction of moves.

**Tab Nepal (interbank)**

* **Model 1 table (policy style inputs).** Balanced accuracy 0.35 on 179 months: barely above chance. Nepal's rate is not driven like a normal policy rate.
* **Model 2 table (liquidity under the peg).** Better, about 0.42, because it uses reserves, foreign assets and government deposits.
* **Diebold Mariano table, first row.** The transmission test: adding India's repo change does not improve a three month forecast of Nepal's market rate (p 0.40). This matches the coin flip.
* **Seasonal effect bar chart.** The interbank rate's usual pattern by calendar month: higher from February to May, lower in August to October. A likely reading is that government revenue piles up at the NRB in the first part of the year and drains bank cash, then spending near the fiscal year end in mid July and festival season remittances refill it.

**Tab Stability and replication**

* **Coefficient table.** For each input, the share of refits in which its effect kept the same sign. All pass the 80 percent rule.
* **Balanced accuracy by three year block charts.** The model (blue) against persistence (grey), with chance as a dotted line. India beats persistence in 3 of 4 blocks, Nepal in 3 of 5. The skill is spread over time, not one lucky spell.
* **Replication table.** File fingerprints. Rebuilding gives identical files.

### Page 6: Blind backtest

* **The big three part chart** (toggle adds the training years as context; the shaded area is the sealed test period):
  * *Top panel:* the repo rate with a marker at every decision. Marker shape is what the RBI did (triangle up hike, circle hold, triangle down cut). Fill colour is what our engine suggested (blue cut, grey hold, red hike, hollow uncertain). A dark ring means the suggestion was wrong.
  * *Middle panel:* the model's probabilities of cut, hold and hike before every decision. Watch the red area grow before the 2022 hikes and the blue area grow before the 2025 cuts.
  * *Bottom panel:* the actual rate (black), the estimated rule (purple) and the textbook Taylor rule (green). The estimated rule hugs the actual rate because the RBI smooths. The Taylor rule swings far away, showing what pure theory would have prescribed.
* **India metrics table.** Every model on the 31 blind decisions. Our model (ordered_probit_economic) has balanced accuracy 0.69; persistence 0.55; majority 0.33; random forest 0.49.
* **Diebold Mariano table.** Our model clearly beats always "hold" (p 0.002). Against persistence the gain is not statistically significant (p 0.51) with only 31 decisions.
* **Suggestion sources table.** How often each source matched the RBI: learned model 77 percent, estimated rule 68 percent, Taylor rule 35 percent. The combined suggestion speaks only when the model and the rule agree; when it speaks it is right 77 percent of the time.
* **Confusion matrix.** Rows are what the RBI did, columns what the model predicted. The diagonal shows correct calls.
* **Turning points table.** For each new cycle, how many meetings late (positive) or early (negative) each source called it. The model called the 2022 hikes and the 2025 cuts one meeting late. Explain: that is smoothing; the first move of a cycle is the hardest to see from data alone.
* **Nepal blind tables.** The three way Nepal model on 57 months: 0.47 against 0.43 for persistence. The first row of the second table again tests whether India's repo helps: it does not, significantly.

### Page 7: India to Nepal transmission

* **Four panel chart (local projections).** For the interbank rate, the T bill, inflation and credit growth: how each changes over the 24 months after a 1 point RBI move. The line is the estimate and the shaded band the 95 percent range. If the band crosses zero, there is no reliable effect. Most bands cross zero. Say: the peg does not carry India's interest rate into Nepal's market rates.
* **Through India's cycles section (the key new result):**
  * *Cycle table:* each of the 12 complete RBI cycles since 2001, how much the RBI moved, and how Nepal's interbank rate and NRB bank rate moved. "Same way" means a move of more than 0.1 point in the RBI's direction. Interbank: 6 of 12, a coin flip. NRB: 7 of 12 overall, and all 3 cycles since 2019.
  * *Two numbers on the right:* the NRB bank rate responds 0.49 per RBI point in the corridor years (p 0.007), against 0.02 before the corridor. The interbank rate shows 0.43 but with p 0.51, so no reliable response.
  * *What to say:* India's interest rate reaches Nepal through the NRB's decisions, at about half strength, not through the market.
* **Liquidity state chart (H4).** The interbank response split by whether banks had plenty or little spare cash. Shows the negative estimates come from periods of plentiful remittance cash that happened to coincide with RBI hikes: timing, not a real negative effect.

### Page 8: Scenarios

* **India tab.** Sliders for the previous decision, the repo rate, the target, the rupee, inflation, the RBI's projection and the growth gap. The bar chart shows the model's probabilities of cut, hold and hike; next to it the estimated rule's and the Taylor rule's verdicts. Use it live: raise the projection revision by 0.5 and watch the hike probability rise. A red warning appears if you go outside past values.
* **Nepal tab.** Pick an RBI move size; the chart scales the local projection responses. Stress that this is conditional on history repeating and is not a forecast.

### Page 9: Next two years

* **What it is.** The frozen India model run forward through the next 12 RBI meetings, December 2026 to October 2028, under five oil and world scenarios (pick one with the buttons). The first three meetings use news based inputs; after April 2027 the inputs follow assumptions written into the decision log before the run (D057).
* **Main chart.** Black steps are the actual repo since 2022. The orange line is the expected repo after each future meeting, with a shaded band covering the middle 80 percent of outcomes (10 to 90 percent). The dotted blue line is the NRB bank rate implied by the 0.49 response measured since 2016.
* **Four numbers.** The expected peak and when it comes (about 5.71 in April 2027 if oil stays near 112), the expected repo in October 2028 with its range (5.25, from 4.25 to 6.25), and the implied NRB bank rate at the peak (about 5.98) and in October 2028 (back to about 5.75).
* **Bar chart.** The probability of a hike (red) and a cut (blue) at each meeting. Hikes dominate until April 2027; from June 2027 cuts are more likely.
* **All scenarios table.** The expected repo after each meeting under every scenario. They differ in the first year and converge in the second.
* **What to say.** The model sees a short cycle like 2013 and 2018: one or two more hikes, a peak by spring 2027, then a slow easing as the oil shock leaves yearly inflation (a base effect: a price jump raises twelve month inflation for one year only). Nepal follows at about half strength through the NRB.
* **The honest caveat.** Beyond about a year the assumptions (inflation returning to 4.7, the oil effect dropping out, each repo point cutting inflation by 0.4) drive the path more than the news does. The band widens with every meeting. It is a conditional outlook to show how the RBI's reaction function plays out, not a promise.

### Page 10: Methods and limitations

* Lists how leakage and overfitting were controlled, and the honest limitations. Expanders open the full decision log, protocol and written interpretation.

## Part 5: The slides, one by one

1. **Title.** Two questions: is India entering a new rate cycle, and how does it reach Nepal through the peg at 1.6?
2. **The answers.** Yes, India has started hiking (5.25 to 5.50 on 7 October); a second hike has a 0.56 chance. Likely end 5.75 to 6.00 by April 2027. Nepal: market rate 6 of 12 cycles, but since 2016 the NRB moves 0.5 point per RBI point.
3. **Seven steps.** Collect data, choose variables, build features at the cutoff, define targets, train walk forward, check the skill, freeze and test blind. Each step matches a dashboard page.
4. **Data and the ledger.** 1,015 of 1,177 downloaded files usable, from the RBI, MoSPI, IMF, BIS, FRED and NRB. 64 variables, 25 used. Failures logged, not dropped.
5. **Features and targets.** India: one row per RBI decision, target cut, hold or hike. Nepal: one row per month, target whether the interbank rate rises or falls by more than 0.5 point in three months. Data enter only after their publication date.
6. **Walk forward.** Train on the past, predict the next, repeat. The gap for Nepal keeps unknown answers out of training. Benchmarks are scored on the same decisions.
7. **Three model generations.** Balanced accuracy climbed from 0.44 (realised data) to 0.59 (adding the RBI's own forecast) to 0.64 (inflation measured from each regime's target). Persistence 0.53. Each step was declared before it was run.
8. **Is the skill real and stable?** Permutation test p 0.01; all coefficient signs stable; better than persistence in most three year blocks; 0.69 against 0.55 and 0.33 on unseen years; news and political indices did not help; replication identical.
9. **Freeze and blind test.** Settings fingerprinted, then tested once on November 2021 to October 2026.
10. **India's cycles since 2001.** The repo rate line and the hiking cycles table. Long cycles (2005, 2010, 2022) answered broad inflation and strong demand; short ones (2013, 2018) answered the rupee and oil. Today's trigger, oil and a weak rupee, looks like the short kind.
11. **What the RBI reacts to.** Previous decision plus 24.5 points, revision to its own forecast plus 27.6. Message: the RBI smooths and is forecast led.
12. **Model against reality, repo rate.** Black is the actual repo, orange the rate the estimated rule set before each meeting. It tracks the turns: up in 2022, flat in 2023, down in 2025. If asked: its closeness comes largely from smoothing, since simply assuming no change is about as close; the probit on the next slide is the forecasting model.
13. **Model against reality, hikes and cuts.** Bars are what the RBI did (orange hikes, blue cuts); the line is the model's lean, probability of a hike minus probability of a cut. The model leaned the right way before 32 of 42 actual moves. Balanced accuracy 0.69 on unseen years.
14. **Over and underfitting.** India 0.60 in sample, 0.64 walk forward, 0.69 unseen: no overfitting. Nepal rise holds at 0.64 to 0.67. Nepal fall drops after 2021 because the rate sits on the floor and cannot fall further unless the NRB cuts the floor: a change of regime, not overfitting.
15. **Will the new cycle continue?** Five oil and world scenarios. December hike chance about 0.56 in every scenario, because inflation and the recent hike are already known. From February oil decides: dear oil keeps hiking, cheap oil or a world slowdown ends the cycle.
16. **Where the cycle ends.** The chance of each repo level after April 2027 in three scenarios. Most likely 5.75. 6.00 or higher has a 0.48 chance if the Gulf escalates, 0.21 if tensions ease.
17. **Next two years.** The model chained through 12 RBI meetings to October 2028. Orange is the expected repo, light orange the 10 and 90 percent bounds, blue the NRB bank rate implied by the 0.49 response. The cycle peaks by April 2027 at about 5.7 to 5.8, cuts overtake hikes from June 2027 as the oil shock drops out of yearly inflation, and by October 2028 the repo is back near 5.25 (range 4.25 to 6.25). The NRB rises from 5.75 to about 6.0, then drifts back. Say clearly: after April 2027 the inputs are declared assumptions, so this is a conditional outlook, not a forecast.
18. **How India's cycle reaches Nepal.** The flow: RBI moves, the peg passes it on, three channels: prices (strong), NRB policy corridor (0.5 since 2016), market rate (a coin flip, set by liquidity).
19. **The market rate: a coin flip.** The 12 cycle table. Interbank 6 of 12; in 2010 it fell 10.7 points while India hiked. Economic point: the textbook says a peg imports the anchor's interest rate; capital controls stop that.
20. **Channel 1, prices.** India and Nepal inflation lines move together, 0.88 since 2021, 0.66 since 2013. Fixed rupee price plus two thirds of imports from India. An RBI hike that cools India's inflation cools Nepal's too.
21. **Channel 2, the NRB follows at 0.5.** RBI repo and NRB bank rate since 2016. Test result: 0.49 per RBI point in the corridor years (range 0.14 to 0.85, p 0.007), 0.02 before. The last three cycles each show 0.6. For the current cycle: an NRB move of about 0.25 to 0.37 point. Why the NRB follows: a central bank defending a peg leans with the anchor so the interest gap does not strain its reserves, and the corridor gave it the tool to do so.
22. **Channel 3, liquidity.** The corridor chart with three episodes: floor in 2020 to 2021 (deposits outgrew credit), ceiling in 2021 to 2022 (credit grew 20 percent against deposits 13), floor since late 2023 (remittances 29 percent of broad money, NRB soaking up cash in 94 percent of months).
23. **Model against reality, Nepal.** Bars are actual rises and falls of more than 0.5 point; the line is the model's lean three months ahead. India's repo change is one of its inputs. It leaned right before 65 percent of rises and 73 percent of falls in training; since 2021 it called quiet months quiet 94 percent of the time.
24. **What India's new cycle means for Nepal.** Prices first; the NRB corridor next, about 0.25 to 0.37 point; the market rate only once liquidity tightens; the Gulf links both, since a Gulf war raises India's oil bill and cuts Nepal's remittances.
25. **Conclusion.** India is in a new hiking cycle, probably ending at 5.75 to 6.00. The peg carries India's prices; the market rate follows only half the time; the NRB follows at half strength since 2016. Over two years: a peak near 5.75 by April 2027, then easing towards 5.25 by late 2028. First test: the December RBI decision against our recorded 0.56.

## Part 6: Hard questions and honest answers

* **"Your model barely beats just repeating the last decision. Why bother?"** Repeating the last decision is a very strong benchmark for a central bank that smooths. It can never call the start of a cycle. Our model beats it on balanced accuracy (0.69 against 0.55) because it gets the direction of moves right, which is what matters for a rate cycle. With only 31 unseen decisions, the gain is not statistically significant, and we say so.
* **"Why does the model call cycles one meeting late?"** The first move of a cycle often follows signals the model does not see: the RBI's speeches, bond markets and global events. After the first move, smoothing makes the next one easier to see. Adding market data is a natural next step.
* **"Is your estimated rule overfitted?"** No. It has five parameters, is refitted only on past decisions, was frozen before the blind test, and scored better on unseen years (68 percent) than in training (51 percent). Its closeness to the actual rate comes mostly from smoothing.
* **"If Nepal's rate follows India only half the time, how can you say Nepal is derived from India?"** Because India reaches Nepal through two other channels: prices (0.88 correlation) and the NRB's own policy rate (0.49 per point since 2016, p 0.007). The coin flip is about the market rate only, and it shows capital controls at work.
* **"Isn't 0.5 based on three cycles?"** No. The 0.5 comes from a monthly regression over 298 months, declared before it was run, with a 95 percent range of 0.14 to 0.85. The three recent cycles agree with it.
* **"Correlation is not causation."** Agreed. The price and cycle comparisons are descriptive. The policy test controls for timing, and its economic logic (the NRB defends the peg by leaning with India) is standard, but we do not claim a full causal proof.
* **"Why not use machine learning?"** We did. The random forest scored 0.49 on unseen years against 0.69 for the simple model. With about 146 decisions, simple models generalise better.
* **"How do we know you did not tune the model to the test years?"** The settings were fingerprinted before the test, the scoring script refuses to run if the fingerprint changes, and every choice is dated in the decision log.
* **"What could go wrong with the outlook?"** Oil. If Gulf tensions ease and oil falls toward 90 dollars, the cycle may stop at 5.50 or 5.75. The December decision is our first live test.
* **"How can you predict two years ahead?"** We do not claim to. We run the tested model forward under assumptions we wrote down before the run and show the full range. The first year is driven by today's news; the second mostly by the assumption that the oil shock fades. The range of 4.25 to 6.25 by October 2028 is the honest answer.
