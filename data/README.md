# Public observations and aggregate evidence

[historical-results.json](historical-results.json) contains selected **real reported historical aggregates**, transcribed from completed TradingBotHQ reports and primary decision records. Each record includes its source label, sample classification, interval and limitations. It contains no raw market observations, individual trades or production configuration.

The [evidence register](../docs/evidence.md) explains which sources were inspected and what remains private. Source labels identify studies; they are not public links to inaccessible evidence. Additional case-study statistics are linked to the same source register.

The [generated tables](../results/historical-tables.md) retain exact transcribed precision. Figures use readable rounding. R-space profit factor, price-space profit factor, monetary profit factor, percentage-point effects and ATR-normalized markouts remain distinct.

[experiments/protocol.json](../experiments/protocol.json) and [results/study.json](../results/study.json) belong to the separate synthetic methods study. They must not be used as historical evidence.

[ecb-fx-reference.csv](ecb-fx-reference.csv) contains actual selected ECB reference observations, with [separate reuse terms](../DATA_LICENSE.md). [Acquisition](ecb-acquisition.json) identifies source bytes, snapshot selection and the preaccess method commit. [Execution](ecb-execution.json) discloses the pinned runtime and an initial runtime correction. [ecb-fx-results.json](ecb-fx-results.json) is rebuilt offline from those observations by the [public pipeline](../scripts/fx_study.py). It contains reference-rate associations, not executable trading returns.

[claim-registry.json](claim-registry.json) binds reviewed numeric prose and figure inputs to source IDs. [Scientific checks](../docs/scientific-checks.md) explain the controls and their limits. Original raw archive bytes and sensitive TradingBotHQ provenance stay outside Git.
