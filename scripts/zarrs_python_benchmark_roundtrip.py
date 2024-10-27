#!/usr/bin/env python3

import timeit
import click

import zarr
from zarr.storage import LocalStore, RemoteStore

import zarrs_python  # noqa: F401
zarr.config.set(
    codec_pipeline={
        "path": "zarrs_python.ZarrsCodecPipeline",
        "validate_checksums": False,
        "store_empty_chunks": False,
        "concurrent_target": None,
    }
)

@click.command()
@click.argument('path', type=str)
@click.argument('output', type=str)
def main(path, output):
    if path.startswith("http"):
        store = RemoteStore(url=path) # broken with zarr-python 3.0.0a0
    else:
        store = LocalStore(path)

    dataset = zarr.open(store=store, mode='r')
    dataset_out = zarr.create(store=LocalStore(output), mode='w', shape=dataset.shape, chunks=dataset.chunks, dtype=dataset.dtype, codecs=dataset.metadata.codecs)

    start_time = timeit.default_timer()

    dataset_out[:] = dataset[:]

    elapsed = timeit.default_timer() - start_time
    elapsed_ms = elapsed * 1000.0

    print(f"Round trip in {elapsed_ms:.2f}ms")

if __name__ == "__main__":
    main()
