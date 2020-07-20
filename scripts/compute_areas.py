from utils import parameters as pm
from utils import utils
import os
import pandas as pd

def compute_area(assetId, threshold):
    
    aoi_name = utils.get_aoi_name(assetId)
    
    hist_file = pm.getStatDir() + aoi_name + "gfc_stats_{}.txt".format(threshold)
    
    map_raster = pm.getGfcDir() + aoi_name + 'gfc_{}_map_clip_pct.tif'.format(threshold)
    
    #skip if output already exist 
    if os.path.isfile(hist_file):
        return 'stats already computed'
    
    hist = utils.pixel_count(map_raster)
    
    if not os.path.isfile(mask): 
        return 'No gfc map'
    
    src = gdal.Open(map_raster)
    proj = osr.SpatialReference(wkt=src.GetProjection())
    bb = utils.get_bounding_box(assetID)
    res = {}
    _, res['x'], _, _, _, res['y']  = src.GetGeoTransform()
    src = None
    
    #convert to hectars
    hist['area'] = hist['pixels']*res['x']*res['x']/10000
    
    treecover_area = hist.loc[hist['code'] == 40 or (hist[code] > 0 and hist['code'] < 30), 'area'].sum()
    loss_area = hist.loc[host['code'] > 0 and hist['code'] < 30, 'area'].sum()
    
    #create an output file
    hist.to_csv(hist_file, index=False)