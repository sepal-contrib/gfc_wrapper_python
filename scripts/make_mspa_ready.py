import os

import ee 
from matplotlib.colors import ListedColormap, to_hex, to_rgba
from matplotlib import pyplot as plt
import numpy as np
import rasterio as rio
from bqplot import *
import ipyvuetify as v
from sepal_ui import mapping as sm

from utils import parameters as pm
from utils import utils

ee.Initialize()

def make_mspa_ready(aoi_name, threshold, clip_map):
    
    #skip if output already exist 
    mspa_masked_map = f'{pm.getGfcDir()}{aoi_name}_{threshold}_mspa_masked_map.tif'
    
    if not os.path.isfile(mspa_masked_map):
    
        #create the forest mask for MSPA analysis
        with rio.open(clip_map) as src:
        
            out_meta = src.meta.copy()
            out_meta.update(dtype=np.uint8)
            raw_data = src.read()
        
            data = (
                ((raw_data > 0) * (raw_data < 40) + (raw_data > 40)) * 1 # non_forest <=> A != 40
                + (raw_data == 40) * 2 # forest
                + raw_data * 0
            )                
            data = data.astype(out_meta['dtype'])
                
            with rio.open(mspa_masked_map, 'w', **out_meta) as dest:
                dest.write(data)
    
    return mspa_masked_map

def fragmentationMap(raster, aoi_io, output):
    
    output.add_live_msg('Displaying results')
    
    map_ = sm.SepalMap()

    #read the raster file
    with rio.open(raster) as src:
        data = src.read()
        
        min_ = int(np.amin(data[0]))
        max_ = int(np.amax(data[0]))
        ct = src.colormap(1)
        
        
    color_map = []
    for i in range(min_, max_):
        if list(ct[i]) == pm.mspa_colors['no-data']:
            color_map.append([.0, .0, .0, .0])
        else:
            color_map.append([val/255 for val in list(ct[i])])

    color_map = ListedColormap(color_map, N=max_)

    #display a raster on the map
    map_.add_raster(raster, colormap=color_map, layer_name='framgmentation map');

    #add a legend 
    legend_keys = [index for index in pm.mspa_colors]
    legend_colors = [to_hex([val/255 for val in pm.mspa_colors[index]]) for index in pm.mspa_colors] 
    map_.add_legend(legend_keys=legend_keys, legend_colors=legend_colors, position='topleft')
    
    #Create an empty image into which to paint the features, cast to byte.
    aoi = aoi_io.get_aoi_ee()
    empty = ee.Image().byte()
    outline = empty.paint(**{'featureCollection': aoi, 'color': 1, 'width': 3})
    map_.addLayer(outline, {'palette': '283593'}, 'aoi')
    map_.zoom_ee_object(aoi.geometry())
    
    output.add_live_msg('Mspa process complete', 'success')
    
    return map_

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
    
def export_legend(filename):
    
    #create a color list
    color_map = []
    for index in pm.mspa_colors: 
        color_map.append([val/255 for val in list(pm.mspa_colors[index])])

    columns = ['entry']
    rows = [' '*10 for index in pm.mspa_colors] #trick to see the first column
    cell_text = [[index] for index in pm.mspa_colors]

    fig, ax = plt.subplots(1,1)

    #remove the graph box
    ax.axis('tight')
    ax.axis('off')

    #set the tab title
    ax.set_title('Raster legend')

    #create the table
    the_table = ax.table(
        colColours = [to_rgba('lightgrey')],
        cellText   = cell_text,
        rowLabels  = rows,
        colWidths  = [.4],
        rowColours = color_map,
        colLabels  = columns,
        loc        = 'center'
    )
    the_table.scale(1, 1.5)

    #save &close
    plt.savefig(filename)
    plt.close()
    
    return

