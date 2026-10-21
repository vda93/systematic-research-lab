# Circular-block means: faster sampling without floating prefix cancellation

[Portfolio](../README.md) · [Source](../src/srl/block_means.py) · [Oracle tests](../tests/test_block_means.py) · [Benchmark](../scripts/benchmark_block_means.py)

Dependence-aware bootstrap inference repeatedly samples neighboring observations. The released [reference sampler](../src/srl/resampling.py) expands every selected block into observation indices and sums those values for every draw. This is straightforward to inspect but repeats work when blocks are long. The new optional kernel computes each possible block total once, then samples totals. It leaves the existing studies and their frozen outputs unchanged.

This contribution was designed and implemented with AI assistance under the candidate's project requirements. Source, tests and measurements establish released behavior; they do not establish the candidate's unaided authorship or technical mastery. See [ownership](ownership.md).

## Mathematical contract

Supply an ordered vector of already qualified observations, such as aligned treatment-minus-control daily differences. Alignment, missing-day handling, risk units and construction of those differences remain the caller's responsibility. Each observation counts once in the original mean; no weighting or calendar is inferred.

For sample length n, block length L and draw r, choose independent uniform starts s(r,j) from the n observation indices. Read consecutive indices modulo n. Let k=floor(n/L), h=n mod L. A draw contains k full blocks and, when h is positive, one independently started length-h block. Its mean is

```text
T(s,l) = sum(x[(s+i) mod n], i=0,...,l-1)
m[r]  = (sum(T(s[r,j],L), j=1,...,k) + T(s[r,k+1],h)) / n
```

The last term is omitted when h is zero. Each draw contains exactly n values, including duplicated selections. Truncating a final block is part of the sampling law. The seed and uniform-start calls match `circular_indices`, so comparisons use identical selected observations. Increasing repetitions preserves the earlier draw prefix.

The API requires at least four observations, a positive integer repetition count, an integer seed and `1 <= block_size <= n//2`. Booleans, strings and nonfinite values fail. Built-in integers are converted to float first; integers beyond exact float precision may change value. Signed zero is not retained as provenance. The return is an immutable tuple in draw order.

## Why integer prefixes

A floating cumulative sum can lose a small increment beside a large prefix; subtracting two prefixes cannot recover it. Summing individually rounded block totals can also lose cancellation between blocks. `math.fsum` over every selected observation avoids much of this error, but expanding every draw remains costly and a large intermediate sum can overflow even when its mean is representable.

Every accepted binary float has an exact ratio p/q, with q a power of two. Choose D as the largest input denominator and form integers a[i]=p[i]*(D/q[i]). Then x[i]=a[i]/D exactly for the accepted float values. Python integers preserve all bits of the cumulative sums:

```text
P[0] = 0
P[j+1] = P[j] + a[j]
T_int(s,l) = P[s+l] - P[s]                       if s+l <= n
             P[n] - P[s] + P[s+l-n]              otherwise
m[r] = float(Fraction(sum_of_selected_T_int, n*D))
```

The implementation stores all full-block totals and, when needed, all tail totals. The sampled total is an integer. There is one rational-to-float conversion per mean, after exact aggregation; no floating prefix subtraction or rounded intermediate block sum occurs. A true mean smaller than float resolution can round to zero. Inputs' decimal interpretation is not recovered: the exact ratio represents the supplied binary float. Python documents this distinction for [Fraction](https://docs.python.org/3.12/library/fractions.html); the conversion is implemented in [CPython's rational-number code](https://github.com/python/cpython/blob/3.12/Lib/fractions.py).

This is deliberately an optional API. The old `fsum`-then-divide method and the new exact-rational mean need not be bit-identical for arbitrary inputs because the former can round twice. Changing a scientific output requires a versioned methods decision, rather than silently swapping kernels under a frozen artifact.

## Source and failure cases

`_ratios` validates and converts inputs. `_block_totals` implements the two wrap cases above. `circular_block_means` chooses starts, adds full and tail totals and performs the final conversion. The [test oracle](../tests/test_block_means.py) instead expands every selected observation into an independent `Fraction` sum. It shares no prefix, wrap or block-total helper with production code.

The tests cover a hand-calculated random stream, every permitted block length on several short paths, partial final blocks, wraparound, constant effects, catastrophic cancellation, extreme finite magnitudes, subnormal rounding, invalid parameters, reproducible prefixes and preservation of the input. The all-maximum-float example is particularly useful: summing in float can overflow, while an average of identical maximum floats is still that finite float. Deterministic oracle agreement verifies arithmetic for these cases, not the coverage of a market-data confidence interval.

## Performance and its cost

The [measurement receipt](../data/block-means-benchmark.json) retains a before-implementation run and the subsequent side-by-side run. Fixtures are deterministic sine values with a small periodic offset, not synthetic trading evidence. Measurements use Python 3.12.10 on Windows, 2,048 draws, a warm-up and five timing repeats with alternating algorithm order. Timings include preprocessing and output allocation; `tracemalloc` peaks are measured separately so tracing does not distort those times.

| Observations / block length | Reference median | Exact-block median | Speedup | Traced peak, reference / exact |
| --- | ---: | ---: | ---: | ---: |
| 1,024 / 1 | 1.4955 s | 0.5652 s | 2.65× | 105,328 / 254,100 bytes |
| 1,024 / 16 | 0.2527 s | 0.0379 s | 6.68× | 106,936 / 255,484 bytes |
| 4,096 / 32 | 0.8432 s | 0.0739 s | 11.40× | 233,616 / 881,260 bytes |

The original before-run reference medians were 1.4279, 0.2576 and 0.8550 seconds, in the same case order. Both phases retain the released reference source hash. The side-by-side result tuples match exactly on these bounded fixtures; the oracle, rather than benchmark agreement alone, checks difficult arithmetic. These are local measurements of this sampling kernel. They establish neither a universal speedup nor an end-to-end acceleration of the frozen FX pipeline, which already has its own implementation. More prefix storage explains the higher measured memory use.

The reference needs O(B*n) observation visits for B draws. Integer blocks need O(n) preprocessing and O(B*ceil(n/L)) sampled additions. Storage is O(n+B) objects; no B-by-n draw matrix is allocated. This count hides integer bit length: a mix of extreme and subnormal floats creates large integers, arithmetic costs grow with their bits, and rational reduction/conversion has its own cost. Benchmarks on ordinary bounded values cannot establish performance on that worst case. Large n, short L or few draws can make preprocessing unattractive.

Reproduce correctness and then measure on your machine:

```sh
python scripts/reproduce.py --check
python scripts/benchmark_block_means.py --repeats 5 --repetitions 2048
```

## What the kernel does not establish

Circular blocks assume that the supplied sequence is an adequate approximately stationary representation of dependence. Wrapping the endpoint creates an artificial adjacency. A short sample, a structural break, a poor block length, sample selection or a misspecified estimand can invalidate inference despite exact arithmetic. The kernel supplies replicate means, not a p-value, a trading signal, a fill model or a qualified research conclusion. Block-length choice and multiplicity belong in the study protocol; sensitivity results cannot be selected after seeing which one passes.
