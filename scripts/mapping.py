import geemap
import ee 
from math import cos, asin, sqrt, pi
import numpy as np
from haversine import haversine

#initialize earth engine
ee.Initialize()

def init_map():
    '''Initialize a map centered on the point [0,0] with zoom at 1
    
    Returns:
        dc (DrawControl): a draw control for polygon drawing 
        m (Map): a map
    '''
    center = [0, 0]
    zoom = 2

    dc = geemap.DrawControl(
        marker={},
        circlemarker={},
        polyline={},
        rectangle={'shapeOptions': {'color': '#0000FF'}},
        circle={'shapeOptions': {'color': '#0000FF'}},
        polygon={'shapeOptions': {'color': '#0000FF'}},
     )

    m = geemap.Map(center=center, zoom=zoom)
    m.clear_layers()
    m.clear_controls()
    m.add_basemap('Esri Satellite')
    m.add_basemap('CartoDB.Positron')
    m.add_control(geemap.ZoomControl(position='topright'))
    m.add_control(geemap.LayersControl(position='topright'))
    m.add_control(geemap.AttributionControl(position='bottomleft'))
    m.add_control(geemap.ScaleControl(position='bottomleft', imperial=False))
    
    return (dc, m)

def update_map(m, dc, asset_name):
    """Update the map with the asset overlay and by removing the selected drawing controls
    
    Args:
        m (Map): a map
        dc (DrawControl): the drawcontrol to be removed
        asset_name (str): the asset ID in gee assets
    """  
    m.centerObject(ee.FeatureCollection(asset_name), zoom=update_zoom(asset_name))
    m.addLayer(ee.FeatureCollection(asset_name), {'color': 'green'}, name='aoi')
    dc.clear()
    try:
        m.remove_control(dc)
    except:
        pass
    
def update_zoom(asset_id):
    """search for the dimension of the AOI and adapt the map zoom acordingly
    
    Args: 
        asset_id (str): the assetID
    
    Returns: 
        zoom (int): the zoom value riquired
    """
    
    #retreive the asset 
    geom = ee.FeatureCollection(asset_id).geometry()
    coordinates = geom.getInfo()["coordinates"]
    #transform into a single list of all the coordinates
    shape = []
    get_coords(coordinates, shape)
    #in the coordinates search for the 4 cardinal points of the aoi
    #gee format coords [lng, lat]
    count = 0 
    for coords in shape: #perimeter of each shape
        count += 1
        if count == 1:
            north = coords
            east = coords
            south = coords
            west = coords
            continue
            
        if coords[0] < west[0]:
            west = coords
        if coords[0] > east[0]:
            east = coords
        if coords[1] < south[1]:
            south = coords
        if coords[1] > north[1]:
            north = coords

    maxsize = max(haversine(east, west), haversine(north, south))
    
    lg = 40075 #number of displayed km at zoom 1
    zoom = 1
    while lg > maxsize:
        zoom += 1
        lg /= 2
        
    return zoom-1

def get_coords(coordinates, array_coord=[]):
    """get all the coordinates and set them in a single table without knowing in advance the depth of the tab"""
    if isinstance(coordinates[0], float):
        array_coord.append((coordinates[0], coordinates[1]))
        return array_coord
    
    for item in coordinates:
        get_coords(item,array_coord)

    
            
    