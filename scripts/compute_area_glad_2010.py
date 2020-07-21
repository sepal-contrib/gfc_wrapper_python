from utils import parameters as pm
from utils import utils
import os
import pandas as pd

def compute_area_glad_2010(assetId, thershold):
    
    aoi_name = utils.get_aoi_name(assetId)
    
    hist_file = pm.getStatDir() + aoi_name + "_stats_{}.csv".format(threshold)
    
    map_raster = pm.getGfcDir() + aoi_name + 'glad_check_{}'.format(threshold)
    
    #skip if output already exist 
    if os.path.isfile(hist_file):
        return 'stats already computed'
    
    
    src = gdal.Open(map_raster)
    proj = osr.SpatialReference(wkt=src.GetProjection())
    bb = utils.get_bounding_box(assetID)
    res = {}
    _, res['x'], _, _, _, res['y']  = src.GetGeoTransform()
    src = None
    
    hist = utils.pixel_count(map_raster)
    hist['area'] = hist['pixels']*res['x']*res['x']/10000
    




    # add the legend (don't know where it come from)
    # df <- merge(hist,legend,by.x="code",by.y="code",all.x=T)
    
    #remove empty codes lines 
    #df.loc[(df!=0).any(axis=1)]
    #df[df.values.sum(axis=1) != 0] super fast
    df = df= df[df['code'] != 0]
    
    #add %
    total_area = df['area'].sum()
    df['percent'] = round(df['area']/total_area*100,2)

    df.columns = [
        "code",
        "fnf_gfc_2000",
        "chg_gfc",
        "agree",
        "pixels",
        "area",
        "percent"
    ]

    #debug
    #tapply(df$percent,df$agree,sum)
    
    filename = 'stt_dir,"stats_",countrycode,"_",threshold,".csv"'
    df.to_csv(filename)
    
    return 1


