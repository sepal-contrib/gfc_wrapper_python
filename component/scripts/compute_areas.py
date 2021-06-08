import os 
if 'GDAL_DATA' in list(os.environ.keys()): del os.environ['GDAL_DATA']
if 'PROJ_LIB' in list(os.environ.keys()): del os.environ['PROJ_LIB']

from distutils.version import LooseVersion

import rasterio as rio
from rasterio.crs import CRS as RioCRS
from pyproj.crs import CRS
from pyproj.enums import WktVersion
from rasterio.warp import calculate_default_transform, reproject, Resampling
from matplotlib import pyplot as plt
from matplotlib.colors import to_rgba
import ee
from bqplot import *
import ipyvuetify as v

from component import parameter as cp

from .utils import pixel_count, to_hectar

ee.Initialize()

def create_hist(result_dir, map_raster, alert):
    
    if not map_raster.is_file(): 
        raise Exception('No gfc map')
    
    # project raster in world mollweide
    with rio.open(map_raster) as src:
        
        proj_crs = CRS.from_string('ESRI:54009')
        if LooseVersion(rio.__gdal_version__) < LooseVersion("3.0.0"):
            rio_crs = RioCRS.from_wkt(proj_crs.to_wkt(WktVersion.WKT1_GDAL))
        else:
            rio_crs = RioCRS.from_wkt(proj_crs.to_wkt())
        
        transform, width, height = calculate_default_transform(src.crs, rio_crs, src.width, src.height, *src.bounds)
    
        kwargs = src.meta.copy()
    
        kwargs.update({
            'crs': rio_crs,
            'transform': transform,
            'width': width,
            'height': height
        })
    
        map_raster_proj = result_dir/f'{map_raster.stem}_proj.tif'
        
        with rio.open(map_raster_proj, 'w', **kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(
                    source=rio.band(src, i),
                    destination=rio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=rio_crs,
                    resampling=Resampling.nearest
                )
                
            resx, resy = dst.res
    
    # realize a primary hist
    hist = pixel_count(map_raster_proj)
    
    # convert to hectars
    hist['area'] = to_hectar(hist['pixels'], abs(resx), abs(resy))
    
    return hist

def plot_loss(df, aoi_name):
    
    d_hist = df[(df['code'] > 0) & (df['code'] < 30)]

    x_sc = LinearScale()
    y_sc = LinearScale()  
    
    ax_x = Axis(label = 'year', scale = x_sc)
    ax_y = Axis(label = 'tree cover loss surface (ha)', scale = y_sc, orientation = 'vertical') 
    bar = Bars(x = [i + 2000 for i in d_hist['code']], y = d_hist['area'], scales = {'x': x_sc, 'y': y_sc})
    title = f'Distribution of tree cover loss per year in {aoi_name}'
    fig = Figure(
        title     = title,
        marks     = [bar], 
        axes      = [ax_x, ax_y], 
        padding_x = 0.025, 
        padding_y = 0.025
    )
    
    return fig

def area_table(df):
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
        {'class':row['class'], 'area':f'{int(row.area)}'} for index, row in df_masked.iterrows()
    ]
    
    table = v.DataTable(
        class_             = 'ma-3',
        headers            = headers,
        items              = items,
        disable_filtering  = True,
        disable_sort       = True,
        hide_default_footer= True
    )
    
    return table
    
def compute_ee_map(aoi_model, threshold):
     
    # load the dataset and AOI
    dataset = ee.Image(cp.gfc_dataset)
    aoi = aoi_model.feature_collection

    #clip the dataset on the aoi 
    clip_dataset = dataset.clip(aoi)
        
    # create a composite band based on the user threshold 
    calc = "gfc = (A<={0})*((C==1)*50 + (C==0)*30) + " # Non forest 
    calc += "(A>{0})*(C==1)*(B>0)*51 + "         # gain + loss 
    calc += "(A>{0})*(C==1)*(B==0)*50 + "        # gain 
    calc += "(A>{0})*(C==0)*(B>0)*B + "          # loss
    calc += "(A>{0})*(C==0)*(B==0)*40"           # stable forest

    calc = calc.format(threshold)
    
    bands = {
        'A': clip_dataset.select('treecover2000'),
        'B': clip_dataset.select('lossyear').unmask(0), # be carefull the 0 values are now masked
        'C': clip_dataset.select('gain'),
    }
    
    gfc = clip_dataset.expression(calc, bands)
    
    return gfc.select('gfc').uint8()

def export_legend(filename):
    
    #create a color list
    color_map = []
    for index in cp.gfc_colors: 
        color_map.append([val for val in list(cp.gfc_colors[index])])

    columns = ['entry']
    rows = [' '*10 for index in cp.gfc_colors] #trick to see the first column
    cell_text = [[index] for index in cp.gfc_colors]

    fig, ax = plt.subplots(1,1, figsize=[6.4, 8.6])

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