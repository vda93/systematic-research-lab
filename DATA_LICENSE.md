# ECB reference data: source and reuse conditions

The selected dataset `data/ecb-fx-reference.csv`, when acquired and qualified,
contains European Central Bank (ECB) euro foreign exchange reference
observations. `data/ecb-fx-results.json` contains identified author calculations.
Synthetic software fixtures are explicitly marked in the tests. The software
license does not apply to ECB source observations.

Source: European Central Bank, euro foreign exchange reference rates.

- [Provider and historical downloads](https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html).
- [Historical ZIP](https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.zip).
- [ECB copyright and disclaimer conditions](https://www.ecb.europa.eu/services/using-our-site/disclaimer/html/index.en.html).
- [Reference-rate framework](https://www.ecb.europa.eu/stats/pdf/exchange/Frameworkfortheeuroforeignexchangereferencerates.en.pdf).

The ECB retains copyright. Its published conditions permit free use of
information obtained directly from its website, with accurate reproduction and
ECB source acknowledgement. Modifications must be identified. If incorporated
in a document sold for a fee, buyers must be told before payment and whenever
accessing the information that it is available free from the ECB. Business or
promotional links must display the full ECB page without framing. Named-author
documents have a separate permission exception. This notice does not replace
the provider's complete terms.

The source observations are available free from the ECB. This project selects
`[2016-06-01,2026-01-01)`, USD-per-EUR and JPY-per-EUR, sorts dates and normalizes
file serialization. Selected source decimal values are preserved. USDJPY is
calculated as JPY-per-EUR divided by USD-per-EUR. Momentum features and
logarithmic changes are author calculations, not additional ECB publications.
The [protocol](experiments/ecb-fx-mom20-protocol.md) defines all transformations.
The acquisition receipt and evidence manifest, once created, identify retrieval
time, original ZIP hash, selected CSV hash and protocol commit. This notice
does not assert that acquisition or qualification has already occurred.

No public-domain, CC0, CC-BY or MIT license is asserted for ECB data. No ECB
endorsement is implied and no ECB logo is used. Archive contents must pass the
documented notice check before redistribution. An unexpected document or
restriction blocks publication pending explicit review.

These reference observations are provided for information. They are not
executable bid/ask quotes. The study does not establish fills, trading costs,
financing, net profitability or suitability for live trading. The snapshot is a
retrieval vintage and does not prove the information available at every past
publication time. Provider terms and disclaimers remain applicable.
