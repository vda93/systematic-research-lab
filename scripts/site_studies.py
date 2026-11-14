"""Curated, source-bound reading editions; complete research remains in studies/*.md."""

from __future__ import annotations

import json

STUDIES = json.loads(r"""{
  "orbindex": {
    "name": "ORBINDEX",
    "title": "ORBINDEX: promising timings, later losses",
    "technical": "studies/orbindex.md",
    "cover": "orbindex-economics.svg",
    "cover_alt": "Fixed-volume EUR outcomes in discovery and the later historical comparison",
    "subtitle": "A timing search across three index markets led to three German-index portfolios. The later historical results changed the decision.",
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
    ]
  },
  "macroimpulse": {
    "name": "News-Release Trading",
    "title": "News-Release Trading: poor live execution",
    "technical": "studies/news-research.md",
    "cover": "macro-mechanics.svg",
    "cover_alt": "Conceptual buy-stop and sell-stop triggers around an economic release",
    "subtitle": "A historically promising strategy became impractical when traded around real news releases.",
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
    ]
  }
}""")
