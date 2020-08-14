from utils import parameters as pm
from utils import utils
import os
from bqplot import *
import ipywidgets as widgets
from sepal_ui.scripts import utils as su 
import ipyvuetify as v
import gdal

def make_mspa_ready(assetId, threshold, clip_map):
    
    aoi_name = utils.get_aoi_name(assetId)
    
    #skip if output already exist 
    mspa_masked_map = pm.getGfcDir() + aoi_name + '_{}_mspa_masked_map.tif'.format(threshold)
    
    if os.path.isfile(mspa_masked_map):
        print('mspa masked map already ready')
        return mspa_masked_map
    
    #create the forest mask for MSPA analysis
    calc = '((A>0)*(A<40)+(A>40))*1' #non_forest <=> A != 40
    calc += '+ (A==40)*2' #forest
    
    mspa_masked_tmp_map = pm.getGfcDir() + aoi_name + '_{}_mspa_tmp_map.tif'.format(threshold)
    
    command = [
        'gdal_calc.py',
        '-A', clip_map,
        '--co', '"COMPRESS=LZW"',
        '--outfile={}'.format(mspa_masked_tmp_map),
        '--calc="{}"'.format(calc),
        '--type="Byte"'
    ]
    
    os.system(' '.join(command))
    
    #compress
    gdal.Translate(mspa_masked_map, mspa_masked_tmp_map, creationOptions=['COMPRESS=LZW'])
    os.remove(mspa_masked_tmp_map)
    
    return mspa_masked_map

def fragmentationMap(path, output):
    # TODO before I found how to display tif as interactive maps I use a simple ipywidget
    su.displayIO(output, 'Displaying results') 
    with open(path, 'rb') as f:
        raw_image = f.read()
    su.displayIO(output, 'Image read')
    su.displayIO(output, 'Creating the widget')
    ipyimage = widgets.Image(value=raw_image, format='tif')
    
    su.displayIO(output, 'Mspa process complete', 'success')
    
    return ipyimage

def getTable(stat_file):
    
    list_ = ['Core', 'Islet', 'Perforation', 'Edge', 'Loop', 'Bridge', 'Branch']
    
    #create the header
    headers = [
        {'text': 'MSPA-class', 'align': 'start', 'value': 'class'},
        {'text': 'Proportion (%)', 'value': 'prop' }
    ]
    
    #open and read the file 
    with open(stat_file, "r") as f:
        text = f.read()
     
    #split lines
    text = text.split('\n')
    
    #identify values of interes and creat the item array 
    items = []
    for value in list_:
        for line in text:
            if line.startswith(value):
                val = '{:.2f}'.format(float(line.split(':')[1][:-2]))
                items.append({'class':value, 'prop':val})
    
    
    table = v.DataTable(
        class_='ma-3',
        headers=headers,
        items=items,
        disable_filtering=True,
        disable_sort=True,
        hide_default_footer=True
    )
    
    return table
    


