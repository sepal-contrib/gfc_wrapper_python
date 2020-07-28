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
        return 'stats already computed'
    
    hist = utils.pixelCount(map_raster)
    
    if not os.path.isfile(map_raster): 
        return 'No gfc map'
    
    src = gdal.Open(map_raster)
    proj = osr.SpatialReference(wkt=src.GetProjection())
    bb = utils.get_bounding_box(assetId)
    _, resx, _, _, _, resy  = src.GetGeoTransform()
    src = None
    
    print(proj)
    print (resx)
    
    #convert to hectars
    hist['area'] = hist['pixels']*resx*resx/10000
    
    treecover_area = hist.loc[(hist['code'] == 40) | ((hist['code'] > 0) & (hist['code'] < 30)), ['area']].sum()
    loss_area = hist.loc[(hist['code'] > 0) & (hist['code'] < 30), ['area']].sum()
    
    #create an output file
    hist.to_csv(hist_file, index=False)