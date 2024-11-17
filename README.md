
# Zarr Benchmarks

This repository contains benchmarks of Zarr V3 implementations.

> [!NOTE]
> Contributions are welcomed for additional benchmarks, more implementations, or otherwise cleaning up this repository.
>
> Also consider restarting development of the official zarr benchmark repository: https://github.com/zarr-developers/zarr-benchmark

## Implementations Benchmarked
- [`LDeakin/zarrs`](https://github.com/LDeakin/zarrs) via [`LDeakin/zarrs_tools`](https://github.com/LDeakin/zarrs_tools)
  - Read executable: [zarrs_benchmark_read_sync](https://github.com/LDeakin/zarrs_tools/blob/main/src/bin/zarrs_benchmark_read_sync.rs)
  - Round trip executable: [zarrs_reencode](https://github.com/LDeakin/zarrs_tools/blob/main/src/bin/zarrs_reencode.rs)
- Python (v3.12.7):
  - [`google/tensorstore`](https://github.com/google/tensorstore)
  - [`zarr-developers/zarr-python`](https://github.com/zarr-developers/zarr-python)
    - With and without the `ZarrsCodecPipeline` from [`ilan-gold/zarrs-python`](https://github.com/ilan-gold/zarrs-python)
    - With and without [`dask`](https://github.com/dask/dask)

Benchmark scripts are in the [scripts](./scripts/) folder and implementation versions are listed in the benchmark charts.

> [!WARNING]
> Python benchmarks are subject to the overheads of Python and may not be using an optimal API/parameters.
>
> Please open a PR if you can improve these benchmarks.

## `make` Targets
 - `pydeps`: install python dependencies (recommended to activate a venv first)
 - `zarrs_tools`: install `zarrs_tools` (set `CARGO_HOME` to override the installation dir)
 - `generate_data`: generate benchmark data
 - `benchmark_read_all`: run [read all](#read-all-benchmark) benchmark
 - `benchmark_read_chunks`: run [chunk-by-chunk](#read-chunk-by-chunk-benchmark) benchmark
 - `benchmark_roundtrip`: run [roundtrip](#round-trip-benchmark) benchmark
 - `benchmark_all`: run all benchmarks

## Benchmark Data
All datasets are $1024x2048x2048$ `uint16` arrays.


| Name                               | Chunk Shape | Shard Shape | Compression                 | Size   |
|------------------------------------|-------------|-------------|-----------------------------|--------|
| data/benchmark.zarr                | $256^3$     |             | None                        | 8.0 GB |
| data/benchmark_compress.zarr       | $256^3$     |             | `blosclz` 9 + bitshuffling  | 377 MB |
| data/benchmark_compress_shard.zarr | $32^3$      | $256^3$     | `blosclz` 9 + bitshuffling  | 1.1 GB |

## Benchmark System
- AMD Ryzen 5900X
- 64GB DDR4 3600MHz (16-19-19-39)
- 2TB Samsung 990 Pro
- Ubuntu 22.04 (in Windows 11 WSL2, swap disabled, 32GB available memory)

## Round Trip Benchmark

This benchmark measures time and peak memory usage to "round trip" a dataset (potentially chunk-by-chunk).
 - The disk cache is cleared between each measurement
 - These are best of 3 measurements

[Table of raw measurements (benchmarks_roundtrip.md)](./measurements/benchmark_roundtrip.md)

### Standalone

![roundtrip benchmark image](./plots/benchmark_roundtrip.svg)

### Dask

![roundtrip benchmark image dask](./plots/benchmark_roundtrip_dask.svg)

## Read Chunk-By-Chunk Benchmark

This benchmark measures the the minimum time and peak memory usage to read a dataset chunk-by-chunk into memory.
 - The disk cache is cleared between each measurement
 - These are best of 1 measurements

[Table of raw measurements (benchmarks_read_chunks.md)](./measurements/benchmark_read_chunks.md)

### Standalone

![read chunks benchmark image](./plots/benchmark_read_chunks.svg)

> [!NOTE]
> `zarr-python` benchmarks with sharding are not visible in this plot

### Dask

![read chunks benchmark image dask](./plots/benchmark_read_chunks_dask.svg)

## Read All Benchmark
This benchmark measures the minimum time and and peak memory usage to read an entire dataset into memory.
 - The disk cache is cleared between each measurement
 - These are best of 3 measurements

[Table of raw measurements (benchmarks_read_all.md)](./measurements/benchmark_read_all.md)

### Standalone

![read all benchmark image](./plots/benchmark_read_all.svg)

### Dask

![read all benchmark image dask](./plots/benchmark_read_all_dask.svg)
