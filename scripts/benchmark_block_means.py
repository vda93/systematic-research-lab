"""Compare the released observation loop with exact block totals; no market data."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import platform
import random
import statistics
import sys
import time
import tracemalloc

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from srl.block_means import circular_block_means
from srl.resampling import circular_indices


def reference(values: list[float], *, block_size: int, repetitions: int, seed: int) -> tuple[float, ...]:
    """The old per-observation sampling loop, including its final float arithmetic."""
    rng = random.Random(seed)
    n = len(values)
    return tuple(math.fsum(values[i] for i in circular_indices(n, block_size, rng)) / n
                 for _ in range(repetitions))


def benchmark(repeats: int, repetitions: int) -> dict:
    rows = []
    for n, block in [(1024, 1), (1024, 16), (4096, 32)]:
        values = [math.sin(i * .17) + .001 * (i % 17) for i in range(n)]
        parameters = dict(block_size=block, repetitions=repetitions, seed=7401)
        timings: dict[str, list[float]] = {'reference': [], 'exact_blocks': []}
        algorithms = {'reference': reference, 'exact_blocks': circular_block_means}
        output = {}
        for name, algorithm in algorithms.items():
            algorithm(values, block_size=block, repetitions=8, seed=7401)
            output[name] = algorithm(values, **parameters)
        # Alternate order to reduce a systematic warm-machine advantage.
        for trial in range(repeats):
            order = list(algorithms) if trial % 2 == 0 else list(reversed(algorithms))
            for name in order:
                start = time.perf_counter()
                algorithms[name](values, **parameters)
                timings[name].append(time.perf_counter() - start)
        peaks = {}
        for name, algorithm in algorithms.items():
            tracemalloc.start()
            algorithm(values, **parameters)
            peaks[name] = tracemalloc.get_traced_memory()[1]
            tracemalloc.stop()
        medians = {name: statistics.median(times) for name, times in timings.items()}
        rows.append(dict(n=n, **parameters, seconds=timings, median_seconds=medians,
                         speedup=medians['reference'] / medians['exact_blocks'],
                         peak_traced_bytes=peaks,
                         max_abs_mean_difference=max(abs(a-b) for a, b in
                                                    zip(output['reference'], output['exact_blocks'])),
                         result_sha256={name: hashlib.sha256(repr(result).encode()).hexdigest()
                                        for name, result in output.items()}))
    return dict(python=platform.python_version(), platform=platform.platform(),
                repetitions=repetitions, timing_repeats=repeats,
                scope='deterministic mathematical fixture; no financial observations',
                sources_sha256={name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                                for name in ('src/srl/block_means.py', 'src/srl/resampling.py',
                                             'scripts/benchmark_block_means.py')}, cases=rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repeats', type=int, default=5)
    parser.add_argument('--repetitions', type=int, default=2048)
    args = parser.parse_args()
    if args.repeats < 1 or args.repetitions < 1:
        parser.error('repeats and repetitions must be positive')
    print(json.dumps(benchmark(args.repeats, args.repetitions), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
