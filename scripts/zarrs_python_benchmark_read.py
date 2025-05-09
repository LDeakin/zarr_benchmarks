#!/usr/bin/env python3

import numpy as np
import timeit
import asyncio
import click
from functools import wraps
import sys

import zarr
from zarr.storage import LocalStore, FsspecStore
from zarr.core.indexing import BlockIndexer
from zarr.core.buffer import default_buffer_prototype

import zarrs
zarr.config.set({
    "threading.num_workers": None,
    "array.write_empty_chunks": False,
    "codec_pipeline": {
        'batch_size': 1,
        "path": "zarrs.ZarrsCodecPipeline",
        "validate_checksums": True,
        "store_empty_chunks": False,
        "chunk_concurrent_minimum": 4,
        "chunk_concurrent_maximum": None,
    }
})


def coro(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper

@click.command()
@coro
@click.argument('path', type=str)
@click.option('--concurrent_chunks', type=int, default=None, help='Number of concurrent async chunk reads. Ignored if --read-all is set')
@click.option('--read_all', is_flag=True, show_default=True, default=False, help='Read the entire array in one operation.')
async def main(path, concurrent_chunks, read_all):
    # if "benchmark_compress_shard.zarr" in path:
    #     sys.exit(1)

    if path.startswith("http"):
        store = FsspecStore.from_url(url=path) # broken with zarr-python 3.0.0a0
    else:
        store = LocalStore(path, read_only=True)

    dataset = zarr.open(store=store, mode='r')

    domain_shape = dataset.shape
    chunk_shape = dataset.shards or dataset.chunks

    print("Domain shape", domain_shape)
    print("Chunk shape", chunk_shape)
    num_chunks =[(domain + chunk_shape - 1) // chunk_shape for (domain, chunk_shape) in zip(domain_shape, chunk_shape)]
    print("Number of chunks", num_chunks)

    async def chunk_read(chunk_index):
        indexer = BlockIndexer(chunk_index, dataset.shape, dataset.metadata.chunk_grid)
        return await dataset._async_array._get_selection(
            indexer=indexer, prototype=default_buffer_prototype()
        )

    start_time = timeit.default_timer()
    if read_all:
        print(dataset[:].shape)
    elif concurrent_chunks is None:
        async with asyncio.TaskGroup() as tg:
            for chunk_index in np.ndindex(*num_chunks):
                tg.create_task(chunk_read(chunk_index))
    elif concurrent_chunks == 1:
        for chunk_index in np.ndindex(*num_chunks):
            dataset[tuple(slice(i * s, (1 + i) * s) for i, s in zip(chunk_index, chunk_shape))]
    else:
        semaphore = asyncio.Semaphore(concurrent_chunks)
        async def chunk_read_concurrent_limit(chunk_index):
            async with semaphore:
                return await chunk_read(chunk_index)
        async with asyncio.TaskGroup() as tg:
            for chunk_index in np.ndindex(*num_chunks):
                tg.create_task(chunk_read_concurrent_limit(chunk_index))

    elapsed = timeit.default_timer() - start_time
    elapsed_ms = elapsed * 1000.0
    print(f"Decoded in {elapsed_ms:.2f}ms")

if __name__ == "__main__":
    asyncio.run(main())
