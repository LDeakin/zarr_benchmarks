

pydeps:
	pip install -r requirements.txt

zarrs_tools:
	cargo install --features=benchmark,binary2zarr --git=https://github.com/LDeakin/zarrs_tools.git

generate_data:
	python3 scripts/generate_benchmark_array.py data/benchmark.zarr
	python3 scripts/generate_benchmark_array.py --compress data/benchmark_compress.zarr
	python3 scripts/generate_benchmark_array.py --compress --shard data/benchmark_compress_shard.zarr

benchmark_read_all:
	python3 scripts/run_benchmark_read_all.py

benchmark_read_chunks:
	python3 scripts/run_benchmark_read_chunks.py

benchmark_roundtrip:
	python3 scripts/run_benchmark_roundtrip.py

plot:
	python3 scripts/plot_benchmarks.py

benchmark_all: benchmark_read_all benchmark_read_chunks benchmark_roundtrip
