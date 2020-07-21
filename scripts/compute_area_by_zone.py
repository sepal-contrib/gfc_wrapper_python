from utils import parameters as pm
from utils import utils
import os
import pandas as pd


def compute_area_by_zone(assetId, threshold):
    
        aoi_name = utils.get_aoi_name(assetId)
    
    hist_file = pm.getStatDir() + aoi_name + "_stats_clump.csv"
    
    map_raster = pm.getGfcDir() + aoi_name + 'gfc_{}_map_clip_pct.tif'.format(threshold)
    
    #skip if output already exist 
    if os.path.isfile(hist_file):
        return 'stats already computed'
    
    hist = utils.pixel_count(map_raster)
    
    if not os.path.isfile(mask): 
        return 'No gfc map'
    
    src = gdal.Open(map_raster)
    proj = osr.SpatialReference(wkt=src.GetProjection())
    bb = utils.get_bounding_box(assetID)
    res = {}
    _, res['x'], _, _, _, res['y']  = src.GetGeoTransform()
    src = None
    
    #convert to hectars
    hist['area'] = hist['pixels']*res['x']*res['x']/10000
    
    treecover_area = hist.loc[hist['code'] == 40 or (hist[code] > 0 and hist['code'] < 30), 'area'].sum()
    loss_area = hist.loc[host['code'] > 0 and hist['code'] < 30, 'area'].sum()
    
    #create an output file
    filename = utils.getStatDir() + aoi_name + "_" + threshold + '.txt'
    hist.to_csv(filename, index=False)  
    
    #reproject zones in EA projection 
    aoi_shp_proj = pm.getTmpDir() + aoi_name + '_aoi_shp_proj.shp'
    aoi_shp = 'toto'
    command = [
        'ogr2ogr',
        '-t_srs', '"{}"'.format(proj),
        aoi_shp_proj,
        aoi_shp
    ]  
    os.system(' '.join(command))
    
    #compute stats by zone 
    tmp_stat_clip = pm.getTmpDir() + aoi_name + '_tmp_stats_gfc_map_clip.txt'
    command = [
        'oft-zonal_large_list.py',
        '-um', aoi_shp_proj,
        '-i', map_raster,
        '-o', tmp_stat_clip,
        aoi_field 
    ]
    
    os.system(' '.join(command))
    
    #faut trouver d'ou vient cette variable "aoi"
    code = aoi['data']

    df = pd.read_csv(tmp_stat_clip)
    
    #remove the empty line 
    df = df[(df.T != 0).any()]
    
    #add the columns header 
    df.columns= [
        "zone_id", 
        "total", 
        "no_data", 
        "loss_{}".format(max_year), 
        "non_forest", 
        "forest", 
        "gain", 
        "gain_loss"
    ]
    
    df["zones"] = code['id']

    d0 = df[["zones", "zone_id"]].copy()
    d0[[2+1:(max_year+6)]] = df[[1+1:(max_year+6)]]*res['x']*res['x']/10000
    
    filename = utils.getStatDir() + aoi_name + "_stats_gfc_map_clip.csv"
    d0.to_csv(filename, index=False)
    
    #rasterize zones
    aoi_raster = pm.getTmpDir() + aoi_name + "_shp_proj.tif" 
    command = [
        'python',
        pm.getscriptDir()+"/oft-rasterize_attr.py",
        '-v', aoi_shp_proj,
        '-i', map_raster,
        '-o', aoi_raster,
        '-a', aoi_field
    ]
    
    os.system(' '.join(command))

    #clump
    
    command = [
        'oft-clump',
        '-i', gfc_dir,"gfc_",countrycode,"_",threshold,"_map_clip_pct.tif",
        '-o', gfc_dir,"tmp_clump_gfc_",countrycode,"_",threshold,"_map_clip_pct.tif"
    ]
    
    os.system(' '.join(command))
    
    #map histograms on clump 
    command = [
        'oft-stat',
        '-um', paste0(gfc_dir,"tmp_clump_gfc_",countrycode,"_",threshold,"_map_clip_pct.tif"),
        '-i', paste0(gfc_dir,"gfc_",countrycode,"_",threshold,"_map_clip_pct.tif"),
        '-o', paste0(stt_dir,"clump_stats_gfc_",countrycode,"_",threshold,".txt")
    ]
    
    os.system(' '.join(command))
    
    #zonal histogram on clumps
    command = [
        'oft-his',
        '-um', paste0(gfc_dir,"tmp_clump_gfc_",countrycode,"_",threshold,"_map_clip_pct.tif"),
        '-i', paste0(tmp_dir,"aoi_shp_proj_",countrycode,".tif"),
        '-o', paste0(stt_dir,"clump_stats_aoi_shp.txt"),
        '-maxval', 13
    ]
    
    os..system(' '.join(command))
    
    dz = pd.read_csv(paste0(stt_dir,"clump_stats_aoi_shp.txt"))
    dm = pd.read_csv(paste0(stt_dir,"clump_stats_gfc_",countrycode,"_",threshold,".txt"))[[1:3]]

    dz = dz.sort_values('V1', axis=0, ascending=False, inplace=False, kind='quicksort', na_position='last')
    dm = dm.sort_values('V1', axis=0, ascending=False, inplace=False, kind='quicksort', na_position='last')
    
    df = df.join(dz[[3:16]])
    df.columns = [
        "patch_id",
        "patch_size",
        "class",
        "nodata",
        code["id"]
    ]
    
    filename = 'stt_dir,"stats_clump_",countrycode,".csv"'
    df.to_csv(filename)
    
    return 1



