from utils import parameters as pm
from utils import utils
import os
import gdal
import osr


def make_map_theshold_clump(assetID, threshold):
    
    aoi_name = utils.get_aoi_name(assetId)
    
    #skip if outpu already exist 
    ouput_file = pm.getGfcDir() + aoi_name + 'gfc_{}_map_clip_pct_clumps.tif'.format(threshold)
    
    if os.path.isfile(ouput_file):
        return 'gfc clump map already performed'
    
    
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
    
    #combination into national scale map 
    "treecover2000","lossyear","gain","datamask"
    gfc_treecover = pm.getDwnDir() + aoi_name + '_' + pm.getTypes()[0] + '.tif'
    gfc_loss = pm.getDwnDir() + aoi_name + '_' + pm.getTypes()[1] + '.tif'
    gfc_gain = pm.getDwnDir() + aoi_name + '_' + pm.getTypes()[2] + '.tif'
    gfc_datamask = pm.getDwnDir() + aoi_name + '_' + pm.getTypes()[3] + '.tif'
    gfc_tmp_map = pm.getTmpDir() + aoi_name + '_gfc_map.tif'
    
    calc = "(A<={})*((C==1)*50 + (C==0)*30 +".format(threshold) #Non forest 
    calc += "(A>{})*((C==1)*(".format(threshold)
    calc += "(B>0)*51 +" #gain + loss 
    calc += "(B==0)*50" #gain 
    calc += ") + (C==0) * ("
    calc += "(B>0)*B +" #loss
    calc += "(B==0)*40" #stable forest 
    calc +="))"
    
    print(calc)

    command =[
        'gdal_calc.py',
        '-A', gfc_treecover,
        '-B', gfc_loss,
        '-C', gfc_gain,
        '-D', gfc_datamask,
        '--co', 'COMPRESS=LZW',
        '--outfile={}'.format(gfc_tmp_map),
        '--calc="{}"'.format(calc)
    ]
    
    os.system(' '.join(command))
    
    #crop and reproject
    gfc_clip = pm.getTmpDir() + aoi_name + 'gfc_map_clip_clump.tif'

    options = gdal.WarpOptions(
        dstSRS = proj,
        outputType = gdalconst.GDT_Byte,
        creationOptions = "COMPRESS=LZW", 
        cutlineDSName = aoi_shp
    )
    
    ds = gdal.Warp(gfc_clip, gfc_tmp_map, options=options)
    ds = None
    
    #add pseudo colors 
    gfc_pct = pm.getTmpDir() + aoi_name + '_gfc_map_clip_pct_clump.tif'
    command = [
        "(echo {})".format(pm.getUtilsDir()+'color_table_glad.txt'),
        '|',
        'oft-addpct.py',
        gfc_clip,
        gfc_pct
    ]
     
    os.system(' '.join(command))
    
    #compress 
    options = gdal.TranslateOptions(
        outputType = gdalconst.GDT_Byte,
        creationOptions = "COMPRESS=LZW",
    )
    
    gdal.translate(ouput_file, gfc_pct, options)
    
    return 1




