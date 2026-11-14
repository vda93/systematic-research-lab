"""Editorial selections from the canonical public library and study articles.

Each section selects whole Markdown paragraphs by their unique opening words.
The evidence IDs refer to headings in docs/evidence.md. The owner's MacroImpulse
decision has its own provenance link in the selected paragraph.
"""

ORB = "studies/opening-range.md"
EBP = "studies/engulfing-and-support.md"
INDEX = "studies/orbindex.md"
MACRO = "studies/news-research.md"
CALENDAR = "studies/data-forensics.md"
LIBRARY = "studies/README.md"

STUDIES = {
    "orb": {
        "title": "Opening Range Breakout (ORB)",
        "question": "Does the opening range tell us more than the time of day?",
        "decision": "Tested branches closed for deployment.",
        "finding": (
            "The Nasdaq candidate passed its first validation block and failed its second. "
            "In a separate gold study, the implementations agreed, but financing erased the "
            "discovery gains of both candidates in the monetary comparison."
        ),
        "caveat": "Some successor candidates never reached an out-of-sample test and still have no verdict.",
        "article": ORB,
        "hero": "orb-summary.svg",
        "result_figure": "orb-gold-economics.svg",
        "sections": (
            ("From an opening range to a trade", (
                (ORB, "The intuition is continuation", ("O1",)),
            )),
            ("Two markets with separate test periods", (
                (ORB, "The index study began with", ("O1",)),
                (ORB, "The gold research asked a different set", ("O3", "O4")),
            )),
            ("Gold financing and the deployment decision", (
                (ORB, "This ledger supplies a direct economic comparison", ("O4",)),
            )),
            ("What did the range boundary explain?", (
                (ORB, "A timing plateau does not establish", ("O1",)),
                (ORB, "The special-geometry claim failed this test", ("O1",)),
            )),
            ("The second Nasdaq validation block", (
                (ORB, "The subsequent block tested eligible sessions", ("O2",)),
                (ORB, "The second block produced", ("O2",)),
            )),
            ("Limits of the comparison", (
                (ORB, "This case study covers separate index and gold", ("O1", "O2", "O4")),
            )),
            ("Closeout of the tested branches", (
                (ORB, "The opening-range breakout program closed", ("O6",)),
            )),
        ),
        "evidence": ("O1", "O2", "O3", "O4", "O5", "O6"),
    },
    "ebp": {
        "title": "Engulfing Bar Play (EBP)",
        "question": "Which engulfing-candle signals actually reach a trade?",
        "decision": "All order-policy variants parked.",
        "finding": (
            "On four-hour gold signals, leaving a retracement order open could block later setups, "
            "while replacing it admitted a different set of trades."
        ),
        "caveat": (
            "The positive good-till-cancelled variants each closed only 3 trades. "
            "That left too little evidence to choose an order policy."
        ),
        "article": EBP,
        "hero": "ebp-order-policy.svg",
        "result_figure": "ebp-native-timeframe.svg",
        "sections": (
            ("The engulfing candle and the retracement", (
                (EBP, "An engulfing bar can sweep", ("B21",)),
                (EBP, "Can an engulfing candle support", ("B21",)),
            )),
            ("Four contracts on the same gold signals", (
                (EBP, "*EBP-PY-H002, XAUUSD2 H4", ("B21",)),
            )),
            ("The separate native-timeframe study", (
                (EBP, "The repaired native-clock matrix is mostly negative", ("B22",)),
            )),
            ("Which rules changed trade eligibility?", (
                ("docs/ebp-visual-evidence.md", "GTC blocks later signals", ("B21",)),
                (EBP, "The frozen ambiguity matrix quantified", ("B21",)),
            )),
            ("What later validation could establish", (
                (EBP, "This map describes already-examined Discovery history", ("B22",)),
            )),
            ("Limits of historical order acceptance", (
                (EBP, "EBP tooling separated reconstructed signal geometry", ("B24",)),
            )),
            ("Order-policy and timeframe decisions", (
                (LIBRARY, "The positive good-till-cancelled variants", ("B21", "B22")),
            )),
        ),
        "evidence": ("B21", "B22", "B24"),
    },
    "orbindex": {
        "title": "ORBINDEX",
        "question": "Did promising opening times hold up in a later period?",
        "decision": "Three frozen German index portfolios rejected for economic promotion.",
        "finding": (
            "The DE30, JP225 and UK100 discovery search compared overlapping opening times. "
            "All three DE30 portfolios subsequently lost euros at fixed lot size before "
            "additional commission or financing."
        ),
        "caveat": (
            "Historical broker-net profit remains unverified, and earlier research may "
            "already have examined part of the later period."
        ),
        "article": INDEX,
        "hero": "orbindex-economics.svg",
        "result_figure": "orbindex-economics.svg",
        "sections": (
            ("The opening-time hypothesis", (
                (INDEX, "An opening-range breakout trades a move", ("IX1",)),
            )),
            ("Index quotes and local clocks", (
                (INDEX, "The source was **Exness historical Bid/Ask quotes**", ("IX1",)),
            )),
            ("Fixed-volume euros and price risk", (
                (INDEX, "Why can A have", ("IX3",)),
            )),
            ("Could neighbouring start times confirm the peak?", (
                (INDEX, "The same discovery search found no qualifying neighbourhood", ("IX1",)),
                (INDEX, "B's extra OR5 short made", ("IX2",)),
            )),
            ("Testing the frozen portfolios on later history", (
                (INDEX, "The discovery results justified testing the frozen alternatives", ("IX3",)),
                (INDEX, "In 2025 alone, A lost", ("IX3",)),
            )),
            ("Broker economics and possible prior exposure", (
                ("docs/limitations.md", "The featured [ORBINDEX study]", ("IX1", "IX2", "IX3")),
            )),
            ("Portfolio closeout", (
                (INDEX, "I closed the program without promoting a portfolio.", ("IX3",)),
            )),
        ),
        "evidence": ("IX1", "IX2", "IX3"),
    },
    "macroimpulse": {
        "title": "MacroImpulse",
        "question": "Could scheduled currency news be traded at the available fills?",
        "decision": "Shelved over live execution.",
        "finding": (
            "The project owner reported wide fills, large spreads and slippage across brokers "
            "around scheduled releases. Those conditions made the strategy impractical to trade."
        ),
        "caveat": (
            "A separate historical test relied on a calendar that missed medium-impact events. "
            "The missing releases left profitability on that event universe unresolved."
        ),
        "article": MACRO,
        "hero": "macro-mechanics.svg",
        "result_figure": "macro-baseline.svg",
        "sections": (
            ("Trading the release", (
                (MACRO, "Scheduled economic announcements can reprice currencies", ("B08",)),
            )),
            ("High-impact and medium-impact samples", (
                (MACRO, "The frozen high-impact baseline was evaluated", ("B09",)),
                (CALENDAR, "The development sample was 2021", ("B14", "B15")),
            )),
            ("Baseline results and the spread filter", (
                (MACRO, "A separately frozen spread-filter validation", ("B09",)),
            )),
            ("Execution checks against a reference implementation", (
                (MACRO, "The AI-assisted engineering program reconstructed", ("B08",)),
            )),
            ("The later medium-impact test", (
                (MACRO, "A later medium-impact extension initially appeared", ("B15",)),
            )),
            ("What historical costs can establish", (
                (CALENDAR, "Costs have a separate evidence limit", ("B14",)),
            )),
            ("Why the owner shelved the strategy", (
                (MACRO, "MacroImpulse was shelved because live execution", ()),
            )),
        ),
        "evidence": ("B08", "B09", "B14", "B15"),
    },
}
