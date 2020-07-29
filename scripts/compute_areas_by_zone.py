from utils import parameters as pm
from utils import utils
import os
import pandas as pd
import gdal
from osgeo import osr, gdalconst

def compute_areas_by_zone(assetId, threshold):
    
    aoi_name = utils.get_aoi_name(assetId)
    
    hist_output = pm.getStatDir() + aoi_name + "_stats_clump.csv".format(threshold)
    
    map_raster = pm.getGfcDir() + aoi_name + '_{}_gfc_map.tif'.format(threshold)
    
    #skip if output already exist 
    if os.path.isfile(hist_output):
        print('stats already computed')
        return hist_output
    
    if not os.path.isfile(map_raster): 
        print('No gfc map')
        return None
    
    hist = utils.pixelCount(map_raster)
    
    src = gdal.Open(map_raster)
    proj = osr.SpatialReference(wkt=src.GetProjection())
    bb = utils.get_bounding_box(assetId)
    _, resx, _, _, _, resy  = src.GetGeoTransform()
    src = None
    
    #the prjection is not equal-area. Approximation of the pixel surface is done with the followings : 1° = 111 km
    
    resx_proj = resx * 111321
    
    #convert to hectars
    hist['area'] = utils.toHectar(hist['pixels'], resx_proj)
    
    #treecover_area = hist.loc[hist['code'] == 40 or (hist[code] > 0 and hist['code'] < 30), 'area'].sum()
    #loss_area = hist.loc[host['code'] > 0 and hist['code'] < 30, 'area'].sum()
    
    #drop 0 ha lines and croped values (255)
    hist = hist[(hist['area'] != 0) & (hist['code'] != 255.)]
    hist_file = pm.getStatDir() + aoi_name + "_{}_stats_clump.csv".format(threshold)
    hist.to_csv(hist_file, index=False)  
    
    #reproject zones in EA projection 
    aoi_shp_proj = pm.getTmpDir() + aoi_name + '_proj.shp'
    aoi_shp = pm.getDwnDir() + aoi_name + '.shp'
    command = [
        'ogr2ogr',
        '-t_srs', '"{}"'.format(proj.ExportToProj4()),
        aoi_shp_proj,
        aoi_shp
    ]

    os.system(' '.join(command))
    
    # rasterize the shape
    aoi_raster_tmp = pm.getTmpDir() + aoi_name + '.tif'
    command = [
        'gdal_rasterize',
        '-a', 'id', #manually add when created the shp file
        '-l', aoi_name + '_proj',
        '-ot', 'UInt32', #check if it accept byte
        '-te', str(bb['minx']), str(bb['miny']), str(bb['maxx']), str(bb['maxy']),
        '-tr', str(resx), str(resy),
        '-co', '"COMPRESS=LZW"',
        aoi_shp_proj,
        aoi_raster_tmp
    ]
    
    #print( ' '.join(command))
    os.system(' '.join(command))
    
    #crop to country boundaries
    aoi_raster = pm.getGfcDir() + aoi_name + '.tif'

    options = gdal.WarpOptions(
        dstSRS          = proj,
        outputType      = gdalconst.GDT_Byte,
        creationOptions = "COMPRESS=LZW", 
        cutlineDSName   = aoi_shp,
        cropToCutline   = True
    )
    
    ds = gdal.Warp(aoi_raster, aoi_raster_tmp, options=options)
    ds = None
    
    #compute stats by zone 
    
    # TODO there is no zones in my shapefile 
    
    tmp_stat_clip = pm.getTmpDir() + aoi_name + '_{}_stats_gfc_map.txt'.format(threshold)
    command = [
        'oft-zonal_large_list.py',
        '-um', aoi_raster_tmp,
        '-i', map_raster,
        '-o', tmp_stat_clip,
    ]
    
    #print( ' '.join(command))
    os.system(' '.join(command))
    
    df = pd.read_csv(tmp_stat_clip, delimiter=' ', header=None)
    df = df.loc[:, (df != 0).any(axis=0)] #drop 0 value columns
    df.columns = pm.getZonalLabels() #add the labels
    ########        # TODO merge the name instead of zone code
    df = df.apply(lambda x: utils.toHectar(x, resx_proj) if x.name != 'zone_id' else x)
    
    hist_zonal = pm.getStatDir() + aoi_name + '_{}_stats_gfc_map.csv'.format(threshold)
    df.to_csv(hist_zonal, index=False) 
    
    # clump the results 
    clip_map = pm.getGfcDir() + aoi_name +'_glad_check.tif'
    clump_map = pm.getGfcDir() + aoi_name + '_{}_clump_gfc_map.tif'.format(threshold)
    command = [
        'oft-clump',
        '-i', clip_map,
        '-o', clump_map
    ]
    
    #print(' '.join(command))
    os.system(' '.join(command))
    
    #map histograms on clump 
    clumps = pm.getStatDir() + aoi_name + '_{}_clump_gfc.txt'.format(threshold)
    command = [
        'oft-stat',
        '-um', clump_map,
        '-i', clip_map,
        '-o', clumps
    ]
    
    #print(' '.join(command))
    os.system(' '.join(command))
    
    ##zonal histogram on clumps
    clump_stat = pm.getStatDir() + aoi_name + '_{}_clump_stat_gfc.txt'.format(threshold)
    command = [
        'oft-his',
        '-um', clump_map,
        '-i', clip_map,
        '-o', clump_stat,
        '-maxval', str(255) #don't know what to do with the none values (sea and rivers)
    ]
    
    #print(' '.join(command))
    os.system(' '.join(command))
    
    dz = pd.read_csv(clump_stat, sep=' ', header=None)
    dm = pd.read_csv(clumps, sep=' ', header=None, usecols=[0, 1, 2])
    
    #sortt by patch_id 
    dz = dz.sort_values([0], axis=0, ascending=True, kind='quicksort')
    dm = dm.sort_values([0], axis=0, ascending=True, kind='quicksort')
    
    df = pd.merge(dm, dz, [0])
    
    #not the right values 
    codes = [i for i in range(1,14)]
    label = [
        'patch_id',
        'patch_size',
        'class',
        'nodata',
    ]
    label += codes
    
    df.columns = label
    
    df.to_csv(hist_output, index=False)
    
    return hist_output



