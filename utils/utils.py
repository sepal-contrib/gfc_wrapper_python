import os
import csv
import ee 
import geemap
import math
import shapely.geometry as sg
import gdal
import pandas
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import sys
sys.path.append("..") # Adds higher directory to python modules path
from utils import parameters as pm
import pandas as pd

ee.Initialize()

def get_bounding_box(assetID):
    """return a list of str of the (minx, miny, maxx, maxy) of the asset
    """
    aoi = ee.FeatureCollection('users/bornToBeAlive/aoi_PU')
    aoiJson = geemap.ee_to_geojson(aoi)
    aoiShp = sg.shape(aoiJson['features'][0]['geometry'])
    
    bb = {}
    bb['minx'], bb['miny'], bb['maxx'], bb['maxy'] = aoiShp.bounds
    
    bb['minx'] = str(math.floor(bb['minx']))
    bb['miny'] = str(math.floor(bb['miny']))
    bb['maxx'] = str(math.ceil(bb['maxx']))
    bb['maxy'] = str(math.ceil(bb['maxy']))
    
    return bb
    

def create_FIPS_dic():
    """create the list of the country code in the FIPS norm using the CSV file provided in utils
        
    Returns:
        fips_dic (dic): the country FIPS_codes labelled with english country names
    """
     
    pathname = os.path.join(os.path.dirname(__file__), 'FIPS_code_to_country.csv')
    fips_dic = {}
    with open(pathname, newline='') as f:
        reader = csv.reader(f, delimiter=';')
        next(reader)
        for row in reader:
            fips_dic[row[1]] = row[3]
            
        fips_sorted = {}
        for key in sorted(fips_dic):
            fips_sorted[key] = fips_dic[key]
        
    return fips_sorted

def get_aoi_name(asset_name):
    """Return the corresponding aoi_name from an assetId"""
    return os.path.split(asset_name)[1].replace('aoi_','')


def pixelCount(raster):
    """ give the results of the hist function from Gdalinfo. NaN and 0 are removed
  
    Args: 
        raster(str): the pathname to the raster used to perform the histogramm
    
    Returns:
        hist (): the histogram to be used
    """
    info = gdal.Info(raster, reportHistograms=True)
    info = info.split(' ')
    
    index = info.index('buckets') #find the buket keyword
    
    #buckets_nb = int(info[index-1])
    #min_ = float(info[info.index('from', index)+1])
    #max_ = float(info[info.index('to', index)+1].replace(':\n',''))
    
    #hadr code that the bucket is on pixel value coded on 256 bytes
    buckets_nb = 256
    min_ = 0
    max_ = 256
    
    interval = (abs(min_) + abs(max_))/buckets_nb
    
    codes = [ min_+ i*interval for i in range(buckets_nb)]
    
    values = info[info.index('', index)+1:info.index('\n', index)]
    values = [int(i) for i in values]
    
    d = { "code": codes, "pixels": values}
    d = pd.DataFrame(data=d)
    
    return d
    
def estimate():
    """estimate <- function(x,y){
  nrow(df[
    df$lon_fact%%x == 0 & 
      df$lat_fact%%x == 0 &
      df$code == y
    ,])/
    nrow(df[
      df$lon_fact%%x == 0 & 
        df$lat_fact%%x == 0 &
        (df$code == 40 | (df$code > 0 & df$code < 30))
      ,])
}"""
    
def allaEstimate():
       """all_estimate <- function(x){
  nrow(df[
    df$lon_fact%%x == 0 & 
      df$lat_fact%%x == 0  & 
      (df$code > 0 & df$code < 30)
    ,])/
    nrow(df[
      df$lon_fact%%x == 0 & 
        df$lat_fact%%x == 0 &
        (df$code == 40 | (df$code > 0 & df$code < 30))
      ,])
}"""
        
def nombre():
    """nombre <- function(x){
  nrow(df[
    df$lon_fact%%x == 0 & 
      df$lat_fact%%x == 0 &
      (df$code == 40 | (df$code > 0 & df$code < 30))
    ,]
  )}"""
  
def make_grid(points, spacing):

    xmin,ymin,xmax,ymax = points.total_bounds

    cols = list(range(int(np.floor(xmin)), int(np.ceil(xmax)), spacing))
    rows = list(range(int(np.floor(ymin)), int(np.ceil(ymax)), spacing))
    rows.reverse()

    polygons = []
    for x in cols:
        for y in rows:
            polygons.append( Polygon([(x,y), (x+wide, y), (x+wide, y-length), (x, y-length)]) )

    grid = gpd.GeoDataFrame({'geometry':polygons})
    
    return grid

def colorFader(v=0):
    """ return a rgb (0-255) tuple corresponding the v value in a 19 spaces gradient between yellow and darkred"""
    
    c1='yellow'
    c2='darkred'
    
    n = len(range(1,pm.getMaxYear()+1))
    mix = v/n
    
    c1=np.array(mpl.colors.to_rgb(c1))
    c2=np.array(mpl.colors.to_rgb(c2))
    
    return mpl.colors.to_rgb((1-mix)*c1 + mix*c2)


