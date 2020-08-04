from utils import parameters as pm
from utils import utils
import os
import pandas as pd
import gdal
from osgeo import osr
import ee 

ee.Initialize()

def create_hist(ee_map, assetId): 
    
    #define the pixel resolution
    res = 30

    hist = ee_map.reduceRegion(**{
      'reducer': ee.Reducer.autoHistogram(),
      'geometry': ee.FeatureCollection(assetId).geometry(),
      'scale': res,
      'maxPixels': 1e12
    })

    hist = pd.DataFrame(hist.getInfo()['gfc'])

    #add column name
    hist.columns= ['code', 'pixels'] 

    #dropping the useless lines (non user defined)
    hist = hist[hist['code'].isin(pm.getCodes())]

    #construct the surface values
    hist['area'] = hist['pixels']*res*res/10000

    #construct the labels
    label = pm.getMyLabel()
    label.pop(0) #remove the no-data label (it will be removed when it'll work)
    hist['class'] = label
    
    return hist
    
def compute_ee_map(assetId, threshold):
     
    #load the dataset and AOI
    dataset = ee.Image(pm.getDataset())
    aoi = ee.FeatureCollection(assetId)

    #clip the dataset on the aoi 
    clip_dataset = dataset.clip(aoi)
        
    #create a composite band bassed on the user threshold 

    calc = "gfc = (A<={0})*((C==1)*50 + (C==0)*30) + " #Non forest 
    calc += "(A>{0})*(C==1)*(B>0)*51 + "         #gain + loss 
    calc += "(A>{0})*(C==1)*(B==0)*50 + "        #gain                                             
    calc += "(A>{0})*(C==0)*(B>0)*B + "          #loss
    calc += "(A>{0})*(C==0)*(B==0)*40"           #stable forest

    calc = calc.format(threshold)
    
    bands = {
        'A': clip_dataset.select('treecover2000'),
        'B': clip_dataset.select('lossyear').unmask(0), #be carefull the 0 values are now masked
        'C': clip_dataset.select('gain'),
    }
    
    gfc = clip_dataset.expression(calc,bands)
    
    return gfc.select('gfc')