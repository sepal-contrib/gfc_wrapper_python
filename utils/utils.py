import os 
import shapely.geometry as sg
import gdal
import matplotlib as mpl
import numpy as np
import pandas as pd
import ee
from utils import parameters as pm
import geemap
import math
import rasterio as rio

ee.Initialize()

def get_aoi_name(asset_name):
    """Return the corresponding aoi_name from an assetId"""
    return os.path.split(asset_name)[1].replace('aoi_','')

def colorFader(v=0):
    """ return a rgb (0-255) tuple corresponding the v value in a 19 spaces gradient between yellow and darkred"""
    
    c1='yellow'
    c2='darkred'
    
    n = len(range(1,pm.getMaxYear()+1))
    mix = v/n
    
    c1=np.array(mpl.colors.to_rgb(c1))
    c2=np.array(mpl.colors.to_rgb(c2))
    
    return (1-mix)*c1 + mix*c2

def get_bounding_box(assetId):
    """return a list of str of the (minx, miny, maxx, maxy) of the asset
    """
    aoi = ee.FeatureCollection(assetId)
    aoiJson = geemap.ee_to_geojson(aoi)
    aoiShp = sg.shape(aoiJson['features'][0]['geometry'])
    
    bb = {}
    bb['minx'], bb['miny'], bb['maxx'], bb['maxy'] = aoiShp.bounds
    
    bb['minx'] = str(math.floor(bb['minx']))
    bb['miny'] = str(math.floor(bb['miny']))
    bb['maxx'] = str(math.ceil(bb['maxx']))
    bb['maxy'] = str(math.ceil(bb['maxy']))
    
    return bb

def pixelCount(raster):
    """ produce the histogramm of each values in the raster in pixels
  
    Args: 
        raster(str): the pathname to the raster used to perform the histogramm
    
    Returns:
        hist (): the histogram to be used
    """
    
    #readt the file 
    with rio.open(raster) as src:
        info = src.read(1, masked=True)

    #extract the frequency of each value 
    array = np.array(info.ravel())
    codes, frequency = np.unique(array, return_counts=True)
    
    columns = ['code', 'pixels']
    hist = pd.DataFrame([[codes[i], frequency[i]] for i in range(len(codes))], columns=columns)
    
    #drop the 0 line (no-data)
    hist = hist[hist['code'] != 0]
    
    #add the labels 
    hist['class'] = pm.getMyLabel()
    
    return hist

def toHectar(x, resx, resy):
    """convert a pixel number into a surface in hectar using the provided resolution (res in meters)"""
    return x*resx*resy/10000

