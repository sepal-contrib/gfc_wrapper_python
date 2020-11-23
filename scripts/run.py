from sepal_ui import mapping as sm
import time
import subprocess
import pandas as pd
from bqplot import *
from bqplot import pyplot as plt
import ipyvuetify as v
from sepal_ui import sepalwidgets as sw
import geemap
import ee
import matplotlib as mpl
import matplotlib.pyplot as plt
import shutil
import glob
import gdal
from osgeo import osr

from scripts import make_mspa_ready as mmr
from scripts import compute_areas as ca
from gfc_wrapper_python.utils import gdrive
from gfc_wrapper_python.utils import gee
from gfc_wrapper_python.utils import parameters as pm
from gfc_wrapper_python.utils import utils as gfc_utils
from distutils.dir_util import copy_tree


ee.Initialize()

def displayGfcMap(aoi_io, threshold, m, viz, output):
    
    output.add_live_msg('Loading tiles')
    
    #use aoi_name 
    aoi_name = aoi_io.get_aoi_name()
    
    #load the gfc map
    gfc_map = ca.compute_ee_map(aoi_io, threshold)
    
    #load the aoi 
    aoi = aoi_io.get_aoi_ee()
    
    if not viz:
        #Create an empty image into which to paint the features, cast to byte.
        empty = ee.Image().byte()
        #Paint all the polygon edges with the same number and width, display.
        outline = empty.paint(**{
            'featureCollection': aoi,
            'color': 1,
            'width': 3
        })
        m.addLayer(outline, {'palette': '283593'}, 'aoi')
        
        #zoom on the aoi
        m.zoom_ee_object(aoi.geometry())
        
        #empty all the previous gfc masks 
        for i in range (100):
            layer = m.find_layer(f'gfc_{i+1}')
            if layer:
                m.remove_layer(layer)
    
    #add the values to the map
    layer_name = f'gfc_{threshold}'
    if not m.find_layer(layer_name):
        m.addLayer(gfc_map.sldStyle(pm.getSldStyle()), {}, layer_name)
        message = 'Tiles loaded'
    else:
        message = "Tiles were already on the map"
        
    
    output.add_live_msg(message, 'success')
    
    return
     
def displayGfcHist(aoi_io, threshold, output):
    
    
    ###############################
    ##   reload the tiles        ##
    ###############################
    
    output.add_live_msg('Loading tiles')
    
    #use aoi_name 
    aoi_name = aoi_io.get_aoi_name()
    
    #load the gfc map
    gfc_map = ca.compute_ee_map(aoi_io, threshold)
    
    
    output.add_live_msg('Tiles loaded', 'success')
    
    
    ##########################
    ##     compute hist     ##
    ##########################
    
    output.add_live_msg('Compute areas')
    
    #load the df
    df = ca.create_hist_ee(gfc_map, aoi_io, output)
    
    #create an histogram of the losses
    fig = ca.plotLoss(df, aoi_name)
    
    #add table of areas
    table = ca.areaTable(df)
    
    #create the partial layout 
    partial_layout = v.Flex(
        xs12=True,
        class_='pa-0 mt-5', 
        children=[
            table, 
            fig
        ]
    )
         
    output.add_live_msg('Areas computation finished', 'success')
    
    return partial_layout

