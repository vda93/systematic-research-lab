# Public evidence and closeout controls

Run the current public evidence check from the repository root:

```sh
python scripts/research_os.py verify experiments/evidence-example.json
```

The example checks the actual bytes of [the historical aggregate transcription](../data/historical-results.json). It labels that file `reported_aggregate`, `spent` and consumed. Its broad date envelope describes a presentation file containing several studies; it does not combine those studies into a return series. Historical conclusions and sample histories remain unchanged. This validator was independently authored for the public portfolio; no private execution or research implementation was imported.

Create and check a portable evidence closeout:

```sh
python scripts/research_os.py pack experiments/evidence-example.json closeout.zip
python scripts/research_os.py verify-pack closeout.zip
```

Choose a new output filename each time. The pack contains only declared evidence files, the manifest, internal SHA256/size records and, when supplied, the prior role ledger. Sorted member names, stored bytes and constant ZIP timestamps, permissions and platform metadata make identical inputs produce identical ZIP bytes. Verification reads every member and checks CRC, hashes, manifest semantics, exact membership, duplicate or escaping names and symlink entries without extracting anything. Verification is limited to 64 MiB of uncompressed members. To bind a downloaded archive to an independently trusted release digest, use `verify-pack closeout.zip --sha256 DIGEST`. Internal hashes alone cannot detect an attacker rewriting both content and every matching hash.

## Manifest contract

[The example manifest](../experiments/evidence-example.json) is the complete version-1 schema. Fields are mandatory; unknown fields, duplicate JSON keys, unsafe portable paths, symlinks/junctions, size/hash mismatches, repeated IDs, missing ownership/licensing/source metadata and missing public disclosure approval fail. `redistribution` must be explicitly `permitted`. A license string and an approval flag record the author's declaration; the code cannot decide third-party rights or independently authenticate that declaration.

Each evidence item declares a scientific `study_id`, a `sample_space` such as an instrument and observation universe, a half-open date period `[period_start, period_end_exclusive)`, and a role: `development`, `validation`, `test`, `spent`, `invalid`, `engineering` or `illustration`. Different scientific roles cannot overlap within the same study and sample space. Adjacent periods, overlapping records in the same role and separate studies/spaces are permitted. Engineering and illustration periods do not define scientific partitions. Changing study labels does not make previously observed identical bytes unseen: identical hashes share the identity transition restrictions.

To check a revision against a trusted previous ledger:

```sh
python scripts/research_os.py verify revised-manifest.json --previous previous-manifest.json
python scripts/research_os.py pack revised-manifest.json revised-closeout.zip --previous previous-manifest.json
```

An evidence ID cannot change its hash. Consumption is irreversible; spent/invalid identities retain their role. Development/validation identities may retain their role, become spent or become invalid. Consumed, spent, invalid, development or validation evidence cannot become unseen `test` evidence through an alias sharing its hash. Supply retained trusted ledgers when checking revisions; a standalone current manifest cannot reconstruct omitted history. These checks neither detect semantically identical observations in differently encoded files nor prove that a declared test sample was truly unseen. The study protocol still owns horizon purging, participant/instrument separation, access history and other scientific partition rules.

Claims require unique existing evidence IDs and approved disclosure. `engineering` claims describe engineering checks. `historical_report` permits qualified reporting from historical inputs or reported aggregates. `historical_alpha` requires scientifically usable historical evidence; `clean_oos_economic` additionally requires unconsumed `test` samples. Synthetic/engineering inputs and aggregate transcriptions cannot support historical alpha or clean OOS economic claims. Invalid samples cannot support those economic claim kinds. Passing these necessary checks does not establish economic validity, statistical significance, causal identification, execution parity, historical replay or deployment authority. Claim text still needs human review against its referenced evidence and inference method.

## Python API

```python
from pathlib import Path
from srl.evidence import load_manifest, verify_manifest, pack, verify_pack

raw = load_manifest(Path("experiments/evidence-example.json"))
checked = verify_manifest(Path("."), raw)  # typed Manifest/Evidence/Claim records
pack(Path("."), raw, Path("closeout.zip"))
verify_pack(Path("closeout.zip"))
```

The standard-library implementation is in [evidence.py](../src/srl/evidence.py); adversarial tests are in [test_evidence.py](../tests/test_evidence.py). Small synthetic byte fixtures exist only inside temporary test directories. They test governance and archive behavior, not an alpha study. A file may change between filesystem operations; use a controlled immutable checkout for closeout creation. The archive validates its captured bytes again before writing. Neither manifests nor closeouts are signed attestations.
