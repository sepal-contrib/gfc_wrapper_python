import geemap
from utils import parameters as pm

def init_gfc_map():
    """initialize a geemap to display the aggregated data"""
    
    #init a map center in 0,0
    m = geemap.Map(
        center=(0, 0),
        zoom=2
    )
    
    #remove layers and controls
    m.clear_layers()
    m.clear_controls()
    
    #use the carto basemap
    m.add_basemap('CartoDB.DarkMatter')
    
    #add the useful controls 
    m.add_control(geemap.ZoomControl(position='topright'))
    m.add_control(geemap.LayersControl(position='topright'))
    m.add_control(geemap.AttributionControl(position='bottomleft'))
    m.add_control(geemap.ScaleControl(position='bottomleft', imperial=False))
    
    #add the legend 
    keys = pm.getMyLabel() #hack to increase the space next to the names
    colors = pm.getColorPalette()
    m.add_legend(legend_keys=keys, legend_colors=colors, position='topleft')

    return m
    