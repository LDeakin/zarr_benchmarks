#!/usr/bin/env python3

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D

LEGEND_COLS = 2
YMAX_READ_ALL = 6
YMAX_READ_CHUNKS = 4
YMAX_ROUNDTRIP = 20
# YMAX_READ_ALL = None
# YMAX_READ_CHUNKS = None
# YMAX_ROUNDTRIP = None


implementations = {
    "zarrs_rust": "LDeakin/zarrs (0.17.0)",
    "tensorstore_python": "google/tensorstore (0.1.67)",
    "zarr_python": "zarr-developers/zarr-python (3.0.0b1)",
    "zarrs_python": "ilan-gold/zarrs-python (0.1.0)",
    "zarr_dask_python": "zarr-python (3.0.0b1) + dask (2024.10.0)",
    "zarrs_dask_python": "zarrs-python (0.1.0) + dask (2024.10.0)",
}

images = {
    "data/benchmark.zarr": "Uncompressed",
    "data/benchmark_compress.zarr": "Compressed",
    "data/benchmark_compress_shard.zarr": "Compressed\n + Sharded",
}

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "sans-serif",
    "font.sans-serif": ["lmodern"],
    # "axes.autolimit_mode": "round_numbers",
})

def custom_bar_label(ax, padding=5, rotation=90):
    """Adds labels to bars in a bar chart.
    
    Parameters:
        ax (matplotlib.axes.Axes): The axes containing the bars.
        padding (int): Padding for the labels.
        rotation (int): Rotation angle for the labels.
    """
    y_lim = ax.get_ylim()[1]  # Get the upper limit of the y-axis

    for container in ax.containers:
        for bar in container:
            height = bar.get_height()
            # Determine label position based on whether the bar exceeds y-axis limit
            label_position = min(height, y_lim)  # Use y_lim if height exceeds it
            ax.annotate(f'{height:.3g}', 
                        xy=(bar.get_x() + bar.get_width() / 2, label_position),
                        xytext=(0, padding),
                        textcoords="offset points",
                        ha='center', 
                        va='bottom',
                        rotation=rotation,
                        clip_on=False)

def plot_read_all():
    df = pd.read_csv("measurements/benchmark_read_all.csv", header=[0, 1], index_col=0)
    df.index = ["Uncompressed", "Compressed", "Compressed\n+ Sharded"]
    df.rename(level=1, columns=implementations, inplace=True)
    print(df)


    # Prepare split axis figure and axes
    fig = plt.figure(figsize=(9, 4), layout="constrained")
    spec = fig.add_gridspec(2, 2)
    ax_time = fig.add_subplot(spec[:, 0])
    ax_mem = fig.add_subplot(spec[:, 1])

    # Plot the data
    df["Time (s)"].plot(kind='bar', ax=ax_time)
    ax_time.set_ylim(ymin=0)
    fig.legend(loc='outside upper center', ncol=LEGEND_COLS, title="Zarr V3 implementation", borderaxespad=0)
    df["Memory (GB)"].plot(kind='bar', ax=ax_mem)

    # Styling
    ax_time.set_ylabel("Elapsed time (s)")
    ax_time.set_ylim(ymin=0, ymax=YMAX_READ_ALL)
    ax_time.tick_params(axis='x', labelrotation=0)
    ax_time.grid(True, which='both', axis='y')
    ax_time.spines['top'].set_visible(False)
    ax_time.spines['right'].set_visible(False)
    ax_mem.set_ylabel("Peak memory usage (GB)")
    ax_mem.tick_params(axis='x', labelrotation=0)
    ax_mem.grid(True, which='both', axis='y')
    ax_mem.spines['top'].set_visible(False)
    ax_mem.spines['right'].set_visible(False)

    custom_bar_label(ax_time)
    custom_bar_label(ax_mem)

    ax_time.get_legend().remove()
    ax_mem.get_legend().remove()

    fig.savefig("plots/benchmark_read_all.svg", metadata={'Date': None, 'Creator': None})
    fig.savefig("plots/benchmark_read_all.pdf", metadata={'Date': None, 'Creator': None})


