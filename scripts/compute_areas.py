from utils import parameters as pm
from utils import utils
import os
import pandas as pd
import gdal
from osgeo import osr

def compute_areas(assetId, threshold):
    
    aoi_name = utils.get_aoi_name(assetId)
    
    hist_file = pm.getStatDir() + aoi_name + "_{}_gfc_stats.txt".format(threshold)
    
    map_raster = pm.getGfcDir() + aoi_name + '_{}_gfc_map.tif'.format(threshold)
    
    #skip if output already exist 
    if os.path.isfile(hist_file):
        print('stats already computed')
        return hist_file 
    
    if not os.path.isfile(map_raster): 
        print('No gfc map')
        return None
    
    hist = utils.pixelCount(map_raster)
    
    src = gdal.Open(map_raster)
    proj = osr.SpatialReference(wkt=src.GetProjection())
    bb = utils.get_bounding_box(assetId)
    _, resx, _, _, _, resy  = src.GetGeoTransform()
    src = None
    
    #the prjection is not equal-area. Approximation of the pixel surface is done with the followings : 1° = 111 km
    
    resx_proj = resx * 111321
    
    #convert to hectars
    hist['area'] = utils.toHectar(hist['pixels'], resx_proj)
    
    #checks
    treecover_area = hist.loc[(hist['code'] == 40) | ((hist['code'] > 0) & (hist['code'] < 30)), ['area']].sum()
    loss_area = hist.loc[(hist['code'] > 0) & (hist['code'] < 30), ['area']].sum()
    
    #drop 0 ha lines and croped values (255)
    hist = hist[(hist['area'] != 0) & (hist['code'] != 255.)]
    #create an output file
    hist.to_csv(hist_file, index=False)
    
    return hist_file