from utils import parameters as pm
from utils import utils
import os
import gdal
import osr

def make_map_Glad2010(assetID, threshold):
    
    aoi_name = utils.get_aoi_name(assetID)
    
    # skip if process already finished 
    clip_map = pm.getGfcDir() + aoi_name + "_" + str(threshold) + '_map_clip.tif'
    print(clip_map)
    
    if os.path.isfile(clip_map): 
        return 'Glad 2010 map already performed'
    
    # align glad with GFC 
    mask = pm.getDwnDir() + aoi_name + '_' + pm.getTypes()[3] + '.tif'
    
    if not os.path.isfile(mask): 
        return 'No dataframe gfc map'
    
    src = gdal.Open(mask)
    proj = osr.SpatialReference(wkt=src.GetProjection())
    bb = utils.get_bounding_box(assetID)
    res = {}
    _, res['x'], _, _, _, res['y']  = src.GetGeoTransform()
    src = None
    
    # align GFC tree cover with segments 
    glad_raw = pm.getDwnDir() + aoi_name + '_treecover2010.tif'
    glad_aligned = pm.getDwnDir() + aoi_name + '_treecover2010_aligned.tif'
    
    if not os.path.isfile(mask): 
        return 'No treecover file'
    
    options = gdal.WarpOptions(
        xRes             = res['x'], 
        yRes             = res['y'], 
        creationOptions  = "COMPRESS=LZW", 
        outputBounds     = [int(bb[i]) for i in bb],
        #options          = 'overwrite',
        dstSRS           = proj
        
    )
    
    ds = gdal.Warp(glad_aligned, glad_raw, options=options)
    ds = None
    
    # Combination FNF 2000
    calc = "(A>={0})*1+(A<{0})*2".format(threshold)
    print(calc)
    
    #combine into national scale map
    calc = "(A==1)*(B==1)*((C==0)+(C>=11))*1+"   # Foret accord
    calc += "(A==1)*(B==1)*( C> 0)*(C < 11)*2+"  # Pertes GLAD < Pertes GFC
    calc += "(A==1)*(B==2)*( C> 0)*(C < 11)*3+"  # Pertes accord
    calc += "(A==1)*(B==2)*((C==0)+(C>=11))*4+"  # Pertes GLAD > Pertes GFC
    calc += "(A==2)*(B==1)*( D==1)*5+"           # Gains accord
    calc += "(A==2)*(B==1)*( D==0)*6+"           # Gains GLAD > Gains GFC
    calc += "(A==2)*(B==2)*( D==1)*7+"           # Gains GLAD < Gains GFC
    calc += "(A==2)*(B==2)*( D==0)*8"            # Non Foret accord
    
    
    
     
    
    
    return 'toto'