def gfcExport(aoi_io, threshold, output):
    
    #use aoi_name
    aoi_name = aoi_io.get_aoi_name()
    
    #load the map 
    aoi = aoi_io.get_aoi_ee()
    gfc_map = ca.compute_ee_map(aoi_io, threshold)
    
    
    ############################
    ###    create tif file   ###
    ############################
    
    #skip if output already exist 
    output.add_live_msg('Creating the map')
    clip_map = f'{pm.getGfcDir()}{aoi_name}_{threshold}_merged_gfc_map.tif'
    clip_legend = f'{pm.getGfcDir()}{aoi_name}_{threshold}_gfc_legend.pdf'
    
    if os.path.isfile(clip_map):
        output.add_live_msg('Gfc map threshold already performed', 'success')
    else:
        task_name = f'{aoi_name}_{threshold}_gfc_map'
        
        #launch the gee task
        drive_handler = gdrive.gdrive()
        if drive_handler.get_files(task_name) == []:
            #launch the exportation of the map
            task_config = {
                'image':gfc_map,
                'description':task_name,
                'scale': 30,
                'region':aoi.geometry(),
                'maxPixels': 1e12
            }
    
            task = ee.batch.Export.image.toDrive(**task_config)
            task.start()
            
            #wait for the task 
            gee.wait_for_completion(task_name, output)
            
            
        output.add_live_msg('start downloading to Sepal')
        
        #download to sepal
        files = drive_handler.get_files(task_name)
        drive_handler.download_files(files, pm.getGfcDir())
        
        #merge the tiles together 
        #create command
        tmp_clip_map = f'{pm.getGfcDir()}{aoi_name}_{threshold}_tmp_merged_gfc_map.tif'
        file_pattern = f'{pm.getGfcDir()}{task_name}*.tif'
        command = [
            'gdal_merge.py',
            '-o', tmp_clip_map,
            '-v', '-co', '"COMPRESS=LZW"',
        ]
        command += glob.glob(file_pattern)
        os.system(' '.join(command))
        
        #add the color_palette
        tmp_pct_clip_map = f'{pm.getGfcDir()}{aoi_name}_{threshold}_tmp_pct.tif'
        color_table = pm.getColorTable()
        command = [
            '(echo {})'.format(color_table),
            '|',
            'oft-addpct.py',
            tmp_clip_map,
            tmp_pct_clip_map
        ]
        os.system(' '.join(command))
        os.remove(color_table)
        os.remove(tmp_clip_map)
        
        #create the legend 
        ca.export_legend(clip_legend)
        
        #compress
        gdal.Translate(clip_map, tmp_pct_clip_map, creationOptions=['COMPRESS=LZW'])
        os.remove(tmp_pct_clip_map)
        
        #delete the tmp_files
        for file in glob.glob(file_pattern):
            os.remove(file)
            
    output.add_live_msg('Downloaded to Sepal', 'success')
    
    
    output.add_live_msg('Create histogram')
    
    ############################
    ###    create txt file   ###
    ############################
    
    csv_file = f'{pm.getStatDir()}{aoi_name}_{threshold}_gfc_stat.csv'
    hist = ca.create_hist(clip_map, output)
    
    if os.path.isfile(csv_file):
        output.add_live_msg('histogram already created', 'success')
    else:
        hist.to_csv(csv_file, index=False)
        output.add_live_msg('Histogram created', 'success')
        
    #################################
    ###    create sum-up layout   ###
    #################################
    
    fig = ca.plotLoss(hist, aoi_name)
    
    table = ca.areaTable(hist)
    
    m = sm.SepalMap()
    m.add_legend(legend_keys=pm.getMyLabel(), legend_colors=pm.getColorPalette(), position='topleft')
    m.zoom_ee_object(aoi.geometry())
    m.addLayer(gfc_map.sldStyle(pm.getSldStyle()), {}, 'gfc')
    outline = ee.Image().byte().paint(featureCollection=aoi, color=1, width=3)
    m.addLayer(outline, {'palette': '283593'}, 'aoi')
    
    #create the partial layout 
    partial_layout = v.Layout(
        Row=True,
        align_center=True,
        class_='pa-0 mt-5', 
        children=[
            v.Flex(xs12=True, md6=True, class_='pa-0', children=[table, fig]),
            v.Flex(xs12=True, md6=True, class_='pa-0', children=[m])
        ]
    )
    
    #create the links
    gfc_download_csv = sw.DownloadBtn('GFC hist values in .csv', path=csv_file)
    gfc_download_tif = sw.DownloadBtn('GFC raster in .tif', path=clip_map)
    gfc_download_pdf = sw.DownloadBtn('GFC legend in .pdf', path=clip_legend)
    
    #create the display
    children = [ 
        v.Layout(Row=True, children=[
            gfc_download_csv,
            gfc_download_tif,
            gfc_download_pdf
        ]),
        partial_layout
    ]
         
    output.add_live_msg('Export complete', 'success')
    

    return (clip_map, csv_file, children)

