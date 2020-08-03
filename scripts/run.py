from sepal_ui.scripts import utils as su
from sepal_ui.scripts import mapping as sm
import time
import pandas as pd
from bqplot import *
from bqplot import pyplot as plt
import ipyvuetify as v
from sepal_ui import widgetFactory as wf
import geemap
import ee 
import earthpy.plot as ep
import matplotlib as mpl
import matplotlib.pyplot as plt
import rasterio as rio
import gdal
from osgeo import osr
import shutil

from scripts import make_aoi_shp as mas
from scripts import download_merge_glad as dmg
from scripts import make_map_threshold as mmt
from scripts import make_mspa_ready as mmr
from scripts import compute_areas as ca
from gfc_wrapper_python.utils import parameters as pm
from gfc_wrapper_python.utils import utils as gfc_utils
from distutils.dir_util import copy_tree

ee.Initialize()

def gfc_analysis(asset, threshold, output):
    
    #use aoi_name 
    aoi_name = gfc_utils.get_aoi_name(asset)
    
    #create a shapefile for the
    su.displayIO(output, 'Create aoi shapefile')
    time.sleep(2)
    mas.make_aoi_shp(asset)
    su.displayIO(output, 'Aoi shapefile created', alert_type='success')
    time.sleep(2)
    
    #load the Hansen_GFC-2019-v1.7
    su.displayIO(output, 'Download gfc data')
    time.sleep(2)
    types = pm.getTypes()
    prefix = "https://storage.googleapis.com/earthenginepartners-hansen/GFC-2019-v1.7/Hansen_GFC-2019-v1.7_"
    for type in types:
        pattern = prefix + type + "_{0}_{1}.tif"
        name = aoi_name+'_' + type
        dmg.download_merge(asset, pattern, name)
    su.displayIO(output, 'Gfc data downloaded', alert_type='success')
    time.sleep(2)
    
    #make the threshold map
    su.displayIO(output, 'Make threshold map')
    time.sleep(2)
    clip_map = mmt.make_map_threshold(asset, threshold)
    su.displayIO(output, 'Threshold map downloaded', alert_type='success')
    time.sleep(2)
    
    #compute the area values 
    su.displayIO(output, 'Compute areas values')
    time.sleep(2)
    csv_file = ca.compute_areas(asset, threshold)
    su.displayIO(output, 'Area computed', alert_type='success')
    time.sleep(2)
    
    #tell the user the computation is finished 
    su.displayIO(output, 'Process completed', alert_type='success')
    
    return (clip_map, csv_file)

def displayGfcResults(clip_map, csv_file, assetId):
    
    #use aoi_name 
    aoi_name = gfc_utils.get_aoi_name(assetId)
    
    #create an histogram of the losses 
    
    df = pd.read_csv(csv_file)
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
    
    #add table of areas
    df_loss = df[(df['code'] > 0 ) & (df['code'] < 30)] #construct the total loss line
    df_loss = df_loss.sum()
    df_loss['code'] = 60
    df_loss['class'] = 'loss'
    
    df_masked = df.append(df_loss, ignore_index=True)
    df_masked = df_masked[df_masked['code'] >= 30] #drop the loss_[year] lines
     
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
    #create a map to display the tif files

    #wait for an answer on SO
    m = geemap.Map()
    m.clear_layers()
    m.clear_controls()
    m.add_basemap('CartoDB.Positron')
    m.add_control(geemap.ZoomControl(position='topright'))
    m.add_control(geemap.LayersControl(position='topright'))
    m.add_control(geemap.AttributionControl(position='bottomleft'))
    m.add_control(geemap.ScaleControl(position='bottomleft', imperial=False))
    m.centerObject(ee.FeatureCollection(assetId), zoom=sm.update_zoom(assetId))
    
    #wait for bug correction on github/geemap
    #m.add_raster(clip_map, bands=[0], colormap='terrain', layer_name='gfc')
       
    aoi = ee.FeatureCollection(assetId)
    
    #Create an empty image into which to paint the features, cast to byte.
    empty = ee.Image().byte()
    #Paint all the polygon edges with the same number and width, display.
    outline = empty.paint(**{
        'featureCollection': aoi,
        'color': 1,
        'width': 3
    })
    m.addLayer(outline, {'palette': '283593'}, 'aoi')
    
    
    #create the partial layout 
    partial_layout = v.Layout(
        Row=True,
        xs12=True, 
        align_center=True,
        class_='pa-0 mt-5', 
        children=[
            v.Flex(xs12=True, lg6=True, class_='pa-0', children=[table, fig]),
            v.Flex(xs12=True, lg6=True, class_='pa-0', children=[m])
        ]
    )
    
    #create the links
    gfc_download_csv = wf.DownloadBtn('GFC hist values in .csv', path=csv_file)
    gfc_download_tif = wf.DownloadBtn('GFC raster in .tif', path=clip_map)
    
    
    #create the display
    children = [ 
        v.Layout(Row=True, xs12=True, children=[
            gfc_download_csv,
            gfc_download_tif,
        ]),
        partial_layout
    ]
         
    
    return children

