from utils import parameters as pm
from utils import utils
import os
import pandas as pd
import gdal
from osgeo import osr
import ee
from bqplot import *
from bqplot import pyplot as plt
import ipyvuetify as v

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

def plotLoss(df, aoi_name):
    
    d_hist = df[(df['code'] > 0) & (df['code'] < 30)]

    x_sc = LinearScale()
    y_sc = LinearScale()  
    
    ax_x = Axis(label='year', scale=x_sc)
    ax_y = Axis(label='tree cover loss surface (ha)', scale=y_sc, orientation='vertical') 
    bar = Bars(x=[i+2000 for i in d_hist['code']], y=d_hist['area'], scales={'x': x_sc, 'y': y_sc})
    title ='Distribution of forest loss per year in ' + aoi_name
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
        {'class':row['class'], 'area':'{:.2f}'.format(row['area'])} for index, row in df_masked.iterrows()
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