def mspaAnalysis(
    clip_map, 
    aoi_io, 
    threshold, 
    foreground_connectivity, 
    edge_width, 
    transition_core, 
    separate_feature, 
    statistics,
    output
):
    
    #aoi name
    aoi_name = aoi_io.get_aoi_name()
    
    #link the parameters
    mspa_param = [
        str(foreground_connectivity), 
        str(edge_width),
        str(int(transition_core)), 
        str(int(separate_feature)), 
        str(int(statistics))
    ]
    
    #remove the stats parameter for naming 
    mspa_param_name = '_'.join(mspa_param[:-1])
    
    output.add_live_msg(f'Run mspa with "{"_".join(mspa_param)}" inputs')
    
    #check if file already exist
    mspa_map_proj = f'{pm.getGfcDir()}{aoi_name}_{threshold}_{mspa_param_name}_mspa_map.tif'
    mspa_stat = f'{pm.getStatDir()}{aoi_name}_{threshold}_{mspa_param_name}_mspa_stat.txt'
    mspa_legend = f'{pm.getGfcDir()}{aoi_name}_{threshold}_{mspa_param_name}_mspa_legend.pdf'
    
    if os.path.isfile(mspa_map_proj):
        output.add_live_msg('Mspa map already ready', 'success')
    else:
        #convert to bin_map
        bin_map = mmr.make_mspa_ready(aoi_io.get_aoi_name(), threshold, clip_map)
    
        #copy the script folder in tmp 
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
        
        #change mspa mod 
        command = ['chmod', '755', pm.getTmpMspaDir() + 'mspa_lin64']
        os.system(' '.join(command))
    
        #launch the process
        command = ['bash', 'sepal_mspa']
        kwargs = {
            'args' : command,
            'cwd' : pm.getTmpMspaDir(),
            'stdout' : subprocess.PIPE,
            'stderr' : subprocess.PIPE,
            'universal_newlines' : True
        }
        with subprocess.Popen(**kwargs) as p:
            for line in p.stdout:
                output.add_live_msg(line)
    
        #copy result tif file in gfc 
        mspa_tmp_map = f'{mspa_output_dir}input_{mspa_param_name}.tif'
        mspa_map = f'{pm.getGfcDir()}{aoi_name}_{threshold}_{mspa_param_name}_mspa_map_tmp.tif'
    
        shutil.copyfile(mspa_tmp_map, mspa_map)
    
        #compress map (the dst_nodata has been added to avoid lateral bands when projecting as 0 is not the mspa no-data value)
        gdal.Warp(mspa_map_proj, mspa_map, creationOptions=['COMPRESS=LZW'], dstSRS='EPSG:4326', dstNodata=129)
        os.remove(mspa_map)
    
        #copy result txt file in gfc
        mspa_tmp_stat = f'{mspa_output_dir}input_{mspa_param_name}_stat.txt'
        shutil.copyfile(mspa_tmp_stat, mspa_stat)
        
        output.add_live_msg('Mspa map complete', 'success') 
        
        ###################### end of mspa process
    
    #flush tmp directory
    shutil.rmtree(pm.getTmpDir()) 
    
    #create the output 
    table = mmr.getTable(mspa_stat)
    fragmentation_map = mmr.fragmentationMap(mspa_map_proj, aoi_io, output)
    mmr.export_legend(mspa_legend)
    
    ######################################
    #####     create the layout        ###
    ######################################
    
    #create the links
    gfc_download_txt = sw.DownloadBtn('MSPA stats in .txt', path=mspa_stat)
    gfc_download_tif = sw.DownloadBtn('MSPA raster in .tif', path=mspa_map_proj)
    gfc_download_pdf = sw.DownloadBtn('MSPA legend in .pdf', path=mspa_legend)
    
    #create the partial layout 
    partial_layout = v.Layout(
        Row=True,
        align_center=True,
        class_='pa-0 mt-5', 
        children=[
            v.Flex(xs12=True, md4=True, class_='pa-0', children=[table]),
            v.Flex(xs12=True, md8=True, class_='pa-0', children=[fragmentation_map])
        ]
    )
    
    #create the display
    children = [ 
        v.Layout(Row=True, children=[
            gfc_download_txt,
            gfc_download_tif,
            gfc_download_pdf
        ]),
        partial_layout
    ]
    
    
    return children
    