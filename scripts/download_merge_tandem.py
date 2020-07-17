import ee
import geemap
import shapely.geometry as sg
import requests
import os
import subprocess
import glob
from threading import Thread
import time
import zipfile
import shutil
import sys
sys.path.append("..") # Adds higher directory to python modules path
from utils import utils

ee.Initialize()

def get_download_url(latlng, home_path):

    latlng = [int(latlng[0]), int(latlng[1])]
    if latlng[0] < 0:
        lat = "S{:02d}".format(abs(latlng[0]))
    else:
        lat = "N{:02d}".format(abs(latlng[0]))
                               
    if latlng[1] < 0:
        lng = "W{:03d}".format(abs(latlng[1]))
    else:
        lng = "E{:03d}".format(abs(latlng[1]))
        
    #get the folder 
    lng_folder = lat + '/' + lng.replace(lng[-1], '0') + '/'
    
    return home_path + lng_folder + "TDM_FNF_20_{0}{1}.zip".format(lat, lng)

def build_vrt(filename, merged_map, bb):
    """ merge into a single vrt files
    
    Args:
        filename (str): filename pattern of the Tif to merge
        merged_map (str): output filename
        bb (dic): the bounding box of the aoi
        
    Returns:
        process.stdout (str): output of the process
    """
    #cwd = os.path.join(os.path.expanduser('~'), 'tmp')
    
    
    #create command
    command = [
        'gdalbuildvrt',
        '-te', bb['minx'], bb['miny'], bb['maxx'], bb['maxy'],
        merged_map,
        filename
    ]
    
    #launch in os.system because it doesn't work in subprocess
    return os.system(" ".join(command))

def translate(vrt_tile, tif_tile, bb):
    """ translate into a single tif files
    
    Args:
        vrt_tile (str): filename pattern of the vrt to trnaslate
        tif_tile (str): output filename
        bb (dic): the bounding box of the aoi
        
    Returns:
        process.stdout (str): output of the process
    """
    
    #create command
    command = [
        'gdal_translate',
        '-ot', 'Byte',
        '-projwin', bb['minx'], bb['maxy'], bb['maxx'], bb['miny'],
        '-co', 'COMPRESS=LZW',
        vrt_tile,
        tif_tile
    ]
    
    #launch in os.system because it doesn't work in subprocess
    return os.system(" ".join(command))

def download_merge(aoiId, pathname, result_folder, filename):
    """
       retreive data that are tiled and refereced by there NW corner
       
    Args: 
        aoiId (ee.asset) the assetId that will be used to create the tiles
        pathname (str): the paterns of the tiling server {0} being the lat and {1} the lng
        result_folder (str): the result foder where to store everything
        filename (str): the name of the created tile
    """
    
    tiles = []
    #create the list of tiles 
    for lng in range(-180, 180, 1):
        for lat in range(-79, 100, 1):
            lon_point_list = [lng, lng+1, lng+1, lng]
            lat_point_list = [lat, lat, lat-1, lat-1]
            
            polygon = sg.Polygon(zip(lon_point_list, lat_point_list))
            tiles.append(polygon)
        
    ##load the asset
    aoi = ee.FeatureCollection(aoiId)
    aoiJson = geemap.ee_to_geojson(aoi)

    #find the intersections  
    aoiShp = sg.shape(aoiJson['features'][0]['geometry']).convex_hull
    
    #compute bounding box
    bb = utils.get_bounding_box(aoiId)
    

    tiles_country = []
    for tile in tiles:
        if (tile.intersects(aoiShp)):
            tiles_country.append(tile)

    #create the corresonding download urls
    urls=[]
    for tile in tiles_country:
        b = tile.bounds
        # Find the NW corner 
        corner = [b[3], b[0]]
        urls.append(get_download_url(corner, pathname))
    
    #retrieve the tiles 
    for idx, url in enumerate(urls):
        file = url.split('/')[-1].replace('.zip', '.tiff')
        html = requests.get(url)
        with open(result_folder + filename + '_tile_{}.zip'.format(idx), 'wb') as r: 
            r.write(html.content)
            with zipfile.ZipFile(result_folder + filename + '_tile_{}.zip'.format(idx), 'r') as zip_ref:
                with zip_ref.open('FNF/'+file) as zf, open(result_folder + filename + '_tile_{}.tiff'.format(idx), 'wb') as f:
                    shutil.copyfileobj(zf, f)
        os.remove(result_folder + filename + '_tile_{}.zip'.format(idx))
        
    
    # merge the tiles in a tif tmp file
    tiles_name = result_folder + filename + '_tile_*.tiff'
    merged_vrt = result_folder + filename + '_tmp_tile.vrt'
    output = build_vrt(tiles_name, merged_vrt, bb)
    
    #convert into .tif file
    merged_map = result_folder + filename + '.tif'
    output = translate(merged_vrt, merged_map, bb)
    
    #detruire les fichier tmp
    for file in glob.glob(tiles_name):
        os.remove(file)
    os.remove(merged_vrt)
    
    
    return merged_map