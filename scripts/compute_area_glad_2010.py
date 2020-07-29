from utils import parameters as pm
from utils import utils
import os
import pandas as pd
import gdal 
from osgeo import gdalconst, osr

def compute_area_glad_2010(assetId, threshold):
    
    aoi_name = utils.get_aoi_name(assetId)
    
    hist_file = pm.getStatDir() + aoi_name + "_glad_stats_{}.csv".format(threshold)
    
    map_raster = pm.getGfcDir() + aoi_name + '_glad_check.tif'.format(threshold)
    
    #skip if output already exist 
    if os.path.isfile(hist_file):
        print('stats already computed')
        return hist_file
    
    
    src = gdal.Open(map_raster)
    proj = osr.SpatialReference(wkt=src.GetProjection())
    bb = utils.get_bounding_box(assetId)
    _, resx, _, _, _, resy = src.GetGeoTransform()
    src = None
    
    hist = utils.pixelCount(map_raster)
              
    resx_proj = resx * 111321
    hist['area'] = utils.toHectar(hist['pixels'], resx_proj)
            
    #remove the 255 values         
    hist = hist[hist['code'] != 255.]
              
    legend = pm.getGladLabels()
    df = pd.merge(hist, pm.getGladLabels(), on='code')
              
    #remove no_data 
    df = df[df['code'] != 0]
    
    #add %
    total_area = df['area'].sum()
    df['percent'] = round(df['area']/total_area*100,2)

    df.columns = [
        "code",
        "pixels",
        "fnf_gfc_2000",
        "chg_gfc",
        "agree",
        "pixels",
        "area",
        "percent"
    ]
    
    df.to_csv(hist_file, index=False)
    
    return hist_file


