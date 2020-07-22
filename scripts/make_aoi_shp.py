import sys
sys.path.append("..") # Adds higher directory to python modules path
from utils import utils
from utils import parameters as pm
import geemap
import shapely.geometry as sg
from osgeo import ogr, osr
import ee

ee.Initialize()

def make_aoi_shp(assetId):

    aoi_name = utils.get_aoi_name(assetId)
    
    #verify that the asset exist
    aoi = ee.FeatureCollection(assetId)
    
    #convert into shapely
    aoiJson = geemap.ee_to_geojson(aoi)
    aoiShp = sg.shape(aoiJson['features'][0]['geometry'])
    
    
    dwnDir = pm.getDwnDir()
    
    # Now convert it to a shapefile with OGR    
    driver = ogr.GetDriverByName('Esri Shapefile')
    ds = driver.CreateDataSource('{0}{1}.shp'.format(dwnDir, aoi_name))
    layer = ds.CreateLayer('', None, ogr.wkbPolygon)

    # Add one attribute
    layer.CreateField(ogr.FieldDefn('id', ogr.OFTInteger))
    defn = layer.GetLayerDefn()

    # Create a new feature (attribute and geometry)
    feat = ogr.Feature(defn)
    feat.SetField('id', 123)
    
    # Make a geometry, from Shapely object
    geom = ogr.CreateGeometryFromWkb(aoiShp.wkb)
    feat.SetGeometry(geom)
    
    layer.CreateFeature(feat)
    feat = geom = None  # destroy these
    
    # Save and close everything
    ds = layer = feat = geom = None
    
    #add the spatial referecence
    spatialRef = osr.SpatialReference()
    spatialRef.ImportFromEPSG(4326)
    
    spatialRef.MorphToESRI()
    file = open('{0}{1}.prj'.format(dwnDir, aoi_name), 'w')
    file.write(spatialRef.ExportToWkt())
    file.close()
    
    return '{0}{1}.shp'.format(dwnDir, aoi_name)