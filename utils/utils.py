import os 
import shapely.geometry as sg
import gdal
import matplotlib as mpl
import numpy as np
import pandas as pd
import sys
sys.path.append("..") # Adds higher directory to python modules path
from utils import parameters as pm

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
    
    return mpl.colors.to_hex((1-mix)*c1 + mix*c2)


