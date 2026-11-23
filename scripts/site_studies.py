"""Curated, source-bound reading editions; complete research remains in studies/*.md."""

from __future__ import annotations

import json

STUDIES = json.loads(r"""{
  "orb-setup-filters": {
    "name": "ORB Setup and Filters",
    "title": "Opening-range breakout: filters and later performance",
    "technical": "studies/orb-setup-filters.md",
    "appendix": "studies/orb-setup-filters-appendix.md",
    "data": "data/orb-setup-filters-public.json",
    "cover": "orb-setup-filters-comparison.svg",
    "cover_alt": "The same four opening-range setups compared on average gross risk units per close in discovery and two later historical cohorts",
    "subtitle": "Another opening-range breakout study: define the setup, compare range and filter choices, then carry frozen candidates into later historical data.",
    "decision": "No candidate promoted. Later results weakened, the remaining positive margin was sensitive to costs, and the available evidence did not establish positive expectancy.",
    "caveat": "This was a retrospective historical evaluation with incomplete coverage, not a live forward test. The EMA extension has no qualified later result.",
    "facts": {
      "range": {
        "value": "15",
        "source": "ORBF1"
      },
      "open": {
        "value": "09:30",
        "source": "ORBF1"
      },
      "target": {
        "value": "1.5",
        "source": "ORBF1"
      },
      "configurations": {
        "value": "48",
        "source": "ORBF1"
      },
      "us": {
        "value": "US500",
        "source": "ORBF1"
      },
      "tech": {
        "value": "USTEC",
        "source": "ORBF1"
      },
      "discovery_mean": {
        "value": "+0.187",
        "source": "ORBF1"
      },
      "a_mean": {
        "value": "+0.063",
        "source": "ORBF2"
      },
      "b_mean": {
        "value": "+0.056",
        "source": "ORBF2"
      },
      "closes": {
        "value": "114",
        "source": "ORBF2"
      },
      "scenario_total": {
        "value": "+5.32",
        "source": "ORBF2"
      },
      "extra_cost": {
        "value": "0.025",
        "source": "ORBF2"
      },
      "stressed_total": {
        "value": "-0.38",
        "source": "ORBF2"
      },
      "contrasts": {
        "value": "27",
        "source": "ORBF1"
      },
      "ema_pairs": {
        "value": "24",
        "source": "ORBF1"
      },
      "break_even": {
        "value": "0.0233",
        "source": "ORBF2"
      }
    },
    "sections": [
      {
        "heading": "The setup and the research question",
        "paragraphs": [
          "The reference setup measures the first {range} minutes after the {open} New York cash open. A completed fifteen-minute midpoint candle must close outside that range after the preceding close was inside it. Entry uses the next eligible quote, the stop sits at the opposite boundary, and the target is {target} times initial price risk.",
          "Midpoint is the average of Bid and Ask; execution uses the tradeable quote side. Off-grid stops and targets are rejected without rounding. Positions may span days, with one open position per entry session and possible overlap between sessions.",
          "I compared range lengths, directions and an average true range (ATR) volatility filter, then added an exponential moving average (EMA) trend filter during discovery. The matrix covers {configurations} configurations across {us} and {tech} CFDs."
        ],
        "figure": "orb-setup-filters-setup-candles.svg",
        "alt": "Illustrative candlesticks showing the opening range, completed confirmation, next-quote Ask entry, stop at the range low, target, and optional EMA filter",
        "caption": "Illustrative fifteen-minute candles show the range and completed confirmation. The next-quote marker shows entry at Ask. Prices and the EMA line are synthetic; ATR and EMA are optional filters.",
        "sources": [
          "ORBF1"
        ]
      },
      {
        "heading": "The same setups in discovery and later history",
        "paragraphs": [
          "All four selected {us} setups had positive average gross R in discovery. The long-only alternatives turned negative on observed natural closes in both later cohorts. The bidirectional ATR setup stayed slightly positive, with a much smaller average outcome.",
          "R expresses outcomes relative to initial trade risk. Gross R includes quoted spread through Bid/Ask execution but excludes commission and other account charges. The chart compares unchanged setups across periods and includes natural-close counts."
        ],
        "table": {
          "heading": [
            "{us} bidirectional ATR candidate",
            "Average gross R per close"
          ],
          "rows": [
            [
              "Discovery",
              "{discovery_mean}R"
            ],
            [
              "Later cohort A",
              "{a_mean}R"
            ],
            [
              "Later cohort B",
              "{b_mean}R"
            ]
          ]
        },
        "figure": "orb-setup-filters-comparison.svg",
        "alt": "Four frozen US500 configurations show lower average gross R per natural close in the two later historical cohorts than in discovery",
        "caption": "All plotted setups have EMA off. Cohort A has incomplete coverage, so these observed-close outcomes do not establish a complete-cohort return. The comparison is descriptive and does not establish why performance changed.",
        "sources": [
          "ORBF1",
          "ORBF2"
        ]
      },
      {
        "heading": "What adding the EMA actually showed",
        "paragraphs": [
          "EMA permits long breakouts only above the moving average and shorts only below it. Each matched pair holds the other settings fixed.",
          "Discovery results were mixed. Profit factor sometimes improved; drawdown often fell with fewer trades. Neither establishes better daily returns. None of the {contrasts} fixed comparisons survived multiple-testing correction; they tested configuration differences, not every strategy's absolute expectancy.",
          "All later-tested {us} setups had EMA off. The shortlisted EMA-on {tech} candidate was source-blocked, so EMA has no qualified out-of-sample result."
        ],
        "figure": "orb-setup-filters-ema.svg",
        "alt": "All matched EMA-on minus EMA-off differences in commission-scenario R per common eligible day, split by market",
        "caption": "All {ema_pairs} matched comparisons, on the common discovery calendar. Positive values favor EMA. These overlapping configurations are descriptive comparisons, not independent trials or individual significance estimates.",
        "sources": [
          "ORBF1",
          "ORBF2"
        ]
      },
      {
        "heading": "How much margin remained after costs?",
        "paragraphs": [
          "The bidirectional ATR candidate made approximately {scenario_total}R across {closes} natural closes under the published-commission assumption. This combines separately initialized cohorts, not a continuous account return or a complete daily series.",
          "An extra hypothetical {extra_cost}R per fill side reduces that total to approximately {stressed_total}R, before extra financing. The trades stay fixed; this does not estimate actual slippage. Historical all-in broker net performance remains unknown."
        ],
        "figure": "orb-setup-filters-cost-sensitivity.svg",
        "alt": "Combined observed closed-trade scenario R falls as hypothetical extra cost per fill side increases",
        "caption": "The line crosses zero at approximately {break_even}R extra per fill side, using rounded public aggregates. It describes only these observed closes; financing remains extra.",
        "sources": [
          "ORBF2"
        ]
      },
      {
        "heading": "What the research can support",
        "paragraphs": [
          "The candidate list was frozen before its later strategy outcomes were opened, but the evaluation was historical and some related work had exposed later data. It should not be described as a completely untouched forward test.",
          "Incomplete confirmation coverage in cohort A prevents the full primary daily-return statistic from being estimated. Positions still open at the cutoff were censored rather than counted as ordinary exits. The supplemental estimate from the fully observed cohort B remained inconclusive.",
          "Discovery missing-source sessions contributed zero recorded execution while remaining in the calendar denominator. The later analysis instead leaves unavailable daily outcomes missing. Neither convention turns absent quotes into an observed no-signal day."
        ],
        "sources": [
          "ORBF1",
          "ORBF2"
        ]
      },
      {
        "heading": "The decision and the next useful test",
        "paragraphs": [
          "The study supports withholding promotion: the long-only results deteriorated, the remaining positive margin was fragile, and the EMA extension still lacks a qualified later evaluation.",
          "The next useful evidence would be a complete, admissible later sample evaluated under frozen rules and declared costs. Retuning on the outcomes already examined would create a new development exercise and require a fresh evaluation sample."
        ],
        "sources": [
          "ORBF1",
          "ORBF2"
        ]
      }
    ],
    "verification": [
      "The released aggregates reproduce the charts and selected arithmetic. They do not contain the daily inputs needed to recompute the reported bootstrap intervals or adjusted significance tests.",
      "Research choices and final decisions were directed by the repository author, with AI-assisted implementation and test automation."
    ]
  },
  "orbindex": {
    "name": "ORBINDEX",
    "title": "ORBINDEX: promising timings, later losses",
    "technical": "studies/orbindex.md",
    "cover": "orbindex-economics.svg",
    "cover_alt": "Fixed-volume EUR outcomes in discovery and the later historical comparison",
    "subtitle": "An opening-range timing search tested neighbouring configurations, cross-market robustness and portfolio interactions before a later economic comparison.",
    "decision": "None of the frozen portfolios was promoted. Each lost fixed-volume EUR in the later historical comparison before additional commission or financing.",
    "caveat": "The later period may already have been inspected in other German-index research, so it cannot be treated as a completely fresh independent test. Broker-net returns also remain unverified.",
    "facts": {
      "configurations": {
        "value": "3,456",
        "source": "IX1"
      },
      "period": {
        "value": "2024–July 2026",
        "source": "IX3"
      },
      "a_eur": {
        "value": "−€18.73",
        "source": "IX3"
      },
      "b_eur": {
        "value": "−€15.34",
        "source": "IX3"
      },
      "c_eur": {
        "value": "−€159.73",
        "source": "IX3"
      }
    },
    "sections": [
      {
        "heading": "Where the candidates came from",
        "paragraphs": [
          "The discovery searched {configurations} opening-range configurations across German, Japanese and UK index CFDs. Different start times, range lengths and trade directions overlapped, so the strongest result was not automatically the most convincing.",
          "On the German index, some favourable timings had nearby settings that also looked promising. That mattered more than a single isolated peak, but the evidence was sensitive to even modest additional costs."
        ],
        "figure": "orbindex-search.svg",
        "alt": "German-index timing heatmap showing results across the local trading day",
        "caption": "The verified German-index heatmap shows one slice of the discovery search, not net broker profit.",
        "sources": [
          "IX1"
        ]
      },
      {
        "heading": "Did the pattern hold across markets?",
        "paragraphs": [
          "Japan and the UK produced occasional positive configurations, but neither supplied a neighbourhood that passed the same robustness screen. The result applies to this particular rule and search, not to those markets generally."
        ],
        "figure": "orbindex-jp-uk-heatmaps.svg",
        "alt": "Japanese and UK index opening-range timing heatmaps across directions and range lengths",
        "caption": "The original cross-market heatmaps help distinguish isolated peaks from a supported region.",
        "sources": [
          "IX1"
        ]
      },
      {
        "heading": "From individual trades to portfolios",
        "paragraphs": [
          "The German candidates were combined into three frozen portfolios. A shared pending-order or position slot mattered: an earlier order could block a later opportunity, so simply adding standalone backtest returns would have been misleading.",
          "Each portfolio was evaluated under those same order-ownership rules before being carried into the later historical comparison."
        ],
        "sources": [
          "IX2"
        ]
      },
      {
        "heading": "Discovery versus later performance",
        "paragraphs": [
          "The discovery portfolios accumulated positive gross price R, but their later-period trajectories weakened considerably. Each sample restarts at zero, so these are not continuous account equity curves."
        ],
        "figure": "orbindex-curves.svg",
        "alt": "Cumulative gross price R lines for frozen German-index portfolios in discovery and the later historical test",
        "caption": "Quarter-end cumulative gross price R snapshots are connected by straight segments. They do not show intraperiod drawdowns, and the periods differ in length. This is not an annualized or broker-net comparison.",
        "sources": [
          "IX3"
        ]
      },
      {
        "heading": "What happened later",
        "paragraphs": [
          "Across the {period} historical scenario, all three portfolios lost money in fixed-volume euros with Bid/Ask spread already included. The comparison below is gross of additional commission and financing; it is not verified historical broker-net profit."
        ],
        "table": {
          "heading": [
            "Frozen portfolio",
            "Later gross EUR"
          ],
          "rows": [
            [
              "A",
              "{a_eur}"
            ],
            [
              "B",
              "{b_eur}"
            ],
            [
              "C",
              "{c_eur}"
            ]
          ]
        },
        "figure": "orbindex-economics.svg",
        "alt": "Discovery and later-period fixed-volume EUR results for three frozen German-index portfolios",
        "caption": "All three later monetary outcomes were negative before additional commission or financing.",
        "sources": [
          "IX3"
        ]
      },
      {
        "heading": "What the result means",
        "paragraphs": [
          "The subsequent review found that spread costs contributed to weaker results, but unfavourable midquote movement mattered too. Breakouts could briefly move in the expected direction and still fail to finish as winners.",
          "The frozen portfolios were closed, not retuned using already-seen history. The finding is about these specific portfolios, not proof that opening-range strategies cannot work elsewhere.",
          "The later test is informative but not a pristine independent holdout, because some of its history may have been inspected in earlier research."
        ],
        "sources": [
          "IX3",
          "IX4"
        ]
      }
    ],
    "data": "data/orbindex-public.json"
  },
  "macroimpulse": {
    "name": "News-Release Trading",
    "title": "News-Release Trading: poor live execution",
    "technical": "studies/news-research.md",
    "cover": "macro-mechanics.svg",
    "cover_alt": "Conceptual buy-stop and sell-stop triggers around an economic release",
    "subtitle": "A scheduled-news strategy tested historical momentum, then confronted the spreads, slippage and fills available around real releases.",
    "decision": "Shelved because live spreads, fills and slippage across brokers made the trading conditions unworkable.",
    "caveat": "This is a practical execution decision, not a verified broker-by-broker measurement of live trading costs. The historical tests used narrower cost assumptions.",
    "facts": {
      "period": {
        "value": "2023–2024",
        "source": "B09"
      },
      "trades": {
        "value": "1,396",
        "source": "B09"
      },
      "pnl": {
        "value": "+$4,250.48",
        "source": "B09"
      }
    },
    "sections": [
      {
        "heading": "Why I shelved this",
        "paragraphs": [
          "The problem was execution, not a lack of interesting historical signals. Around scheduled releases, spreads widened, orders filled away from intended prices and slippage consumed too much of the move. Those were the conditions faced across the brokers tried.",
          "That was enough to stop pursuing the strategy. It does not establish that every news-trading approach is unworkable, and there is no new verified broker-level slippage study behind this decision."
        ],
        "sources": [
          "B08"
        ]
      },
      {
        "heading": "What the strategy attempted",
        "paragraphs": [
          "Before a scheduled release, the strategy placed triggers on both sides of the market. A sharp move could activate one side; a stop-out could leave the opposite trigger available. Bid and Ask prices, order timing and broker fills are central to whether such a setup can be traded."
        ],
        "figure": "macro-mechanics.svg",
        "alt": "Fictional two-sided order triggers with protective and possible opposite-side exits",
        "caption": "Conceptual order mechanics, not a measured historical fill or price path.",
        "sources": [
          "B08"
        ]
      },
      {
        "heading": "What the backtest could, and couldn't, show",
        "paragraphs": [
          "The {period} high-impact baseline recorded {trades} trades and {pnl} under historical spread-only accounting, before commission. That justified further investigation; it did not prove that trades could be filled at those prices during live releases.",
          "A separate spread-filter comparison removed profitable trades rather than improving the historical result. The tested interventions did not solve the execution conditions that ultimately mattered."
        ],
        "figure": "macro-baseline.svg",
        "alt": "Historical FX news baseline trades and spread-only results by currency pair and year",
        "caption": "Historical spread-only outcomes must not be read as independently verified live profitability.",
        "sources": [
          "B09"
        ]
      }
    ],
    "data": "data/macro-public.json"
  }
}""")
