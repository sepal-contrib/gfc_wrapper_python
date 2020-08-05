import geemap

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

    return m
    