def mspaAnalysis(
    clip_map, 
    assetId, 
    threshold, 
    foreground_connectivity, 
    edge_width, 
    transition_core, 
    separate_feature, 
    statistics,
    output
):
    
    #aoi name
    aoi_name = gfc_utils.get_aoi_name(assetId)
    
    #link the parameters
    mspa_param = [
        str(foreground_connectivity), 
        str(edge_width),
        str(transition_core), 
        str(separate_feature), 
        str(statistics)
    ]
    
    su.displayIO(output, 'Run mspa with "{}" inputs'.format('_'.join(mspa_param)))
    
    #check if file already exist
    mspa_map_proj = pm.getGfcDir() + aoi_name + '{}_{}_mspa_map.tif'.format(
        threshold, 
        '_'.join(mspa_param)
    )
    
    if os.path.isfile(mspa_map_proj):
        su.displayIO(output, 'mspa masked map already ready', alert_type='success')
        return mspa_map_proj
    
    #convert to bin_map
    bin_map = mmr.make_mspa_ready(assetId, threshold, clip_map)
    
    #get the init file proj system 
    src = gdal.Open(clip_map)
    proj = osr.SpatialReference(wkt=src.GetProjection())
    src = None
    
    #copy the script files in tmp 
    copy_tree(pm.getMspaDir(), pm.getTmpMspaDir())
    
    #create the 3 new tmp dir
    mspa_input_dir = pm.create_folder(pm.getTmpMspaDir() + 'input') + '/'
    mspa_output_dir = pm.create_folder(pm.getTmpMspaDir() + 'output') + '/'
    mspa_tmp_dir = pm.create_folder(pm.getTmpMspaDir() + 'tmp') + '/' 
    
    #copy the bin_map to input_dir
    bin_tmp_map = mspa_input_dir + 'input.tif'
    shutil.copyfile(bin_map, bin_tmp_map)
    
    #create the parameter file     
    str_ = ' '.join(mspa_param)
    with open(mspa_input_dir + 'mspa-parameters.txt',"w+") as file:
        file.write(' '.join(mspa_param))
        file.close()
        
    #launch the process 
    command = [
        'chmod', '755',
        pm.getTmpMspaDir() + 'mspa_lin64'
    ]
    os.system(' '.join(command))
    print(' '.join(command))
    
    return
    
    #copy result files in gfc
    mspa_tmp_stat = mspa_output_dir + 'input_' + '_'.join(mspa_param) + '_stat.txt'
    mspa_stat = pm.getStatDir() + aoi_name + '{}_{}_mspa_stat.txt'.format(
        threshold, 
        '_'.join(mspa_param)
    )
    shutil.copyfile(mspa_tmp_stat, mspa_stat)
    
    mspa_tmp_map = mspa_output_dir + 'input_' + '_'.join(mspa_param) + '.tif'
    mspa_map = pm.getGfcDir() + aoi_name + '{}_{}_mspa_map_tmp.tif'.format(
        threshold, 
        '_'.join(mspa_param)
    )
    shutil.copyfile(mspa_tmp_map, mspa_map)
    
    #add projection
    options = gdal.TranslateOptions(outputSRS=proj)
    gdal.Translate(mspa_map_proj, mspa_map, options=options)
    
    #flush tmp directory
    shutil.rmtree(pm.getTmpDir())
    
    return mspa_map_proj
    