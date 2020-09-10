from utils import parameters as pm
from utils import utils
import os
import pandas as pd
from osgeo import osr, gdal
import ee
from bqplot import *
from bqplot import pyplot as plt
import ipyvuetify as v
from sepal_ui.scripts import utils as su
from utils import parameters as pm
from pathlib import Path
import subprocess
from pyproj import CRS

ee.Initialize()

def create_hist(map_raster, assetId, output):
    
    if not os.path.isfile(map_raster): 
        print('No gfc map')
        return None
    
    #project raster in world mollweide
    map_raster_proj = pm.getTmpDir() + Path(map_raster).stem + '_proj.tif'
    input_ = gdal.Open(map_raster)
    gdal.Warp(map_raster_proj, input_, dstSRS='ESRI:54009')
    
    #realize a primary hist
    hist = utils.pixelCount(map_raster_proj)
    
    src = gdal.Open(map_raster_proj)
    gt =src.GetGeoTransform()
    resx = gt[1]
    resy =gt[5]
    #src.close()
    
    #convert to hectars
    hist['area'] = utils.toHectar(hist['pixels'], abs(resx), abs(resy))
    
    #delete the tmp file 
    os.remove(map_raster_proj)
    
    return hist

def create_hist_ee(ee_map, assetId, output): 
    
    #construct the labels
    label = pm.getMyLabel()
    
    columns=['code', 'area_square_meters']
    row_list = []
    geom = ee.FeatureCollection(assetId).geometry()
    for index, code in enumerate(pm.getCodes()):
        su.displayIO(output, 'computing ' + label[index])
        code = int(code)
        mask = ee_map.eq(code)
        mask_surface = mask.multiply(ee.Image.pixelArea())
        stats = mask_surface.reduceRegion(**{
            'reducer': ee.Reducer.sum(),
            'geometry': geom,
            'maxPixels': 1e13
        });
        row_list.append([code, stats.getInfo()['gfc']])

    
    hist = pd.DataFrame(row_list, columns=columns)
    
    #create an hectares column
    hist['area'] = hist['area_square_meters']/10000
    
    #add the labels
    hist['class'] = label
    
    return hist

def plotLoss(df, aoi_name):
    
    d_hist = df[(df['code'] > 0) & (df['code'] < 30)]

    x_sc = LinearScale()
    y_sc = LinearScale()  
    
    ax_x = Axis(label='year', scale=x_sc)
    ax_y = Axis(label='tree cover loss surface (ha)', scale=y_sc, orientation='vertical') 
    bar = Bars(x=[i+2000 for i in d_hist['code']], y=d_hist['area'], scales={'x': x_sc, 'y': y_sc})
    title ='Distribution of tree cover loss per year in ' + aoi_name
    fig = Figure(
        title= title,
        marks=[bar], 
        axes=[ax_x, ax_y], 
        padding_x=0.025, 
        padding_y=0.025
    )
    
    return fig

def areaTable(df):
    #construct the total loss line
    df_loss = df[(df['code'] > 0 ) & (df['code'] < 30)] 
    df_loss = df_loss.sum()
    df_loss['code'] = 60
    df_loss['class'] = 'loss'
    df_masked = df.append(df_loss, ignore_index=True)
    
    #drop the loss_[year] lines
    df_masked = df_masked[df_masked['code'] >= 30] 
    
    #create the header
    headers = [
        {'text': 'Class', 'align': 'start', 'value': 'class'},
        {'text': 'Area (ha)', 'value': 'area' }
    ]
    
    items = [
        {'class':row['class'], 'area':'{}'.format(int(row['area']))} for index, row in df_masked.iterrows()
    ]
    
    table = v.DataTable(
        class_='ma-3',
        headers=headers,
        items=items,
        disable_filtering=True,
        disable_sort=True,
        hide_default_footer=True
    )
    
    return table
    
def compute_ee_map(assetId, threshold):
     
    #load the dataset and AOI
    dataset = ee.Image(pm.getDataset())
    aoi = ee.FeatureCollection(assetId)

    #clip the dataset on the aoi 
    clip_dataset = dataset.clip(aoi)
        
    #create a composite band based on the user threshold 

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