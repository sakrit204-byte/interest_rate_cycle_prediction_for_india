# Political Event Coding Guide

File: `data/events/political_events.csv`. One row per event, 98 rows (54 India, 44 Nepal), compiled on 26 October 2026.

## Columns

| Column | Meaning |
|---|---|
| event_id | IN or NP plus a number |
| event_type | election_schedule_announcement, election_first_polling, election_results, pm_swearing_in, budget_full, budget_interim, policy_shock, royal_takeover, royal_takeover_reversal, monarchy_abolition, election_ca, election_parliament, unrest, unrest_start, unrest_end, natural_disaster, government_collapse, parliament_dissolution |
| event_date | When the event happened |
| announcement_date | When the public first knew it (schedule announcement for elections; presentation date for budgets; swearing in for governments unless an earlier public announcement fixed it) |
| source_url | The page the date was read from |
| verified | yes when a source page was read and agreed; no otherwise |
| note | Conflicts between sources and the choice made |

## Rules

1. Features join events on announcement date, never on event date, so nothing is used before it was public.
2. Only rows with verified yes enter features.
3. Where sources disagreed, the choice and the alternative are written in the note. Recorded conflicts: the 2004 interim budget (3 February chosen over 4 February), the 2024 full budget (23 July, not the Economic Survey date of 22 July), the 2019 swearing in (30 May), the 2006 Koirala oath (30 April, announced 25 April), the Karki oath (12 September 2025) and the 2015 blockade start (23 September).
4. NRB web pages were not used (site unavailable during compilation).

## Known gaps

Nepal prime minister rows use the swearing in date as the announcement date; the parliamentary vote was often one to three days earlier. Budget dates could not be checked against indiabudget.gov.in (access refused); they rest on Wikipedia and a second published table. Oli's House dissolutions of December 2020 and May 2021, the 2015 constitution promulgation and Nepal's own budget dates are not coded.