def plot_read_chunks():
    df = pd.read_csv("measurements/benchmark_read_chunks.csv", header=[0, 1], index_col=[0, 1])
    df = df.reset_index(level=1)
    print(df)

    fig = plt.figure(figsize=(9, 4), layout="constrained")
    spec = fig.add_gridspec(2, 2)
    ax_time = fig.add_subplot(spec[:, 0])
        
    ax_mem = fig.add_subplot(spec[:, 1])

    cmap = plt.rcParams['axes.prop_cycle'].by_key()['color']
    image_ls = {'data/benchmark.zarr': ":", 'data/benchmark_compress.zarr': '--', 'data/benchmark_compress_shard.zarr': '-'}
    for image, row in df.groupby("Image"):
        row.plot(x="Concurrency", y="Time (s)", ax=ax_time, color=cmap, ls=image_ls[image])
        row.plot(x="Concurrency", y="Memory (GB)", ax=ax_mem, color=cmap, ls=image_ls[image])

    # Custom legend
    custom_lines = [Line2D([0], [0], color=cmap[i]) for i in range(len(implementations))]
    fig.legend(custom_lines, [implementation.replace(" ", " ") for implementation in implementations.values()], loc="outside upper left", ncol=2, title="Zarr V3 implementation", borderaxespad=0)
    custom_lines = [Line2D([0], [0], color='k', ls=':'),
                Line2D([0], [0], color='k', ls='--'),
                Line2D([0], [0], color='k', ls='-')]
    fig.legend(custom_lines, images.values(), loc="outside upper right", ncol=2, title="Dataset", borderaxespad=0)

    ax_time.get_legend().remove()
    ax_mem.get_legend().remove()

    ax_time.set_ylabel("Elapsed time (s)")

    xticks = [1, 2, 4, 8, 16, 32]
    ax_time.set_ylim(ymin=0, ymax=YMAX_READ_CHUNKS)
    ax_time.set_xscale('log', base=2)
    ax_time.xaxis.set_major_formatter(plt.FuncFormatter("{:.0f}".format))
    ax_time.set_xlim(1, 32) 
    ax_time.set_xticks(xticks)
    ax_time.set_xlabel("Concurrent chunks")
    ax_time.grid(True, which='both', axis='y')
    ax_time.spines['top'].set_visible(False)
    ax_time.spines['right'].set_visible(False)

    ax_mem.set_yscale('log')
    ax_mem.set_xscale('log', base=2)
    ax_mem.xaxis.set_major_formatter(plt.FuncFormatter("{:.0f}".format))
    ax_mem.set_xlim(1, 32)
    ax_mem.set_xticks(xticks)
    ax_mem.set_xlabel("Concurrent chunks")
    ax_mem.set_ylabel("Peak memory usage (GB)")
    ax_mem.grid(True, which='both', axis='y')
    ax_mem.spines['top'].set_visible(False)
    ax_mem.spines['right'].set_visible(False)

    custom_bar_label(ax_time)
    custom_bar_label(ax_mem)

    fig.savefig("plots/benchmark_read_chunks.svg", metadata={'Date': None, 'Creator': None})
    fig.savefig("plots/benchmark_read_chunks.pdf", metadata={'Date': None, 'Creator': None})


def plot_roundtrip():
    df = pd.read_csv("measurements/benchmark_roundtrip.csv", header=[0, 1], index_col=0)
    df.index = ["Uncompressed", "Compressed", "Compressed\n+ Sharded"]
    df.rename(level=1, columns=implementations, inplace=True)
    print(df)


    # Prepare split axis figure and axes
    fig = plt.figure(figsize=(9, 4), layout="constrained")
    spec = fig.add_gridspec(2, 2)
    ax_time = fig.add_subplot(spec[:, 0])
    ax_mem = fig.add_subplot(spec[:, 1])

    # Plot the data
    df["Time (s)"].plot(kind='bar', ax=ax_time)
    ax_time.set_ylim(ymin=0, ymax=YMAX_ROUNDTRIP)
    fig.legend(loc='outside upper center', ncol=LEGEND_COLS, title="Zarr V3 implementation", borderaxespad=0)
    df["Memory (GB)"].plot(kind='bar', ax=ax_mem)

    # Styling
    ax_time.set_ylabel("Elapsed time (s)")
    ax_time.tick_params(axis='x', labelrotation=0)
    ax_time.grid(True, which='both', axis='y')
    ax_time.spines['top'].set_visible(False)
    ax_time.spines['right'].set_visible(False)
    ax_mem.set_ylabel("Peak memory usage (GB)")
    ax_mem.tick_params(axis='x', labelrotation=0)
    ax_mem.grid(True, which='both', axis='y')
    ax_mem.spines['top'].set_visible(False)
    ax_mem.spines['right'].set_visible(False)

    custom_bar_label(ax_time)
    custom_bar_label(ax_mem)

    ax_time.get_legend().remove()
    ax_mem.get_legend().remove()

    fig.savefig("plots/benchmark_roundtrip.svg", metadata={'Date': None, 'Creator': None})
    fig.savefig("plots/benchmark_roundtrip.pdf", metadata={'Date': None, 'Creator': None})

if __name__ == "__main__":
    plot_read_all()
    plot_read_chunks()
    plot_roundtrip()

plt.show()
