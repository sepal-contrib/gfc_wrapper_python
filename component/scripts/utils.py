import rasterio as rio
import numpy as np
import pandas as pd

from component import parameter as cp


def pixel_count(raster):
    """produce the histogramm of each values in the raster in pixels

    Args:
        raster(str): the pathname to the raster used to perform the histogramm

    Returns:
        hist (): the histogram to be used
    """

    # readt the file
    with rio.open(raster) as src:
        info = src.read(1, masked=True)

    # extract the frequency of each value
    array = np.array(info.ravel())
    codes, frequency = np.unique(array, return_counts=True)

    columns = ["code", "pixels"]
    hist = pd.DataFrame(
        [[codes[i], frequency[i]] for i in range(len(codes))], columns=columns
    )

    # drop the 0 line (no-data)
    hist = hist[hist["code"] != 0]

    # add the labels
    hist["class"] = cp.gfc_labels

    return hist


def to_hectar(x, resx, resy):
    """convert a pixel number into a surface in hectar using the provided resolution (res in meters)"""
    return x * resx * resy / 10000
