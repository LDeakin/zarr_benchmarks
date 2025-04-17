setup:
	uv venv --python 3.12
	uv pip install -r requirements.txt
	cargo binstall zarrs_tools@0.7.1

binstall:
	curl -L --proto '=https' --tlsv1.2 -sSf https://raw.githubusercontent.com/cargo-bins/cargo-binstall/main/install-from-binstall-release.sh | bash

generate_data:
	uv run scripts/generate_benchmark_array.py data/benchmark.zarr
	uv run scripts/generate_benchmark_array.py --compress data/benchmark_compress.zarr
	uv run scripts/generate_benchmark_array.py --compress --shard data/benchmark_compress_shard.zarr

benchmark_read_all:
	uv run scripts/run_benchmark_read_all.py

benchmark_read_chunks:
	uv run scripts/run_benchmark_read_chunks.py

benchmark_roundtrip:
	uv run scripts/run_benchmark_roundtrip.py

plot:
	uv run scripts/plot_benchmarks.py

benchmark_all: benchmark_read_all benchmark_read_chunks benchmark_roundtrip
