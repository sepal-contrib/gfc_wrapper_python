from utils import parameters as pm
from utils import utils
import os

def make_mspa_ready(assetId, threshold, clip_map):
    
    aoi_name = utils.get_aoi_name(assetId)
    
    #skip if outpu already exist 
    mspa_masked_map = pm.getGfcDir() + aoi_name + '{}_mspa_masked_map.tif'.format(threshold)
    
    if os.path.isfile(mspa_masked_map):
        print('mspa masked map already ready')
        return mspa_masked_map
    
    #create the forest mask for MSPA analysis
    calc = '(A==40)*2' #forest
    calc += '+ ((A>0)*(A<40)+(A>40))*1' #non_forest <=> A != 40
    
    command = [
        'gdal_calc.py',
        '-A', clip_map,
        '--co', '"COMPRESS=LZW"',
        '--outfile={}'.format(mspa_masked_map),
        '--calc="{}"'.format(calc)
    ]
    
    os.system(' '.join(command))
    
    return mspa_masked_map

